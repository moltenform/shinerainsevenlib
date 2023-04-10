
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
    listFiles = [path.strip() for path in listFiles if path.strip()]
        
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
            found = [item for item in listFiles if item['path'] == child]
            if not found:
                raise Exception('not found in ordering.txt ' + child)

def addHeaderToPyFiles(pathDir, prefix, importStar):
    listFiles = getSpecFile(pathDir, prefix)
    ensureCovered(listFiles, pathDir, prefix)
    
    listRelevantFiles = [item for item in listFiles if not item['opts']['prefixOnly']]
    for i in range(len(listRelevantFiles)):
        fullPath = pathDir + '/' + listRelevantFiles[i]['path']
        _removeHeaderFromPyFile(fullPath, prefix)
        
        nextLine = ''
        if i > 0:
            stepBelow = listRelevantFiles[i-1]['path'].replace('.py', '')
            nextLine = 'from {stepBelow} import *' if importStar else 'import {stepBelow}'
        
        toAdd = '\n' + prefix + '\n' + nextLine + '\n'
        _addHeaderToPyFile(fullPath, toAdd)
    
    listHeaderOnlyFiles = [item for item in listFiles if item['opts']['prefixOnly']]
    for i in range(len(listHeaderOnlyFiles)):
        fullPath = pathDir + '/' + listRelevantFiles[i]['path']
        _removeHeaderFromPyFile(fullPath, prefix)
        toAdd = '\n' + prefix + '\n\n'
        _addHeaderToPyFile(fullPath, toAdd)

def _addHeaderToPyFile(fullPath, toAdd):
    from .. import files
    
    reHeader = re.escape(prefix)
    reHeader += r'\n[^\n]*\n'
    
    contents = files.readAll(f)
    newContents = re.sub(reHeader, '\n', contents)
    if newContents != contents:
        print('removed header in ' + f)
        files.writeAll(f, newContents)
    
    
def removeHeaderFromPyFiles(pathDir, prefix, recurse=True):
    # use this to change the header on files (running this then )
    from .. import files
    for f, short in files.listFiles(pathDir, allowedExts=['py'], recurse=recurse):
        _removeHeaderFromPyFile(f, prefix)
    
    print('complete.')

def _removeHeaderFromPyFile(f, prefix):
    from .. import files
    
    reHeader = re.escape(prefix)
    reHeader += r'\n[^\n]*\n'
    
    contents = files.readAll(f)
    newContents = re.sub(reHeader, '\n', contents)
    if newContents != contents:
        print('removed header in ' + f)
        files.writeAll(f, newContents)
    

    