
from shinerainsoftsevencommon.infrastructure import gen_tests_divide
from shinerainsoftsevencommon import *
import pytest
import re

testCases = """
▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ exampleTypical ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃
# commentHeader1
import foo
# commentHeader2
import bar
# commentE
code1 = 1
# begin auto tests
import other_later

class TestE:
    def test_typicalCases(self):
        pass

def helperFnF():
    pass

class TestF:
    def test_typicalCases(self):
        pass

class HelperClassG():
    pass

class TestG(OtherClass):
    def test_typicalCases(self):
        pass

\"\"\" docstring H \"\"\"

class TestH(OtherClass): # and comment
    def test_typicalCases(self):
        pass

\'\'\' docstring I \'\'\'

class TestI: # with comment
    def test_typicalCases(self):
        pass

# end auto tests

# commentFooterAfterEnd

footerCodeHere = 1
------------------------- expect `got.header` --------------------------
# commentHeader1
import foo
# commentHeader2
import bar
# commentE
code1 = 1
------------------------- expect `got.strMapTestNameToSection` --------------------------
{
'E:': '''import other_later

class TestE:
    def test_typicalCases(self):
        pass
''',
'F:': '''def helperFnF():
    pass

class TestF:
    def test_typicalCases(self):
        pass
''',
'G': '''class HelperClassG():
    pass

class TestG(OtherClass):
    def test_typicalCases(self):
        pass
''',
'H': '''\"\"\" docstring H \"\"\"

class TestH(OtherClass): # and comment
    def test_typicalCases(self):
        pass
''',
'I:': '''\'\'\' docstring I \'\'\'

class TestI: # with comment
    def test_typicalCases(self):
        pass
'''}
------------------------- expect `got.footer` --------------------------
# commentFooterAfterEnd

footerCodeHere = 1

▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ exampleEmptyHeader ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃
# begin auto tests

class TestF:
    def test_typicalCases(self):
        pass

class TestG:
    def test_typicalCases(self):
        pass

# end auto tests

extraCodeHere = 1
------------------------- expect `got.header` --------------------------
------------------------- expect `got.strMapTestNameToSection` --------------------------
{
'F:': '''
class TestF:
    def test_typicalCases(self):
        pass
''',
'G:': '''class TestG:
    def test_typicalCases(self):
        pass
'''}
------------------------- expect `got.footer` --------------------------
extraCodeHere = 1

▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ exampleEmptyFooter ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃
import foo

# begin auto tests

class TestF:
    def test_typicalCases(self):
        pass

class TestG:
    def test_typicalCases(self):
        pass
        
# end auto tests
------------------------- expect `got.header` --------------------------
------------------------- expect `got.strMapTestNameToSection` --------------------------
{
'F:': '''
class TestF:
    def test_typicalCases(self):
        pass
''',
'G:': '''class TestG:
    def test_typicalCases(self):
        pass
        '''}
------------------------- expect `got.footer` --------------------------
extraCodeHere = 1

▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ exampleFirstSectionCanStartWithCode ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃
# begin auto tests
testCode = 1
class TestF:
    def test_typicalCases(self):
        pass

class TestG:
    def test_typicalCases(self):
        pass

# end auto tests
------------------------- expect `got.header` --------------------------
------------------------- expect `got.strMapTestNameToSection` --------------------------
{
'F:': '''testCode = 1
class TestF:
    def test_typicalCases(self):
        pass
''',
'G:': '''class TestG:
    def test_typicalCases(self):
        pass
'''}
------------------------- expect `got.footer` --------------------------

▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ exampleLastSectionCannotHaveLooseCommments_ShouldError ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃
# begin auto tests
testCode = 1
class TestF:
    def test_typicalCases(self):
        pass

# extra comment
# end auto tests
------------------------- expect error type --------------------------
ShineRainSoftSevenCommonError
------------------------- expect error contains --------------------------
not see a test name
▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ exampleLastSectionCannotHaveLooseCode_ShouldError ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃
# begin auto tests
testCode = 1
class TestF:
    def test_typicalCases(self):
        pass

code = 1
# end auto tests

extraCodeHere = 1
------------------------- expect error type --------------------------
ShineRainSoftSevenCommonError
------------------------- expect error contains --------------------------
not see a test name

▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ exampleIndentedBlocksThatArentATestClass ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃
# begin auto tests
def fn1():
    pass

class NotATest:
    pass

otherLines = 1

class TestIsATest:
    pass
# end auto tests
------------------------- comment --------------------------
     this is why I can't have a check like
     if not hasEnteredClassYet and not _isLineIndented(line) and line.startswith('def '):
        assertTrue(False, 'make sure everything in a test class is indented', context)
     because it would misfire on helper classes.
------------------------- expect `got.header` --------------------------
------------------------- expect `got.strMapTestNameToSection` --------------------------
{
'IsATest:': '''def fn1():
    pass

class NotATest:
    pass

otherLines = 1

class TestIsATest:
    pass'''}
------------------------- expect `got.footer` --------------------------

▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ exampleSpaceShouldBeOKBetweenTests ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃
# begin auto tests
class TestFoo:
    def test1(self):
        emptyLineAfterThis

    def test2(self):
        spacesAfterThis
        
    def test3(self):
        tabsAfterThis
\t\t\t
    def test4(self):
        indentedStringAfterThis
    "a string"
    def test5(self):
        indentedCommentAfterThis
    # a comment
    
# end auto tests
------------------------- expect `got.header` --------------------------
------------------------- expect `got.strMapTestNameToSection` --------------------------
{
'Foo:': '''class TestFoo:
    def test1(self):
        emptyLineAfterThis

    def test2(self):
        spacesAfterThis
        
    def test3(self):
        tabsAfterThis
\t\t\t
    def test4(self):
        indentedStringAfterThis
    "a string"
    def test5(self):
        indentedCommentAfterThis
    # a comment
    '''}
------------------------- expect `got.footer` --------------------------

▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ exampleForgettingMarkers_ShouldError ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃
class TestFoo:
    def test1(self):
        pass
------------------------- expect error type --------------------------
AssertionError
------------------------- expect error contains --------------------------
add the string

▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ exampleNonIndentedMultilineString_ShouldError ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃
# begin auto tests
class TestFoo:
    def test1(self):
        a = \"\"\"this
is a long
string\"\"\"
# end auto tests
------------------------- expect error type --------------------------
ShineRainSoftSevenCommonError
------------------------- expect error contains --------------------------
text or code outside

▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ exampleIndentedMultilineStringIsFine ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃
# begin auto tests
class TestFoo:
    def test1(self):
        a = \"\"\"this
 is a long
 string\"\"\"
# end auto tests
------------------------- expect `got.header` --------------------------
------------------------- expect `got.strMapTestNameToSection` --------------------------
{
'Foo:': '''class TestFoo:
    def test1(self):
        a = \"\"\"this
 is a long
 string\"\"\"'''}
------------------------- expect `got.footer` --------------------------

▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ exampleRandomCodeBetweenTests_ShouldError ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃
# begin auto tests
class TestFoo:
    def test1(self):
        pass
code = 1
    def test2(self):
        pass
# end auto tests
------------------------- expect error type --------------------------
ShineRainSoftSevenCommonError
------------------------- expect error contains --------------------------
text or code outside

▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ exampleRandomCodeBetweenTestsIsOKIfFirstLineIsKeywordOrComment ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃
# begin auto tests
class TestFoo:
    def test1(self):
        pass
import aaaaa
code = 1
class TestBar:
    def test2(self):
        pass
# comments work too
code = 1
class TestBaz:
    def test3(self):
        pass
# end auto tests
------------------------- expect `got.header` --------------------------
------------------------- expect `got.strMapTestNameToSection` --------------------------
{
'Foo:': '''class TestFoo:
    def test1(self):
        pass''',
'Bar:': '''import aaaaa
code = 1
class TestBar:
    def test2(self):
        pass''',
'Baz:': '''# comments work too
code = 1
class TestBaz:
    def test3(self):
        pass'''}
------------------------- expect `got.footer` --------------------------
▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ exampleRandomCodeBetweenTestsIsOKIfStructuredDecorated ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃
# begin auto tests
class TestFoo:
    def test1(self):
        pass
@decorate
class TestBar:
    def test2(self):
        pass
# end auto tests
------------------------- expect `got.header` --------------------------
------------------------- expect `got.strMapTestNameToSection` --------------------------
{
'Foo:': '''class TestFoo:
    def test1(self):
        pass''',
'Bar:': '''@decorate
class TestBar:
    def test2(self):
        pass'''}
------------------------- expect `got.footer` --------------------------
▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ exampleForgettingToIndentComment_ShouldErrorBecauseLastHasNoName ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃
# begin auto tests
class TestFoo:
    def test1(self):
        pass
# a comment
    def test2(self):
        pass
# end auto tests
------------------------- expect error type --------------------------
ShineRainSoftSevenCommonError
------------------------- expect error contains --------------------------
text or code outside
▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃ exampleDupeName_ShouldError ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃
# begin auto tests
class TestFoo:
    def test1(self):
        pass
class TestFoo:
    def test2(self):
        pass
# end auto tests
------------------------- expect error type --------------------------
AssertionError
------------------------- expect error contains --------------------------
dupe name
"""

class RunTestByStringBase:
    pass

class RunTestByString(RunTestByStringBase):
    def __init__(self, context=''):
        self.largeDelimiter = '▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃'
        self.smallDelimiter = '-------------------------'
        self.context = context
        
    def parseString(self, s):
        split = re.split(r'\n' + (self.largeDelimiter[0]*3) + '+', s)
        anythingBefore = split[0]
        assertTrue(not anythingBefore.strip(), 'should not be anything before first test', anythingBefore)
        split.pop(0)
        results = []
        for testName, testContent in takeBatch(split, 2):
            results.append({'testName': testName.strip()})
            splitSections = re.split(r'\n' + (self.smallDelimiter[0]*3) + '+', testContent)
            splitSections.insert(0, 'main')
            for sectionName, sectionContent in takeBatch(splitSections, 2):
                results[-1][sectionName.strip()] = sectionContent
        return results
    
    def unparseString(self, listTests):
        result = ''
        for test in listTests:
            result += '\n' + self.largeDelimiter + ' ' + test['testName'] + ' ' + self.largeDelimiter
            result += test.get('main', '')
            for sectionName in test:
                if sectionName != 'testName' and sectionName != 'main':
                    result += '\n' + self.smallDelimiter + ' ' + sectionName + ' ' + self.smallDelimiter
                    result += '\n' + test[sectionName]
        return result
        
    def runAndRecordResults(self, listTests, defaultTestsIfEmpty=None):
        for i, testSections in enumerate(listTests):
            try:
                self.runAndRecordResultsOne(defaultTestsIfEmpty, testSections)
            except Exception as e:
                trace('exception in test ', testSections.get('testName', ''), self.context)
                raise
        
        updatedTests = self.unparseString(listTests)
        print(updatedTests)

    def runAllTests(self):
        results = []
        for i, testSections in enumerate(listTests):
            try:
                self.runAllTestsOne(testSections)
            except Exception as e:
                trace('exception in test ', testSections.get('testName', ''), self.context)
                raise
        
        trace('tests complete', self.context)

    def runAndRecordResultsOne(self, defaultTestsIfEmpty, testSections):
        prep = self.prepOne(testSections)
        hadException = None
        try:
            got = self.runOne(testSections, prep)
        except Exception as e:
            hadException = e
        
        if hadException:
            # build a completely new section
            self.deleteOtherSections(testSections, exceptionSeen=True)
            
            if not (testSections.get('expect error type').strip() and isinstance(hadException, self.evalStr(testSections['expect error type']))):
                testSections['expect error type'] = hadException.__class__.__name__
            
            if not (testSections.get('expect error contains').strip() and testSections['expect error contains'] in str(hadException)):
                testSections['expect error contains'] = str(hadException)
        else:
            self.deleteOtherSections(testSections, exceptionSeen=False)
            
            got = self.interpretOne(got)
            if defaultTestsIfEmpty and len(testSections) <= 2:
                for sectionName in defaultTestsIfEmpty:
                    testSections[sectionName] = ''
            
            for sectionName in testSections:
                if sectionName.startswith('expect '):
                    sToEval = sectionName.split('`')[1]
                    wasEvalled = self.evalStr(wasEvalled, got)
                    testSections[sectionName] = wasEvalled
    
            
    def runAllTestsOne(self, testSections):
        prep = self.prepOne(testSections)
        if any(sectionName.startswith('expect error' for sectionName in testSections)):
            hadException = None
            try:
                got = self.runOne(testSections, prep)
            except Exception as e:
                hadException = e
            
            assertTrue(hadException, 'exception expected but did not occur', testSections)
            if 'expect error type' in testSections:
                assertTrue(isinstance(hadException, self.evalStr(testSections['expect error type'])),
                    f"wrong error type expected {testSections['expect error type']} but got {hadException.__class__.__name__}")
            if 'expect error contains' in testSections:
                assertTrue(testSections['expect error contains'] in str(hadException),
                    f"string '{testSections['expect error contains']}' not in '{str(e)}'")
        else:
            got = self.runOne(testSections, prep)
            got = self.interpretOne(got)
            for sectionName in testSections:
                if sectionName.startswith('expect '):
                    sToEval = sectionName.split('`')[1]
                    wasEvalled = self.evalStr(wasEvalled, got)
                    assertEq(testSections[sectionName], wasEvalled, sectionName)
        
    
    def deleteOtherSections(self, exceptionSeen):
        for key in list(testSections.keys()):
            if exceptionSeen:
                if key.startswith('expect ') and not key.startswith('expect error'):
                    del testSections[key]
            else:
                if key.startswith('expect error'):
                    del testSections[key]
    
    def evalStr(self, s, got=None):
        # the local var `got` will be magically passed in.
        return eval(s)
    
    ######################
    
    def prepOne(self, testSections):
        '''Prepare to run the test (not run in a try/except)'''
        pass
    
    def runOne(self, testSections, prep):
        '''Run the specific test (is run in a try/except)'''
        got = gen_tests_divide.divideTestFile('', testSections['main'])
        return got
    
    def interpretOne(self, testSections, got):
        '''Interpret the results so that they can be easily compared later'''
        strExpected = '{'
        for key in expected.mapTestNameToSection:
            strExpected += f"\n'{key}': '''{expected.mapTestNameToSection[key]}''',"
        strExpected += '}'
        
        strExpected = strExpected.replace("\\n", "\n")
        strExpected = strExpected.replace(",})", "})")
        strExpected = strExpected.replace("''''''", "''")
        strExpected = strExpected.replace("\t\t\t", r"\t\t\t")
        strExpected = strExpected.replace("'' docstring I '''", r"'''\'\'\' docstring I \'\'\'")
        strExpected = strExpected.replace("def testExample", "def test")
        got.strMapTestNameToSection = strExpected
        return got

defaultSubstituteChars = [['\0', '0x00']]
def directoryToString(dir, substituteChars=defaultSubstituteChars):
    # all leading and trailing whitespace is lost
    result = 'FILES'
    for f, short in files.recurseFiles(dir):
        result += '\n' + f.replace(dir, '').replace(files.dirSep, '/')
        contents = files.readAll(f)
        indentedContents = '    ' + contents.replace('\n', '    \n')
        result += '\n' + indentedContents
    
    if substituteChars:
        for binary, text in substituteChars:
            result = result.replace(binary, text)
    
    return result

def _deleteDirectoryAndReplaceContentsByStringParse(s, substituteChars=defaultSubstituteChars):
    if substituteChars:
        for binary, text in substituteChars:
            s = s.replace(text, binary)
    
    results = []
    assertTrue(s.startswith('FILES'))
    s = s[len('FILES'):]
    s = s.lstrip()
    sections = re.split(r'\n\w', s)
    for section in sections:
        fileName = section.split('\n')[0]
        lines = section.split('\n')[1:]
        lines = [line.strip() for line in lines]
        fileContents = '\n'.join(lines)
        results.append(Bucket(fileName=fileName, fileContents=fileContents))
    
    return results
        
def deleteDirectoryAndReplaceContentsByString(s, dir, substituteChars=defaultSubstituteChars):
    files.ensureEmptyDir(dir)
    for result in _deleteDirectoryAndReplaceContentsByStringParse(s, substituteChars=substituteChars):
        files.writeAll(result.fileName, result.fileContents)
        
    


