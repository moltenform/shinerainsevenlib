

import os
import pytest
from ..files import join
from ..common_ui import *
from .test_files import fxDirPlain as fixture_dir_
fxDirPlain = fixture_dir_


class TestCommonUI:
    

    def test_softDeleteFileShouldMakeFileNotExist(self, fxDirPlain):
        path = join(fxDirPlain, 'testdelfile1.txt')
        files.writeAll(path, 'contents')
        assert os.path.exists(path)
        newlocation = softDeleteFile(path)
        assert not os.path.exists(path)
        assert os.path.exists(newlocation)

    def test_softDeleteFileShouldRenameFirstCharOfFile(self, fxDirPlain):
        path = join(fxDirPlain, 'zzzz', 'testdelfile2.txt')
        files.makeDirs(files.getParent(path))
        files.writeAll(path, 'contents')
        newlocation = softDeleteFile(path)
        assert os.path.exists(newlocation)
        assert files.getName(newlocation).startswith('z')
