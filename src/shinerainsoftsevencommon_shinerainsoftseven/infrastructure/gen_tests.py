
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

then make map of testname->test code
    go through test file line by line
    currentSection=None
    if we have been in an indent and we leave an indent, start a new section (not yet named)
    if line starts with class, name the current section
    if file ends and section not named, name it closingJunk
    at first we are in a section called openingJunk that stops on first classTestF
    
    if line starts with spaces, fine
    if line starts with def, it gets tagged on to current section
    if line starts with #, or ', or ", it gets tagged on to current section
    if line starts with class Other, it gets tagged on to current section
    if line starts with class TestF, start a new section and say currentIndentedInTestClass
    as soon as that indentation ends, start new section


openinng junk ends on last import at the top of the file--- strip this out first 
that way a comment after last import correctly gets attached to first test
also that way opening code can contain globalscope code, string literals, etc
so can simplify by first removing openingJunk
    its ok if helpers get attached to a test, that is fine!

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

statemachine:
    amInIndentFromATest
    
    if line starts with spaces, append to current section
    if line not starts with spaces
    if amInIndentFromATest
        amInIndentFromATest = False
        start a new section
        
        if line starts with def, append to current section
        if line starts with #, or ', or ", append  to current section
        if line starts with @ or from or import, append  to current section
        if line starts with class Other, it gets tagged on to current section
        if line starts with class TestF, name the current section this
        but if line starts with other text, throw an error-could be a multiline string literal or globalscope code which we don't like

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
        return contents[len(found.group(1):]
    
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
    return sections

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
    
