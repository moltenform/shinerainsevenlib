
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

import pytest
from shinerainsoftsevenutil.standard import *

class TestTemporary:
    def testParseSchema(self):
        config = SrssConfigReader()

        # standard usage, including different types

        # standard usage, with wildcard cols and wildcard sections
        
        # different ways of representing bool

        # should throw if a default is given for a * section

        # should throw if a default is wrong type #1

        # should throw if a default is wrong type #2

        # getting and setting a manual override works

        # get some from defaults and some from cfg file

        # should throw if input cfg is wrong datatype

        # should throw if input cfg is unknown column

        # multi-line strings should work

        config.setSchemaForSection('main', {
            'string1' : [str, ''],
            'stringWithDefault' : [str, 'hasDefault'],
            'bool1' : [bool, False],
            'boolWithDefault' : [bool, True],
            'pattern_*' : [str, ''],})

        input3 = r'''
        tempEphemeralDirectory=G:\data\local\temp
        tempDirectory=D:\data\local\temp
        softDeleteDirectoryAll=D:\data\local\trash
        softDeleteDirectory_aColonBackslashb=a:\path2
        softDeleteDirectory_aColonBackslash=a:\pa
        th1
        warnSoftDeleteBetweenDrives=1
        '''
        config.parseText(input3)
        print(config.parsed.main.tempEphemeralDirectory)
        print(config.parsed.main.softDeleteDirectory_aColonBackslash)
        print(config.parsed.main.warnSoftDeleteBetweenDrives)
        print(config.findKeyForPath('a:\\tryone', 'softDeleteDirectory_'))
        print(config.findKeyForPath('a:\\b\\trytwo', 'softDeleteDirectory_'))

    def testFindKeyByLongestMatch(self):
        pass