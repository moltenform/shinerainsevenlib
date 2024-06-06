
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

import sys
sys.path.append('src')
from shinerainsoftsevenutil.standard import *
import re

def cleanupAfterRuff(path):
    trace('Postprocessing', path)
    txt = files.readAll(path)
    txt = txt.replace('\n\n\ndef ', '\n\ndef ')
    txt = txt.replace('\n\n\ndef ', '\n\ndef ')
    txt = txt.replace('\n\n\nclass ', '\n\nclass ')
    txt = txt.replace('\n\n\nclass ', '\n\nclass ')
    # note that we stole one of the whitespaces by putting outside the (capture)
    txt = re.sub(r'\n (  +)\+', r' +\n\1', txt)
    txt = re.sub(r'\n (  +)\band\b', r' and\n\1', txt)
    txt = re.sub(r'\n (  +)\bor\b', r' or\n\1', txt)
    files.writeAll(path, txt)

def cleanupAfterRuffAll(dirPath):
    for f, short in files.recurseFiles(dirPath):
        if short.lower().endswith('.py'):
            cleanupAfterRuff(f)

def goRuff():
    files.run([
        "D:\\OnlyHere\\devkits\\Python64_312\\Scripts\\ruff",
        "format",
        "src\\shinerainsoftsevenutil",
    ])
    cleanupAfterRuffAll("src\\shinerainsoftsevenutil")

def goPylint():
    retcode, stdout, stderr = files.run([
        "D:\\OnlyHere\\devkits\\Python64_312\\python",
        "-m",
        "pylint",
        "src\\shinerainsoftsevenutil",
    ], throwOnFailure=False)
    stdout = stdout.decode('utf-8')
    lines = stdout.replace('\r\n', '\n').split('\n')
    for line in lines:
        if " E1101: Instance of 'Bucket' " in line:
            pass
        elif " W0201: Attribute 'spans' defined outside " in line:
            pass
        elif " W0201: Attribute 'getTotalSpan' defined outside " in line:
            pass
        else:
            print(line)

if __name__ == '__main__':
    if 'ruff' in sys.argv:
        goRuff()
    elif 'pylint' in sys.argv:
        goPylint()
    else:
        assertTrue(False, 'please specfiy ruff or pylint')

