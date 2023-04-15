
from gen_tests_divide import *
from preferences import *
import ast

# possible future feature: configs could have wildcards

def getParsedTests(dirSrcModules, dirTests, previewOnly=False):
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

def getListOfRelevantTestsNeeded(path, cfg):
    contents = files.readAll(path)
    getListOfRelevantTestsNeededImpl(path, contents, cfg)
    
    
def getListOfRelevantTestsNeededImpl(path, contents, cfg):
    if 'tests_not_needed' not in cfg:
        cfg['tests_not_needed'] = {}
    if 'test_all_methods_in_class' not in cfg:
        cfg['test_all_methods_in_class'] = {}
    
    if cfg['test_not_needed'].get(files.getname(path)) or files.getname(path).startswith('_'):
        return []
    
    results = []
    parsed = parsePythonModuleIntoListOfFunctionsAndClasses(contents)
    for item in parsed:
        if item.type == 'fn':
            if not item.name.startswith('_') and not cfg['tests_not_needed'].get(item.name):
                results.append(_determineTestName(item.name))
        elif item.type == 'cls':
            if not item.name.startswith('_') and not cfg['tests_not_needed'].get(item.name):
                if cfg['test_all_methods_in_class'].get(item.name):
                    for methodName in item.methods:
                        results.append(_determineTestName(clsName=item.name, fnName=methodName))
                else:
                    results.append(_determineTestName(item.name))
                    
    return results
    
    
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
