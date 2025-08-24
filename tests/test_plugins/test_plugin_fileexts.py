
#~ class TestFilesUtils:
    #~ def test_extensionPossiblyExecutableNoExt(self, fxDirPlain):
        #~ assert extensionPossiblyExecutable('noext') is False
        #~ assert extensionPossiblyExecutable('/path/noext') is False

    #~ def test_extensionPossiblyExecutableExt(self, fxDirPlain):
        #~ assert extensionPossiblyExecutable('ext.jpg') is False
        #~ assert extensionPossiblyExecutable('/path/ext.jpg') is False

    #~ def test_extensionPossiblyExecutableDirsep(self, fxDirPlain):
        #~ assert extensionPossiblyExecutable('dirsep/') is False
        #~ assert extensionPossiblyExecutable('/path/dirsep/') is False

    #~ def test_extensionPossiblyExecutablePeriod(self, fxDirPlain):
        #~ assert 'exe' == extensionPossiblyExecutable('test.jpg.exe')
        #~ assert 'exe' == extensionPossiblyExecutable('/path/test.jpg.exe')

    #~ def test_extensionPossiblyExecutablePeriodOk(self, fxDirPlain):
        #~ assert extensionPossiblyExecutable('test.exe.jpg') is False
        #~ assert extensionPossiblyExecutable('/path/test.exe.jpg') is False

    #~ def test_extensionPossiblyExecutableOk(self, fxDirPlain):
        #~ assert extensionPossiblyExecutable('ext.c') is False
        #~ assert extensionPossiblyExecutable('/path/ext.c') is False
        #~ assert extensionPossiblyExecutable('ext.longer') is False
        #~ assert extensionPossiblyExecutable('/path/ext.longer') is False

    #~ def test_extensionPossiblyExecutableExe(self, fxDirPlain):
        #~ assert 'exe' == extensionPossiblyExecutable('ext.exe')
        #~ assert 'exe' == extensionPossiblyExecutable('/path/ext.exe')
        #~ assert 'exe' == extensionPossiblyExecutable('ext.com')
        #~ assert 'exe' == extensionPossiblyExecutable('/path/ext.com')
        #~ assert 'exe' == extensionPossiblyExecutable('ext.vbScript')
        #~ assert 'exe' == extensionPossiblyExecutable('/path/ext.vbScript')

    #~ def test_extensionPossiblyExecutableWarn(self, fxDirPlain):
        #~ assert 'warn' == extensionPossiblyExecutable('ext.Url')
        #~ assert 'warn' == extensionPossiblyExecutable('/path/ext.Url')
        #~ assert 'warn' == extensionPossiblyExecutable('ext.doCM')
        #~ assert 'warn' == extensionPossiblyExecutable('/path/ext.doCM')
        #~ assert 'warn' == extensionPossiblyExecutable('ext.EXOPC')
        #~ assert 'warn' == extensionPossiblyExecutable('/path/ext.EXOPC')