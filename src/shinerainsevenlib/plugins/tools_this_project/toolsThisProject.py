
def getProjectRoot():
    if files.exists('pyproject.toml'):
        return '.'
    if files.exists('../pyproject.toml'):
        return '..'
    if files.exists('shinerainsevenlib/pyproject.toml'):
        return './shinerainsevenlib'
    if files.exists('../shinerainsevenlib/pyproject.toml'):
        return '../shinerainsevenlib'

def chDirToProjectRoot():
    os.path.chdir(getProjectRoot())
