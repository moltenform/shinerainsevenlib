
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.core import *
import os


class TestImageTypeFromExtension:
    def testBasic(self):
        assert SrssMedia.imageTypeFromExtension('a.avif') == 'avif'
        assert SrssMedia.imageTypeFromExtension('a.bmp') == 'bmp'
        assert SrssMedia.imageTypeFromExtension('a.gif') == 'gif'
        assert SrssMedia.imageTypeFromExtension('a.heic') == 'heic'
        assert SrssMedia.imageTypeFromExtension('a.jpeg') == 'jpg'
        assert SrssMedia.imageTypeFromExtension('a.jpg') == 'jpg'
        assert SrssMedia.imageTypeFromExtension('a.jxl') == 'jxl'
        assert SrssMedia.imageTypeFromExtension('a.lossless.webp') == 'webp'
        assert SrssMedia.imageTypeFromExtension('a.lossy.webp') == 'webp'
        assert SrssMedia.imageTypeFromExtension('a.mpo.jpg') == 'jpg'
        assert SrssMedia.imageTypeFromExtension('a.png') == 'png'
        assert SrssMedia.imageTypeFromExtension('a.tif') == 'tif'
        assert SrssMedia.imageTypeFromExtension('a.tiff') == 'tif'
    
    def testNotSupported(self):
        assert SrssMedia.imageTypeFromExtension('a.txt') == None
    
    def testAliases(self):
        assert SrssMedia.imageTypeFromExtension('a.png_large') == 'png'
        assert SrssMedia.imageTypeFromExtension('a.jfif') == 'jpg'
    
    def testEdgeCases(self):
        assert SrssMedia.imageTypeFromExtension('') == None
        assert SrssMedia.imageTypeFromExtension('.') == None
        assert SrssMedia.imageTypeFromExtension('a.') == None
        assert SrssMedia.imageTypeFromExtension('a') == None
        assert SrssMedia.imageTypeFromExtension('jpg') == None
    

class TestImageTypeFromContents:
    def testBasic(self):
        os.chdir(files.getParent(files.getParent(__file__)))
        assert SrssMedia.imageTypeFromContents('collat/img/a.avif') == 'avif'
        assert SrssMedia.imageTypeFromContents('collat/img/a.bmp') == 'bmp'
        assert SrssMedia.imageTypeFromContents('collat/img/a.dng') == 'dng'
        assert SrssMedia.imageTypeFromContents('collat/img/a.gif') == 'gif'
        assert SrssMedia.imageTypeFromContents('collat/img/a.heic') == 'heic'
        assert SrssMedia.imageTypeFromContents('collat/img/a.j.jxl') == 'jxl'
        assert SrssMedia.imageTypeFromContents('collat/img/a.jpeg') == 'jpg'
        assert SrssMedia.imageTypeFromContents('collat/img/a.jpg') == 'jpg'
        assert SrssMedia.imageTypeFromContents('collat/img/a.l.jxl') == 'jxl'
        assert SrssMedia.imageTypeFromContents('collat/img/a.lookslikempo.jpg') == 'jpg'
        assert SrssMedia.imageTypeFromContents('collat/img/a.lossless.jxl') == 'jxl'
        assert SrssMedia.imageTypeFromContents('collat/img/a.lossless.webp') == 'webp'
        assert SrssMedia.imageTypeFromContents('collat/img/a.lossy.webp') == 'webp'
        assert SrssMedia.imageTypeFromContents('collat/img/a.mpo.jpg') == 'jpg'
        assert SrssMedia.imageTypeFromContents('collat/img/a.png') == 'png'
        assert SrssMedia.imageTypeFromContents('collat/img/a.tif') == 'tif'
        assert SrssMedia.imageTypeFromContents('collat/img/a.tiff') == 'tif'
        assert SrssMedia.imageTypeFromContents('collat/img/a.txt') == 'unknown'

    def testMpo(self):
        os.chdir(files.getParent(files.getParent(__file__)))
        assert SrssMedia.imageTypeFromContents('collat/img/a.jpeg', treatMpoAsJpg=False) == 'jpg'
        assert SrssMedia.imageTypeFromContents('collat/img/a.jpg', treatMpoAsJpg=False) == 'jpg'
        assert SrssMedia.imageTypeFromContents('collat/img/a.lookslikempo.jpg', treatMpoAsJpg=False) == 'mpo'
        
        # this example image is a real mpo, from https://github.com/odrevet/Multi-Picture-Object
        assert SrssMedia.imageTypeFromContents('collat/img/a.mpo.jpg', treatMpoAsJpg=False) == 'mpo'


class TestVidType:
    def getVidType(self, path):
        os.chdir(files.getParent(files.getParent(__file__)))
        results = SrssMedia.getAudAndVidCodec(path)
        if results.err:
            return 'ERR:' + results.err
        else:
            return [results.audFormat, results.vidFormat]
        
    def testBasic(self):
        os.chdir(files.getParent(files.getParent(__file__)))
        assert self.getVidType("collat/media/flac.flac") == ["flac", None]
        assert self.getVidType("collat/media/h264.mp4") == [None, 'h264']
        assert self.getVidType("collat/media/h264_and_flac_aud.mkv") == ["flac", 'h264']
        assert self.getVidType("collat/media/h264_and_m4a_aud.mp4") == ["aac", 'h264']
        assert self.getVidType("collat/media/webm.webm") == [None, 'vp9']
        
        # not a video
        assert self.getVidType("collat/img/a.txt") == 'ERR:Invalid data found when processing input'

        # file not exist
        assert self.getVidType("notexist.txt") == 'ERR:No such file or directory'
