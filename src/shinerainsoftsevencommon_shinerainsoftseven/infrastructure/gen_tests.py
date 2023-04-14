
# shinerainsoftsevencommon
# Released under the LGPLv3 License





# can also do that 


'''
cfgs:
noneedtests

'''



#~ from preferences import SimpleConfigParser

#~ cfg = SimpleConfigParser()
#~ cfg.load('shinerainsoftsevencommon_gen_tests.cfg')

#~ prefs_dict


#~ expectEqualityTwoListsAsSets


'''
make list of what to test:
    go through src files
    in currentClass=None or currentClass=abc
    if see a `def abc` (and not in ignore spec)
        add it and currentClass to list
    if see a `class Foo` (and not in ignore spec)
        if spec says to get its methods, get its methods,
        otherwise create one test for the whole class
ignore spec can have wildcards like AbcFoo*
        keep track of what spec has been used so that in the end we'll warn about unused spec



and then strip out closing junk - which can contain globalscope code, string literals, etc

why the complexity?
if there is code like
```
# comment 1

class TestA:
    def testa:
        pass

# comment 2

class TestB:
    def testb:
        pass

```
we want comment 2 to be attached to TestB

'''

def _isLineATestClass(line):
    return line.startswith('class Test')

def _isLineIndented(line):
    return line.startswith(' ') or line.startswith('\t') or not line.strip()

# we'll define a header as being the file up until the last comments or docstrings before a class
def extractTestFileHeader(contents):
    reCommentOrStartDocstring = r'\n[#"' + "']" + '[^\n]*'
    reClass = r'\nclass Test[^\n]*'
    reParseHeader = rf'^(.*?)({reCommentOrStartDocstring})*{reClass}'
    found = re.match(reParseHeader, contents)
    if not found:
        return None
    else:
        return contents[len(found.group(1)):]
    
# define a footer as being the last lines after a class returns to normal indentation
def extractTextFooter(contents):
    testClasses = contents.split('\nclass Test')
    if len(testClasses) <= 1:
        return None
    else:
        lines = testClasses[-1].split('\n')
        for i, line in enumerate(lines):
            if not _isLineIndented(line):
                break
        
        allFooter = '\n'.join(lines[i:])
        return allFooter

def divideIntoSections(contents):
    lines = contents.split('\n')
    sections = []
    currentSection = Bucket(name=None, lines=[])
    hasEnteredClassYet = False
    for line in lines:
        if hasEnteredClassYet and not _isLineIndented(line):
            sections.append(currentSection)
            currentSection = Bucket(name=None, lines=[])
            hasEnteredClassYet = False
        if _isLineATestClass(line):
            currentSection.name = line.split('class Test')[1].split('#')[0].strip()
            hasEnteredClassYet= True
        currentSection.lines.append(line)
    
    sections.append(currentSection)
    for i, section in enumerate(sections):
        checkSectionValid(section)
    return sections

def checkSectionValid(section):
    # we check for multiline strings, because a class like this would currently break us,
    # class TestF:
    #     def test(self):
    #         my_string = '''
    # a very long string'''
    # if the text starts with a python keyword like def, it's probably real Python code, though, so that's ok.
    
    okStartWiths = 'import /pass /class /for /try /def /from /nonlocal /while /assert /global /with /if /@/#/\'/"'.split('/')
    if len(section.lines) and not any(section.lines[0].startswith(okStartWith) for okStartWith in okStartWiths):
        trace(f'context: {"\n".join(section.lines)}')
        trace(f'It looks like there is text or code outside of a class.')
        trace(f'If this is a multiline string, please add some indentation to each line of the multiline string.')
        trace(f'If this code outside of a class, please move it to the end of the file or into a class.')
        raise Exception("Saw text or code outside of a class.")
            
    return False

def divideTestFile(contents):
    result = Bucket(header='', footer='', mapTestNameToSection={})
    header = extractTestFileHeader(contents)
    if not header:
        # no tests found, so consider the entire file the header
        result.header = contents
        return result
    
    result.header = header
    contents = contents[len(header):]
    listSections = divideIntoSections(contents)
    if not listSections[-1].name:
        lastSection = listSections.pop()
        result.footer = '\n'.join(lastSection.lines)
    
    for section in listSections:
        assertTrue(section.name, 'section with no name?', section)
        assertTrue(not section.name in result.mapTestNameToSection, 'dupe name?', section.name)
        result.mapTestNameToSection[section.name] = '\n'.join(section.lines)
    
    return result
    
