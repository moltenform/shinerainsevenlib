

from ..core import *
from .. import files
import fnmatch as _fnmatch
import configparser as _configparser
import os as _os

class SrssConfigReader:
    """
    example:

    config = SimpleConfigReader()
    config.setSchemaForSection('main', {'setting1' : [int, 0], 'setting2' : [bool, True], 'setting3' : [str, 'default']})
    config.setSchemaForSection('customSection*', {'path*' : [str, '']})

    example config:
    # comment
    ; comment
    key=value
    spaces in keys=allowed
    spaces in values=allowed as well
    emptystring=
    example=a multi-line
        string that continues across strings

    we don't yet support required fields or required sections.

    wrapper around ConfigParser that 1) doesn't need main section 2) validates schema 3) has better defaults.
    """
    def __init__(self, autoInsertDefaultSection='main', checkSchema=True, caseSensitive=True, allowNewLinesInValues=True):
        self.parsed = Bucket()
        self._checkSchema = checkSchema
        self._schema = {}
        self._autoInsertMainSection = autoInsertDefaultSection
        self._caseSensitive = caseSensitive
        self._allowNewLinesInValues = allowNewLinesInValues
    
    def setSchemaForSection(self, sectionName, schemaData):
        self._schema[sectionName] = schemaData

    def _lookupSchemaSection(self, sectionName):
        for key in self._schema:
            if _fnmatch.fnmatch(sectionName, key):
                return self._schema[key]
        
        assertTrue(False, 'unknown section name', sectionName)
    
    def _lookupSchemaCol(self, sectionName, colName):
        sectionData = self._lookupSchemaSection(sectionName)
        for key in sectionData:
            if _fnmatch.fnmatch(colName, key):
                return sectionData[key]
            
        assertTrue(False, 'unknown column', colName)
    
    def _populateDefaultsForAll(self):
        for sectionName in self._schema:
            if '*' not in sectionName:
                self._populateDefaultsForSection(sectionName)

    def _populateDefaultsForSection(self, sectionName):
        sectionData = self._lookupSchemaSection(sectionName)
        for colName in sectionData:
            colType, colDefaultVal = sectionData[colName]
            if '*' in colName:
                assertTrue(not colDefaultVal, "we don't support default values for wildcard ")
            else:
                # confirm that the default value is the correct type
                colDefaultVal = self.interpretValue(colDefaultVal, colType, context=f'col {colName}')
                self.setVal(sectionName, colName, colDefaultVal)

    def setVal(self, section, col, v):
        if not hasattr(self.parsed, section):
            setattr(self.parsed, section, Bucket())
        parsedSection = getattr(self.parsed, section)
        setattr(parsedSection, col, v)
    
    def getValOrNone(self, section, col):
        if not hasattr(self.parsed, section):
            setattr(self.parsed, section, Bucket())
        parsedSection = getattr(self.parsed, section)
        if hasattr(parsedSection, col):
            return getattr(parsedSection, col)
        else:
            return None

    def checkSchemaCol(self, sectionName, colName, val):
        if not self._checkSchema:
            return val
        colData = self._lookupSchemaCol(sectionName, colName)
        assertTrue(colData, 'unknown col')
        colType, colDefaultVal = colData
        return self.interpretValue(val, colType, context=f'col {colName}')

    def interpretValue(self, val, colType, context):
        if colType is bool:
            val = SrssConfigReader.strToBool(val)
        else:
            assertTrue(callable(colType), 'invalid col type, want function or class', context)
            val = colType(val)
        return val

    def parse(self, path):
        text = files.readAll(path)
        return self.parseText(text)
    
    def parseText(self, text):
        # different versions of python have different configparser behavior
        assertTrue(isPy3OrNewer, 'Py2 not supported')

        # check expected start
        if self._autoInsertMainSection:
            expectSection = '[' + self._autoInsertMainSection + ']\n'
            if not (text.strip().startswith(expectSection) or ('\n' + expectSection) in text):
                text = expectSection + text

        # start configparser
        rawparsed = _configparser.ConfigParser(strict=True,
            empty_lines_in_values=False, interpolation=None, delimiters='=')
        if self._caseSensitive:
            rawparsed.optionxform = str
        rawparsed.read_string(text)
        self._populateDefaultsForAll()
        sections = rawparsed.sections()
        for sectionName in sections:
            # populate again for this section, to support wildcards
            assertTrue(not sectionName == 'DEFAULT', 'we do not support defaults')
            self._populateDefaultsForSection(sectionName)
            options = rawparsed.options(sectionName)
            for option in options:
                val = rawparsed.get(sectionName, option)
                val = self.checkSchemaCol(sectionName, option, val)
                self.setVal(sectionName, option, val)
        
    def findKeyForPath(self, path, prefix, sectionName='main'):
        """Helper method finding the longest match,
        that starts with the prefix. See tests."""
        path = _os.path.realpath(path)
        path = path.lower()
        path = path.replace(':', 'Colon')
        path = path.replace('/', 'Slash')
        path = path.replace('\\', 'Backslash')
        return self.findKeyByLongestMatch(path, prefix, sectionName)

    def findKeyByLongestMatch(self, s, prefix, sectionName='main'):
        """Helper method finding the longest match:
        Find the column that starts with the prefix
        and matches as much of `s` as possible. See tests."""
        section = getattr(self.parsed, sectionName)
        cols = getObjAttributes(section)
        cols = [col for col in cols if col.startswith(prefix)]
        results = []
        for col in cols:
            if col.startswith(prefix):
                withoutPrefix = col[len(prefix):]
                if s.startswith(withoutPrefix):
                    results.append(col)

        if not results:
            return None, None
        results.sort(key=lambda col: len(col))
        return results[-1], getattr(section, results[-1])

    @staticmethod
    def strToBool(s, context=''):
        if not s:
            return False
        elif s in (True, False):
            return s
        elif s.lower() in ('true', 'yes', '1'):
            return True
        elif s.lower() in ('false', 'no', '0'):
            return False
        else:
            raise ValueError(rf'Expected true or false but got {s}, {context}')
    
_cachedInternalPrefs = None
def getSsrsInternalPrefs():
    if not _cachedInternalPrefs:
        myPath = _os.path.realpath(__file__)
        dir = files.getParent(files.getParent(myPath))
        cfgPath = dir + '/shinerainsoftsevenutil.cfg'
        if files.exists(cfgPath):
            configText = files.readAll(cfgPath)
        else:
            configText = ''
        
        _cachedInternalPrefs = SrssConfigReader()
        _cachedInternalPrefs.setSchemaForSection('main', {
            'tempDirectory' : [str, ''],
            'tempEphemeralDirectory' : [str, ''],
            'warnSoftDeleteBetweenDrives' : [bool, False],
            'softDeleteDirectory' : [str, ''],
            'softDeleteDirectory_*' : [str, ''],
            })
        _cachedInternalPrefs.parse(configText)

        if not _cachedInternalPrefs.parsed.main.tempEphemeralDirectory:
            _cachedInternalPrefs.parsed.main.tempDirectory

    return _cachedInternalPrefs


