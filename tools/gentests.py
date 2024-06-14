#!/usr/bin/env python3


from shinerainsoftsevenutil.standard import *
from enum import StrEnum, auto

class Mode(StrEnum):
    generate=auto()
    check=auto()

def goAll(mode):
    encountered = {}
    for f, short in files.recurseFiles('./src/shinerainsoftsevenutil'):
        encountered[f] = True
        if f.endswith('.py') and '__init__' not in short:
            if 'standard.py' not in short and not short.endswith('compression_7z.py') and not short.endswith('compression_rar.py'):
                goOne(f, mode)
    
    if mode==Mode.check:
        for f, short in files.recurseFiles('./test'):
            if not f in encountered and not 'fixture' in short:
                alert("extra file in tests dir, {f}")

def goOne(f, mode):
    pathparts = f.replace('\\', '/').split('/')
    restOfPath = pathparts[pathparts.index('shinerainsoftsevenutil')+1:]
    restOfPath = jslike.map(restOfPath, lambda s:'test_'+s)
    restOfPath = './test/' + '/'.join(restOfPath)
    trace(restOfPath)
    if mode == Mode.generate:
        tContent = files.readAll('tools/gentests_template.py')
        if files.isFile(restOfPath):
            trace('skipping, file already exists')
        else:
            files.makeDirs(files.getParent(restOfPath))
            files.writeAll(restOfPath, tContent)
    elif mode == Mode.check:
        if not files.exists(restOfPath):
            alert(rf"There isn't a test file at {restOfPath}")
    else:
        assertTrue(False, 'unknown mode')


    return
    
    if (files.isFile(restOfPath)):
        return
    

#~ goAll(Mode.generate)
try:
    #~ import fghfgh
    ff = open('q:\\nothere')
except Exception as e:
    import inspect
    for chain in (inspect.getmro(e.__class__)):
        print(repr(chain).replace("<class '", '').replace("'>", ''))
    #~ print(e.__class__.__bases__)
    #~ print(repr(e))

print(repr("abc"))

#~ ModuleNotFoundError *abc*
