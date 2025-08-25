
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.core import *
import pytest
import os


extensionPossiblyExecutable = SrssFileExts.extensionPossiblyExecutable
isCompressedTarExtension = SrssFileExts.isCompressedTarExtension
isSingleFileCompressionExtension = SrssFileExts.isSingleFileCompressionExtension
removeDotsFromExts = SrssFileExts.removeDotsFromExts

class TestFilesUtils:
    def test_extensionPossiblyExecutableNoExt(self):
        assert extensionPossiblyExecutable('noext') is False
        assert extensionPossiblyExecutable('/path/noext') is False

    def test_extensionPossiblyExecutableExt(self):
        assert extensionPossiblyExecutable('ext.jpg') is False
        assert extensionPossiblyExecutable('/path/ext.jpg') is False

    def test_extensionPossiblyExecutableDirsep(self):
        assert extensionPossiblyExecutable('dirsep/') is False
        assert extensionPossiblyExecutable('/path/dirsep/') is False

    def test_extensionPossiblyExecutablePeriod(self):
        assert 'exe' == extensionPossiblyExecutable('test.jpg.exe')
        assert 'exe' == extensionPossiblyExecutable('/path/test.jpg.exe')

    def test_extensionPossiblyExecutablePeriodOk(self):
        assert extensionPossiblyExecutable('test.exe.jpg') is False
        assert extensionPossiblyExecutable('/path/test.exe.jpg') is False

    def test_extensionPossiblyExecutableOk(self):
        assert extensionPossiblyExecutable('ext.c') is False
        assert extensionPossiblyExecutable('/path/ext.c') is False
        assert extensionPossiblyExecutable('ext.longer') is False
        assert extensionPossiblyExecutable('/path/ext.longer') is False

    def test_extensionPossiblyExecutableExe(self):
        assert 'exe' == extensionPossiblyExecutable('ext.exe')
        assert 'exe' == extensionPossiblyExecutable('/path/ext.exe')
        assert 'exe' == extensionPossiblyExecutable('ext.com')
        assert 'exe' == extensionPossiblyExecutable('/path/ext.com')
        assert 'exe' == extensionPossiblyExecutable('ext.vbScript')
        assert 'exe' == extensionPossiblyExecutable('/path/ext.vbScript')

    def test_extensionPossiblyExecutableWarn(self):
        assert 'warn' == extensionPossiblyExecutable('ext.Url')
        assert 'warn' == extensionPossiblyExecutable('/path/ext.Url')
        assert 'warn' == extensionPossiblyExecutable('ext.doCM')
        assert 'warn' == extensionPossiblyExecutable('/path/ext.doCM')
        assert 'warn' == extensionPossiblyExecutable('ext.EXOPC')
        assert 'warn' == extensionPossiblyExecutable('/path/ext.EXOPC')

    
    class TestExtensionHelpers:
        def testTarExtension(self):
            assert isCompressedTarExtension('example.tar.gz')
            assert isCompressedTarExtension('example.tar.xz')
            assert isCompressedTarExtension('example.tgz')
            assert isCompressedTarExtension('example.txz')
            assert not isCompressedTarExtension('example.jpg')
            assert not isCompressedTarExtension('example.tar.jpg')
            assert not isCompressedTarExtension('example.tgz.jpg')
            assert not isCompressedTarExtension('example.tar.gz.jpg')
            assert isCompressedTarExtension('a.b.tar.gz')
            assert isCompressedTarExtension('a.b.TAR.gz')

            # by convention these are dotfiles not actual extensions
            assert not isCompressedTarExtension('.tar.gz')

        def testTarExtensionFullPath(self):
            assert isCompressedTarExtension('/path/to/example.tar.gz')
            assert isCompressedTarExtension('/path/to/example.tar.xz')
            assert isCompressedTarExtension('/path/to/example.tgz')
            assert isCompressedTarExtension('/path/to/example.txz')
            assert not isCompressedTarExtension('/path/to/example.jpg')
            assert not isCompressedTarExtension('/path/to/example.tar.jpg')
            assert not isCompressedTarExtension('/path/to/example.tgz.jpg')
            assert not isCompressedTarExtension('/path/to/example.tar.gz.jpg')
            assert isCompressedTarExtension('/path/to/a.b.tar.gz')
            assert isCompressedTarExtension('/path/to/a.b.TAR.gz')

            # by convention these are dotfiles not actual extensions
            assert not isCompressedTarExtension('/path/to/.tar.gz')

        def testSsSingleFileCompression(self):
            assert isSingleFileCompressionExtension('example.z')
            assert isSingleFileCompressionExtension('example.gz')
            assert isSingleFileCompressionExtension('example.xz')
            
            assert not isSingleFileCompressionExtension('example.jpg')
            assert not isSingleFileCompressionExtension('example.gz.jpg')
            assert not isSingleFileCompressionExtension('example.tar.gz.jpg')
            assert not isSingleFileCompressionExtension('example.tgz.jpg')
            assert isSingleFileCompressionExtension('a.b.gz')
            assert isSingleFileCompressionExtension('a.b.GZ')

            # crucial that these are false
            assert not isSingleFileCompressionExtension('example.tar.z')
            assert not isSingleFileCompressionExtension('example.tar.gz')
            assert not isSingleFileCompressionExtension('example.tar.xz')

            # by convention these are dotfiles not actual extensions
            assert not isSingleFileCompressionExtension('.gz')

        def testSsSingleFileCompressionFullPath(self):
            assert isSingleFileCompressionExtension('/path/to/example.z')
            assert isSingleFileCompressionExtension('/path/to/example.gz')
            assert isSingleFileCompressionExtension('/path/to/example.xz')
            
            assert not isSingleFileCompressionExtension('/path/to/example.jpg')
            assert not isSingleFileCompressionExtension('/path/to/example.gz.jpg')
            assert not isSingleFileCompressionExtension('/path/to/example.tar.gz.jpg')
            assert not isSingleFileCompressionExtension('/path/to/example.tgz.jpg')
            assert isSingleFileCompressionExtension('/path/to/a.b.gz')
            assert isSingleFileCompressionExtension('/path/to/a.b.GZ')

            # crucial that these are false
            assert not isSingleFileCompressionExtension('/path/to/example.tar.z')
            assert not isSingleFileCompressionExtension('/path/to/example.tar.gz')
            assert not isSingleFileCompressionExtension('/path/to/example.tar.xz')

            # by convention these are dotfiles not actual extensions
            assert not isCompressedTarExtension('/path/to/.gz')
    

class TestRemoveDotsFromExts:
    def testBasic(self):
        s1 = set(['.a', '.b', '.c'])
        assert removeDotsFromExts(s1) == set(['a', 'b', 'c'])
        
        s1 = list(['.a', '.b', '.c'])
        assert removeDotsFromExts(s1) == set(['a', 'b', 'c'])
        
        s1 = {'.a': 1, '.b': 1, '.c': 1}
        assert removeDotsFromExts(s1) == set(['a', 'b', 'c'])

    def testEdgeCases(self):
        s1 = set(['a.a', '', '.', 'other'])
        assert removeDotsFromExts(s1) == set(['a.a', '', '', 'other'])
    