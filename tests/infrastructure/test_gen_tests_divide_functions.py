
from shinerainsoftsevencommon.infrastructure import gen_tests
from shinerainsoftsevencommon import *
import pytest

exampleTypical = '''
# commentHeader1
import foo
# commentHeader2
import bar
# commentE
code1 = 1
# begin tests
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

""" docstring H """

class TestH(OtherClass): # and comment
    def test_typicalCases(self):
        pass

\'\'\' docstring I \'\'\'

class TestI: # with comment
    def test_typicalCases(self):
        pass

# end tests

# commentFooterAfterEnd

footerCodeHere = 1
'''

exampleEmptyHeader = '''
# begin tests

class TestF:
    def test_typicalCases(self):
        pass

class TestG:
    def test_typicalCases(self):
        pass

# end tests

extraCodeHere = 1
'''

exampleEmptyFooter = '''
import foo

# begin tests

class TestF:
    def test_typicalCases(self):
        pass

class TestG:
    def test_typicalCases(self):
        pass
        
# end tests
'''

exampleFirstSectionCanStartWithCode = '''
# begin tests
testCode = 1
class TestF:
    def test_typicalCases(self):
        pass

class TestG:
    def test_typicalCases(self):
        pass

# end tests
'''

exampleLastSectionCannotHaveLooseCommments_ShouldError = '''
# begin tests
testCode = 1
class TestF:
    def test_typicalCases(self):
        pass

# extra comment
# end tests
'''

exampleLastSectionCannotHaveLooseCode_ShouldError = '''
# begin tests
testCode = 1
class TestF:
    def test_typicalCases(self):
        pass

code = 1
# end tests

extraCodeHere = 1
'''

exampleIndentedBlocksThatArentATestClass = '''
# begin tests
def fn1():
    pass

class NotATest:
    pass

otherLines = 1

class TestIsATest:
    pass
# end tests
'''

exampleSpaceShouldBeOKBetweenTests = '''
# begin tests
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
    
# end tests
'''


exampleForgettingMarkers_ShouldError = '''
class TestFoo:
    def test1(self):
        pass
'''

exampleNonIndentedMultilineString_ShouldError = '''
# begin tests
class TestFoo:
    def test1(self):
        a = """this
is a long
string"""
# end tests
'''

exampleIndentedMultilineStringIsFine = '''
# begin tests
class TestFoo:
    def test1(self):
        a = """this
 is a long
 string"""
# end tests
'''

exampleRandomCodeBetweenTests_ShouldError = '''
# begin tests
class TestFoo:
    def test1(self):
        pass
code = 1
    def test2(self):
        pass
# end tests
'''

exampleRandomCodeBetweenTestsIsOKIfFirstLineIsKeywordOrComment = '''
# begin tests
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
# end tests
'''

exampleRandomCodeBetweenTestsIsOKIfStructuredDecorated = '''
# begin tests
class TestFoo:
    def test1(self):
        pass
@decorate
class TestBar:
    def test2(self):
        pass
# end tests
'''

exampleForgettingToIndentComment_ShouldErrorBecauseLastHasNoName = '''
# begin tests
class TestFoo:
    def test1(self):
        pass
# a comment
    def test2(self):
        pass
# end tests
'''

exampleDupeName_ShouldError = '''
# begin tests
class TestFoo:
    def test1(self):
        pass
class TestFoo:
    def test2(self):
        pass
# end tests
'''

class TestDivideTestFile:
    def testTypical(self):
        got = gen_tests.divideTestFile('', exampleTypical, verbose=False)
        assertEq(got.header, '''
# commentHeader1
import foo
# commentHeader2
import bar
# commentE
code1 = 1''')
        assertEq(got.footer, '''
# commentFooterAfterEnd

footerCodeHere = 1
''')
        assertEq(got.mapTestNameToSection, {
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
'H': '''""" docstring H """

class TestH(OtherClass): # and comment
    def test_typicalCases(self):
        pass
''',
'I:': '''\'\'\' docstring I \'\'\'

class TestI: # with comment
    def test_typicalCases(self):
        pass
'''})

    def testEmptyHeader(self):
        got = gen_tests.divideTestFile('', exampleEmptyHeader, verbose=False)
        assertEq(got.header, '')
        assertEq(got.footer, '''
extraCodeHere = 1
''')
        assertEq(got.mapTestNameToSection, {
'F:': '''
class TestF:
    def test_typicalCases(self):
        pass
''',
'G:': '''class TestG:
    def test_typicalCases(self):
        pass
'''})

    def testEmptyFooter(self):
        got = gen_tests.divideTestFile('', exampleEmptyFooter, verbose=False)
        assertEq(got.header, '''
import foo
''')
        assertEq(got.footer, '')
        assertEq(got.mapTestNameToSection, {
'F:': '''
class TestF:
    def test_typicalCases(self):
        pass
''',
'G:': '''class TestG:
    def test_typicalCases(self):
        pass
        '''})

    def testFirstSectionCanStartWithCode(self):
        got = gen_tests.divideTestFile('', exampleFirstSectionCanStartWithCode, verbose=False)
        assertEq(got.header, '')
        assertEq(got.footer, '')
        assertEq(got.mapTestNameToSection, {
'F:': '''testCode = 1
class TestF:
    def test_typicalCases(self):
        pass
''',
'G:': '''class TestG:
    def test_typicalCases(self):
        pass
'''})

    def testLastSectionCannotHaveLooseCommments_ShouldError(self):
        with pytest.raises(Exception) as e:
            gen_tests.divideTestFile('', exampleLastSectionCannotHaveLooseCommments_ShouldError, verbose=False)
        
        assert isinstance(e.value, ShineRainSevenCommonError)
        assert 'not see a test name' in str(e.value)

    def testLastSectionCannotHaveLooseCode_ShouldError(self):
        with pytest.raises(Exception) as e:
            gen_tests.divideTestFile('', exampleLastSectionCannotHaveLooseCode_ShouldError, verbose=False)
        
        assert isinstance(e.value, ShineRainSevenCommonError)
        assert 'text or code outside' in str(e.value)

    def testIndentedBlocksThatArentATestClass(self):
        # this is why I can't have a check like
        # if not hasEnteredClassYet and not _isLineIndented(line) and line.startswith('def '):
        #    assertTrue(False, 'make sure everything in a test class is indented', context)
        # because it would misfire on helper classes.

        got = gen_tests.divideTestFile('', exampleIndentedBlocksThatArentATestClass, verbose=False)
        assertEq(got.header, '')
        assertEq(got.footer, '')
        assertEq(got.mapTestNameToSection, {
'IsATest:': '''def fn1():
    pass

class NotATest:
    pass

otherLines = 1

class TestIsATest:
    pass'''})

    def testSpaceShouldBeOKBetweenTests(self):
        got = gen_tests.divideTestFile('', exampleSpaceShouldBeOKBetweenTests, verbose=False)
        assertEq(got.header, '')
        assertEq(got.footer, '')
        assertEq(got.mapTestNameToSection, {
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
    '''})

    def testForgettingMarkers_ShouldError(self):
        with pytest.raises(Exception) as e:
            gen_tests.divideTestFile('', exampleForgettingMarkers_ShouldError, verbose=False)
        
        assert isinstance(e.value, AssertionError)
        assert 'add the string' in str(e.value)
        
    def testNonIndentedMultilineString_ShouldError(self):
        with pytest.raises(Exception) as e:
            gen_tests.divideTestFile('', exampleNonIndentedMultilineString_ShouldError, verbose=False)
        
        assert isinstance(e.value, ShineRainSevenCommonError)
        assert 'text or code outside' in str(e.value)
        
    def testIndentedMultilineStringIsFine(self):
        got = gen_tests.divideTestFile('', exampleIndentedMultilineStringIsFine, verbose=False)
        assertEq(got.header, '')
        assertEq(got.footer, '')
        assertEq(got.mapTestNameToSection, {
'Foo:': '''class TestFoo:
    def test1(self):
        a = """this
 is a long
 string"""'''})

    def testRandomCodeBetweenTests_ShouldError(self):
        with pytest.raises(Exception) as e:
            gen_tests.divideTestFile('', exampleRandomCodeBetweenTests_ShouldError, verbose=False)
        
        assert isinstance(e.value, ShineRainSevenCommonError)
        assert 'text or code outside' in str(e.value)
    
    def testRandomCodeBetweenTestsIsOKIfFirstLineIsKeywordOrComment(self):
        got = gen_tests.divideTestFile('', exampleRandomCodeBetweenTestsIsOKIfFirstLineIsKeywordOrComment, verbose=False)
        assertEq(got.header, '')
        assertEq(got.footer, '')
        assertEq(got.mapTestNameToSection, {
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
        pass'''})

    def testRandomCodeBetweenTestsIsOKIfStructuredDecorated(self):
        got = gen_tests.divideTestFile('', exampleRandomCodeBetweenTestsIsOKIfStructuredDecorated, verbose=False)
        assertEq(got.header, '')
        assertEq(got.footer, '')
        assertEq(got.mapTestNameToSection, {
'Foo:': '''class TestFoo:
    def test1(self):
        pass''',
'Bar:': '''@decorate
class TestBar:
    def test2(self):
        pass'''})

    def testForgettingToIndentComment_ShouldErrorBecauseLastHasNoName(self):
        with pytest.raises(Exception) as e:
            gen_tests.divideTestFile('', exampleForgettingToIndentComment_ShouldErrorBecauseLastHasNoName, verbose=False)
        
        assert isinstance(e.value, ShineRainSevenCommonError)
        assert 'not see a test name' in str(e.value)
    
    def testDupeName_ShouldError(self):
        with pytest.raises(Exception) as e:
            gen_tests.divideTestFile('', exampleDupeName_ShouldError, verbose=False)
        
        assert isinstance(e.value, AssertionError)
        assert 'dupe name' in str(e.value)

showExpectedResultStrings = False
#~ showExpectedResultStrings = True
if showExpectedResultStrings:
    tests = [['exampleTypical', exampleTypical],
['exampleEmptyHeader', exampleEmptyHeader],
['exampleEmptyFooter', exampleEmptyFooter],
['exampleFirstSectionCanStartWithCode', exampleFirstSectionCanStartWithCode],
['exampleLastSectionCannotHaveLooseCommments_ShouldError', exampleLastSectionCannotHaveLooseCommments_ShouldError ],
['exampleLastSectionCannotHaveLooseCode_ShouldError', exampleLastSectionCannotHaveLooseCode_ShouldError],
['exampleIndentedBlocksThatArentATestClass', exampleIndentedBlocksThatArentATestClass],
['exampleSpaceShouldBeOKBetweenTests', exampleSpaceShouldBeOKBetweenTests],
['exampleForgettingMarkers_ShouldError', exampleForgettingMarkers_ShouldError],
['exampleNonIndentedMultilineString_ShouldError', exampleNonIndentedMultilineString_ShouldError],
['exampleIndentedMultilineStringIsFine', exampleIndentedMultilineStringIsFine],
['exampleRandomCodeBetweenTests_ShouldError', exampleRandomCodeBetweenTests_ShouldError],
['exampleRandomCodeBetweenTestsIsOKIfFirstLineIsKeywordOrComment', exampleRandomCodeBetweenTestsIsOKIfFirstLineIsKeywordOrComment],
['exampleRandomCodeBetweenTestsIsOKIfStructuredDecorated', exampleRandomCodeBetweenTestsIsOKIfStructuredDecorated],
['exampleForgettingToIndentComment_ShouldErrorBecauseLastHasNoName', exampleForgettingToIndentComment_ShouldErrorBecauseLastHasNoName],
['exampleDupeName_ShouldError', exampleDupeName_ShouldError],]

    for testName, testContent in tests:
        testNameUpper = testName[0].upper() + testName[1:]
        if 'ShouldError' in testName:
            template = f'''
    def test{testNameUpper}(self):
        with pytest.raises(Exception) as e:
            gen_tests.divideTestFile('', {testName}, verbose=False)
            
        assert isinstance(e.value, ShineRainSevenCommonError)
        assert 'ffffff' in str(e.value)
    '''
        else:        
            expected = gen_tests.divideTestFile('', 'test'+testName, testContent)
            strExpected = '{'
            for key in expected.mapTestNameToSection:
                strExpected += f"\n'{key}': '''{expected.mapTestNameToSection[key]}''',"
            strExpected += '}'
            
            template = f'''
    def test{testNameUpper}(self):
        got = gen_tests.divideTestFile('', {testName}, verbose=False)
        assertEq(got.header, ''{repr(expected.header)}'')
        assertEq(got.footer, ''{repr(expected.footer)}'')
        assertEq(got.mapTestNameToSection, {strExpected})
        '''
        template = template.replace("\\n", "\n")
        template = template.replace(",})", "})")
        template = template.replace("''''''", "''")
        template = template.replace("\t\t\t", r"\t\t\t")
        template = template.replace("'' docstring I '''", r"'''\'\'\' docstring I \'\'\'")
        template = template.replace("def testExample", "def test")
        
        trace('    ' + template.strip() + '\n')

