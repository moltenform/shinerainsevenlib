
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.core import *
import pytest
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
    def getVidType(self, path, retcode=None, stdout=None, stderr=None):
        os.chdir(files.getParent(files.getParent(__file__)))
        customFn = None
        if stderr is not None:
            customFn = lambda *_args, **_kwargs: [retcode, stdout, stderr]

        results = SrssMedia.getAudAndVidCodec(path, customFn=customFn)
        if results.err:
            return 'ERR:' + str(results.err)
        else:
            return [results.audFormat, results.vidFormat]
    
    def exampleOutput(self):
        return r'''ffmpeg version 7.0.1-full_build-www.gyan.dev Copyright (c) 2000-2024 the FFmpeg developers
  built with gcc 13.2.0 (Rev5, Built by MSYS2 project)
  configuration: --enable-gpl --enable-version3 --enable-static --disable-w32threads --disable-autodetect --enable-fontconfig --enable-iconv --enable-gnutls --enable-libxml2 --enable-gmp --enable-bzlib --enable-lzma --enable-libsnappy --enable-zlib --enable-librist --enable-libsrt --enable-libssh --enable-libzmq --enable-avisynth --enable-libbluray --enable-libcaca --enable-sdl2 --enable-libaribb24 --enable-libaribcaption --enable-libdav1d --enable-libdavs2 --enable-libuavs3d --enable-libxevd --enable-libzvbi --enable-librav1e --enable-libsvtav1 --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxavs2 --enable-libxeve --enable-libxvid --enable-libaom --enable-libjxl --enable-libopenjpeg --enable-libvpx --enable-mediafoundation --enable-libass --enable-frei0r --enable-libfreetype --enable-libfribidi --enable-libharfbuzz --enable-liblensfun --enable-libvidstab --enable-libvmaf --enable-libzimg --enable-amf --enable-cuda-llvm --enable-cuvid --enable-dxva2 --enable-d3d11va --enable-d3d12va --enable-ffnvcodec --enable-libvpl --enable-nvdec --enable-nvenc --enable-vaapi --enable-libshaderc --enable-vulkan --enable-libplacebo --enable-opencl --enable-libcdio --enable-libgme --enable-libmodplug --enable-libopenmpt --enable-libopencore-amrwb --enable-libmp3lame --enable-libshine --enable-libtheora --enable-libtwolame --enable-libvo-amrwbenc --enable-libcodec2 --enable-libilbc --enable-libgsm --enable-libopencore-amrnb --enable-libopus --enable-libspeex --enable-libvorbis --enable-ladspa --enable-libbs2b --enable-libflite --enable-libmysofa --enable-librubberband --enable-libsoxr --enable-chromaprint
  libavutil      59.  8.100 / 59.  8.100
  libavcodec     61.  3.100 / 61.  3.100
  libavformat    61.  1.100 / 61.  1.100
  libavdevice    61.  1.100 / 61.  1.100
  libavfilter    10.  1.100 / 10.  1.100
  libswscale      8.  1.100 /  8.  1.100
  libswresample   5.  1.100 /  5.  1.100
  libpostproc    58.  1.100 / 58.  1.100
Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'C:\b\devarchive\mycode\archivetier1\org2025shinerain\2025\shinerainsevenlib\tests\collat\media\h264_and_m4a_aud.mp4':
  Metadata:
    major_brand     : isom
    minor_version   : 512
    compatible_brands: isomiso2avc1mp41
    encoder         : Lavf61.1.100
  Duration: 00:00:01.00, start: 0.000000, bitrate: 714 kb/s
  Stream #0:0[0x1](und): Video: h264 (High 4:4:4 Predictive) (avc1 / 0x31637661), yuv444p(progressive), 400x400 [SAR 1:1 DAR 1:1], 537 kb/s, 14 fps, 14 tbr, 14336 tbn (default)
      Metadata:
        handler_name    : VideoHandler
        vendor_id       : [0][0][0][0]
        encoder         : Lavc61.3.100 libx264
  Stream #0:1[0x2](und): Audio: aac (LC) (mp4a / 0x6134706D), 48000 Hz, mono, fltp, 162 kb/s (default)
      Metadata:
        handler_name    : SoundHandler
        vendor_id       : [0][0][0][0]
At least one output file must be specified
'''

    @pytest.mark.skipif('os.getenv("GITHUB_ACTION")')
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
    
    def testFfmpegHandleCommas(self, mocker):
        s = self.exampleOutput()
        s = srss.replaceMustExist(s, 'Video: h264 (High 4:4:4 Predictive)', 'Video: rpza,x')
        s = srss.replaceMustExist(s, 'Audio: aac (LC)', 'Audio: pcm_u8,x')
        retcode = 1
        stdout = b''
        stderr = s.encode('utf-8')
        assert self.getVidType("collat/media/h264.mp4", retcode, stdout, stderr) == \
            ['smallwav_u8', 'applequicktime_rpza']

    def testFfmpegImpliedErrorByAbsenceoOfOutputFileMsg(self, mocker):
        s = self.exampleOutput()
        s = srss.replaceMustExist(s, 'At least one output file must be specified', 'At least one output file')
        retcode = 0 # even though retcode is 0 this should be an error
        stdout = b''
        stderr = s.encode('utf-8')
        assert self.getVidType("collat/media/h264.mp4", retcode, stdout, stderr) == \
            'ERR:Could not interpret the file'


    def testFfmpegNonZeroRetcodeNothingFound(self, mocker):
        s = self.exampleOutput()
        s = srss.replaceMustExist(s, 'Stream #0:0[0x1](und)', '')
        s = srss.replaceMustExist(s, 'Stream #0:1[0x2](und)', '')
        retcode = 1
        stdout = b''
        stderr = s.encode('utf-8')
        assert self.getVidType("collat/media/h264.mp4", retcode, stdout, stderr) == \
            'ERR:No streams found'
        
    def testFfmpegSuccessButNothingFound(self, mocker):
        s = self.exampleOutput()
        s = srss.replaceMustExist(s, 'Stream #0:0[0x1](und)', '')
        s = srss.replaceMustExist(s, 'Stream #0:1[0x2](und)', '')
        retcode = 0 # won't happen in practice
        stdout = b''
        stderr = s.encode('utf-8')
        assert self.getVidType("collat/media/h264.mp4", retcode, stdout, stderr) == \
            'ERR:No streams found'

    def testFfmpegSuccessButUnrecognizedAFormat(self, mocker):
        s = self.exampleOutput()
        s = srss.replaceMustExist(s, 'Audio: aac (LC)', 'Audio: monkeyaudio,x')
        retcode = 1
        stdout = b''
        stderr = s.encode('utf-8')
        assert self.getVidType("collat/media/h264.mp4", retcode, stdout, stderr) == \
            'ERR:unknown audio format monkeyaudio x (mp4a / 0x6134706D)  48000 Hz  mono  fltp  162 kb/s (default) monkeyaudio'
        
    def testFfmpegSuccessButUnrecognizedVFormat(self, mocker):
        s = self.exampleOutput()
        s = srss.replaceMustExist(s, 'Video: h264 (High 4:4:4 Predictive)', 'Video: binkvideo,x')
        retcode = 1
        stdout = b''
        stderr = s.encode('utf-8')
        assert self.getVidType("collat/media/h264.mp4", retcode, stdout, stderr) == \
            'ERR:unknown vid format binkvideo x (avc1 / 0x31637661)  yuv444p(progressive)  400x400 [SAR 1:1 DAR 1:1]  537 kb/s  14 fps  14 tbr  14336 tbn (default) binkvideo'

    def testFfmpegTwoV(self, mocker):
        s = self.exampleOutput()
        s = srss.replaceMustExist(s, 'Audio: aac (LC)', 'Video: h264 (High 4:4:4 Predictive),x')
        retcode = 1
        stdout = b''
        stderr = s.encode('utf-8')
        assert self.getVidType("collat/media/h264.mp4", retcode, stdout, stderr) == \
            'ERR:two video tracks? collat/media/h264.mp4'
        
    def testFfmpegTwoA(self, mocker):
        s = self.exampleOutput()
        s = srss.replaceMustExist(s, 'Video: h264 (High 4:4:4 Predictive)', 'Audio: aac (LC)')
        retcode = 1
        stdout = b''
        stderr = s.encode('utf-8')
        assert self.getVidType("collat/media/h264.mp4", retcode, stdout, stderr) == \
            'ERR:two audio tracks? collat/media/h264.mp4'
        
    def testSkipOverDataSectionAndLookForUnknownStreamType(self, mocker):
        s = self.exampleOutput()
        append = r'''  
Stream #0:2[0x3](und): Data: abc xyz
      Metadata:
        handler_name    : SoundHandler
        vendor_id       : [0][0][0][0]
Stream #0:3[0x4](und): SomeOtherType: aac (LC)
      Metadata:
        handler_name    : SoundHandler
        vendor_id       : [0][0][0][0]
'''
        s = srss.replaceMustExist(s, 'At least one output', f'{append}At least one output')
        retcode = 1
        stdout = b''
        stderr = s.encode('utf-8')
        assert self.getVidType("collat/media/h264.mp4", retcode, stdout, stderr) == \
            'ERR:unknown stream type SomeOtherType: aac (LC) collat/media/h264.mp4'


