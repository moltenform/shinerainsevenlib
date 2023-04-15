
# shinerainsoftsevencommon
# Released under the LGPLv3 License

from shinerainsoftsevencommon import *

#~ expectEqualityTwoListsAsSets

'''

if there is test code like this:
# comment 1

class TestA:
    def testa:
        pass

# comment 2

class TestB:
    def testb:
        pass

we want comment 2 to be attached to TestB

'''

gMarkerStart = '# begin tests'
gMarkerEnd = '# end tests'

def _isLineATestClass(line):
    return line.startswith('class Test')

def _isLineIndented(line):
    return line.startswith(' ') or line.startswith('\t') or not line.strip()

def _divideIntoSections(context, contents, verbose):
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
            className = getClassOrFnName(line)
            currentSection.name = className[len('Test'):]
            hasEnteredClassYet = True
        
        currentSection.lines.append(line)
    
    sections.append(currentSection)
    for i, section in enumerate(sections):
        _checkSectionValid(context, section, i, verbose)
    
    return sections

def getClassOrFnName(line):
    if line.startswith('class '):
        line = line[len('class '):]
    if line.startswith('def '):
        line = line[len('def '):]
    line = line.split('#')[0].split('(')[0].strip()
    return line

def _checkSectionValid(context, section, i, verbose):
    # we check for multiline strings, because a class like this would currently break us,
    # class TestF:
    #     def test(self):
    #         my_string = '''
    # a very long string'''
    # if the text starts with a python keyword like def, it's probably real Python code, though, so that's ok.
    # (except for the first section)
    
    okStartWiths = 'import /pass /class /for /try /def /from /nonlocal /while /assert /global /with /if /@/#/\'/"'.split('/')
    isFirst = i == 0
    if len(section.lines) and not isFirst and not any(section.lines[0].startswith(okStartWith) for okStartWith in okStartWiths):
        joinedLines = "\n".join(section.lines)
        if verbose:
            trace(f'context: {context}\n{joinedLines}')
            trace(f'It looks like there is text or code outside of a class.')
            trace(f'If this is a multiline string, please add some indentation to each line of the multiline string.')
            trace(f'If this code outside of a class, please move it to the end of the file or into a class.')
        
        raise ShineRainSevenCommonError("Saw text or code outside of a class.")
    
    if not section.name:
        joinedLines = "\n".join(section.lines)
        if verbose:
            trace(f'context: {context}\n{joinedLines}')
            trace(f'Did not see a test name. Consider placing this code after {gMarkerEnd}')
        
        raise ShineRainSevenCommonError("Did not see a test name.")
            
    return False

def divideTestFile(context, contents, verbose=True):
    spl = contents.split('\n' + gMarkerStart + '\n')
    assertEq(2, len(spl), f'Please add the string {gMarkerStart} exactly once to the test file', context)
    header, contents = spl
    
    spl = contents.split('\n' + gMarkerEnd + '\n')
    assertEq(2, len(spl), f'Please add the string {gMarkerEnd} exactly once to the test file', context)
    contents, footer = spl
    
    result = Bucket(header=header, footer=footer, mapTestNameToSection={})
    listSections = _divideIntoSections(context, contents, verbose=verbose)
    
    for section in listSections:
        assertTrue(not section.name in result.mapTestNameToSection, 'dupe name?', context, section.name)
        result.mapTestNameToSection[section.name] = '\n'.join(section.lines)
    
    return result
    
def divideTestFileByPath(path):
    contents = files.readAll(path)
    return divideTestFile(context=path, contents=contents)
    
    