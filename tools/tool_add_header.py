# ruff: noqa
from shinerainsoftsevenutil.standard import *

def goAll(root):
    for f, short in files.recurseFiles(root):
        if files.getExt(f) == 'py':
            goOne(f)

def goOne(f):
    code = files.readAll(f)
    want = srss.standardNewlines(r'''
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License
    ''')
    if not code.startswith(want):
        code = want + code
        files.writeAll(f, code)
    


if __name__ == '__main__':
    goAll()
    
