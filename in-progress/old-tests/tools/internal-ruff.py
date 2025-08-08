
import sys
sys.path.append('src')
from shinerainsevenlib.standard import *
import re



def goRuff():
    files.run([
        "D:\\OnlyHere\\devkits\\Python64_312\\Scripts\\ruff",
        "format",
        #~ "src\\shinerainsevenlib",
        r"C:\b\pydev\dev\contracts\gnostic\gnosticnotepad\src\tools\typescript-super-auto-import",
    ])
    cleanupAfterRuffAll("src\\shinerainsevenlib")

def goPylint():
    retcode, stdout, stderr = files.run([
        "D:\\OnlyHere\\devkits\\Python64_312\\python",
        "-m",
        "pylint",
        #~ "src\\shinerainsevenlib",
        r"C:\b\pydev\dev\contracts\gnostic\gnosticnotepad\src\tools\typescript-super-auto-import",

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
    alert('wrong path intentionally')
    import os
    import sys
    os.chdir(r"C:\b\pydev\dev\contracts\gnostic\gnosticnotepad\src\tools\typescript-super-auto-import")
    if 'ruff' in sys.argv:
        goRuff()
    elif 'pylint' in sys.argv:
        goPylint()
    else:
        assertTrue(False, 'please specfiy ruff or pylint')

