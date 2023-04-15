
from gen_tests_divide import *
from preferences import *
import ast

# possible future feature: configs could have wildcards

def getFilePairs(dirSrcModules, dirTests, cfg, recurse):
    def withTestPrefix(path):
        if files.dirSep in path:
            return files.getParent(path) + files.dirSep + 'test_' + files.getName(path)
        else:
            return 'test_' + path
    
    pairsSourceAndTest = []
    for f, short in files.listFiles(dirSrcModules, recurse=recurse):
        if not short.startswith('test') and not short.startswith('_') and short.endswith('.py'):
            if not cfg['test_not_needed'].get(short):
                relativePath = f.replace(dirTests, '')
                correspondingTestFile = dirTests + files.dirSep + withTestPrefix(relativePath)
                if not files.exists(correspondingTestFile):
                    raise ShineRainSoftSevenCommonError('corresponding test file not found', correspondingTestFile)
                
                pairsSourceAndTest.append(Bucket(sourcesPath=f, testsPath=correspondingTestFile))
    
    return pairsSourceAndTest

def getParsedTests(pairsSourceAndTest, cfg):
    allSymbolsSeen = {}
    for pair in pairsSourceAndTest:
        pair.sources = getListOfRelevantTestsNeeded(pair.sourcesPath, cfg, allSymbolsSeen)
        pair.tests = divideTestFileByPath(pair.testsPath, cfg)
    
    return pairsSourceAndTest, allSymbolsSeen


def go():
    pairs = getFilePairs(dirSrcModules, dirTests, cfg, recurse)
    pairsSourceAndTest, allSymbolsSeen = getParsedTests(pairs, cfg)
    checkForDuplicates


def checkForDuplicates():
    listAllInSources = [testName for testName in pair.sources for pair in pairs]
    listAllInTests = [testName for testName in pair.tests.mapTestNameToSection for pair in pairs]
    throwIfDuplicates(listAllInSources)
    throwIfDuplicates(listAllInTests)
    
    # were there any in config that aren't real?
    for symbol in cfg['test_not_needed']:
        if not symbol.endswith('.py') and symbol not in allSymbolsSeen:
            warn('this is in the cfg file but not in sources', symbol)
    


def getParsedTests(dirSrcModules, dirTests, cfg, previewOnly=False):
    mapFilenameToParsedTest = {}
    for f, short in files.recurseFiles(dirTests):
        relativePath = f.replace(dirTests, '')
        if short.startswith('test') and short.endswith('.py'):
            mapFilenameToParsedTest[relativePath] = divideTestFileByPath(f)
    
    # make this just about the function name. that way if you move a function from one file to another,
    # the tests will automatically pick up that change and move the test too!
    mapFunctionNameToTestContent = {}
    for testFile in mapFilenameToParsedTest:
        for testName in testFile.mapTestNameToSection:
            if testName in mapFunctionNameToTestContent:
                assertTrue(False, 'test name seen twice', testName, testFile)
            
            mapFunctionNameToTestContent[testName] = testFile.mapTestNameToSection[testName]
    
    mapSrcNameToListOfTestsNeeded = {}
    allTestsNeeded = []
    for f, short in files.recurseFiles(dirSrcModules):
        if not short.startswith('test') and short.endswith('.py'):
            relativePath = f.replace(dirSrcModules, '')
            if not cfg['test_not_needed'].get(files.getname(path)) and not files.getname(path).startswith('_'):
                testsNeeded = getListOfRelevantTestsNeeded(path, cfg)
                mapSrcNameToListOfTestsNeeded[relativePath] = testsNeeded
                allTestsNeeded.extend(testsNeeded)
    
    throwIfDuplicates(allTestsNeeded, lambda item: item.replace('Test', ''), context=path)
    
    pairs = []
    for relativePath in mapSrcNameToListOfTestsNeeded:
        if files.dirsep in relativePath:
            correspondingFile = files.getparent(relativePath) + files.dirSep + 'test_' + files.getname(relativePath)
        else:
            correspondingFile = 'test_' + files.getname(relativePath)
        
        existsOnDisk = files.exists(dirTests + files.dirSep + correspondingFile)
        foundInMap = mapFilenameToParsedTest.get(correspondingFile)
        assertTrue(foundInMap, f'Not found {correspondingFile}, existsOnDisk={existsOnDisk}')
        pairs.append(Bucket(sourceFile=relativePath, testFile=foundInMap))
    
    
    
def parsePythonModuleIntoListOfFunctionsAndClasses(contents):
    # use real ast parsing. otherwise it is hard to know where classes end.
    # and we can get tripped up by multiline strings.
    def _getMethods(node):
        return [item.name for item in node if isinstance(item, ast.FunctionDef)]

    results = []
    parsed = ast.parse(contents)
    
    # do not use walk/iterate because we only want top level, not nested, functions
    for item in parsed.body:
        if isinstance(item, ast.FunctionDef):
            results.append(Bucket(type='fn', name=item.name))
        elif isinstance(item, ast.ClassDef):
            results.append(Bucket(type='cls', name=item.name, methods=_getMethods(item.body)))
    
    return results

def _determineTestName(fnName, clsName=''):
    result = fnName[0].upper() + fnName[1:]
    if clsName:
        result = clsName[0].upper() + clsName[1:] + result
    return 'Test' + result

def getListOfRelevantTestsNeeded(path, cfg, allSymbolsSeen):
    contents = files.readAll(path)
    results = getListOfRelevantTestsNeededImpl(path, contents, cfg, allSymbolsSeen)
    throwIfDuplicates(results, context=path)
    return results
    
def getListOfRelevantTestsNeededImpl(path, contents, cfg, allSymbolsSeen):
    results = []
    parsed = parsePythonModuleIntoListOfFunctionsAndClasses(contents)
    allSymbolsSeen = {}
    for item in parsed:
        if item.type == 'fn':
            allSymbolsSeen[item.name] = 1
            if not item.name.startswith('_') and not cfg['tests_not_needed'].get(item.name):
                results.append(_determineTestName(item.name))
        elif item.type == 'cls':
            allSymbolsSeen[item.name] = 1
            if not item.name.startswith('_') and not cfg['tests_not_needed'].get(item.name):
                if cfg['test_all_methods_in_class'].get(item.name):
                    for methodName in item.methods:
                        results.append(_determineTestName(clsName=item.name, fnName=methodName))
                else:
                    results.append(_determineTestName(item.name))
                    
    return results

def loadCfg(pathCfg):
    configParser = SimpleConfigParser()
    configParser.load(pathCfg)
    cfg = configParser.prefs_dict
    if 'tests_not_needed' not in cfg:
        cfg['tests_not_needed'] = {}
    if 'test_all_methods_in_class' not in cfg:
        cfg['test_all_methods_in_class'] = {}
    
    return cfg
    
    
#~ cc = SimpleConfigParser()
#~ cc.load('shinerainsoftsevencommon_gen_tests.cfg')
#~ trace(cc.prefs_dict)
#~ trace(cc.prefs_dict['test_methods'].get('abc'))
#~ trace(cc.prefs_dict['test_methods'].get('abcd'))
#~ for k in cc.prefs_dict['test_methods']:
    #~ trace(k)

#~ code = files.readAll('preferences.py')
#~ parsed = ast.parse(code)
#~ for k in parsed.body:
    #~ if isinstance(k, ast.FunctionDef):
        #~ trace(k, k.name)
    #~ if isinstance(k, ast.ClassDef):
        #~ trace(k, k.name)
        #~ for classPart in k.body:
            #~ trace('within', classPart, dirFields(classPart))

trace(getListOfRelevantTestsNeeded('preferences.py', {}),)
