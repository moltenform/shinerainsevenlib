# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv3 license.

import pytest
import tempfile
import os
import sys
import shutil
import zipfile
from os.path import join
from ...common_util import isPy3OrNewer, ustr
from ...common_higher import getNowAsMillisTime
from ..test_files import fixture_dir
from ... import files
from ...plugins import common_compression

class TestCompression(object):

    def test_addAllToZip(self, fixture_dir):
        # defaults to deflate method
        outPath, lst = self._prepMakeZip(fixture_dir)
        assert 4 == len(lst)
        assert ('a/b.bmp', zipfile.ZIP_DEFLATED, 11) == (lst[0].filename, lst[0].compress_type, lst[0].file_size)
        assert ('a/b/im.png', zipfile.ZIP_DEFLATED, 9) == (lst[1].filename, lst[1].compress_type, lst[1].file_size)
        assert ('a/b/te.txt', zipfile.ZIP_DEFLATED, 9) == (lst[2].filename, lst[2].compress_type, lst[2].file_size)
        assert ('a/noext', zipfile.ZIP_DEFLATED, 9) == (lst[3].filename, lst[3].compress_type, lst[3].file_size)

        # use deflate+store
        outPath, lst = self._prepMakeZip(fixture_dir, method=common_compression.zipMethods.deflate,
            alreadyCompressedAsStore=True)
        assert 4 == len(lst)
        assert ('a/b.bmp', zipfile.ZIP_DEFLATED, 11) == (lst[0].filename, lst[0].compress_type, lst[0].file_size)
        assert ('a/b/im.png', zipfile.ZIP_STORED, 9) == (lst[1].filename, lst[1].compress_type, lst[1].file_size)
        assert ('a/b/te.txt', zipfile.ZIP_DEFLATED, 9) == (lst[2].filename, lst[2].compress_type, lst[2].file_size)
        assert ('a/noext', zipfile.ZIP_DEFLATED, 9) == (lst[3].filename, lst[3].compress_type, lst[3].file_size)

        # use lzma
        if isPy3OrNewer:
            outPath, lst = self._prepMakeZip(fixture_dir, method=common_compression.zipMethods.lzma)
            assert 4 == len(lst)
            assert ('a/b.bmp', zipfile.ZIP_LZMA, 11) == (lst[0].filename, lst[0].compress_type, lst[0].file_size)
            assert ('a/b/im.png', zipfile.ZIP_LZMA, 9) == (lst[1].filename, lst[1].compress_type, lst[1].file_size)
            assert ('a/b/te.txt', zipfile.ZIP_LZMA, 9) == (lst[2].filename, lst[2].compress_type, lst[2].file_size)
            assert ('a/noext', zipfile.ZIP_LZMA, 9) == (lst[3].filename, lst[3].compress_type, lst[3].file_size)
    
    
    @pytest.mark.skipif('not sys.platform.startswith("win")')
    def test_createArchives(self, fixture_dir):
        if not files.exists(common_compression.getRarPath().binRar):
            print('Note::: Skipping test, rar not found')
            return
        
        if not files.exists('7z') and not shutil.which('7z'):
            print('Note::: Skipping test, 7z not found')
            return
        
        tmpdir, dirToArchive = self._prepTempDirectory(fixture_dir)
        
        archive = files.join(tmpdir, 'zip-7z-max.zip')
        common_compression.addAllTo7z(dirToArchive, archive, common_compression.optsCompression.optsMax, solid=False)
        self._checkSizeCloseToKB(archive, 96.5)
        
        archive = files.join(tmpdir, 'zip-7z-strong.zip')
        common_compression.addAllTo7z(dirToArchive, archive, common_compression.optsCompression.optsStrong, solid=False)
        self._checkSizeCloseToKB(archive, 96.5)
        
        archive = files.join(tmpdir, 'zip-7z-default.zip')
        common_compression.addAllTo7z(dirToArchive, archive, common_compression.optsCompression.optsDefault, solid=False)
        self._checkSizeCloseToKB(archive, 98.1)
        
        archive = files.join(tmpdir, 'zip-7z-store.zip')
        common_compression.addAllTo7z(dirToArchive, archive, common_compression.optsCompression.optsStore, solid=False)
        self._checkSizeCloseToKB(archive, 165)
        
        archive = files.join(tmpdir, 'zip-winrar-default.zip')
        common_compression.addAllToRar(dirToArchive, archive, solid=False)
        self._checkSizeCloseToKB(archive, 92.1)
        
        archive = files.join(tmpdir, 'zip-py-store.zip')
        common_compression.addAllToZip(dirToArchive, archive, common_compression.zipMethods.store)
        self._checkSizeCloseToKB(archive, 165)
        
        archive = files.join(tmpdir, 'zip-py-deflate.zip')
        common_compression.addAllToZip(dirToArchive, archive, common_compression.zipMethods.deflate)
        self._checkSizeCloseToKB(archive, 99.1)
        
        archive = files.join(tmpdir, 'zip-py-lzma.zip')
        common_compression.addAllToZip(dirToArchive, archive, common_compression.zipMethods.lzma)
        self._checkSizeCloseToKB(archive, 92.3)
        
        for isSolid in [True, False]:
            isSolidStr = 'solid' if isSolid else 'not-solid'
            archive = files.join(tmpdir, 'rar-rar4-%s-4096kb.rar'%(isSolidStr))
            common_compression.addAllToRar(dirToArchive, archive, formatVersion='4',
                dictSize='4096k', solid=isSolid)
            self._checkSizeCloseToKB(archive, 55.8 if isSolid else 77.7)
            
            archive = files.join(tmpdir, 'rar-rar5-%s-512mb.rar'%(isSolidStr))
            common_compression.addAllToRar(dirToArchive, archive, formatVersion='5',
                dictSize='512m', solid=isSolid)
            self._checkSizeCloseToKB(archive, 69.3 if isSolid else 91.4)
            
            archive = files.join(tmpdir, 'rar-rar4-%s-store.rar'%(isSolidStr))
            common_compression.addAllToRar(dirToArchive, archive, formatVersion='4',
                                           solid=isSolid, effort=common_compression.optsCompression.optsStore)
            self._checkSizeCloseToKB(archive, 165)
            
            archive = files.join(tmpdir, 'rar-rar5-%s-store.rar'%(isSolidStr))
            common_compression.addAllToRar(dirToArchive, archive, formatVersion='5',
                                           solid=isSolid, effort=common_compression.optsCompression.optsStore)
            self._checkSizeCloseToKB(archive, 165)
            
            archive = files.join(tmpdir, '7z-%s-max.7z'%(isSolidStr))
            common_compression.addAllTo7z(dirToArchive, archive, solid=isSolid,
                effort=common_compression.optsCompression.optsMax)
            self._checkSizeCloseToKB(archive, 70.0 if isSolid else 92.0)
            
            archive = files.join(tmpdir, '7z-%s-strong.7z'%(isSolidStr))
            common_compression.addAllTo7z(dirToArchive, archive, solid=isSolid,
                effort=common_compression.optsCompression.optsStrong)
            self._checkSizeCloseToKB(archive, 70.0 if isSolid else 92.0)
            
            archive = files.join(tmpdir, '7z-%s-default.7z'%(isSolidStr))
            common_compression.addAllTo7z(dirToArchive, archive, solid=isSolid,
                effort=common_compression.optsCompression.optsDefault)
            self._checkSizeCloseToKB(archive, 70.3 if isSolid else 92.3)
            
            archive = files.join(tmpdir, '7z-%s-store.7z'%(isSolidStr))
            common_compression.addAllTo7z(dirToArchive, archive, solid=isSolid,
                effort=common_compression.optsCompression.optsStore)
            self._checkSizeCloseToKB(archive, 165)
    
        self._checkArchiveListAll(tmpdir)
    
    @pytest.mark.skipif('not sys.platform.startswith("win")')
    def test_checkArchiveIntegrityVia7z(self, fixture_dir):
        outPath, lst = self._prepMakeZip(fixture_dir)
        common_compression.checkArchiveIntegrityVia7z
    
    def _prepMakeZip(self, fixture_dir, **zipArgs):
        files.ensureEmptyDirectory(fixture_dir)
        files.makedirs(join(fixture_dir, 'a/b'))
        files.writeall(join(fixture_dir, 'a/b.bmp'), 'contents111')
        files.writeall(join(fixture_dir, 'a/b/im.png'), 'contents3')
        files.writeall(join(fixture_dir, 'a/b/te.txt'), 'contents4')
        files.writeall(join(fixture_dir, 'a/noext'), 'contents2')
        outPath = join(fixture_dir, 'a.zip')
        common_compression.addAllToZip(files.join(fixture_dir, 'a'), outPath, **zipArgs)
        with zipfile.ZipFile(outPath) as z:
            lst = z.infolist()
            lst.sort(key=lambda item: item.filename)
        
        return outPath, lst
        
    def _prepTempDirectory(self, fixture_dir):
        tmpdir = fixture_dir + '/tmp'
        out = tmpdir + '/dir-within-archive'
        # create a directory called 'dir-within-archive' with the contents:
        # unicodes.bmp -- compressible and has unicode filename
        # beach-redundant-1.jpg -- not compressible
        # beach-redundant-2.jpg -- same as other jpg, so solid mode will be much smaller
        zipPath = files.join(files.getparent(__file__), 'collat/testarchive.zip')
        with zipfile.ZipFile(zipPath, 'r') as zip:
            zip.extractall(path=out, members=None, pwd=None)
        
        files.copy(out + '/beach-redundant-1.jpg', out + '/beach-redundant-2.jpg', True)
        return tmpdir, out
    
    def _checkSizeCloseToKB(self, archive, expectedSize):
        gotInKb = files.getsize(archive) / 1024
        assert abs(expectedSize - gotInKb) < 5, 'Difference is more than 5kb ' + str(gotInKb)
    
    def _checkArchiveListAll(self, tmpdir):
        count = 0
        for f, short in list(files.recursefiles(tmpdir)):
            if files.getext(short) in ['zip', '7z', 'rar']:
                count += 1
                self._checkArchiveList(f)
                self._checkArchiveIntegrity(f)
                
        assert count == 24
        
    def _checkArchiveList(self, f):
        lst = common_compression.getContents(f, silenceWarnings='zip-winrar-' in f)
        lst.sort(key=lambda item: item['Path'])
        if 'zip-py-' in files.getname(f):
            assert len(lst) == 3
            assert lst[0]['Path'].endswith('\\beach-redundant-1.jpg')
            assert lst[0]['Size'] == "22686"
            assert lst[0]['CRC'] == '9B47D08F'
            
            assert lst[1]['Path'].endswith('\\beach-redundant-2.jpg')
            assert lst[1]['Size'] == "22686"
            assert lst[1]['CRC'] == '9B47D08F'
            
            assert '\\st-helens-' in lst[2]['Path']
            assert lst[2]['Size'] == "123570"
            assert lst[2]['CRC'] == 'CB5985DD'
        else:
            assert len(lst) == 4
            assert lst[0]['Path'].endswith('dir-within-archive')
            assert lst[0]['Type'] == 'Directory'
            
            assert lst[1]['Path'].endswith('\\beach-redundant-1.jpg')
            assert lst[1]['Size'] == "22686"
            assert lst[1]['CRC'] == '9B47D08F'
            
            assert lst[2]['Path'].endswith('\\beach-redundant-2.jpg')
            assert lst[2]['Size'] == "22686"
            assert lst[2]['CRC'] == '9B47D08F'
            
            assert '\\st-helens-' in lst[3]['Path']
            assert lst[3]['Size'] == "123570"
            assert lst[3]['CRC'] == 'CB5985DD'

    def _checkArchiveIntegrity(self, f):
        assert common_compression.checkArchiveIntegrityVia7z(f)
        corrupted = f + '.corrupt.' + files.getext(f)
        allBytes = files.readall(f, 'rb')
        allBytes = bytearray(allBytes)
        allBytes[1024 * 51] = (allBytes[1024 * 51] + 1) % 256
        files.writeall(corrupted, allBytes, 'wb')
        assert not common_compression.checkArchiveIntegrityVia7z(corrupted)
        files.delete(corrupted)
        
    

