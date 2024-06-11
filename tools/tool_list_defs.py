from shinerainsoftsevenutil.standard import *
import ast
import astunparse
import pprint


def goForFile(filename):
    with open(filename, encoding='utf-8') as file:
        node = ast.parse(file.read())

    #~ print(astunparse.dump(node))
    functions = [n for n in node.body if isinstance(n, ast.FunctionDef)]
    classes = [n for n in node.body if isinstance(n, ast.ClassDef)]
    results = Bucket()
    results.functions = [f.name for f in functions if not f.name.startswith('_')]
    results.classes = [f.name for f in classes if not f.name.startswith('_')]
    return results



def getValidSymbols(thedir):
    allSymbols = {}
    for f, short in files.recurseFiles(thedir):
        if short.lower().endswith('.py'):
            if short.startswith('nocpy_') or '/nocpy_' in f or '\\nocpy_' in f:
                trace('skipping nocpy file')
                continue
            results = goForFile(f)
            rlits = results.functions + results.classes
            if short == 'files.py':
                scope = 'files'
            else:
                scope = '(global)'
            
            if not scope in allSymbols:
                allSymbols[scope] = {}
            for item in rlits:
                allSymbols[scope][item] = f
            for item in getTopLevelConstantsAndImportFroms(f):
                if item.symbolname.startswith('_'):
                    continue
                trace(rf'adding constant scope={scope}, symname={item.symbolname}.')
                allSymbols[scope][item.symbolname] = f
            
        # get ones in commonutil.py
        if short == 'common_util.py':
            allSymbols['(global)']['endswith'] = f
            allSymbols['(global)']['startswith'] = f
            allSymbols['(global)']['iterbytes'] = f
            allSymbols['(global)']['bytes_to_string'] = f
            allSymbols['(global)']['asbytes'] = f
            allSymbols['(global)']['rinput'] = f
            allSymbols['(global)']['ustr'] = f
            allSymbols['(global)']['uchr'] = f
            allSymbols['(global)']['anystringtype'] = f
            allSymbols['(global)']['bytetype'] = f
            allSymbols['(global)']['xrange'] = f
            allSymbols['(global)']['isPy3OrNewer'] = f

    # get builtins
    import builtins
    for item in dir(builtins):
        if not item.startswith('_'):
           allSymbols['(global)'][item] = '(builtin)' 
    return allSymbols

def checkValidSyms(allSymbols, filename):
    for item in getAllFnCalls(filename):
        if item.symbolname.startswith('_'):
            continue
        if item.type == 'method' and item.obj == 'files':
            if item.symbolname not in allSymbols['files']:
                print(rf'====\nunknown files call {item.symbolname}', item)
        elif item.type == 'fncall':
            if item.symbolname not in allSymbols['(global)']:
                print('====\nunknown call', item)


def getTopLevelConstantsAndImportFroms(filename):
    lns = files.readAll(filename).replace('\r\n', '\n').split('\n')
    trace(filename)

    with open(filename, encoding='utf-8') as file:
        tree = ast.parse(file.read())
        for node in tree.body: # don't walk, we only want top levels
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        ret = Bucket(linecontext = files.getName(filename) +':'+ lns[node.lineno - 1])
                        ret.type = 'global'
                        ret.symbolname = target.id
                        yield ret
                    
            if isinstance(node, ast.ImportFrom):
                for name in node.names:
                    if isinstance(name, ast.alias):
                        ret = Bucket(linecontext = files.getName(filename) +':'+ lns[node.lineno - 1])
                        if name.name == '*' or name.asname == '*':
                            continue
                        ret.type = 'importfrom'
                        if name.asname:
                            ret.symbolname = name.asname
                        else:
                            ret.symbolname = name.name
                        yield ret

def getAllFnCalls(filename):
    lns = files.readAll(filename).replace('\r\n', '\n').split('\n')
    with open(filename, encoding='utf-8') as file:
        tree = ast.parse(file.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    # method 
                    
                    if isinstance(node.func.value, ast.Name):
                        ret = Bucket(linecontext = files.getName(filename) +':'+ lns[node.lineno - 1])
                        ret.type = 'method'
                        ret.symbolname = node.func.attr
                        ret.obj = node.func.value.id
                        yield ret
                    else:
                        # could be a complicated expression like (a or b).doThis()
                        # which we don't support yet
                        pass
                elif isinstance(node.func, ast.Name):
                    ret = Bucket(linecontext = files.getName(filename) +':'+lns[node.lineno - 1])
                    ret.type = 'fncall'
                    ret.symbolname = node.func.id
                    yield ret

            #~ import astunparse
            #~ if isinstance(i, ast.Call) and isinstance(i.func, ast.Attribute) and i.func.attr == 'split':
                #~ print(astunparse.dump(i))
                #~ continue
                #~ ln = lns[i.lineno-1]
                #~ code = ln[i.col_offset:i.end_col_offset]
                #~ trace('====')
                #~ trace(code, i.lineno, i.col_offset, i.end_col_offset)
                #~ for k in dir(i):
                    #~ trace(k, getattr(i,k))
                #~ print('got it', i.args)
                #~ for arg in i.args:
                    #~ trace('   ', arg)


def goForAll(dir):
    allSyms = getValidSymbols(dir)
    for f, short in files.recurseFiles(dir):
        
        if short.lower().endswith('.py'):
            if short.startswith('nocpy_') or '/nocpy_' in f or '\\nocpy_' in f:
                trace('skipping nocpy file')
                continue
            if not 'bn_python_common' in f:
                checkValidSyms(allSyms, f, )
            #~ results = goForFile(f)
            #~ rlits = results.functions + results.classes
            #~ if len(rlits):
                #~ isInSubd =  'bn_python_common.' if 'bn_python_common' in short else ''
                #~ importst = rf'from {isInSubd}{short.replace(".py", "")} import ' + ', '.join(rlits)
                #~ print(importst)


goForAll(r'C:\b\pydev\devhiatus\pytools_music\labs_coordinate_music\labs_coordinate_music')
#~ goForAll(r'C:\b\pydev\dev\contracts\gnostic\gnosticnotepad\src\tools\typescript-super-auto-import')
#~ goForFile('tools/test.py')
#~ it = getAllFnCalls(r"C:\b\pydev\dev\contracts\gnostic\gnosticnotepad\src\tools\typescript-super-auto-import\bn_python_common\common_ui.py")
#~ for item in it:
    #~ if item.symbolname == 'split':
        #~ print(item)         
