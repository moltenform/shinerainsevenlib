
# shinerainsoftsevencommon
# Released under the LGPLv3 License

# a meta-tool to 1) add gpl headers to files
# and 2) add ordering; I layer my modules sequentially

from ben_python_common import *
import os
import re

def getSpecFile(pathDir, prefix):
    if not os.path.exists(pathDir):
        raise Exception('path not found')
        
    specFile = pathDir + '/ordering.txt'
    if not os.path.exists(specFile):
        raise Exception('specFile not found, ' + specFile)
    
    with open(specFile, encoding='utf-8') as f:
        listFiles = f.read().split('\n')
    
    # remove whitespace
    listFiles = [path.strip() for path in listFiles if path.strip() and not path.startswith('#')]

    listFiles = [{'path': path, 'opts': {}} for path in listFiles]
    for item in listFiles:
        if '(prefix only)' in item['path']:
            item['path'] = item['path'].replace('(prefix only)', '')
            item['opts']['prefixOnly'] = True
    
    return listFiles

def ensureCovered(listFiles, pathDir, prefix):
    # everything in ordering.txt should exist
    for item in listFiles:
        path = pathDir + '/' + item['path']
        if not os.path.exists(path):
            raise Exception('path not found ' + path)
        
    # nothing should exist not in ordering.txt
    for child in os.listdir(pathDir):
        if child.lower().endswith('.py'):
            if not ignoreOrdering(child):
                found = [item for item in listFiles if item['path'] == child]
                if not found:
                    raise Exception('not found in ordering.txt ' + child)

def ignoreOrdering(filename):
    return filename == '__init__.py' or filename.startswith('nocpy_')

def addHeaderToPyFiles(pathDir, prefix, importStar, isPackage):
    listFiles = getSpecFile(pathDir, prefix)
    print(listFiles)
    ensureCovered(listFiles, pathDir, prefix)
    
    listRelevantFiles = [item for item in listFiles if not item['opts'].get('prefixOnly')]
    listRelevantFiles.reverse()
    for i in range(len(listRelevantFiles)):
        fullPath = pathDir + '/' + listRelevantFiles[i]['path']
        _removeHeaderFromPyFile(fullPath, prefix, verbose=False)
        
        nextLine = ''
        if i > 0:
            stepBelow = listRelevantFiles[i-1]['path'].replace('.py', '')
            if isPackage and importStar:
                # a relative-import within current package
                stepBelow = '.' + stepBelow
                
            nextLine = f'from {stepBelow} import *\n' if importStar else f'import {stepBelow}\n'
        
        toAdd = '\n' + prefix + '\n' + nextLine + '\n'
        _addHeaderToPyFile(fullPath, toAdd)
    
    listHeaderOnlyFiles = [item for item in listFiles if item['opts'].get('prefixOnly')]
    for i in range(len(listHeaderOnlyFiles)):
        fullPath = pathDir + '/' + listHeaderOnlyFiles[i]['path']
        _removeHeaderFromPyFile(fullPath, prefix)
        toAdd = '\n' + prefix + '\n\n'
        _addHeaderToPyFile(fullPath, toAdd)

def _addHeaderToPyFile(fullPath, toAdd, verbose=True):
    contents = files.readAll(fullPath)
    newContents = toAdd + contents.lstrip()
    if newContents != contents:
        files.writeAll(fullPath, newContents)
        if verbose:
            print('updated the header in ' + fullPath)
    
    
def removeHeaderFromPyFiles(pathDir, prefix, recurse=True):
    # use this to change the header on files (running this then )
    from .. import files
    for f, short in files.listFiles(pathDir, allowedExts=['py'], recurse=recurse):
        _removeHeaderFromPyFile(f, prefix)
    
    print('complete.')

def _removeHeaderFromPyFile(fullPath, prefix, verbose=True):
    reHeader = '\n' + re.escape(prefix)
    reHeader += r'\n(|from [^\n]+)\n'
    
    contents = files.readAll(fullPath)
    newContents = re.sub(reHeader, '\n', contents)
    if newContents != contents:
        files.writeAll(fullPath, newContents)
        if verbose:
            print('removed the header in ' + fullPath)
    

    