
# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv2.1 License

import fnmatch as _fnmatch
import configparser as _configparser
import os as _os
import shutil as _shutil

from .plugin_fileexts import *
from .. import files
from .. import core as srss
from ..core import assertTrue, assertEq, Bucket, jslike

class SrssConfigReader:
    """
    Example:

    >>> config = SimpleConfigReader()
    >>> config.setSchemaForSection('main', {'setting1' : [int, 0], 'setting2' : [bool, True], 'setting3' : [str, 'default']})
    >>> config.setSchemaForSection('customSection*', {'path*' : [str, '']})

    example config:
    >>> # comment
    >>> ; comment
    >>> key=value
    >>> spaces in keys=allowed
    >>> spaces in values=allowed as well
    >>> emptystring=
    >>> example=a multi-line
    >>>     string that continues across strings

    We don't yet support required fields or required sections.

    Wrapper around ConfigParser that 1) doesn't need a main section 2) validates schema 3) has better defaults.
    """

    def __init__(self, autoInsertDefaultSection='main', checkSchema=True, caseSensitive=True):
        self.parsed = Bucket()
        self._checkSchema = checkSchema
        self._schema = {}
        self._autoInsertMainSection = autoInsertDefaultSection
        self._caseSensitive = caseSensitive

    def setSchemaForSection(self, sectionName, schemaData):
        self._schema[sectionName] = schemaData

    def _lookupSchemaSection(self, sectionName):
        for key, val in self._schema.items():
            if _fnmatch.fnmatch(sectionName, key):
                return val

        assertTrue(False, 'unknown section name', sectionName)
        return None

    def _lookupSchemaCol(self, sectionName, colName):
        sectionData = self._lookupSchemaSection(sectionName)
        for key in sectionData:
            if _fnmatch.fnmatch(colName, key):
                return sectionData[key]

        assertTrue(False, 'unknown column', colName)
        return None

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
                colDefaultVal = self.interpretValue(
                    colDefaultVal, colType, context=f'col {colName}'
                )
                self.setVal(sectionName, colName, colDefaultVal)

    def setVal(self, section, col, v):
        if not self.parsed.get(section):
            setattr(self.parsed, section, Bucket())
        parsedSection = self.parsed.get(section)
        setattr(parsedSection, col, v)

    def getValOrNone(self, section, col):
        if not self.parsed.get(section):
            setattr(self.parsed, section, Bucket())
        parsedSection = self.parsed.get(section)
        if parsedSection.get(col):
            return parsedSection.get(col)
        else:
            return None

    def checkSchemaCol(self, sectionName, colName, val):
        if not self._checkSchema:
            return val
        colData = self._lookupSchemaCol(sectionName, colName)
        assertTrue(colData, 'unknown col')
        colType, _colDefaultVal = colData
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
        assertTrue(srss.isPy3OrNewer, 'Py2 not supported')

        # check expected start
        if self._autoInsertMainSection:
            expectSection = '[' + self._autoInsertMainSection + ']\n'
            if not (text.strip().startswith(expectSection) or ('\n' + expectSection) in text):
                text = expectSection + text

        # start configparser
        rawparsed = _configparser.ConfigParser(
            strict=True, empty_lines_in_values=False, interpolation=None, delimiters='='
        )
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
                val = rawparsed.get(sectionName, option, fallback=None)
                assertTrue(val is not None)
                val = self.checkSchemaCol(sectionName, option, val)
                self.setVal(sectionName, option, val)

    def findKeyForPath(self, path, prefix, sectionName='main'):
        """Helper method finding the longest match,
        that starts with the prefix. See tests."""
        path = _os.path.abspath(path)
        path = path.lower()
        path = path.replace(':', 'Colon')
        path = path.replace('/', 'Slash')
        path = path.replace('\\', 'Backslash')
        return self.findKeyByLongestMatch(path, prefix, sectionName)

    def findKeyByLongestMatch(self, s, prefix, sectionName='main'):
        """Helper method finding the longest match:
        Find the column that starts with the prefix and
        matches as much of `s` as possible. See tests."""
        section = self.parsed.get(sectionName)
        cols = srss.getObjAttributes(section)
        cols = [col for col in cols if col.startswith(prefix)]
        results = []
        for col in cols:
            if col.startswith(prefix):
                withoutPrefix = col[len(prefix) :]
                if s.startswith(withoutPrefix):
                    results.append(col)

        if not results:
            return None, None

        results.sort(key=lambda col: len(col))
        return results[-1], section.get(results[-1])

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

myPath = _os.path.abspath(__file__)

def getSrssConfigLocation():
    "Internal helper for finding where shinerainsevenlib's own cfgs are"
    dirPath = files.getParent(files.getParent(myPath))
    userHome = _os.path.expanduser('~')
    candidates = [
        dirPath + '/shinerainsevenlib.cfg',
        dirPath + '/core/shinerainsevenlib.cfg',
        dirPath + '/shinerainsevenlib/core/shinerainsevenlib.cfg',
        userHome + '/.shinerainsevenlib/shinerainsevenlib.cfg',
    ]

    return jslike.find(candidates, lambda path: files.exists(path))

_gCachedInternalPrefs = None

def getSsrsInternalPrefs():
    "Internal helper for getting shinerainsevenlib's own cfgs"
    global _gCachedInternalPrefs
    if not _gCachedInternalPrefs:
        cfgPath = getSrssConfigLocation()
        assertTrue(cfgPath and files.isFile(cfgPath), 'currently require cfg file')
        if cfgPath:
            configText = files.readAll(cfgPath)
        else:
            configText = ''

        _gCachedInternalPrefs = SrssConfigReader()
        _gCachedInternalPrefs.setSchemaForSection(
            'main',
            {
                'tempDirectory': [str, ''],
                'tempEphemeralDirectory': [str, ''],
                'warnSoftDeleteBetweenDrives': [bool, False],
                'softDeleteDirectory': [str, ''],
                'softDeleteDirectory_*': [str, ''],
                'pathExecutable*': [str, ''],
            },
        )
        _gCachedInternalPrefs.parseText(configText)

    return _gCachedInternalPrefs

def getExecutablePathFromPrefs(name, throwIfNotFound, fallbacksToTry=None):
    "We let people configure by putting paths to external executables in the cfg file,"
    from .. import files
    prefs = getSsrsInternalPrefs()
    keyname = f'pathExecutable{name[0].upper()}{name[1:].lower()}'
    got = prefs.parsed.main.get(keyname)
    if got:
        assertTrue(files.isFile(got) or _shutil.which(got), "shinerainsevenlib.cfg File not found", keyname, got)
        return got

    if files.isFile(name) or _shutil.which(name):
        return name
    
    if fallbacksToTry:
        for fallback in fallbacksToTry:
            if files.isFile(fallback) or _shutil.which(fallback):
                return fallback

    if throwIfNotFound:
        assertTrue(False, f"path to executable {name} not found. Please put it on system path, or add an entry for {keyname} in shinerainsevenlib.cfg")
    else:
        return None

