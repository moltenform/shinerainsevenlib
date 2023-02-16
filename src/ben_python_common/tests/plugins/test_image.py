# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv3 license.

import pytest
import os

from ... import files
from ... import common_image
from ..test_files import fixture_dir

def getRawImageType(inPath):
    from PIL import Image
    im = Image.open(inPath)
    return im.format

class TestImage(object):
    def _getInPath(self):
        # this example image is a real mpo, from https://github.com/odrevet/Multi-Picture-Object
        myParent = files.getparent(os.path.abspath(__file__))
        return files.join(myParent, 'collat/sample.mpo.jpg')
        
    def test_identity(self, fixture_dir):
        f = self._getInPath()
        assert getRawImageType(f) == 'MPO'
        assert common_image.getImageType(f) == 'JPG'

