# BenPythonCommon,
# 2015 Ben Fisher, released under the GPLv3 license.

import pytest
import tempfile
import os
import sys
from os.path import join
from ...common_util import isPy3OrNewer, ustr
from ...common_higher import getNowAsMillisTime
from ...files import ensureEmptyDirectory, makedirs, writeall, join
from ...plugins import common_compression

class TestCompression(object):
    def test_addAllToZip(self, fixture_dir):
        import zipfile

        def makeZip(**kwargs):
            ensureEmptyDirectory(fixture_dir)
            makedirs(join(fixture_dir, 'a/b'))
            writeall(join(fixture_dir, 'a/b.bmp'), 'contents111')
            writeall(join(fixture_dir, 'a/noext'), 'contents2')
            writeall(join(fixture_dir, 'a/b/im.png'), 'contents3')
            writeall(join(fixture_dir, 'a/b/te.txt'), 'contents4')
            outname = join(fixture_dir, 'a.zip')
            common_compression.addAllToZip(join(fixture_dir, 'a'), outname, **kwargs)
            with zipfile.ZipFile(outname) as z:
                lst = z.infolist()
                lst.sort(key=lambda o: o.filename)
            return outname, lst

        # defaults to deflate method
        outname, lst = makeZip()
        assert 4 == len(lst)
        assert ('b.bmp', zipfile.ZIP_DEFLATED, 11) == (lst[0].filename, lst[0].compress_type, lst[0].file_size)
        assert ('b/im.png', zipfile.ZIP_DEFLATED, 9) == (lst[1].filename, lst[1].compress_type, lst[1].file_size)
        assert ('b/te.txt', zipfile.ZIP_DEFLATED, 9) == (lst[2].filename, lst[2].compress_type, lst[2].file_size)
        assert ('noext', zipfile.ZIP_DEFLATED, 9) == (lst[3].filename, lst[3].compress_type, lst[3].file_size)

        # use deflate+store
        outname, lst = makeZip(method=common_compression.zipMethods.deflate, alreadyCompressedAsStore=True)
        assert 4 == len(lst)
        assert ('b.bmp', zipfile.ZIP_DEFLATED, 11) == (lst[0].filename, lst[0].compress_type, lst[0].file_size)
        assert ('b/im.png', zipfile.ZIP_STORED, 9) == (lst[1].filename, lst[1].compress_type, lst[1].file_size)
        assert ('b/te.txt', zipfile.ZIP_DEFLATED, 9) == (lst[2].filename, lst[2].compress_type, lst[2].file_size)
        assert ('noext', zipfile.ZIP_DEFLATED, 9) == (lst[3].filename, lst[3].compress_type, lst[3].file_size)

        # use lzma
        if isPy3OrNewer:
            outname, lst = makeZip(method=common_compression.zipMethods.lzma)
            assert 4 == len(lst)
            assert ('b.bmp', zipfile.ZIP_LZMA, 11) == (lst[0].filename, lst[0].compress_type, lst[0].file_size)
            assert ('b/im.png', zipfile.ZIP_LZMA, 9) == (lst[1].filename, lst[1].compress_type, lst[1].file_size)
            assert ('b/te.txt', zipfile.ZIP_LZMA, 9) == (lst[2].filename, lst[2].compress_type, lst[2].file_size)
            assert ('noext', zipfile.ZIP_LZMA, 9) == (lst[3].filename, lst[3].compress_type, lst[3].file_size)


@pytest.fixture()
def fixture_dir():
    basedir = join(tempfile.gettempdir(), 'ben_python_common_test', 'empty')
    basedir = ustr(basedir)
    ensureEmptyDirectory(basedir)
    os.chdir(basedir)
    yield basedir
    ensureEmptyDirectory(basedir)
    