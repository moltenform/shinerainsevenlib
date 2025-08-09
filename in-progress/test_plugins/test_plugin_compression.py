
# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv2.1 License

import pytest
import zipfile
import shutil
import sys

from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.plugins.plugin_configreader import getExecutablePathFromPrefs
from src.shinerainsevenlib.plugins.plugin_compression_rar import getRarExecutablePath
from src.shinerainsevenlib.core import assertException

from test.test_core.common import fixtureDir


class TestPluginCompression:
    def test_listZipPython(self):
        def fn(s):
            result = (str(helperGetContentsViaPython(f'./test/collat/compression/{s}')))
            result = result.replace('incremental_autocompletion', 'd').replace('scintilla.patch', '1.txt').replace('scite.patch', '2.txt')
            return result

        assert fn("test_zip_made_with_7z.zip") == "['d/;0;0;algorithm=0', 'd/1.txt;1920;d16db268;algorithm=8', 'd/2.txt;1745;93f8f25a;algorithm=8']"
        assert fn("test_zip_made_with_7z_store.zip") == "['d/;0;0;algorithm=0', 'd/1.txt;1920;d16db268;algorithm=0', 'd/2.txt;1745;93f8f25a;algorithm=0']"
        assert fn("test_zip_made_with_py_default.zip") == "['d/1.txt;1920;d16db268;algorithm=8', 'd/2.txt;1745;93f8f25a;algorithm=8']"
        assert fn("test_zip_made_with_py_lzma.zip") == "['d/1.txt;1920;d16db268;algorithm=14', 'd/2.txt;1745;93f8f25a;algorithm=14']"
        assert fn("test_zip_made_with_winrar.zip") == "['d/;0;0;algorithm=0', 'd/1.txt;1920;d16db268;algorithm=8', 'd/2.txt;1745;93f8f25a;algorithm=8']"    
    
    def test_listZipSrssCompress(self):
        def fn(s):
            result = str(helperGetContents(f'./test/collat/compression/{s}')).replace('"', "'")
            result = result.replace('incremental_autocompletion', 'd').replace('scintilla.patch', '1.txt').replace('scite.patch', '2.txt')
            return result

        assert fn("test_zip_made_with_7z.zip") == r"Path=d,Type=Directory,CRC=00000000,Size=0,PackedSize=0,;Path=d\1.txt,Type=File,CRC=D16DB268,Size=1920,PackedSize=724,;Path=d\2.txt,Type=File,CRC=93F8F25A,Size=1745,PackedSize=710,;"
        assert fn("test_zip_made_with_7z_store.zip") == r"Path=d,Type=Directory,CRC=00000000,Size=0,PackedSize=0,;Path=d\1.txt,Type=File,CRC=D16DB268,Size=1920,PackedSize=1920,;Path=d\2.txt,Type=File,CRC=93F8F25A,Size=1745,PackedSize=1745,;"
        assert fn("test_zip_made_with_py_default.zip") == r"Path=d\1.txt,Type=File,CRC=D16DB268,Size=1920,PackedSize=725,;Path=d\2.txt,Type=File,CRC=93F8F25A,Size=1745,PackedSize=713,;"
        assert fn("test_zip_made_with_py_lzma.zip") == r"Path=d\1.txt,Type=File,CRC=D16DB268,Size=1920,PackedSize=753,;Path=d\2.txt,Type=File,CRC=93F8F25A,Size=1745,PackedSize=749,;"
        assert fn("test_zip_made_with_winrar.zip") == r"Path=d,Type=Directory,CRC=00000000,Size=0,PackedSize=0,;Path=d\1.txt,Type=File,CRC=D16DB268,Size=1920,PackedSize=726,;Path=d\2.txt,Type=File,CRC=93F8F25A,Size=1745,PackedSize=710,;"
    
    def test_listOtherArchivetypes(self):
        def fn(s, alwaysUse7z=False):
            result = str(helperGetContents(f'./test/collat/compression/{s}', alwaysUse7z=alwaysUse7z)).replace('"', "'")
            result = result.replace('incremental_autocompletion', 'd').replace('scintilla.patch', '1.txt').replace('scite.patch', '2.txt')
            return result

        assert fn("otherformat.tar") == r"Path=d,Type=Directory,CRC=00000000,Size=0,PackedSize=0,;Path=d\1.txt,Type=File,CRC=--no crc found,Size=1920,PackedSize=2048,;Path=d\2.txt,Type=File,CRC=--no crc found,Size=1745,PackedSize=2048,;"
        assert fn("otherformat.tar.bz2") == r"Path=d,Type=Directory,CRC=00000000,Size=0,PackedSize=0,;Path=d\1.txt,Type=File,CRC=--no crc found,Size=1920,PackedSize=2048,;Path=d\2.txt,Type=File,CRC=--no crc found,Size=1745,PackedSize=2048,;"
        assert fn("otherformat.tar.gz") == r"Path=d,Type=Directory,CRC=00000000,Size=0,PackedSize=0,;Path=d\1.txt,Type=File,CRC=--no crc found,Size=1920,PackedSize=2048,;Path=d\2.txt,Type=File,CRC=--no crc found,Size=1745,PackedSize=2048,;"
        assert fn("otherformat.tar.xz") == r"Path=d,Type=Directory,CRC=00000000,Size=0,PackedSize=0,;Path=d\1.txt,Type=File,CRC=--no crc found,Size=1920,PackedSize=2048,;Path=d\2.txt,Type=File,CRC=--no crc found,Size=1745,PackedSize=2048,;"
        assert fn("test_7z.7z") == r"Path=d,Type=Directory,CRC=00000000,Size=0,PackedSize=0,;Path=d\1.txt,Type=File,CRC=D16DB268,Size=1920,PackedSize=1271,;Path=d\2.txt,Type=File,CRC=93F8F25A,Size=1745,PackedSize=,;"

        # rar files, using both 7z and rar
        assert fn("test_rar_nosolid_nostore.rar") == r"Path=d,Type=Directory,CRC=00000000,Size=--no size found,PackedSize=--no packedsize found,;Path=d\1.txt,Type=File,CRC=D16DB268,Size=1920,PackedSize=746,;Path=d\2.txt,Type=File,CRC=93F8F25A,Size=1745,PackedSize=745,;"
        assert fn("test_rar_nosolid_store.rar") == r"Path=d,Type=Directory,CRC=00000000,Size=--no size found,PackedSize=--no packedsize found,;Path=d\1.txt,Type=File,CRC=D16DB268,Size=1920,PackedSize=1920,;Path=d\2.txt,Type=File,CRC=93F8F25A,Size=1745,PackedSize=1745,;"
        assert fn("test_rar_solid_nostore.rar") == r"Path=d,Type=Directory,CRC=00000000,Size=--no size found,PackedSize=--no packedsize found,;Path=d\1.txt,Type=File,CRC=D16DB268,Size=1920,PackedSize=763,;Path=d\2.txt,Type=File,CRC=93F8F25A,Size=1745,PackedSize=522,;"
        assert fn("test_rar_nosolid_nostore.rar", alwaysUse7z=True) == r"Path=d,Type=Directory,CRC=00000000,Size=0,PackedSize=0,;Path=d\1.txt,Type=File,CRC=D16DB268,Size=1920,PackedSize=746,;Path=d\2.txt,Type=File,CRC=93F8F25A,Size=1745,PackedSize=745,;"
        assert fn("test_rar_nosolid_store.rar", alwaysUse7z=True) == r"Path=d,Type=Directory,CRC=00000000,Size=0,PackedSize=0,;Path=d\1.txt,Type=File,CRC=D16DB268,Size=1920,PackedSize=1920,;Path=d\2.txt,Type=File,CRC=93F8F25A,Size=1745,PackedSize=1745,;"
        assert fn("test_rar_solid_nostore.rar", alwaysUse7z=True) == r"Path=d,Type=Directory,CRC=00000000,Size=0,PackedSize=0,;Path=d\1.txt,Type=File,CRC=D16DB268,Size=1920,PackedSize=763,;Path=d\2.txt,Type=File,CRC=93F8F25A,Size=1745,PackedSize=522,;"

        # we kind-of support single files
        assert fn("singlefile.xml.bz2") == "Path=singlefile.xml,Type=File,CRC=--no crc found,Size=666,PackedSize=--no packedsize found,;"
        assert fn("singlefile.xml.gz") == "Path=singlefile.xml,Type=File,CRC=--no crc found,Size=666,PackedSize=--no packedsize found,;"

        # we don't support non archive files
        assertException(lambda: fn("singlefile.xml"), Exception, "Cannot open the file as archive'")


    def test_unicodeAndZeroByte(self):
        def fn(s, alwaysUse7z=False):
            result = str(helperGetContents(f'./test/collat/compression/{s}', alwaysUse7z=alwaysUse7z)).replace('"', "'")
            return result
        assert fn("unicode_and_zero_byte.zip") == "Path=beach-redundant-1.jpg,Type=File,CRC=9B47D08F,Size=22686,PackedSize=22587,;Path=st-helens-unicodes-_.bmp,Type=File,CRC=CB5985DD,Size=123570,PackedSize=49012,;Path=zero_bytes.txt,Type=File,CRC=00000000,Size=0,PackedSize=0,;"
        assert fn("unicode_and_zero_byte.7z") == "Path=beach-redundant-1.jpg,Type=File,CRC=9B47D08F,Size=22686,PackedSize=71692,;Path=st-helens-unicodes-_.bmp,Type=File,CRC=CB5985DD,Size=123570,PackedSize=,;Path=zero_bytes.txt,Type=File,CRC=00000000,Size=0,PackedSize=0,;"
        assert fn("unicode_and_zero_byte.rar") == "Path=beach-redundant-1.jpg,Type=File,CRC=9B47D08F,Size=22686,PackedSize=22605,;Path=st-helens-unicodes-?.bmp,Type=File,CRC=CB5985DD,Size=123570,PackedSize=47850,;Path=zero_bytes.txt,Type=File,CRC=00000000,Size=0,PackedSize=0,;"
        assert fn("unicode_and_zero_byte.rar", alwaysUse7z=True) == "Path=beach-redundant-1.jpg,Type=File,CRC=9B47D08F,Size=22686,PackedSize=22605,;Path=st-helens-unicodes-_.bmp,Type=File,CRC=CB5985DD,Size=123570,PackedSize=47850,;Path=zero_bytes.txt,Type=File,CRC=00000000,Size=0,PackedSize=0,;"
    
    def test_checkArchiveIntegrity(self):
        def fn(s):
            return SrssCompression.checkArchiveIntegrity(f'./test/collat/compression/{s}')
        
        assert fn("test_zip_made_with_7z.zip") == True
        assert fn("test_zip_made_with_7z_store.zip") == True
        assert fn("test_zip_made_with_py_default.zip") == True
        assert fn("test_zip_made_with_py_lzma.zip") == True
        assert fn("test_zip_made_with_winrar.zip") == True

        assert fn("feature_corrupt_minor.zip") == False
        assertException(lambda: fn("feature_password.rar"), Exception, 'Wrong password')
        assert fn("otherformat.tar") == True
        assert fn("otherformat.tar.bz2") == True
        assert fn("otherformat.tar.gz") == True
        assert fn("otherformat.tar.xz") == True

        # non-archives return false
        assert fn("singlefile.xml") == False
        assert fn("singlefile.xml.bz2") == True
        assert fn("singlefile.xml.gz") == True
        assert fn("test_7z.7z") == True
        assert fn("test_rar_nosolid_nostore.rar") == True
        assert fn("test_rar_nosolid_store.rar") == True
        assert fn("test_rar_solid_nostore.rar") == True
        
        assert fn("unicode_and_zero_byte.7z") == True
        assert fn("unicode_and_zero_byte.rar") == True
        assert fn("unicode_and_zero_byte.zip") == True
        
    def test_checkArchiveIntegrityWithPassword(self):
        def fn(s, pword=None):
            return SrssCompression.checkArchiveIntegrity(f'./test/collat/compression/{s}', pword=pword)
        
        # we do Not want 7z not to block on stdin causing script to stall
        assertException(lambda: fn("feature_password.rar"), Exception, 'Wrong password')
        assertException(lambda: fn("feature_password.rar", pword='wrong'), Exception, 'Wrong password')
        assert fn("feature_password.rar", pword='abc') == True

    def test_checkArchiveContentsWithPassword(self):
        def fn(s, alwaysUse7z=False, pword=None):
            result = (str(helperGetContents(f'./test/collat/compression/{s}', alwaysUse7z=alwaysUse7z, pword=pword)))
            result = result.replace('incremental_autocompletion', 'd').replace('scintilla.patch', '1.txt').replace('scite.patch', '2.txt')
            return result
        
        assertException(lambda: fn("feature_password.rar"), Exception, 'Wrong password')
        assertException(lambda: fn("feature_password.rar", alwaysUse7z=True), Exception, 'Wrong password')
        assertException(lambda: fn("feature_password.rar", pword='wrong'), Exception, 'Wrong password')
        assertException(lambda: fn("feature_password.rar", pword='wrong', alwaysUse7z=True), Exception, 'Wrong password')
        assert fn("feature_password.rar", pword='abc') == r"Path=d,Type=Directory,CRC=00000000,Size=--no size found,PackedSize=--no packedsize found,;Path=d\1.txt,Type=File,CRC=D16DB268,Size=1920,PackedSize=752,;Path=d\2.txt,Type=File,CRC=93F8F25A,Size=1745,PackedSize=752,;"
        assert fn("feature_password.rar", pword='abc', alwaysUse7z=True) == r"Path=d,Type=Directory,CRC=00000000,Size=0,PackedSize=0,;Path=d\1.txt,Type=File,CRC=D16DB268,Size=1920,PackedSize=752,;Path=d\2.txt,Type=File,CRC=93F8F25A,Size=1745,PackedSize=752,;"

    def test_checkArchivePassword(self):
        def fn(s, pword=None):
            results = SrssCompression.checkArchivePassword(f'./test/collat/compression/{s}', pword=pword)
            delattr(results, 'stdout')
            delattr(results, 'stderr')
            results = str(results).replace('\n', ';')
            return str(results)
        
        assert fn("singlefile.xml") == r"failedOtherReason=True;failedWrongPword=False;success=False"
        assert fn("singlefile.xml", pword='wrong') == r"failedOtherReason=True;failedWrongPword=False;success=False"
        assert fn("singlefile.xml", pword='abc') == r"failedOtherReason=True;failedWrongPword=False;success=False"
        assert fn("test_zip_made_with_py_default.zip") == r"failedOtherReason=False;failedWrongPword=False;success=True"
        assert fn("test_zip_made_with_py_default.zip", pword='wrong') == r"failedOtherReason=False;failedWrongPword=False;success=True"
        assert fn("test_zip_made_with_py_default.zip", pword='abc') == r"failedOtherReason=False;failedWrongPword=False;success=True"
        assert fn("feature_password.rar") == r"failedOtherReason=False;failedWrongPword=True;success=False"
        assert fn("feature_password.rar", pword='wrong') == r"failedOtherReason=False;failedWrongPword=True;success=False"
        assert fn("feature_password.rar", pword='abc') == r"failedOtherReason=False;failedWrongPword=False;success=True"
    
    def test_runProcessThatCreatesOutput(self, fixtureDir):
        cjxl = getExecutablePathFromPrefs('cjxl', throwIfNotFound=True,)
        _tmpDir, dirToArchive = prepareForMakingArchives(fixtureDir)
        def fn(listArgs, inName, expectFail=False, **kwargs):
            assert (not 'outPath' in kwargs and not 'inPath' in kwargs)
            inPath = f'{dirToArchive}/{inName}'
            outPath = f'{dirToArchive}/{inName}.jxl'
            files.deleteSure(inPath)
            files.copy(f'{dirToArchive}/beach-redundant-1.jpg', inPath, True)
            if expectFail:
                assertException(lambda: SrssCompression.runProcessThatCreatesOutput(listArgs, inPath=inPath, outPath=outPath, **kwargs), Exception, expectFail)
            else:
                SrssCompression.runProcessThatCreatesOutput(listArgs, inPath=inPath, outPath=outPath, **kwargs )
                assert files.exists(outPath)
                assert files.getSize(outPath) > 1024

        # test standard usage
        files.deleteSure(f'{dirToArchive}/file.jpg.jxl')
        fn([cjxl, '%input%', '%output%'], 'file.jpg')
        assert (files.getSize(f'{dirToArchive}/file.jpg.jxl') > 0)

        # test with input given directly
        files.deleteSure(f'{dirToArchive}/other.jpg.jxl')
        fn([cjxl, f'{dirToArchive}/beach-redundant-1.jpg', '%output%'], 'other.jpg')
        assert (files.getSize(f'{dirToArchive}/other.jpg.jxl') > 0)

        # test file not found
        files.deleteSure(f'{dirToArchive}/other.jpg.jxl')
        fn([cjxl, 'not--found.jpg', '%output%'], 'other.jpg', expectFail='Reading image data failed')
        assert (not files.isFile(f'{dirToArchive}/other.jpg.jxl'))
        
        # fail with unicode input if feature turned off (and on windows)
        files.deleteSure(f'{dirToArchive}/unicode넬.jpg.jxl')
        if sys.platform.startswith('win'):
            fn([cjxl, '%input%', '%output%'], 'unicode넬.jpg', expectFail='Reading image data failed', handleUnicodeInputs=False)
            assert (not files.isFile(f'{dirToArchive}/unicode넬.jpg.jxl'))
        else:
            fn([cjxl, '%input%', '%output%'], 'unicode넬.jpg', handleUnicodeInputs=False)
            assert (files.getSize(f'{dirToArchive}/unicode넬.jpg.jxl') > 0)

        # test with unicode input
        files.deleteSure(f'{dirToArchive}/unicode넬.jpg.jxl')
        fn([cjxl, '%input%', '%output%'], 'unicode넬.jpg')
        assert (files.getSize(f'{dirToArchive}/unicode넬.jpg.jxl') > 0)
        
        # should warn if output not seen in args
        files.deleteSure(f'{dirToArchive}/file.jpg.jxl')
        fn([cjxl, '-V'], 'file.jpg', expectFail='expected to see %output%')
        assert (not files.isFile(f'{dirToArchive}/file.jpg.jxl'))
        
        # should assert if output not created
        files.deleteSure(f'{dirToArchive}/file.jpg.jxl')
        fn([cjxl, '-V', '%output%'], 'file.jpg', expectFail='output not created')
        assert (not files.isFile(f'{dirToArchive}/file.jpg.jxl'))

        # should assert if output already there
        files.writeAll(f'{dirToArchive}/file.jpg.jxl', 'abc')
        fn([cjxl, '-V', '%output%'], 'file.jpg',  expectFail='output already there',)
        assert (files.isFile(f'{dirToArchive}/file.jpg.jxl'))
        
        # should assert if output too small
        files.deleteSure(f'{dirToArchive}/file.jpg.jxl')
        fn([cjxl, '%input%', '%output%'], 'file.jpg',  expectFail='output too small', sizeMustBeGreaterThan=1024*1024,)
        assert (not files.isFile(f'{dirToArchive}/file.jpg.jxl'))

        # (change file lmt)
        for f, _short in files.listFiles(dirToArchive):
            files.setLastModTime(f, files.getLastModTime(f) - 1000)

        # without last-modified
        files.deleteSure(f'{dirToArchive}/file.jpg.jxl')
        fn([cjxl, '%input%', '%output%'], 'file.jpg')
        assert (files.getSize(f'{dirToArchive}/file.jpg.jxl') > 0)
        assert files.getLastModTime(f'{dirToArchive}/file.jpg') != files.getLastModTime(f'{dirToArchive}/file.jpg.jxl')

        # copy last-modified
        files.deleteSure(f'{dirToArchive}/file.jpg.jxl')
        fn([cjxl, '%input%', '%output%'], 'file.jpg', copyLastModTimeFromInput=True)
        assert (files.getSize(f'{dirToArchive}/file.jpg.jxl') > 0)
        assert files.getLastModTime(f'{dirToArchive}/file.jpg') == files.getLastModTime(f'{dirToArchive}/file.jpg.jxl')

    def test_createZipsWithPython(self, fixtureDir):
        def fn(s):
            return str(helperGetContentsViaPython(s))
        
        path = helperMakeZip(fixtureDir, 'standard.zip')
        assert fn(path) == "['a/b/im.bmp;9;4d09f139;algorithm=8', 'a/b/im.png;10;6eb06c37;algorithm=8', 'a/noext;11;cdd8c08e;algorithm=8']"

        path = helperMakeZip(fixtureDir, 'lzma.zip', method=SrssCompression.ZipMethods.Lzma)
        assert fn(path) == "['a/b/im.bmp;9;4d09f139;algorithm=14', 'a/b/im.png;10;6eb06c37;algorithm=14', 'a/noext;11;cdd8c08e;algorithm=14']"

        path = helperMakeZip(fixtureDir, 'store.zip', method=SrssCompression.ZipMethods.Store)
        assert fn(path) == "['a/b/im.bmp;9;4d09f139;algorithm=0', 'a/b/im.png;10;6eb06c37;algorithm=0', 'a/noext;11;cdd8c08e;algorithm=0']"

        path = helperMakeZip(fixtureDir, 'automatic.zip', alreadyCompressedAsStore=True)
        assert fn(path) == "['a/b/im.bmp;9;4d09f139;algorithm=8', 'a/b/im.png;10;6eb06c37;algorithm=0', 'a/noext;11;cdd8c08e;algorithm=8']"

        path = helperMakeZip(fixtureDir, 'path_prefix.zip', pathPrefix='prefix')
        assert fn(path) == "['prefixb/im.bmp;9;4d09f139;algorithm=8', 'prefixb/im.png;10;6eb06c37;algorithm=8', 'prefixnoext;11;cdd8c08e;algorithm=8']"

        path = helperMakeZip(fixtureDir, 'no_recurse.zip', recurse=False)
        assert fn(path) == "['a/noext;11;cdd8c08e;algorithm=8']"

    def test_createArchives(self, fixtureDir):
        tmpDir, dirToArchive = prepareForMakingArchives(fixtureDir)
        archive = files.join(tmpDir, 'zip-7z-max.zip')
        SrssCompression.addAllTo7z(dirToArchive, archive, SrssCompression.Strength.Max, solid=False)
        checkSizeCloseToKB(archive, 96.5)

        archive = files.join(tmpDir, 'zip-7z-strong.zip')
        SrssCompression.addAllTo7z(dirToArchive, archive, SrssCompression.Strength.Strong, solid=False)
        checkSizeCloseToKB(archive, 96.5)

        archive = files.join(tmpDir, 'zip-7z-default.zip')
        SrssCompression.addAllTo7z(dirToArchive, archive, SrssCompression.Strength.Default, solid=False)
        checkSizeCloseToKB(archive, 98.1)

        archive = files.join(tmpDir, 'zip-7z-store.zip')
        SrssCompression.addAllTo7z(dirToArchive, archive, SrssCompression.Strength.Store, solid=False)
        checkSizeCloseToKB(archive, 165)

        archive = files.join(tmpDir, 'zip-winrar-default.zip')
        SrssCompression.addAllToRar(dirToArchive, archive, solid=False)
        checkSizeCloseToKB(archive, 92.1)

        archive = files.join(tmpDir, 'zip-py-store.zip')
        SrssCompression.addAllToZip(dirToArchive, archive, SrssCompression.ZipMethods.Store)
        checkSizeCloseToKB(archive, 165)

        archive = files.join(tmpDir, 'zip-py-deflate.zip')
        SrssCompression.addAllToZip(dirToArchive, archive, SrssCompression.ZipMethods.Deflate)
        checkSizeCloseToKB(archive, 99.1)

        archive = files.join(tmpDir, 'zip-py-lzma.zip')
        SrssCompression.addAllToZip(dirToArchive, archive, SrssCompression.ZipMethods.Lzma)
        checkSizeCloseToKB(archive, 92.3)

    def test_create7zAndRar(self, fixtureDir):
        tmpDir, dirToArchive = prepareForMakingArchives(fixtureDir)
        self._createRar(tmpDir, dirToArchive, True)
        self._createRar(tmpDir, dirToArchive, False)
        self._create7z(tmpDir, dirToArchive, True)
        self._create7z(tmpDir, dirToArchive,False)
        
    def _createRar(self, tmpDir, dirToArchive, isSolid):
        isSolidStr = 'solid' if isSolid else 'not-solid'
        archive = files.join(tmpDir, 'rar-rar4-%s-4096kb.rar'%(isSolidStr))
        SrssCompression.addAllToRar(dirToArchive, archive, formatVersion='4',
            dictSize='4096k', solid=isSolid)
        checkSizeCloseToKB(archive, 55.8 if isSolid else 77.7)

        archive = files.join(tmpDir, 'rar-rar5-%s-512mb.rar'%(isSolidStr))
        SrssCompression.addAllToRar(dirToArchive, archive, formatVersion='5',
            dictSize='512m', solid=isSolid)
        checkSizeCloseToKB(archive, 69.3 if isSolid else 91.4)

        archive = files.join(tmpDir, 'rar-rar4-%s-store.rar'%(isSolidStr))
        SrssCompression.addAllToRar(dirToArchive, archive, formatVersion='4',
                                        solid=isSolid, effort=SrssCompression.Strength.Store)
        checkSizeCloseToKB(archive, 165)

        archive = files.join(tmpDir, 'rar-rar5-%s-store.rar'%(isSolidStr))
        SrssCompression.addAllToRar(dirToArchive, archive, formatVersion='5',
                                        solid=isSolid, effort=SrssCompression.Strength.Store)
        checkSizeCloseToKB(archive, 165)
        
    def _create7z(self, tmpDir, dirToArchive, isSolid):
        isSolidStr = 'solid' if isSolid else 'not-solid'
        archive = files.join(tmpDir, '7z-%s-max.7z'%(isSolidStr))
        SrssCompression.addAllTo7z(dirToArchive, archive, solid=isSolid,
            effort=SrssCompression.Strength.Max)
        checkSizeCloseToKB(archive, 70.0 if isSolid else 92.0)

        archive = files.join(tmpDir, '7z-%s-strong.7z'%(isSolidStr))
        SrssCompression.addAllTo7z(dirToArchive, archive, solid=isSolid,
            effort=SrssCompression.Strength.Strong)
        checkSizeCloseToKB(archive, 70.0 if isSolid else 92.0)

        archive = files.join(tmpDir, '7z-%s-default.7z'%(isSolidStr))
        SrssCompression.addAllTo7z(dirToArchive, archive, solid=isSolid,
            effort=SrssCompression.Strength.Default)
        checkSizeCloseToKB(archive, 70.3 if isSolid else 92.3)

        archive = files.join(tmpDir, '7z-%s-store.7z'%(isSolidStr))
        SrssCompression.addAllTo7z(dirToArchive, archive, solid=isSolid,
            effort=SrssCompression.Strength.Store)
        checkSizeCloseToKB(archive, 165)

    def test_rarPath(self):
        rarPath = getRarExecutablePath()
        assert files.isFile(rarPath) or shutil.which(rarPath), "path to rar not found, can continue but will not get as much code coverage"


def checkSizeCloseToKB(archive, expectedSize):
    gotInKb = files.getSize(archive) / 1024
    assert expectedSize == pytest.approx(gotInKb, abs=5)


def helperGetContentsViaPython(path):
    results = []
    with zipfile.ZipFile(path) as z:
        lst = z.infolist()
        lst.sort(key=lambda item: item.filename)
        for item in lst:
            results.append(f'{item.filename};{item.file_size};{'%x' % item.CRC};algorithm={item.compress_type}')
    return results

def helperGetContents(path, alwaysUse7z=True, pword=None):
    lst = SrssCompression.getContents(path, alwaysUse7z=alwaysUse7z, okToFallbackTo7zForRar=False, pword=pword)
    lst.sort(key=lambda item: item['Path'])
    results = ''
    for item in lst:
        del item['Raw']
        del item['Modified']
        for k, v in item.items():
            results += f'{k}={v},'
        results += ';'
    
    return results

def helperMakeZip(fixtureDir, outName, **zipArgs):
    files.ensureEmptyDirectory(fixtureDir)
    files.makeDirs(files.join(fixtureDir, 'a/b'))
    files.writeAll(files.join(fixtureDir, 'a/b/im.bmp'), 'contents1')
    files.writeAll(files.join(fixtureDir, 'a/b/im.png'), 'contents22')
    files.writeAll(files.join(fixtureDir, 'a/noext'), 'contents333')
    outPath = files.join(fixtureDir, outName)
    SrssCompression.addAllToZip(files.join(fixtureDir, 'a'), outPath, **zipArgs)
    return outPath


def prepareForMakingArchives(fixtureDir):
    tempDir = fixtureDir + '/tmp'
    dirToArchive = tempDir + '/dir-within-archive'
    # create a directory called 'dir-within-archive' with the contents:
    # unicodes.bmp -- compressible and has unicode filename
    # beach-redundant-1.jpg -- not compressible
    # beach-redundant-2.jpg -- same as other jpg, so solid mode will be much smaller
    zipPath = './test/collat/compression/unicode_and_zero_byte.zip'
    with zipfile.ZipFile(zipPath, 'r') as zip:
        zip.extractall(path=dirToArchive, members=None, pwd=None)

    files.deleteSure(dirToArchive + '/zero_bytes.txt')
    files.copy(dirToArchive + '/beach-redundant-1.jpg', dirToArchive + '/beach-redundant-2.jpg', True)
    return tempDir, dirToArchive


    