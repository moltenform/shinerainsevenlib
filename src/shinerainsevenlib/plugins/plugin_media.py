
# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv2.1 License

import re as _re
from .. import files as _files
from . import plugin_fileexts as _plugin_fileexts
from ..core import assertTrue as _assertTrue

def imageTypeFromExtension(path):
    "Gets the image type like `jpg`, `png`, etc or None if this is not a common image type."
    ext = _files.getExt(path, removeDot=False)
    if ext in _plugin_fileexts.mostCommonImageExtAlternatives:
        ext = _plugin_fileexts.mostCommonImageExtAlternatives[ext]

    if ext in _plugin_fileexts.mostCommonImageExt:
        return ext.replace('.', '')
    else:
        return None

# for more, see pages like
# http://fileformats.archiveteam.org/wiki/JPEG
def imageTypeFromContents(path, treatMpoAsJpg=True):
    "Gets the image type like `jpg`, `png`, etc. Works even if extension is wrong."
    from PIL import Image

    with open(path, 'rb') as f:
        firstBytes = f.read(128)
        if b'ftypheic' in firstBytes:
            return 'heic'
        elif b'ftypavif' in firstBytes:
            return 'avif'
        elif b'\x0c\x4a\x58\x4c' in firstBytes:
            return 'jxl'
        elif firstBytes.startswith(b'\xff\x0a'):
            return 'jxl'

    try:
        with Image.open(path) as im:
            imFormat = str(im.format).lower()
            if imFormat == 'tiff':
                if _evidenceOfDng(im):
                    imFormat = 'dng'
                else:
                    imFormat = 'tif'
            elif imFormat == 'mpo' and treatMpoAsJpg:
                # some cameras save their images in a mpo form,
                # but 99% of the time we want to treat the file as a typical jpg image.
                imFormat = 'jpg'
            elif imFormat == 'jpeg':
                imFormat = 'jpg'

    except Image.UnidentifiedImageError:
        return 'unknown'

    return imFormat

def _evidenceOfDng(im):
    from PIL.TiffTags import TAGS
    for key in im.tag_v2:
        nameOfTag = TAGS.get(key, '')
        if 'DNG' in nameOfTag:
            return True

    return False


def getAudAndVidCodec(inPath, customFn=None):
    """Given a container format, determine the actual encoding.
    For example, a .mp4 video could internally be x264 or x265,
    and the audio could be aac or wav."""
    
    class AudAndVidCodecResults:
        def __init__(self, audFormat=None, vidFormat=None, fullResults=None, err=None):
            self.audFormat = audFormat
            self.vidFormat = vidFormat
            self.fullResults = fullResults
            self.err = err

    results = AudAndVidCodecResults()
    try:
        _getAudAndVidCodecImpl(inPath, results, customFn=customFn)
    except Exception as e:
        results.err = e
    
    return results

def _getAudAndVidCodecImpl(inPath, results, customFn=None):
    if customFn:
        _ret, _stdout, stderr = customFn(inPath, results)
    else:
        args = ['ffmpeg', '-nostdin', '-i', inPath]
        _ret, _stdout, stderr = _files.run(args, throwOnFailure=None, confirmExists=True)
    
    stderr = stderr.decode('utf-8').replace('\r\n', '\n')
    expectedErrSeen = False
    if 'At least one output file must be specified' in stderr:
        # take this out of the stderr returned to user, or it's misleading
        expectedErrSeen = True
        stderr = stderr.replace('At least one output file must be specified', '(Placeholder)')
    
    results.fullResults = stderr
    if 'Error opening input: Invalid data found when processing input' in stderr:
        # often happens for unrecognized input formats / non-video files
        results.err = RuntimeError('Invalid data found when processing input')
        return
    elif 'Error opening input: No such file or directory' in stderr:
        results.err = RuntimeError('No such file or directory')
        return
    elif not expectedErrSeen:
        results.err = RuntimeError('Could not interpret the file')
        return

    audFormat = None
    vidFormat = None
    attempts = [
        r'\n\s*Stream #[0-9]\((?:[a-z]{3})\): ',
        r'\n\s*Stream #[0-9]:[0-9]\[0x[0-9a-f]+\]\((?:[a-z]{3})\): ',
        r'\n\s*Stream #[0-9]:[0-9]\[0x[0-9a-f]+\]: ',
        r'\n\s*Stream #[0-9]:[0-9]\((?:[a-z]{3})\): ',
        r'\n\s*Stream #[0-9]:[0-9]: ',
        r'\n\s*Stream #[0-9]: ',
    ]

    for attempt in attempts:
        pts = _re.split(attempt, stderr)
        pts.pop(0)
        for line in pts:
            s = line.split('\n')[0]
            if s.startswith('Audio: '):
                _assertTrue(audFormat is None, 'two audio tracks?', inPath)
                audFormat = _getAFormat(s[len('Audio: ') :])
            elif s.startswith('Video: '):
                _assertTrue(vidFormat is None, 'two video tracks?', inPath)
                vidFormat = _getVFormat(s[len('Video: ') :])
            elif s.startswith('Data: '):
                pass
            else:
                _assertTrue(False, 'unknown stream type', s, inPath)

    if audFormat is None and vidFormat is None:
        results.err = RuntimeError('No streams found')
        return
    
    results.audFormat = audFormat
    results.vidFormat = vidFormat

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
        _assertTrue(False, 'unknown audio format', s, firstWord)

    return aFormatsFfmpeg[firstWord]

def _getVFormat(s):
    s = s.replace(',', ' ')
    firstWord = s.split(' ')[0]
    if firstWord not in vFormatsFfmpeg:
        _assertTrue(False, 'unknown vid format', s, firstWord)

    return vFormatsFfmpeg[firstWord]
