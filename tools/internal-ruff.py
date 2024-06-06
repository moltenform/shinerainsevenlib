

import sys
sys.path.append('src')
from shinerainsoftsevenutil import *


def cleanupAfterRuff(path):
    trace('Cleaning', path)
    txt = files.readAll(path)
    txt = txt.replace('\n\n\ndef ', '\n\ndef ')
    txt = txt.replace('\n\n\ndef ', '\n\ndef ')
    txt = txt.replace('\n\n\nclass ', '\n\nclass ')
    txt = txt.replace('\n\n\nclass ', '\n\nclass ')
    files.writeAll(path, txt)

def cleanupAfterRuffAll(dir):
    for f, short in files.recurseFiles(dir):
        if short.lower().endswith('.py'):
            cleanupAfterRuff(f)

def go():
    files.run([
        "D:\\OnlyHere\\devkits\\Python64_312\\Scripts\\ruff",
        "format",
        "src\\shinerainsoftsevenutil",
        #~ "src\\shinerainsoftsevenutil\\core\\m1_core_util.py"
    ])
    #~ cleanupAfterRuff("src\\shinerainsoftsevenutil\\core\\m1_core_util.py")
    #~ cleanupAfterRuff("src\\shinerainsoftsevenutil\\core\\m1_core_util.py")
    cleanupAfterRuffAll("src\\shinerainsoftsevenutil")

if __name__ == '__main__':
    go()
