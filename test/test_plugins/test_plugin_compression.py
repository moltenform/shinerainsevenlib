
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

import pytest
from shinerainsoftsevenutil.standard import *
from src.shinerainsoftsevenutil.plugins.plugin_configreader import getExecutablePathFromPrefs
from src.shinerainsoftsevenutil.plugins.plugin_compression_rar import getRarExecutablePath
import zipfile
import shutil


class TestPluginCompression:
    def test_listZipPython(self):
        def fn(s):
            result = (str(zipListAsStrViaPython(f'./test/collat/compression/{s}')))
            result = result.replace('incremental_autocompletion', 'd').replace('scintilla.patch', '1.txt').replace('scite.patch', '2.txt')
            return result

        assert fn("test_zip_made_with_7z.zip") == "['d/;0;algorithm=0', 'd/1.txt;1920;algorithm=8', 'd/2.txt;1745;algorithm=8']"
        assert fn("test_zip_made_with_7z_store.zip") == "['d/;0;algorithm=0', 'd/1.txt;1920;algorithm=0', 'd/2.txt;1745;algorithm=0']"
        assert fn("test_zip_made_with_py_default.zip") == "['d/1.txt;1920;algorithm=8', 'd/2.txt;1745;algorithm=8']"
        assert fn("test_zip_made_with_py_lzma.zip") == "['d/1.txt;1920;algorithm=14', 'd/2.txt;1745;algorithm=14']"
        assert fn("test_zip_made_with_winrar.zip") == "['d/;0;algorithm=0', 'd/1.txt;1920;algorithm=8', 'd/2.txt;1745;algorithm=8']"    
    
    def test_listZipSrssCompress(self):
        def fn(s):
            result = (str(zipListAsStrViaPython(f'./test/collat/compression/{s}')))
            result = result.replace('incremental_autocompletion', 'd').replace('scintilla.patch', '1.txt').replace('scite.patch', '2.txt')
            return result

        assert fn("test_zip_made_with_7z.zip") == """"""
        assert fn("test_zip_made_with_7z_store.zip") == ""
        assert fn("test_zip_made_with_py_default.zip") == ""
        assert fn("test_zip_made_with_py_lzma.zip") == ""
        assert fn("test_zip_made_with_winrar.zip") == ""
        assert 1==2
    
    

def zipListAsStrViaPython(path):
    results = []
    with zipfile.ZipFile(path) as z:
        lst = z.infolist()
        lst.sort(key=lambda item: item.filename)
        for item in lst:
            results.append(f'{item.filename};{item.file_size};algorithm={item.compress_type}')
    return results

def archiveListAsStr(path, okToFallbackTo7zForRar=False):
    lst = SrssCompression.getContents(path, okToFallbackTo7zForRar=okToFallbackTo7zForRar)
    lst.sort(key=lambda item: item['Path'])
    return jslike.map(str, lst)

def pathWinrar():
    path = getRarExecutablePath()
    if not (files.isFile(path) or shutil.which(path)):
        path = getExecutablePathFromPrefs('rar')
    
    if not (files.isFile(path) or shutil.which(path)):

    guessLocation = r"C:\Program Files\WinRAR\RAR.exe"
    if path:
        return path
    elif not path and files.isFile(guessLocation):
        return guessLocation
    else:
        return None
    

