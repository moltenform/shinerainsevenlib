
# shinerainsoftsevencommon
# Released under the LGPLv3 License

import os

class BenPythonCommonPreferences:
    def __init__(self):
        self.prefs_dict = {}
    

#~ def runOnModuleLoad(cachedPrefs):
    

def getShineRainSoftSevenCommonPrefsFilePath():
    userHome = os.path.expanduser('~')
    return userHome + '/' + '.shinerainsoftsevencommon'
        

def _getDirRoot(path):
    path = os.path.abspath(path)
    if re.match(r'^[a-zA-Z]:$', path[0:2]):
        return path[0].lower()
    else:
        return None

def getDirectoryBasedOnPath(path, prefix):
    global cachedPrefs
    dict = cachedPrefs.getDict()
    
    if path:
        root = _getDirRoot(path)
        if root:
            key = f'{prefix}_{root}_drive'
            if key in dict and dict[key]:
                return dict[key]
    
    key = f'{prefix}_general'
    if key in dict and dict[key]:
        return dict[key]
    

#~ # run this on module load
#~ cachedPrefs = BenPythonCommonConfigParser()
#~ runOnModuleLoad(cachedPrefs)

def getTempDirectoryForPath(path=None):
    # always returns a valid directory
    result = getDirectoryBasedOnPath(path, 'temp_directory')
    if not result:
        result = tempfile.gettempdir() + '/shinerainsoftsevencommon'
        
    try:
        if not os.path.isdir(result):
            os.makeDirs(result)
    except Exception as e:
        raise Exception(f'getTempDirectoryForPath error creating {result} {e}')
    
    if not os.path.isdir(result):
        raise Exception('getTempDirectoryForPath does not exist {result}')
    
    return result
    
def getSoftDeleteDirectoryForPath(path):
    # returns a directory, or None
    result = getDirectoryBasedOnPath(path, 'soft_delete_directory')
    if result:
        try:
            if not os.path.isdir(result):
                os.makeDirs(result)
        except Exception as e:
            raise Exception(f'getSoftDeleteDirectoryForPath creating {result} {e}')
        
        if not os.path.isdir(result):
            raise Exception('getSoftDeleteDirectoryForPath does not exist {result}')
    
    return result

def diagnosticsEnabled():
    global cachedPrefs
    dict = cachedPrefs.getDict()
    return dict.get('diagnostics_enabled') and dict.get('diagnostics_enabled').strip() != '0'

#~ softDeleteFile:
#~ if no location is set, send to recycle bin (Send2Trash module) (and log what was deleted to a log)
#~ otherwise send it to that location
#~ or if location is set per-drive, send to that place.

#~ scratchLocation:
#~ if no location is set, use a temporary location in c:\temp
#~ or if location is set per-drive, send to that place.



