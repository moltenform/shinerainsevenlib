
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


class RunTestByStringDivideFunctions(RunTestByStringBase):
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


