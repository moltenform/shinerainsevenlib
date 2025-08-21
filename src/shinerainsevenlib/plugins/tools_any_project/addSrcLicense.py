
def addSrcLicense(dirOrDirs, newHeaderToWrite, excerptIndicatingDuplicate='', fileExts=['py']):
    warnings = []
    if isinstance(dirOrDirs, str):
        dirOrDirs = [dirOrDirs]
    
    for root in dirOrDirs:
        for f, _short in files.recurseFiles(root, fileExts=fileExts):
            _goOne(f, newHeaderToWrite, excerptIndicatingDuplicate, warnings)
    
    if warnings:
        warn('\n'.join(warnings))

def _goOne(f, newHeaderToWrite, excerptIndicatingDuplicate, warnings):
    code = files.readAll(f)
    if not code.startswith(newHeaderToWrite):
        # if it's lower down in the file, replace it.
        codeWithoutIt = code.replace(newHeaderToWrite, '')

        # check for a previous version of the header being there
        if excerptIndicatingDuplicate and excerptIndicatingDuplicate in codeWithoutIt:
            warnings.append(f"in {f}, may have a similar header already, should go look.")

        code = newHeaderToWrite + codeWithoutIt
        trace('Writing,', f)
        files.writeAll(f, code)


