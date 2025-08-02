
import re

class TestChecker:
    def __init__(self, okWithout):
        self.okWithout = okWithout
        
    def goAll(self, srcDir, testDir):
        alreadyTested = self.getAlreadyTested(testDir)
        for f, short in files.recurseFiles(srcDir):
            if not short.startswith('nocpy'):
                if not short.startswith('test') and short.endswith('.py'):
                    self.goFile(f, alreadyTested)
        trace('Complete')
        
    def getAlreadyTested(self, testDir):
        alreadyTested = ''
        for f, short in files.recurseFiles(testDir):
            if short.startswith('test') and short.endswith('.py'):
                content = files.readAll(f, encoding='utf-8')
                afterClass = content.split('class', 1)[1]
                alreadyTested += '\n' + afterClass
        return alreadyTested
    
    def goFile(self, f, alreadyTested):
        with open(f, encoding='utf-8') as fIn:
            
                    self.goLine(f, line, 'class ', alreadyTested)
    
    def goLine(self, f, line, prefix, alreadyTested):
        symbol = line[len(prefix):]
        symbol = symbol.split('(')[0].split(':')[0].strip()
        if not symbol in self.okWithout:
            if not symbol.startswith('_'):
                self.goSymbol(f, symbol, alreadyTested)

    def goSymbol(self, f, symbol, alreadyTested):
        if not reSearchWholeWord(alreadyTested, symbol):
            trace(f'Did not see tests for {files.getName(f)}\'s {symbol}')

if __name__ == '__main__':
    okWithout = strToSet(files.readAll('nocpy_okwithout.txt'))
    checker = TestChecker(okWithout)
    checker.goAll('..', '.')
    
    