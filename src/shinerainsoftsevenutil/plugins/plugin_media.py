
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

from .plugin_fileexts import *
import re

def imageTypeFromExtension(path):
    "Gets the image type like `jpg`, `png`, etc"
    ext = files.getExt(path, removeDot=False)
    if ext in mostCommonImageExtAlternatives:
        ext = mostCommonImageExtAlternatives[ext]
    
    if ext in mostCommonImageExt:
        return ext.replace('.', '')
    else:
        return None

def imageTypeFromContents(path, treatMpoAsJpg=True):
    "Gets the image type like `jpg`, `png`, etc. Works even if extension is wrong."
    from PIL import Image

    with open(path, 'rb') as f:
        firstBytes = f.read(128)
        if b'\x0c\x4a\x58\x4c' in firstBytes:
            return 'jxl'
        if b'ftypheic' in firstBytes:
            return 'heic'
        
    im = Image.open(f)
    format = str(im.format).lower()
    if format == 'tiff':
        format = 'tif'
    elif format == 'mpo' and treatMpoAsJpg:
        # some cameras save their images in a mpo form,
        # but 99% of the time we want to treat the file as a typical jpg image.
        format = 'jpg'
    elif format == 'jpeg':
        format = 'jpg'

    return format

def getAudAndVidCodec(inPath, ffmpegPath='ffmpeg'):
    results = Bucket(audFormat=None, vidFormat=None, fullResults=None, err=None)
    try:
        _getAudAndVidCodecImpl(inPath, results, ffmpegPath=ffmpegPath)
    except Exception as e:
        results.err = e
    return results

def _getAudAndVidCodecImpl(inPath, results, ffmpegPath='ffmpeg'):
    args = [ffmpegPath, '-nostdin', '-i', inPath]
    _ret, _stdout, stderr = files.run(args, throwOnFailure=None, confirmExists=True)
    stderr = stderr.decode('utf-8').replace('\r\n', '\n')
    stderr = stderr.replace('At least one output file must be specified', '(Intentional err)')
    results.fullResults = stderr
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

    results.audFormat=audFormat
    results.vidFormat=vidFormat


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

