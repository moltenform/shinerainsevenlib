import re
from shinerainsevenlib.standard import *

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
