
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

import pytest
from src.shinerainsoftsevenutil.standard import *
from src.shinerainsoftsevenutil.plugins.plugin_configreader import getExecutablePathFromPrefs
from src.shinerainsoftsevenutil.plugins.plugin_compression_rar import getRarExecutablePath
from src.shinerainsoftsevenutil.core import assertException
import zipfile
import shutil


class TestPluginCompression:
    def test_listZipPython(self):
        def fn(s):
            result = (str(zipListAsStrViaPython(f'./test/collat/compression/{s}')))
            result = result.replace('incremental_autocompletion', 'd').replace('scintilla.patch', '1.txt').replace('scite.patch', '2.txt')
            return result

        assert fn("test_zip_made_with_7z.zip") == "['d/;0;0;algorithm=0', 'd/1.txt;1920;d16db268;algorithm=8', 'd/2.txt;1745;93f8f25a;algorithm=8']"
        assert fn("test_zip_made_with_7z_store.zip") == "['d/;0;0;algorithm=0', 'd/1.txt;1920;d16db268;algorithm=0', 'd/2.txt;1745;93f8f25a;algorithm=0']"
        assert fn("test_zip_made_with_py_default.zip") == "['d/1.txt;1920;d16db268;algorithm=8', 'd/2.txt;1745;93f8f25a;algorithm=8']"
        assert fn("test_zip_made_with_py_lzma.zip") == "['d/1.txt;1920;d16db268;algorithm=14', 'd/2.txt;1745;93f8f25a;algorithm=14']"
        assert fn("test_zip_made_with_winrar.zip") == "['d/;0;0;algorithm=0', 'd/1.txt;1920;d16db268;algorithm=8', 'd/2.txt;1745;93f8f25a;algorithm=8']"    
    
    def test_listZipSrssCompress(self):
        def fn(s):
            result = str(archiveListAsStr(f'./test/collat/compression/{s}')).replace('"', "'")
            result = result.replace('incremental_autocompletion', 'd').replace('scintilla.patch', '1.txt').replace('scite.patch', '2.txt')
            return result

        assert fn("test_zip_made_with_7z.zip") == r"Path=d,Type=Directory,CRC=00000000,Size=0,PackedSize=0,;Path=d\1.txt,Type=File,CRC=D16DB268,Size=1920,PackedSize=724,;Path=d\2.txt,Type=File,CRC=93F8F25A,Size=1745,PackedSize=710,;"
        assert fn("test_zip_made_with_7z_store.zip") == r"Path=d,Type=Directory,CRC=00000000,Size=0,PackedSize=0,;Path=d\1.txt,Type=File,CRC=D16DB268,Size=1920,PackedSize=1920,;Path=d\2.txt,Type=File,CRC=93F8F25A,Size=1745,PackedSize=1745,;"
        assert fn("test_zip_made_with_py_default.zip") == r"Path=d\1.txt,Type=File,CRC=D16DB268,Size=1920,PackedSize=725,;Path=d\2.txt,Type=File,CRC=93F8F25A,Size=1745,PackedSize=713,;"
        assert fn("test_zip_made_with_py_lzma.zip") == r"Path=d\1.txt,Type=File,CRC=D16DB268,Size=1920,PackedSize=753,;Path=d\2.txt,Type=File,CRC=93F8F25A,Size=1745,PackedSize=749,;"
        assert fn("test_zip_made_with_winrar.zip") == r"Path=d,Type=Directory,CRC=00000000,Size=0,PackedSize=0,;Path=d\1.txt,Type=File,CRC=D16DB268,Size=1920,PackedSize=726,;Path=d\2.txt,Type=File,CRC=93F8F25A,Size=1745,PackedSize=710,;"
    
    def test_listOtherArchivetypes(self):
        def fn(s, alwaysUse7z=False):
            result = str(archiveListAsStr(f'./test/collat/compression/{s}', alwaysUse7z=alwaysUse7z)).replace('"', "'")
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
            result = str(archiveListAsStr(f'./test/collat/compression/{s}', alwaysUse7z=alwaysUse7z)).replace('"', "'")
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
            result = (str(archiveListAsStr(f'./test/collat/compression/{s}', alwaysUse7z=alwaysUse7z, pword=pword)))
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
        
        


    def test_rarPath(self):
        rarPath = getRarExecutablePath()
        assert files.isFile(rarPath) or shutil.which(rarPath), "path to rar not found, can continue but will not get as much code coverage"


def zipListAsStrViaPython(path):
    results = []
    with zipfile.ZipFile(path) as z:
        lst = z.infolist()
        lst.sort(key=lambda item: item.filename)
        for item in lst:
            results.append(f'{item.filename};{item.file_size};{'%x' % item.CRC};algorithm={item.compress_type}')
    return results

def archiveListAsStr(path, alwaysUse7z=True, pword=None):
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


    