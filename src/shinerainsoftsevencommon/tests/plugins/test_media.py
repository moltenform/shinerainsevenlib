# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv3 license.

import pytest
import tempfile
import shutil
import os

from ... import files
from ... import common_media
from ..test_files import fixture_dir

def isFfmpegOnPath():
    if files.exists('ffmpeg') or shutil.which('ffmpeg'):
        return True
    else:
        print('Note::: Skipping test, ffmpeg not found on path')

@pytest.mark.skipif('not isFfmpegOnPath()')
class TestMedia(object):
    def _getMediaMetadata(self, f):
        s = ''
        s += 'ext=' + files.getext(f)
        first8Bytes = files.readall(f, 'rb')[0:8]
        s += ',first8Bytes=' + str(first8Bytes)
        aFormat, vFormat = common_media.getAudAndVidCodec(f)
        s += ',aFormat=' + str(aFormat)
        s += ',vFormat=' + str(vFormat)
        s += ','+ common_media.getMediaHash(f)
        return s
    
    def _getInPath(self):
        myParent = files.getparent(os.path.abspath(__file__))
        return files.join(myParent, 'collat/clip.mkv')
    
    def test_identity(self, fixture_dir):
        got = self._getMediaMetadata(self._getInPath())
        assert got == r"ext=mkv,first8Bytes=b'\x1aE\xdf\xa3\xa3B\x86\x81',aFormat=aac,vFormat=h264,0,v,MD5=b58d6fd2695f5e8df33721ebf1f466d2;1,a,MD5=58bc68a13cae947d89fff2a418f702ca"
    
    def test_changeWrapperLossless(self, fixture_dir):
        common_media.changeWrapperLossless(self._getInPath(), fixture_dir + '/out.mp4')
        got = self._getMediaMetadata(fixture_dir + '/out.mp4')
        assert got == r"ext=mp4,first8Bytes=b'\x00\x00\x00 ftyp',aFormat=aac,vFormat=h264,0,v,MD5=b58d6fd2695f5e8df33721ebf1f466d2;1,a,MD5=58bc68a13cae947d89fff2a418f702ca"

    def test_separateAudioLossless(self, fixture_dir):
        common_media.separateAudioLossless(self._getInPath(), fixture_dir + '/out.m4a')
        got = self._getMediaMetadata(fixture_dir + '/out.m4a')
        assert got == r"ext=m4a,first8Bytes=b'\x00\x00\x00\x1cftyp',aFormat=aac,vFormat=None,0,a,MD5=58bc68a13cae947d89fff2a418f702ca"
        
    def test_separateVideoLossless(self, fixture_dir):
        common_media.separateVideoLossless(self._getInPath(), fixture_dir + '/out.m4v')
        got = self._getMediaMetadata(fixture_dir + '/out.m4v')
        assert got == r"ext=m4v,first8Bytes=b'\x00\x00\x00 ftyp',aFormat=None,vFormat=h264,0,v,MD5=b58d6fd2695f5e8df33721ebf1f466d2"
        
    def test_combineAudioVideoLossless(self, fixture_dir):
        common_media.separateAudioLossless(self._getInPath(), fixture_dir + '/out.m4a')
        common_media.separateVideoLossless(self._getInPath(), fixture_dir + '/out.m4v')
        common_media.combineAudioVideoLossless(fixture_dir + '/out.m4a', fixture_dir + '/out.m4v', fixture_dir + '/out_combined.mp4')
        got = self._getMediaMetadata(fixture_dir + '/out_combined.mp4')
        assert got == r"ext=mp4,first8Bytes=b'\x00\x00\x00 ftyp',aFormat=aac,vFormat=h264,0,v,MD5=b58d6fd2695f5e8df33721ebf1f466d2;1,a,MD5=58bc68a13cae947d89fff2a418f702ca"
        
    def test_combineAudioVideoFlac(self, fixture_dir):
        common_media.separateAudioLossless(self._getInPath(), fixture_dir + '/out.m4a')
        common_media.separateVideoLossless(self._getInPath(), fixture_dir + '/out.m4v')
        common_media.combineAudioVideoFlac(fixture_dir + '/out.m4a', fixture_dir + '/out.m4v', fixture_dir + '/out_combined.mkv')
        got = self._getMediaMetadata(fixture_dir + '/out_combined.mkv')
        # flac is lossless, but it's ok that m4a->flac changes the checksum,
        # most players don't play back lossy formats like m4a completely perfectly.
        assert got == r"ext=mkv,first8Bytes=b'\x1aE\xdf\xa3\xa3B\x86\x81',aFormat=flac,vFormat=h264,0,v,MD5=b58d6fd2695f5e8df33721ebf1f466d2;1,a,MD5=571f8cacb69045b73da2f532839dc887"
        



