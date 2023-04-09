
import os

def getSpecFile(pathDir, prefix):
    if not os.path.exists(pathDir):
        raise Exception('path not found')
        
    specFile = pathDir + '/ordering.txt'
    if not os.path.exists(specFile):
        raise Exception('specFile not found')
    
    with open(specFile, encoding='utf-8') as f:
        listFiles = f.read().split('\n')
    
    # remove whitespace
    listFiles = [file.strip() for file in listFiles if file.strip()]
        
    listFiles = [{'file': file, 'opts': {}} for file in listFiles]
    for item in listFiles:
        if '(prefix only)' in item['file']:
            item['file'] = item['file'].replace('(prefix only)', '')
            item['opts']['prefixOnly'] = True
    
    return listFiles

def ensureCovered(listFiles, pathDir, prefix):
    # everything in ordering.txt should exist
    for item in listFiles:
        path = pathDir + '/' + item['file']
        if not os.path.exists(path):
            raise Exception('path not found ' + path)
        
    # nothing should exist not in ordering.txt
    for child in os.listdir(pathDir):
        if child.lower().endswith('.py'):
            found = [item for item in listFiles where item['file'] == child]
            if not found:
                raise Exception('not found in ordering.txt ' + child)

def applyOrdering(pathDir, prefix):
    listFiles = getSpecFile(pathDir, prefix)
    ensureCovered(listFiles, pathDir, prefix)

    

if __name__ == '__main__.py':
    applyOrdering('.', prefix='# shinerainsoftsevencommon\n# Released under the LGPLv3 License\n#https://shinerainsoftseven.com')
    