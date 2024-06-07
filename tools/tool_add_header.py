
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

# ruff: noqa

from shinerainsoftsevenutil.standard import *

def goAll(root):
    for f, short in files.recurseFiles(root):
        if files.getExt(f, removeDot=True) == 'py':
            goOne(f)

def goOne(f):
    code = files.readAll(f)
    want = srss.standardNewlines(r'''
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

''')
    if not code.startswith(want):
        if 'shinerainsoftsevenutil (Ben Fisher' in code and not 'add_header' in f:
            print("may have added it twice, should go look.")
        code = want + code
        code = code.replace('\n\n\n', '\n\n').replace('\n\n\n', '\n\n').replace('\n\n\n', '\n\n')
        files.writeAll(f, code)
    

if __name__ == '__main__':
    goAll(r'.')

