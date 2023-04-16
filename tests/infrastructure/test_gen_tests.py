
from shinerainsoftsevencommon.infrastructure import gen_tests
from shinerainsoftsevencommon import *
import pytest


# no corresponding test file, generate new test file
# no corresponding test file, in ignored files
# duplicate in sources
# duplicate in tests
# duplicate in sources (different file)
# duplicate in tests (different file)
# test file that doesn't correspond with sources
# test file that doesn't correspond with sources (no marker, so it's fine)
# cfg entry with nothing corresponding in sources
# unit test with nothing corresponding in sources

# reconstructing twice doesn't change anything
# moving a function in source moves it in the tests, even between files
# offer to make new test, class without methods
# offer to make new test, class and all methods
# empty cfg should not throw errors

# full example
# (use both a local file and one in a subdirectory)



    shineRainSoftSevenCommonPreferences.silenceTraceAndAlert = True
