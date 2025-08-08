
import tempfile
import os

class RunTestByStringBase:
    pass

class RunTestByStringDivideFunctions(RunTestByStringBase):
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
    
    def prepOne(self, testSections):
        '''Prepare to run the test (not run in a try/except)'''
        pass
    
    def runOne(self, testSections, prep):
        '''Run the specific test (is run in a try/except)'''
        raise NotImplementedError
    
    def interpretOne(self, testSections, got):
        '''Interpret the results so that they can be easily compared later'''
        raise NotImplementedError


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
    files.ensureEmptyDirectory(dir)
    for result in _deleteDirectoryAndReplaceContentsByStringParse(s, substituteChars=substituteChars):
        files.writeAll(result.fileName, result.fileContents)

def getEmptyTempDirectory(subdir):
    result = os.path.join(tempfile.gettempdir(), 'shinerainsevenlib_test', subdir)
    files.ensureEmptyDirectory(basedir)
    return result

