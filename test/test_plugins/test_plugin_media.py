
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

import pytest
from src.shinerainsoftsevenutil.standard import *
from src.shinerainsoftsevenutil.plugins.plugin_testhelpers import *
from src.shinerainsoftsevenutil.core import assertException
from PIL import Image

class TestPluginMedia:
    def testImageTypeFromExtension(self):
        fn = lambda s: SrssMedia.imageTypeFromExtension(s)
        
        # standard ones
        assert fn('a.avif') == 'avif'
        assert fn('a.bmp') == 'bmp'
        assert fn('a.gif') == 'gif'
        assert fn('a.heic') == 'heic'
        assert fn('a.jpeg') == 'jpg'
        assert fn('a.jpg') == 'jpg'
        assert fn('a.jxl') == 'jxl'
        assert fn('a.lossless.webp') == 'webp'
        assert fn('a.lossy.webp') == 'webp'
        assert fn('a.mpo.jpg') == 'jpg'
        assert fn('a.png') == 'png'
        assert fn('a.tif') == 'tif'
        assert fn('a.tiff') == 'tif'

        # not supported
        assert fn('a.txt') == None

        # aliases
        assert fn('a.png_large') == 'png'
        assert fn('a.jfif') == 'jpg'

        # edge cases
        assert fn('') == None
        assert fn('.') == None
        assert fn('a.') == None
        assert fn('a') == None
        assert fn('jpg') == None
        
    def testImageTypeFromContents(self):
        fn = lambda s,treatMpoAsJpg=True: SrssMedia.imageTypeFromContents(f'test/collat/images/{s}', treatMpoAsJpg)

        assert fn('a.avif') == 'avif'
        assert fn('a.bmp') == 'bmp'
        assert fn('a.gif') == 'gif'
        assert fn('a.heic') == 'heic'
        assert fn('a.jpeg') == 'jpg'
        assert fn('a.jpg') == 'jpg'
        assert fn('a.l.jxl') == 'jxl'
        assert fn('a.lossless.jxl') == 'jxl'
        assert fn('a.j.jxl') == 'jxl'
        assert fn('a.lossless.webp') == 'webp'
        assert fn('a.lossy.webp') == 'webp'
        assert fn('a.mpo.jpg') == 'jpg'
        assert fn('a.png') == 'png'
        assert fn('a.tif') == 'tif'
        assert fn('a.tiff') == 'tif'
        
        # not an image
        assertException(lambda: fn('a.txt'), Image.UnidentifiedImageError,)

        # file not exist
        assertException(lambda: fn('notexist.txt'), FileNotFoundError)

        # mpo case
        assert fn('a.mpo.jpg', treatMpoAsJpg=True) == 'jpg'
        assert fn('a.mpo.jpg', treatMpoAsJpg=False) == 'mpo'

    def testGetAudAndVidCodec(self):
        def fn(s):
            results = SrssMedia.getAudAndVidCodec(f'test/collat/media/{s}')
            if results.err:
                return 'ERR:' + results.err
            else:
                return [results.audFormat, results.vidFormat]
        
        assert fn("flac.flac") == ["flac", None]
        assert fn("h264.mp4") == [None, 'h264']
        assert fn("h264_and_flac_aud.mkv") == ["flac", 'h264']
        assert fn("h264_and_m4a_aud.mp4") == ["aac", 'h264']
        assert fn("webm.webm") == [None, 'vp9']
        
        # not a video
        assert fn("../images/a.txt") == 'ERR:Invalid data found when processing input'

        # file not exist
        assert fn("notexist.txt") == 'ERR:No such file or directory'

