
# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv2.1 License

import pytest
from src.shinerainsevenlib.standard import *
from src.shinerainsevenlib.plugins.plugin_configreader import getExecutablePathFromPrefs
from src.shinerainsevenlib.core import assertException

class TestTemporary:
    def testParseSchema(self):

        # standard usage, including different types
        config = SrssConfigReader()
        config.setSchemaForSection('main', {
            'string1' : [str, ''],
            'stringWithDefault1' : [str, 'hasDefault1'],
            'stringWithDefault2' : [str, 'hasDefault2'],
            'bool1' : [bool, False],
            'boolWithDefault1' : [bool, True],
            'boolWithDefault2' : [bool, True],
            })
        config.setSchemaForSection('othersection', {
            'otherString' : [str, ''],
            'otherBool' : [bool, False],
            })
        cfgInput = r'''
string1=abc
bool1=True
stringWithDefault1=givenValue
[othersection]
boolWithDefault1=False
otherString=def
otherBool=False
        '''
        config.parseText(cfgInput)
        assert config.parsed.main.string1 == 'abc'
        assert config.parsed.main.bool1 is True
        assertException(lambda: config.parsed.main.missingcol)
        assertException(lambda: config.parsed.missingsection.string1)
        assert config.parsed.othersection.otherString == 'def'
        assert config.parsed.othersection.otherBool is False
        assert config.parsed.main.stringWithDefault1 == 'givenValue'
        assert config.parsed.main.stringWithDefault2 == 'hasDefault2'
        assert config.parsed.main.boolWithDefault1 is False
        assert config.parsed.main.boolWithDefault2 is True

        # standard usage, with wildcard cols and wildcard sections
        config = SrssConfigReader()
        config.setSchemaForSection('main', {
            'string1' : [str, ''],
            'pattern_*' : [str, ''],})
        config.setSchemaForSection('sectionwildcard*', {
            'stringwithdefault' : [str, 'hasdefault'],
            'bool1' : [bool, False],
            })
        cfgInput = r'''
string1=abc
bool1=True
[sectionwildcard1]
stringwithdefault=overridehere
bool1=True
[sectionwildcard2]
bool1=True
[sectionwildcard3]
bool1=False
        '''
        config.parseText(cfgInput)
        assertException(lambda: config.parsed.main.missingcol)
        assertException(lambda: config.parsed.sectionwildcard.bool1)
        assert config.parsed.main.stringWithDefault1 == 'givenValue'


        # different ways of representing bool

        # should throw if accesing a missing one with no default
        
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

