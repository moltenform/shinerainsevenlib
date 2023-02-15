
from . import common_compression
from .. import files
from ..common_util import *
from .file_extensions import *

def changeWrapperLossless(input, output, ffmpegBin=None):
    ffmpegBin = ffmpegBin or 'ffmpeg'
    args = [ffmpegBin, '-nostdin', '-i', '%input%', '-acodec', 'copy', '-vcodec', 'copy', output]
    common_compression.sendToShellCommon(args, input, output)
    
def separateVideoLossless(input, output, ffmpegBin=None):
    ffmpegBin = ffmpegBin or 'ffmpeg'
    args = [ffmpegBin, '-nostdin', '-i', '%input%', '-an', '-vcodec', 'copy', output]
    common_compression.sendToShellCommon(args, input, output)

def separateAudioLossless(input, output, ffmpegBin=None):
    ffmpegBin = ffmpegBin or 'ffmpeg'
    args = [ffmpegBin, '-nostdin', '-i', '%input%', '-vn', '-acodec', 'copy', output]
    common_compression.sendToShellCommon(args, input, output)
    
def combineAudioVideoLossless(inputA, inputV, output, ffmpegBin=None):
    combineAudioVideo(inputA, inputV, output, codecA='copy', codecV='copy', ffmpegBin=ffmpegBin)

def combineAudioVideoFlac(inputA, inputV, output, ffmpegBin=None):
    extraParams = dict(compression_level='12')
    combineAudioVideo(inputA, inputV, output, codecA='flac', codecV='copy', ffmpegBin=ffmpegBin, extraParams=extraParams)

def combineAudioVideo(inputA, inputV, output, codecA='copy', codecV='copy', ffmpegBin=None, extraParams=None):
    ffmpegBin = ffmpegBin or 'ffmpeg'
    assertTrue(files.exists(inputV))
    args = [ffmpegBin, '-nostdin', '-i', '%input%', '-i', inputV, '-c:a', codecA, '-c:v', codecV]
    for param in (extraParams or {}):
        args.append('-' + param)
        if extraParams[param] is not None:
            args.append(extraParams[param])

    args.append(output)
    common_compression.sendToShellCommon(args, inputA, output)
 
def getCodec(input):
    args = [ffmpegBin, '-nostdin', '-i', input]
    
def getImageType(input):
    from PIL import Image
    im = Image.open(input)
    format = im.format
    if format == 'MPO':
        format = 'JPG'
    return format

def getAudAndVidCodec(input, retrieveAllowedStatus=False, expectVidStream=True, ffmpegBin=None):
    infoRef = Bucket(stderr='')
    try:
        return getAudAndVidCodecImpl(input, infoRef, retrieveAllowedStatus=retrieveAllowedStatus, 
            expectVidStream=expectVidStream, ffmpegBin=ffmpegBin)
    except Exception as e:
        trace(input)
        trace(infoRef.stderr)
        raise
    
def getAudAndVidCodecImpl(input, infoRef, retrieveAllowedStatus=False, expectVidStream=True, ffmpegBin=None):
    ffmpegBin = ffmpegBin or 'ffmpeg'
    args = [ffmpegBin, '-nostdin', '-i', input]
    ret, stdout, stderr = files.run(args, throwOnFailure=None)
    stderr = stderr.decode('utf-8').replace('\r\n', '\n')
    stderr = stderr.replace('At least one output file must be specified', '(Intentional err)')
    infoRef.stderr = stderr
    audFormat = None
    vidFormat = None
    attempts = [
        '\n  Stream #?:$(eng): ',
        '\n  Stream #?:$(und): ',
        '\n  Stream #?:$(rus): ',
        '\n  Stream #?:$: ',
        '\n  Stream #?:$[0x1c0]: ',
        '\n  Stream #?:$[0x1e0]: ',
        '\n  Stream #?:$[0x1](und): ',
        '\n  Stream #?:$[0x1](eng): ',
        '\n  Stream #?:$[0x$$](und): ',
        '\n  Stream #?:$[0x$$](eng): ',
        '\n  Stream #?:$[0x$$](rus): ',
        '\n  Stream #?:$[0x10$]: ',
        '\n  Stream #?(eng): ',
        '\n  Stream #?(und): ',
        '\n  Stream #?(rus): ',
        '\n  Stream #?: ',]
    
    checked = {}
    for streamnum in range(3):
        for streamnumpart in range(3):
            for baseattempt in attempts:
                attempt = baseattempt.replace('?', str(streamnum))
                attempt = attempt.replace('$$', str(streamnumpart + 1))
                attempt = attempt.replace('$', str(streamnumpart))
                if checked.get(attempt):
                    continue
                checked[attempt] = True
                #~ trace(attempt)
                if attempt in stderr:
                    s = stderr.split(attempt)[1]
                    if s.startswith('Audio: '):
                        assertTrue(audFormat is None, 'two audio tracks?', input)
                        audFormat = getAFormat(s[len('Audio: '):], retrieveAllowedStatus=retrieveAllowedStatus)
                    elif s.startswith('Video: '):
                        assertTrue(vidFormat is None, 'two video tracks?', input)
                        vidFormat =  getVFormat(s[len('Video: '):], retrieveAllowedStatus=retrieveAllowedStatus)
                    elif s.startswith('Data: '):
                        pass
                    else:
                        assertTrue(False, 'unknown stream type', input)
    
    if expectVidStream:
        if not vidFormat and input.lower().endswith('.mp4'):
            assertTrue(False, 'please put mp4 audio into a m4a extension')
        assertTrue(vidFormat, 'no video stream?', input)
    return vidFormat, audFormat



vFormatsFfmpeg = dict(
    av1=('av1', True),
    wmv2=('wmv2', False),
    wmv3=('wmv3', False),
    mpeg1video=('mpeg1', True),
    mpeg2video=('mpeg2', True),
    mpeg4=('mpeg4', True),
    mjpeg=('mjpeg', True),
    theora=('theora', True),
    h263=('h263', True),
    h264=('h264', True),
    hevc=('h265', True),
    vp6f=('vp6', True),
    vp8=('vp8', True),
    vp9=('vp9', True),
    png=('png', 4 * 1024 * 1024),
    rawvideo=('rawvideo', 1),
    cinepak=('cinepak', 1),
    msvideo1=('msvideo1', 1),
    rpza=('applequicktime_rpza', False),
    svq1=('applequicktime_svq1', False),
)

def getVFormat(s, retrieveAllowedStatus=False):
    s = s.replace(',', ' ')
    firstword = s.split(' ')[0]
    if firstword not in vFormatsFfmpeg:
        assertTrue(False, 'unknown or unwanted vid format', s)
    if retrieveAllowedStatus:
        return vFormatsFfmpeg[firstword]
    else:
        return vFormatsFfmpeg[firstword][0]

aFormatsFfmpeg = dict(
    flac=('flac', True),
    mp2=('mp2', True),
    mp3=('mp3', True),
    pcm_u8=('smallwav_u8', True),
    pcm_s16le=('bigwav_s16le', 1),
    pcm_s16be=('bigwav_s16be', 1),
    adpcm_ms=('bigwav_adpcm', 1),
    vorbis=('vorbis', True),
    opus=('opus', True),
    aac=('aac', True),
    qdm2=('applequicktime_qdm2', False),
    wmav2=('wma2', False),
)

    
def getAFormat(s, retrieveAllowedStatus=False):
    s = s.replace(',', ' ')
    firstword = s.split(' ')[0]
    if firstword not in aFormatsFfmpeg:
        assertTrue(False, 'unknown or unwanted audio format', s)
    if retrieveAllowedStatus:
        return aFormatsFfmpeg[firstword]
    else:
        return aFormatsFfmpeg[firstword][0]