
# shinerainsoftsevencommon
# Released under the LGPLv3 License

import os
import re
import tempfile
from configparser import ConfigParser


class SimpleConfigParser:
    def __init__(self, addDefaultSection='main'):
        self.prefs_dict = {}
        self.addDefaultSection = addDefaultSection
    
    def load(self, path):
        with open(path, encoding='utf-8') as f:
            prefs_contents = f.read()
            
        if self.addDefaultSection:
            expect = '[' + self.addDefaultSection + ']\n'
            if expect not in prefs_contents:
                prefs_contents = expect + '\n' + prefs_contents
        
        self.cfg = ConfigParser(delimiters='=')
        
        # make it case-sensitive
        self.cfg.optionxform = str
        
        # read from string, not file handle
        self.cfg.read_string(prefs_contents)
        
        for key in self.cfg:
            self.prefs_dict[key] = self.cfg[key]
    
    def getDict(self):
        return self.prefs_dict
        

def abc():
    return 1
