
import re

from . import common_compression
from .. import files
from ..common_util import *
from .file_extensions import *

def changeWrapperLossless(inPath, outPath, ffmpegPath=None):
    ffmpegPath = ffmpegPath or 'ffmpeg'
    args = [ffmpegPath, '-nostdin', '-i', '%input%', '-acodec', 'copy', '-vcodec', 'copy', '%output%']
    common_compression.sendToShellCommon(args, inPath, outPath)
    
def separateVideoLossless(inPath, outPath, ffmpegPath=None):
    ffmpegPath = ffmpegPath or 'ffmpeg'
    args = [ffmpegPath, '-nostdin', '-i', '%input%', '-an', '-vcodec', 'copy', '%output%']
    common_compression.sendToShellCommon(args, inPath, outPath)

def separateAudioLossless(inPath, outPath, ffmpegPath=None):
    ffmpegPath = ffmpegPath or 'ffmpeg'
    args = [ffmpegPath, '-nostdin', '-i', '%input%', '-vn', '-acodec', 'copy', '%output%']
    common_compression.sendToShellCommon(args, inPath, outPath)
    
def combineAudioVideoLossless(inPathA, inputV, outPath, ffmpegPath=None):
    combineAudioVideo(inPathA, inputV, outPath, codecA='copy', codecV='copy', ffmpegPath=ffmpegPath)

def combineAudioVideoFlac(inPathA, inputV, outPath, ffmpegPath=None):
    extraParams = dict(compression_level='12')
    combineAudioVideo(inPathA, inputV, outPath, codecA='flac', codecV='copy', ffmpegPath=ffmpegPath, extraParams=extraParams)

def combineAudioVideo(inPathA, inputV, outPath, codecA='copy', codecV='copy', ffmpegPath=None, extraParams=None):
    ffmpegPath = ffmpegPath or 'ffmpeg'
    assertTrue(files.exists(inputV))
    args = [ffmpegPath, '-nostdin', '-i', '%input%', '-i', inputV, '-c:a', codecA, '-c:v', codecV]
    for param in (extraParams or {}):
        args.append('-' + param)
        if extraParams[param] is not None:
            args.append(extraParams[param])

    args.append('%output%')
    common_compression.sendToShellCommon(args, inPathA, outPath)
 
def getCodec(inPath):
    args = [ffmpegPath, '-nostdin', '-i', inPath]
    
def getImageType(inPath):
    from PIL import Image
    im = Image.open(inPath)
    format = im.format
    if format == 'MPO':
        format = 'JPG'
    return format

def getAudAndVidCodec(inPath, ffmpegPath=None):
    captureContextForDebugging = Bucket(stderr='')
    try:
        return getAudAndVidCodecImpl(inPath, captureContextForDebugging, ffmpegPath=ffmpegPath)
    except Exception as e:
        trace(inPath)
        trace(captureContextForDebugging.stderr)
        raise
    
def getAudAndVidCodecImpl(inPath, captureContextForDebugging, ffmpegPath=None):
    ffmpegPath = ffmpegPath or 'ffmpeg'
    args = [ffmpegPath, '-nostdin', '-i', inPath]
    ret, stdout, stderr = files.run(args, throwOnFailure=None)
    stderr = stderr.decode('utf-8').replace('\r\n', '\n')
    stderr = stderr.replace('At least one output file must be specified', '(Intentional err)')
    captureContextForDebugging.stderr = stderr
    audFormat = None
    vidFormat = None
    attempts = [
        r'\n  Stream #[0-9]\((?:eng|und|rus)\): ',
        r'\n  Stream #[0-9]:[0-9]\[0x[0-9a-f]+\]\((?:eng|und|rus)\): ',
        r'\n  Stream #[0-9]:[0-9]\[0x[0-9a-f]+\]: ',
        r'\n  Stream #[0-9]:[0-9]\((?:eng|und|rus)\): ',
        r'\n  Stream #[0-9]:[0-9]: ',
        r'\n  Stream #[0-9]: ',
    ]
    
    for attempt in attempts:
        pts = re.split(attempt, stderr)
        trace(attempt, pts)
        pts.pop(0)
        for line in pts:
            s = line.split('\n')[0]
            if s.startswith('Audio: '):
                assertTrue(audFormat is None, 'two audio tracks?', inPath)
                audFormat = _getAFormat(s[len('Audio: '):])
            elif s.startswith('Video: '):
                assertTrue(vidFormat is None, 'two video tracks?', inPath)
                vidFormat =  _getVFormat(s[len('Video: '):])
            elif s.startswith('Data: '):
                pass
            else:
                assertTrue(False, 'unknown stream type', s, inPath)

    return vidFormat, audFormat


aFormatsFfmpeg = dict(
    flac='flac',
    mp2='mp2',
    mp3='mp3',
    pcm_u8='smallwav_u8',
    pcm_s16le='bigwav_s16le',
    pcm_s16be='bigwav_s16be',
    adpcm_ms='bigwav_adpcm',
    vorbis='vorbis',
    opus='opus',
    aac='aac',
    qdm2='applequicktime_qdm2',
    wmav2='wma2',
)

vFormatsFfmpeg = dict(
    av1='av1',
    wmv2='wmv2',
    wmv3='wmv3',
    mpeg1video='mpeg1',
    mpeg2video='mpeg2',
    mpeg4='mpeg4',
    mjpeg='mjpeg',
    theora='theora',
    h263='h263',
    h264='h264',
    hevc='h265',
    vp6f='vp6',
    vp8='vp8',
    vp9='vp9',
    png='png',
    rawvideo='rawvideo',
    cinepak='cinepak',
    msvideo1='msvideo1',
    rpza='applequicktime_rpza',
    svq1='applequicktime_svq1',
)

def _getAFormat(s):
    s = s.replace(',', ' ')
    firstWord = s.split(' ')[0]
    if firstWord not in aFormatsFfmpeg:
        assertTrue(False, 'unknown audio format', s, firstWord)
    
    return aFormatsFfmpeg[firstWord]

def _getVFormat(s):
    s = s.replace(',', ' ')
    firstWord = s.split(' ')[0]
    if firstWord not in vFormatsFfmpeg:
        assertTrue(False, 'unknown vid format', s, firstWord)
    
    return vFormatsFfmpeg[firstWord]
    


def getMediaHash(inPath, excludeVideo=False, hashType='md5', ffmpegPath=None):
    ffmpegPath = ffmpegPath or 'ffmpeg'
    args = ['ffmpeg', '-nostdin', '-i', inPath]
    if excludeVideo:
        # prevent ffmpeg from doing creative things like getting id3image as a videostream
        args.extend(['-vn'])
    
    args.extend(['-f', 'streamhash', '-hash', hashType, '-'])
    # By default audio frames are converted to signed 16-bit raw audio and video frames to raw video before computing the hash
    # (so don't use -c)
    retcode, stdout, stderr = files.run(args)
    stdout = stdout.decode('utf-8')
    stdout = stdout.replace('\r\n', '\n').replace('\n', ';')
    return stdout


