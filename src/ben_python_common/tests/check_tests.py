
from ben_python_common import *
import re

class TestChecker:
    def __init__(self, okWithout):
        self.okWithout = okWithout
        
    def goAll(self, srcDir, testDir):
        alreadyTested = self.getAlreadyTested(testDir)
        for f, short in files.recursefiles(srcDir):
            if not short.startswith('test') and short.endswith('.py'):
                self.goFile(f, alreadyTested)
        
    def getAlreadyTested(self, testDir):
        alreadyTested = ''
        for f, short in files.recursefiles(testDir):
            if short.startswith('test') and short.endswith('.py'):
                content = files.readall(f, encoding='utf-8')
                afterClass = content.split('class', 1)[1]
                alreadyTested += '\n' + afterClass
        return alreadyTested
    
    def goFile(self, f, alreadyTested):
        with open(f, encoding='utf-8') as fIn:
            for line in fIn:
                if line.startswith('def '):
                    self.goLine(f, line, 'def ', alreadyTested)
                elif line.startswith('class '):
                    self.goLine(f, line, 'class ', alreadyTested)
    
    def goLine(self, f, line, prefix, alreadyTested):
        symbol = line[len(prefix):]
        symbol = symbol.split('(')[0].split(':')[0].strip()
        if not symbol in self.okWithout:
            if not symbol.startswith('_'):
                self.goSymbol(f, symbol, alreadyTested)

    def goSymbol(self, f, symbol, alreadyTested):
        if not reSearchWholeWord(symbol, alreadyTested):
            trace(f'Did not see tests for {files.getname(f)}\'s {symbol}')

if __name__ == '__main__':
    okWithout = strToSet(files.readall('nocpy_okwithout.txt'))
    checker = TestChecker(okWithout)
    checker.goAll('..', '.')
    
    