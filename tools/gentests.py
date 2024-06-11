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
        if f.endswith('.py') and '__init__' not in short and 'standard.py' not in short:
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
    if mode == Mode.generate:
        tContent = files.readAll('template-testfile.py')
        if files.isFile(restOfPath):
            trace('skipping, file already exists')
        else:
            files.writeAll(restOfPath, tContent)
    elif mode == Mode.check:
        if not files.exists(restOfPath):
            alert(rf"There isn't a test file at {restOfPath}")
    else:
        assertTrue(False, 'unknown mode')


    trace(f, restOfPath)
    return
    
    if (files.isFile(restOfPath)):
        return
    

goAll()


