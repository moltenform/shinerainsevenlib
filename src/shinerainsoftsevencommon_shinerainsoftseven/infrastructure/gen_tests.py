
from gen_tests_divide import *
from config_file import *
import ast

# possible future feature: configs could have wildcards

def goGenTests(dirSrcModules, dirTests, cfg, recurse=False):
    pairs = getFilePairs(dirSrcModules, dirTests, cfg, recurse)
    pairs, allSymbolsSeen = getParsedTests(pairs, cfg)
    checkForDuplicatesAndExtraTests(pairs, cfg, allSymbolsSeen, dirTests, recurse)
    reconstructTestFiles(pairs, cfg)


def getFilePairs(dirSrcModules, dirTests, cfg, recurse):
    def withTestPrefix(path):
        if files.dirSep in path:
            return files.getParent(path) + files.dirSep + 'test_' + files.getName(path)
        else:
            return 'test_' + path
    
    pairsSourceAndTest = []
    for f, short in list(files.listFiles(dirSrcModules, recurse=recurse)):
        if not short.startswith('test') and not short.startswith('_') and short.endswith('.py'):
            if not cfg['test_not_needed'].get(short):
                relativePath = f.replace(dirSrcModules, '')
                correspondingTestFile = dirTests + files.dirSep + withTestPrefix(relativePath)
                if not files.exists(correspondingTestFile):
                    warn('corresponding test file not found ' + correspondingTestFile + ' . we will generate one.')
                    generateTestFile(correspondingTestFile)
                
                pairsSourceAndTest.append(Bucket(sourcesPath=f, testsPath=correspondingTestFile))
    
    return pairsSourceAndTest

def getParsedTests(pairsSourceAndTest, cfg):
    allSymbolsSeen = {}
    for pair in pairsSourceAndTest:
        pair.sources = getListOfRelevantTestsNeeded(pair.sourcesPath, cfg, allSymbolsSeen)
        pair.tests = divideTestFileByPath(pair.testsPath, cfg)
    
    return pairsSourceAndTest, allSymbolsSeen

def checkForDuplicatesAndExtraTests(pairs, cfg, allSymbolsSeen, dirTests, recurse):
    listAllInSources = [testName for testName in pair.sources for pair in pairs]
    listAllInTests = [testName for testName in pair.tests.mapTestNameToSection for pair in pairs]
    throwIfDuplicates(listAllInSources)
    throwIfDuplicates(listAllInTests)
    
    # were there any test files that don't correspond with a source file?
    allTestFiles = set((item.testPath for item in pairs))
    for f, short in files.listFiles(dirTests):
        if short.startswith('test') and short.endswith('.py') and ('\n' + gMarkerStart) in files.readAll(f):
            if f not in allTestFiles:
                alert(f, f'tests containing {gMarkerEnd} must match 1-1 with a source file, renamed source file?', f)
    
    # were there any in config that aren't real?
    for symbol in cfg['test_not_needed']:
        if not symbol.endswith('.py') and symbol not in allSymbolsSeen:
            alert('this is in the cfg file but not in sources', symbol)
    
    # were there any tests that aren't real?
    compared = compareTwoListsAsSets(listAllInSources, listAllInTests)
    testsNeededForThis = compared.missingItems
    testsHasNoCorrespondingInTheSource = compared.extraItems
    if testsHasNoCorrespondingInTheSource:
        # could override these in cfg, but then hard to get the order right
        assertTrue(False, f'cannot continue. these tests do not correspond to anything in sources. move them after the {gMarkerEnd} marker if intentional.', testsHasNoCorrespondingInTheSource)
    
    # give a preview of what we'll add
    if testsNeededForThis:
        alert("We are about to add a test template for these", testsNeededForThis)

def reconstructTestFiles(pairs, cfg):
    # do it by fn name not file name, so that if we move a function from one file to another, the tests automatically update themselves!
    mapSymbolToTest = {}
    for pair in pairs:
        for symbol in pair.tests.mapTestNameToSection:
            mapSymbolToTest[symbol] = pair.tests.mapTestNameToSection[symbol]
    
    for pair in pairs:
        reconstructTestFile(pair, mapSymbolToTest, cfg)

def reconstructTestFile(pair, mapSymbolToTest, cfg):
    with open(pair.testPath, 'w', encoding='utf-8') as f:
        f.write(pair.test.header + '\n')
        f.write(gMarkerStart + '\n')
        for symbol in pair.source:
            if symbol in mapSymbolToTest:
                f.write(mapSymbolToTest[symbol])
            else:
                f.write(createTestFromTemplate(symbol, cfg))
        
        f.write(gMarkerEnd + '\n')
        f.write(pair.test.footer)
    
def createTestFromTemplate(symbol, cfg):
    defaultTemplate = ''''
class %testName%:
    def typicalCases(self):
        pass
        
    def edgeCases(self):
        pass
    '''
    template = cfg['main'].get('test_template', defaultTemplate)
    template = template.replace('\\n', '\n').replace('\\t', '\t')
    template = template.replace('%testName%', symbol)
    return template

def generateTestFile(f):
    template = f'''
import pytest
from shinerainsoftcommon import *

{gMarkerStart}

{gMarkerEnd}
'''
    files.writeAll(f, template)
    
def parsePythonModuleIntoListOfFunctionsAndClasses(contents):
    # use real ast parsing. otherwise it is hard to know where classes end.
    # and we can get tripped up by multiline strings.
    def _getMethods(node):
        return [item.name for item in node if isinstance(item, ast.FunctionDef)]

    results = []
    parsed = ast.parse(contents)
    
    # do not use walk because we only want top level, not nested, functions
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
    if 'main' not in cfg:
        cfg['main'] = {}
    
    return cfg
    
    
