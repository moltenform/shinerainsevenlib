
# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv2.1 License

from shinerainsevenlib.standard import *

def goAll(root):
    for fullPath, _short in files.recurseFiles(root):
        if files.getExt(fullPath, removeDot=True) == 'py':
            goOne(fullPath)

def goOne(f):
    code = files.readAll(f)
    want = srss.standardNewlines(r'''
# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv2.1 License

''')
    if not code.startswith(want):
        if 'shinerainsevenlib (Ben Fisher' in code and not 'add_header' in f:
            print("may have added it twice, should go look.")
        code = want + code
        code = code.replace('\n\n\n', '\n\n').replace('\n\n\n', '\n\n').replace('\n\n\n', '\n\n')
        files.writeAll(f, code)
    

if __name__ == '__main__':
    goAll(r'.')


