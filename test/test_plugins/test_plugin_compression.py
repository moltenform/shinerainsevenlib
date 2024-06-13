
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

import pytest
from shinerainsoftsevenutil.standard import *

def zipListAsStrViaPython(path):
    results = ''
    with zipfile.ZipFile(outPath) as z:
        lst = z.infolist()
        lst.sort(key=lambda item: item.filename)
        results += f'\n'
    return results

class TestPluginCompression:
    def testTemporary(self):

    def testTemporary(self):
        expectedUnicode = ''
        assert fn("test(tbz).tar.bz2") == "xxxxxx"
        assert fn("test(tgz).tar.gz") == "xxxxxx"
        assert fn("test(txz).tar.xz") == "xxxxxx"
        assert fn("test_7z.7z") == "xxxxxx"
        assert fn("test_rar_nosolid_nostore.rar") == "xxxxxx"
        assert fn("test_rar_nosolid_store.rar") == "xxxxxx"
        assert fn("test_rar_solid_nostore.rar") == "xxxxxx"
        assert fn("test_zip_made_with_7z.zip") == "xxxxxx"
        assert fn("test_zip_made_with_7z_store.zip") == "xxxxxx"
        assert fn("test_zip_made_with_py_default.zip") == "xxxxxx"
        assert fn("test_zip_made_with_py_lzma.zip") == "xxxxxx"
        assert fn("test_zip_made_with_winrar.zip") == "xxxxxx"
        assert fn("unicode.7z") == "xxxxxx"
        assert fn("unicode.rar") == "xxxxxx"
        assert fn("unicode.zip") == "xxxxxx"
        dir=dir #intentionally cause lint err 
        a = 2+4
        assert a == 6

