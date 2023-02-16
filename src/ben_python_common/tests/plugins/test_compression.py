# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv3 license.

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

def mk():
    import zipfile
    tmpdir = r"E:\tmp"
    files.ensureEmptyDirectory(tmpdir)
    out = tmpdir + '/dir-within-archive'
    zipPath = r"C:\b\devarchive\mycode\archivetier1\ben_python_common\src\ben_python_common\tests\plugins\collat\testcollat.zip"
    with zipfile.ZipFile(zipPath, 'r') as zip:
        zip.extractall(path=out, members=None, pwd=None)
    # solid mode will be visible because it will shrink these.
    files.copy(out + '/beach-redundant-1.jpg', out + '/beach-redundant-2.jpg', True)
    
    recordedPaths = []
    def recordPath(short):
        recordedPaths.append(short)
        return tmpdir + '\\' + short
    
    def expectSizeCloseToKB(short, expectedSize):
        gotInKb = files.getsize(tmpdir + '\\' + short) / 1024
        assertTrue(abs(expectedSize - gotInKb) < 5, 'Difference is more than 5kb', gotInKb)

    dirToArchive = out
    archive = 'zip-7z-max.zip'
    common_compression.addAllTo7z(dirToArchive, recordPath(archive), common_compression.optsCompression.optsMax, solid=False)
    expectSizeCloseToKB(archive, 96.5)
    
    archive = 'zip-7z-strong.zip'
    common_compression.addAllTo7z(dirToArchive, recordPath(archive), common_compression.optsCompression.optsStrong, solid=False)
    expectSizeCloseToKB(archive, 96.5)
    
    archive = 'zip-7z-default.zip'
    common_compression.addAllTo7z(dirToArchive, recordPath(archive), common_compression.optsCompression.optsDefault, solid=False)
    expectSizeCloseToKB(archive, 98.1)
    
    archive = 'zip-7z-store.zip'
    common_compression.addAllTo7z(dirToArchive, recordPath(archive), common_compression.optsCompression.optsStore, solid=False)
    expectSizeCloseToKB(archive, 165)
    
    archive = 'zip-winrar-default.zip'
    common_compression.addAllToRar(dirToArchive, recordPath(archive), solid=False)
    expectSizeCloseToKB(archive, 92.1)
    
    archive = 'zip-py-store.zip'
    common_compression.addAllToZip(dirToArchive, recordPath(archive), common_compression.zipMethods.store)
    expectSizeCloseToKB(archive, 165)
    
    archive = 'zip-py-deflate.zip'
    common_compression.addAllToZip(dirToArchive, recordPath(archive), common_compression.zipMethods.deflate)
    expectSizeCloseToKB(archive, 99.1)
    
    archive = 'zip-py-lzma.zip'
    common_compression.addAllToZip(dirToArchive, recordPath(archive), common_compression.zipMethods.lzma)
    expectSizeCloseToKB(archive, 92.3)
    
    for isSolid in [True, False]:
        isSolidStr = 'solid' if isSolid else 'not-solid'
        archive = 'rar-rar4-%s-4096kb.rar'%(isSolidStr)
        common_compression.addAllToRar(dirToArchive, recordPath(archive), formatVersion='4',
            dictSize='4096k', solid=isSolid)
        expectSizeCloseToKB(archive, 55.8 if isSolid else 77.7)
        
        archive = 'rar-rar5-%s-512mb.rar'%(isSolidStr)
        common_compression.addAllToRar(dirToArchive, recordPath(archive), formatVersion='5',
            dictSize='512m', solid=isSolid)
        expectSizeCloseToKB(archive, 69.3 if isSolid else 91.4)
        
        archive = 'rar-rar4-%s-store.rar'%(isSolidStr)
        common_compression.addAllToRar(dirToArchive, recordPath(archive), formatVersion='4',
                                       solid=isSolid, effort=common_compression.optsCompression.optsStore)
        expectSizeCloseToKB(archive, 165)
        
        archive = 'rar-rar5-%s-store.rar'%(isSolidStr)
        common_compression.addAllToRar(dirToArchive, recordPath(archive), formatVersion='5',
                                       solid=isSolid, effort=common_compression.optsCompression.optsStore)
        expectSizeCloseToKB(archive, 165)
        
        archive = '7z-%s-max.7z'%(isSolidStr)
        common_compression.addAllTo7z(dirToArchive, recordPath(archive), solid=isSolid,
            effort=common_compression.optsCompression.optsMax)
        expectSizeCloseToKB(archive, 70.0 if isSolid else 92.0)
        
        archive = '7z-%s-strong.7z'%(isSolidStr)
        common_compression.addAllTo7z(dirToArchive, recordPath(archive), solid=isSolid,
            effort=common_compression.optsCompression.optsStrong)
        expectSizeCloseToKB(archive, 70.0 if isSolid else 92.0)
        
        archive = '7z-%s-default.7z'%(isSolidStr)
        common_compression.addAllTo7z(dirToArchive, recordPath(archive), solid=isSolid,
            effort=common_compression.optsCompression.optsDefault)
        expectSizeCloseToKB(archive, 70.3 if isSolid else 92.3)
        
        archive = '7z-%s-store.7z'%(isSolidStr)
        common_compression.addAllTo7z(dirToArchive, recordPath(archive), solid=isSolid,
            effort=common_compression.optsCompression.optsStore)
        expectSizeCloseToKB(archive, 165)

@pytest.fixture()
def fixture_dir():
    basedir = join(tempfile.gettempdir(), 'ben_python_common_test', 'empty')
    basedir = ustr(basedir)
    ensureEmptyDirectory(basedir)
    os.chdir(basedir)
    yield basedir
    ensureEmptyDirectory(basedir)
    