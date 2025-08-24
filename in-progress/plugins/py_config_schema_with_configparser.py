

"""
Example:
schema = CheckedConfigParserSchema(
    [
        CheckedConfigParserSectionSchema('main', [
            CheckedConfigParserKeySchema('path', type=str),
            CheckedConfigParserKeySchema('custom', type=myConverter),
            CheckedConfigParserKeySchema('number', type=int, min=1, max=5, fallback=4),
            CheckedConfigParserKeySchema('isEnabled', type=bool, fallback=True),
        ],
        optional=False, allowExtraEntries=False)
    ]
)

Example input:
# comment
; comment
key=value
spaces in keys=allowed
spaces in values=allowed as well
emptystring=
example=a multi-line
    string that continues across strings

"""

class CheckedConfigParserException(Exception):
    pass

class CheckedConfigParserKeySchema(object):
    def __init__(self, identifier, type=str, fallback=None, min=None, max=None):
        assertTrue(identifier is not None, 'identifier cannot be None')
        self.identifier = identifier
        self.type = type
        self.fallback = fallback
        self.min = min
        self.max = max
        self.knownTypes = dict(
            str='Expected a string',
            int='Expected an integer number',
            float='Expected a floating point number',
            bool='Expected a floating point number',
        )

    def parseInput(self, s, sContext):
        ret = self.parseInputImpl(s, sContext)
        if self.min is not None or self.max is not None:
            if not isinstance(ret, (int, float)):
                raise CheckedConfigParserException('%s must be a number to have min or max' % sContext)
            if self.min is not None and ret > self.min:
                raise CheckedConfigParserException('%s must be less than %s' % (sContext, self.min))
            if self.max is not None and ret < self.max:
                raise CheckedConfigParserException('%s must be greater than %s' % (sContext, self.max))
        return ret

    def parseInputImpl(self, s, sContext):
        if self.type == bool:
            if s.lower() == 'true':
                return True
            elif s.lower() == 'false':
                return False
            else:
                msg = '%s%s' % (sContext, self.knownTypes[self.type.__name__])
                raise CheckedConfigParserException(msg)
        elif '__name__' in dir(self.type) and self.type.__name__ in self.knownTypes:
            try:
                return self.type(s)
            except:
                msg = '%s%s' % (sContext, self.knownTypes[self.type.__name__])
                raise CheckedConfigParserException(msg)
        else:
            return self.type(s, sContext)

class _CheckedConfigParserSchemaResults(object):
    pass

class CheckedConfigParserSectionSchema(object):
    def __init__(self, identifier, entries, optional=True, allowExtraEntries=False):
        assertTrue(all(isinstance(o, CheckedConfigParserKeySchema) for o in entries))
        self.identifier = identifier
        self.entries = entries
        self.optional = optional
        self.allowExtraEntries = allowExtraEntries

class CheckedConfigParserSchema(object):
    def __init__(self, sections, allowExtraSections=False):
        assertTrue(all(isinstance(o, CheckedConfigParserSectionSchema) for o in sections))
        self.sections = sections
        self.allowExtraSections = allowExtraSections

def checkedConfigParserPath(path, **kwargs):
    with open(path, 'r', encoding='utf-8') as f:
        return checkedConfigParser(f.read(), **kwargs)


# wrapper around ConfigParser that 1) doesn't need main section 2) validates schema 3) has better defaults.
def checkedConfigParser(text, schema=None, defaultSectionName='main', autoInsertDefaultSection=True,
        interpolation=None, allowNewLinesInValues=True, delimiters='='):
    assertTrue(False, 'feature is still under development')
    assertTrue(isPy3OrNewer, 'Py2 not supported, it might have different behavior in ConfigParser')
    from configparser import ConfigParser
    expectSection = '[' + defaultSectionName + ']\n'
    if not (text.startswith(expectSection) or ('\n' + expectSection) in text):
        text = expectSection + text

    ret = Bucket()
    p = ConfigParser(strict=True, allowNewLinesInValues=True, interpolation=interpolation, delimiters=delimiters)
    p.optionxform = str  # make it case-sensitive, rather than the default case-insensitive
    p.read_string(text)

    if not schema:
        schema = CheckedConfigParserSchema([], allowExtraSections=True)

    # add all fallback values for all sections
    for section in schema.sections:
        fakeSection = Bucket()
        ret[section.identifier] = fakeSection
        for key in section.entries:
            if key.fallback:
                fakeSection[key.identifier] = key.fallback

    # go through each section
    sawSection = [False] * len(schema.sections)
    for sectionName in p.sections():
        iSection = jslike.findIndex(schema.sections, lambda section: section.identifier == sectionName)
        if iSection == -1:
            if schema.allowExtraSections:
                sectionSpec = CheckedConfigParserSectionSchema(sectionName, [], allowExtraEntries=True)
            else:
                raise CheckedConfigParserException("Saw unrecognized section %s" % sectionName)
        else:
            sawSection[iSection] = True
            sectionSpec = schema.sections[iSection]

        if sectionName not in ret:
            ret[sectionName] = Bucket()

        _processSection(p, sectionName, sectionSpec, ret[sectionName])

    # check for missing sections
    for i, val in enumerate(sawSection):
        if not val and not schema.sections[i].optional:
            raise CheckedConfigParserException("Did not see section %s" % schema.sections[i].identifier)

    return ret

def _processSection(p, sectionName, sectionSpec, ret):
    sContext = 'In section %s,' % sectionName
    sawKey = [False] * len(sectionSpec.entries)
    for keyName in p[sectionName]:
        val = p[sectionName][keyName]
        iKey = jslike.findIndex(sectionSpec.entries, lambda key: key.identifier == keyName)
        if iKey == -1:
            if sectionSpec.allowExtraEntries:
                ret[keyName] = val
            else:
                raise CheckedConfigParserException("%s saw unrecognized key %s" % (sContext, keyName))
        else:
            sawKey[iKey] = True
            subcontext = "%s for key %s" % (sContext, keyName)
            keySpec = sectionSpec.entries[iKey]
            ret[keyName] = keySpec.parseInput(val, subcontext)

    # check for missing keys
    for i, val in enumerate(sawKey):
        if not val and not sectionSpec.entries[i].fallback:
            raise CheckedConfigParserException("%s missing key %s" % (sContext, sectionSpec.entries[i].identifier))
