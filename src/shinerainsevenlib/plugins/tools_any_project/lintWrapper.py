
# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv2.1 License

import sys
import os
import json
import re
from shinerainsevenlib.standard import *

'''
lintWrapper.py

1) provides a common interface for linting tools.
2) the ignore rules can contain specific context on what to ignore.
    this can be very useful, for example you might want warnings on
    accessing missing attributes almost all of the time - except for
    a certain class where you know that the attribute is added later on.
3) better way to specify excluded files for yapf
 
To configure, add a [tool.shinerainsevenlib] section to your pyproject.toml
To use a builtin collection of configs write
config_collection_modern = 1
(silences warnings that I consider to not be helpful)
or
config_collection_legacy = 1
(silences warnings about some Python2 compat constructs)

Configuration for --pylint
    Add pylint_specific_ignore_containing = ['abc', 'def']
    to ignore warnings that when fully printed contain those substrings
    If starts with re:, it will be treated as a regex

    Add hide_init_py_while_linting = 1
    this temporarily deletes a __init__.py in the current directory,
    because that can cause pylint to emit many warnings.

    Add pylint_args = ['--ignore-paths=.*dir_name.*']
    to add some arguments, for example to ignore certain files

    Add to pylint_ignore what rules you want to ignore
    instead of putting rules in your [tool.pylint.'MESSAGES CONTROL'] section

    You can optionally add pylint_import_suggested_other_settings = 1

Configuration for --rufflint
    Add rufflint_specific_ignore_containing = ['abc', 'def']
    to ignore warnings that when fully printed contain those substrings
    If starts with re:, it will be treated as a regex

    Add rufflint_args = ['--exclude=.*dir_name.*']
    to add some arguments, for example to ignore certain files

    Add to rufflint_ignore what rules you want to ignore,
    Instead of putting rules in your [tool.ruff.lint] section.
    The other contents [tool.ruff] and [tool.ruff.lint] are fine though.

    You can optionally add rufflint_import_suggested_other_settings = 1

Configuration for --format
    Add format_skip_if_path_contains = ['dir_name'] to skip files in a directory with that name

    Add format_args to add some arguments to be passed to yapf

    Your [tool.yapf] section will be used.

'''

def verifyCfg(cfg):
    knownKeys = ['hide_init_py_while_linting', 'format_skip_if_path_contains', 'format_args',
                    'config_collection_modern', 'config_collection_legacy']
    for toolShortName in ['pylint', 'rufflint']:
        for suffix in ['_args', '_specific_ignore_containing', '_ignore', '_import_suggested_other_settings']:
            knownKeys.append(toolShortName + suffix)

    for key in cfg:
        if key not in knownKeys:
            print(f'in the [shinerainsevenlib] section of your pyproject.toml, unknown key {key}')
            print(f' Known keys: {knownKeys}')
            return False
    
    return True

def main(argv):
    retcode = 0
    if not '--pylint' in argv and not '--rufflint' in argv and not '--format' in argv:
        print('Usage:')
        print('python -m shinerainsevenlib --lint-wrapper --pylint')
        print('or')
        print('python -m shinerainsevenlib --lint-wrapper --rufflint')
        print('or')
        print('python -m shinerainsevenlib --lint-wrapper --rufflint --fix')
        print('or')
        print('python -m shinerainsevenlib --lint-wrapper --format')
        return 1

    try:
        import toml
    except ImportError:
        print('Please run "python -m pip install toml"')
        return 1

    tomlPath = findFileInParentDirs("pyproject.toml")
    if not tomlPath:
        print("This script currently assumes that it can find a " +
              "pyproject.toml file in the current directory or a parent.")
        return 1

    tomlCfg = toml.load(tomlPath)
    thisCfg = tomlCfg.get("tool", {}).get("shinerainsevenlib", {})
    if not verifyCfg(thisCfg):
        return 1

    if thisCfg.get('hide_init_py_while_linting') and '--pylint' in argv:
        # feature: this temporarily deletes a __init__.py in the current directory,
        # because that can cause pylint to emit many warnings.
        initPyContents = files.readAll('__init__.py')
        runOnStart = lambda: files.delete('__init__.py')
        runOnEnd = lambda: files.writeAll('__init__.py', initPyContents)
    else:
        runOnStart = lambda: None
        runOnEnd = lambda: None
    
    runOnStart()
    try:
        if '--pylint' in argv:
            assertTrue(not '--rufflint' in argv and not '--format' in argv, "Only specify one")
            retcode = mainPylint(argv, thisCfg, tomlCfg, tomlPath)
        elif '--rufflint' in argv:
            assertTrue(not '--pylint' in argv and not '--format' in argv, "Only specify one")
            retcode = mainRufflint(argv, thisCfg, tomlCfg, tomlPath)
        elif '--format' in argv:
            assertTrue(not '--pylint' in argv and not '--rufflint' in argv, "Only specify one")
            retcode = mainFormat(argv, thisCfg, tomlCfg, tomlPath)
        else:
            assertTrue(False, "Must specify type of task")
    finally:
        runOnEnd()
    
    return retcode

def _getTaskArgs(args, argv, thisCfg, toolShortName):
    pyExe = sys.executable
    args.insert(0, pyExe)
    args.extend(getFromCfgTyped(thisCfg, toolShortName + '_args', list))
    return args

def mainPylint(argv, thisCfg, tomlCfg, tomlPath):
    if not files.isFile('./pyproject.toml'):
        print("Currently please run this script from the directory with your pyproject.toml")
        return 1
    
    toolShortName = 'pylint'
    args = [
        '-m', 'pylint', '--rcfile', 'pyproject.toml', '--output-format=json2',
    ]
    args = _getTaskArgs(args, argv, thisCfg, toolShortName)
    args.append('.')
    return _mainLint(argv, thisCfg, tomlCfg, tomlPath, toolShortName, 
        args, formatOneLinePylint, lambda j: j['messages'],
        "[tool.pylint.'MESSAGES CONTROL']", 'disable')
    
def mainRufflint(argv, thisCfg, tomlCfg, tomlPath):
    if not files.isFile('./pyproject.toml'):
        print("Currently please run this script from the directory with your pyproject.toml")
        return 1
    
    toolShortName = 'rufflint'
    args = [
        '-m', 'ruff', 'check', '--config=pyproject.toml', '--output-format=json',
    ]
    if '--fix' in argv:
        warn("Fixes don't always listen to what's ignored. Recommend saving all your files first.")
        args.append('--fix')

    args = _getTaskArgs(args, argv, thisCfg, toolShortName)
    args.append('.')
    return _mainLint(argv, thisCfg, tomlCfg, tomlPath, toolShortName, 
        args, formatOneLineRuff, lambda j: j,
        '[tool.ruff.lint]', 'ignore')

def mainFormat(argv, thisCfg, tomlCfg, tomlPath):
    if not files.isFile('./pyproject.toml'):
        print("Currently please run this script from the directory with your pyproject.toml")
        return 1

    toolShortName = 'format'
    skipThese = getFromCfgTyped(thisCfg, 'format_skip_if_path_contains', list)
    onesToProcess = []
    for f, _short in files.recurseFiles('.', allowedExts=['py']):
        if any(skipThis.replace('\\', '/') in f.replace('\\', '/') for skipThis in skipThese):
            continue

        onesToProcess.append(f)

    for f in onesToProcess:
        # yapf also supports '--recursive', '--parallel' params
        # but those don't matter now that we target one file at a time
        # yapf --exclude=OUTSIDE/**/*.py did not seem to work.
        args = ['-m', 'yapf', '--in-place']
        args = _getTaskArgs(args, argv, thisCfg, toolShortName)
        args.append(f)
        files.run(args)

def _mainLint(argv, thisCfg, tomlCfg, tomlPath, toolShortName, args, fnFormatOneLine, fnGetFromJson,
    toolSectionName, ignoreSectionName):
    ourIgnoreKey = toolShortName + '_ignore'

    # we'll temporarily modify the toml to add our ignores.
    # first, see if the sections are as expected.
    tomlTxt = files.readAll(tomlPath)
    if not f'\n{toolSectionName}\n' in tomlTxt:
        print(f"Please add {toolSectionName} to {tomlPath}, even if it's empty")
        return 1
    
    sectionExist = getSectionFromToml(tomlCfg, toolSectionName)
    if ignoreSectionName in sectionExist:
        print(f"Please do not have a `{ignoreSectionName}` in {toolSectionName}")
        print(f"Put the entries into a list in {ourIgnoreKey} inside [tool.shinerainsevenlib] instead")
        return 1
    
    tempTomlText = tomlTxt
    if thisCfg.get(f'{toolShortName}_import_suggested_other_settings'):
        tempTomlText, retcode = _addOtherSettings(tempTomlText, thisCfg, tomlCfg, toolShortName)
        if retcode != 0:
            return retcode

    allIgnores = []
    if thisCfg.get('config_collection_modern'):
        allIgnores.extend(getIgnoresModern(toolShortName))
    elif thisCfg.get('config_collection_legacy'):
        allIgnores.extend(getIgnoresModern(toolShortName))
        allIgnores.extend(getIgnoresLegacy(toolShortName))

    customIgnoreValsFromUser = getFromCfgTyped(thisCfg, ourIgnoreKey, list)
    allIgnores.extend(customIgnoreValsFromUser)

    # add it as a string (a bit hacky)
    asString = json.dumps(allIgnores)
    insertIntoToml = '\n' + ignoreSectionName + ' = ' + asString + '\n'
    tempTomlText = srss.replaceMustExist(tempTomlText, '\n' + toolSectionName + '\n', 
        '\n' + toolSectionName + '\n' + insertIntoToml)
    
    origTextUtf8 = tomlTxt.encode('utf-8')
    try:
        files.writeAll(tomlPath, tempTomlText)
        retcode =_mainLintInterpretResults(args, toolShortName, thisCfg, fnFormatOneLine, fnGetFromJson)
    finally:
        # write with unix newlines regardless of platform
        files.writeAll(tomlPath, origTextUtf8, mode='wb')
    
    return retcode

def _addOtherSettings(tempTomlText, thisCfg, tomlCfg, toolShortName):
    otherSettingsSectionName, otherSettingsKeys, otherSettingsVal = getRecommendedOtherSettings(
        toolShortName)
    otherSettingsSection = getSectionFromToml(tomlCfg, otherSettingsSectionName)
    lookForReplace = f'\n{otherSettingsSectionName}\n'
    for key in otherSettingsKeys:
        if key in otherSettingsSection:
            print(f"You can't have a `{key}` in {lookForReplace}")
            print(f"This is because you've set {toolShortName}_import_suggested_other_settings to True")
            print("Set that to False if you want to add your own values there.")
            return '', 1
        
    if not lookForReplace in tempTomlText:
        print(f"Please add a {lookForReplace} section to your toml, even if it's empty")
        return '', 1

    insertIntoToml = '\n' + otherSettingsVal + '\n\n'
    tempTomlText = srss.replaceMustExist(tempTomlText, lookForReplace, lookForReplace + insertIntoToml)
    return tempTomlText, 0


def _mainLintInterpretResults(args, toolShortName, thisCfg, fnFormatOneLine, fnGetFromJson):
    _retcode, stdout, stderr = files.run(args, throwOnFailure=False)
    if stderr:
        print(f'{toolShortName} failed', stdout.decode('utf-8'), stderr.decode('utf-8'))
        return 1
    
    stdout = stdout.decode('utf-8')
    events = json.loads(stdout)
    events = fnGetFromJson(events)
    specificIgnores = getFromCfgTyped(thisCfg, f'{toolShortName}_specific_ignore_containing', list)
    builtinSpecificIgnores = getBuiltinSpecificIgnores(toolShortName)
    countSpecificIgnores = 0
    countBuiltinIgnores = 0
    for event in events:
        line = fnFormatOneLine(event)
        if _shouldIgnore(line, specificIgnores):
            countSpecificIgnores += 1
            continue
        if _shouldIgnore(line, builtinSpecificIgnores):
            countBuiltinIgnores += 1
            continue

        print(line)
    
    print(f'Ignored {countSpecificIgnores} warnings due to {toolShortName}_specific_ignore_containing.')
    print(f'Ignored {countBuiltinIgnores} warnings due to builtin specific_ignore rules.')
    return 0

def _shouldIgnore(line,specificIgnores):
    for ignore in specificIgnores:
        assertTrue(ignore, 'should not be blank')
        if ignore.startswith('re:'):
            if re.search(ignore[3:], line):
                return True
        elif ignore in line:
            return True

def findFileInParentDirs(filename, path = ""):
    if not path:
        path = os.path.abspath(os.getcwd())

    assertTrue(os.path.isabs(path), "path must be absolute")
    file_path = os.path.join(path, filename)
    if os.path.exists(file_path):
        return os.path.abspath(file_path)

    parent_dir = os.path.abspath(os.path.join(path, os.pardir))
    if parent_dir == path or len(parent_dir) <= 3:
        # We've reached the root directory and haven't found the file
        return ""

    return findFileInParentDirs(filename, parent_dir)

def formatOneLineRuff(msg):
    # example.py:32:67: W0640: An example message (the-warning-type)
    return f"{msg['filename']}:{msg['location'].get('row')}:{msg['location'].get('column')}: {msg['code']} {msg['message']} ({msg.get('url', '').split('/')[-1]})"

def formatOneLinePylint(msg):
    # example.py:32:67: W0640: An example message (the-warning-type)
    return f"{msg['path']}:{msg['line']}:{msg['column']}: {msg['messageId']}: {msg['message']} ({msg['symbol']})"

def getFromCfgTyped(cfg, key, type):
    val = cfg.get(key, type())
    if not isinstance(val, type):
        assertTrue(False, f'for the key {key}, expected type {type}')

    return val

def getSectionFromToml(cfg, key):
    if key == "[tool.pylint.'MESSAGES CONTROL']":
        return cfg.get('tool', {}).get('pylint', {}).get('MESSAGES CONTROL', {})
    elif key == "[tool.ruff]":
        return cfg.get('tool', {}).get('ruff', {})
    elif key == "[tool.ruff.lint]":
        return cfg.get('tool', {}).get('ruff', {}).get('lint', {})
    else:
        assertTrue(False, 'please add the key to the hard-coded list here', key)

def getBuiltinSpecificIgnores(toolShortName):
    if toolShortName == 'pylint':
        return [r"re:^..[^:]*test.*?: S101:.*$", # ok for test files to have asserts
                "Redefining built-in 'dir'",
                "Redefining built-in 'type'",
                ] 
    elif toolShortName == 'rufflint':
        return [
            "Variable `dir` is shadowing", 
            "argument `dir` is shadowing",
            "Variable `type` is shadowing", 
            "argument `type` is shadowing",
                r"re:^..[^:]*test.*?S101 Use of `assert`.*$", # ok for test files to have asserts
                ]
    else:
        assertTrue(False, 'unknown toolShortName', toolShortName)

def getIgnoresModern(toolShortName):
    if toolShortName == 'rufflint':
        return ["F401", # imported but unused
            "F403", # 'from module import *' used; unable to detect undefined names
            "F405", # Name may be undefined, or it might have come from a star import
            "E302", # Expected 2 blank lines, found 0
            "E305", # blank-lines-after-function-or-class
            "E722", # Do not use bare 'except'
            "E731", # Do not assign a lambda expression to var
            "TID252", # prefer absolute imports
            "SIM201", # a != b vs not a == b
            "C408", # i prefer dict(a=b) instead of {a:b}
            "UP031", # i still have old code with '%2d' % x instead of f'{x}'
            "PGH004", # ok to have bare noqa
            "I001", # ok to have unsorted imports for now
            "SIM103", # ok to if x and y and z: return True instead of return x and y and z
            "UP028", # it wants yield from
            "SIM102", # nested if ok
            "SIM114", # it wants combined branches
            "SIM117", # it wants combined with statements
            "SIM108", # it wants ternary
            "SIM105", # it wants contextlib.suppress, cool but i don't want that to be mandatory
            "ISC003", # it implicit string concatenation within parens, i don't want that
            "E713", # ok to say either if a not in b and if not a in b
            "PIE810", # ok to not combine endswith(a, b) 
            "RUF001", # ok to have ambiguous-unicode-character-string
            "SIM300", # prefer no yoda condition
            "C405", # ok to not use fancy set() constructors
            "COM812", # ok to have no trailing comma
            "T201", # ok to have print()
            "PLC0415", # imports that aren't on top
            "RET504", # ok to say ret='abc'; return ret
            "RET505", # unneeded else after return (i think it's more readable)
            "RET506", # unneeded else after raise (i think it's more readable)
            "RET507", # unneeded else after continue (i think it's more readable)
            "RET508", # unneeded else after break (i think it's more readable)
            "PLC1802", # ok to test on if len(foo)
            "E501", # line too long
            "PT011", # pytest raise too broad
            "B904", # wants raise from
            "S602", # shell=True is ok, I'm aware of risks
            "PT018", # wants separate assert for separate checks
            "TRY300", # try move to else
            "PERF401", # make it a comprehension
            "PT009", # make it a comprehension
            # leave on:
            #"E128", # Continuation line under-indented for visual indent
            #"W504", # Line break occurred after a binary operator
            # these might also be useful to disable:
            # F405 ok to use a symbol from a import *
            # W293 Blank line contains whitespace
            # W391 Blank line at end of file
            ]
    elif toolShortName == 'pylint':
        return [
            "C0103", # name styles
            "W0401", # wildcard imports
            "C0116", # missing docsstring
            "C0114", # module docstring
            "W0614", # unused import
            "W0611", # unused import
            "R0913", # too many args
            "C0209", # fstring
            "C0305", # newlines
            "W0702", # bare except
            "C0115", # no docstring
            "R1705", # unneeded elif
            "R1720", # unneeded elif
            "R0902", # too many attributes
            "E0401", # pylint can't find the module being imported
            "C1802", # i think it's ok to say if len(lst)
            "R0914", # too many locals
            "R1735", # dict literal
            "R1737", # wants yield from
            "W0718", # broad exception
            "W0108", # unnecessary lambda (false positives)
            "R1703", # i prefer return True
            "R0903", # too few methods
            "C0303", # whitespace
            "R0917", # it's not that bad to have many arguments
            "R1710", # too many if branches
            "C3001", # Lambda expression assigned to a variable
            "C0413", # import outside top
            "R1716", # it wants a < b < c
            "W0311", # bad indentation
            "W0613", # unused-argument
            "R1723", # unnecessary else or elif block following an if statement that contains a break statement.
            "R0904", # class has too many public methods
            "R1724", # "Unnecessary 'else' after 'continue'
            "R0915", # Used when a function or method has too many statements
            "R1714", # color in ("red", "green", "blue")
            "R1702", # too-many-nested-blocks
            "W0707", # recommend raise from
            "C0411", # standard import "os.path.join" should be placed before third party import "pytest" 
            "W0719", # too general exception is being raised.
            "C0206", # recommends iterating over items()
            # considered, but leaving on:
            #"W0622", # a variable or function in your code is overriding a built-in Python name
            #"W0612", # a variable has been defined but is not subsequently used 
            #"W0201", # attributed-defined-outside-init
            # The warning E1101 we want enabled because it's useful to catch missing functions.
        ]
    else:
        assertTrue(False, 'unknown toolShortName', toolShortName)
        
def getIgnoresLegacy(toolShortName):
    if toolShortName == 'rufflint':
        return [
            "E402", # Module level import not at top of file
            "E228", # Missing whitespace around modulo operator
            "E401", # Multiple imports on one line
            "ERA001", # commented out code
            "RUF015", # single element slice
            "UP036", # it's ok to check for python2
            "UP025", # keep unicode prefix for py2 compat
            "UP008", # keep super(Base) for py2 compat
            "SIM115", # keep raw open() close() for less code churn in legacy code
            "ARG001", # unused argument
            "TRY002", # ok to raise generic exceptions
            "TRY003", # ok to raise generic exception msgs
            "UP024", # ok to raise aliased exceptions
            "UP034", # ok to have more parens
            "PLC0206", # missing .items()
            "PLW2901", # overwrite in loop
            "ARG002", # unused arg
        ]
    elif toolShortName == 'pylint':
        return [
            "R0911", # too many returns
            "R0912", # too many branches
            "C0415", # import outside top
            "R0913", # too many args
            "C0209", # fstring
            "C0305", # newlines
            "W0603", # global ok
            "R0401", # cyclic import... aggressive and fires even when the cycle is within a function call (safe)
            "R1732", # use with to autoclose resources... consider fixing later
            "W1406", # no longer need u''
            "R1725", # In Python 3, super() can be called without any arguments
        ]
    else:
        assertTrue(False, 'unknown toolShortName', toolShortName)

def getRecommendedOtherSettings(toolShortName):
    if toolShortName == 'rufflint':
        return '[tool.ruff.lint]', ['fixable', 'unfixable', 'extend-select', ], '''

unfixable = [
    # do not autoremove commented out code
    "ERA", 
    # blank-lines related rules
    "E301",
    "E302",
    "E303",
    "E304",
    "E305",
    "E306",
    "F401", # unused import
    "F841", # unused variables
    "PIE804", # unnecessary dict kwargs
]

# Possible to define a fixable=[] section here, for ones like F403
# A good one for testing fixability is to
# temporarily allow the rule UP025 and add u'abc' to the source,
# autofix should remove it

extend-select = [
    "A",   # flake8-builtins
    'ASYNC', # async
    "B",   # flake8-bugbear
    'BLE', # flake8-blind-except
    "C4",  # flake8-comprehensions
    'COM',  # flake8-commas
    'DTZ', # flake8-datetimez
    'E',  # pycodestyle
    "ERA", # no commented out code
    'EXE', # flake8-executable
    'F',  # pyflakes
    'FLY',  # flynt
    'G',  # flake8-logging-format
    "I",   # isort
    'ICN', # https://github.com/joaopalmeiro/flake8-import-conventions
    'ISC', # https://pypi.org/project/flake8-implicit-str-concat/
    'LOG', # flake8-logging
    'PERF', # perflint
    "PIE", # flake8-pie
    "PGH", # pygrep
    'PLC',  # Pylint conventions
    'PLE',  # Pylint error
    'PLW',  # Pylint warnings
    'PT',  # https://pypi.org/project/flake8-pytest-style/
    'RET', # https://pypi.org/project/flake8-return/
    "RUF", # ruff checks
    'S',  # https://docs.astral.sh/ruff/rules/#flake8-bandit-s
    'SIM',  # https://pypi.org/project/flake8-simplify/
    'T',  # flake8-debugger
    'TRY',  # tryceratops
    "TID", # flake8-tidy-imports
    "UP",  # pyupgrade
    'ARG',  # flake8 unused arguments
    
    # leave disabled for now:
    # "N" pep8-naming
    # TCH flake8-type-checking
    # 'D',  # pydocstyle
    # 'N',  # pep8-naming
    # 'NPY', # numpy
    # 'PD', # pandas
    # 'PL',  # Full Pylint
    # 'PLR',  # Pylint refactor
    # 'PTH',  # flake8 use pathlib
]
'''
    # when we used ruff for formatting (now using yapf instead)
    # we told ruff not to fix blank-lines-after-function-or-class,
    # or wrote a python script to turn the double-empty-lines into single.
    elif toolShortName == 'pylint':
        # don't check line length with pylint, use other tools
        return "[tool.pylint.'MESSAGES CONTROL']", ['max-line-length'], '''
max-line-length = 999
'''
    else:
        assertTrue(False, 'unknown toolShortName', toolShortName)

if __name__=='__main__':
    main(['--rufflint'])
