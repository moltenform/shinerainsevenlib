
# shinerainsoftsevenutil (Ben Fisher, moltenform.com)
# Released under the LGPLv3 License

# ruff: noqa

assertTrue(not srss.SrssFileIterator.pathHasThisDirectory('node_modules', ''))
assertTrue(not srss.SrssFileIterator.pathHasThisDirectory('node_modules', 'abcd'))
assertTrue(not srss.SrssFileIterator.pathHasThisDirectory('node_modules', 'ab/cd'))
for SEP in ('/', '\\'):
    assertTrue(not srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}node{SEP}_modules{SEP}b'))
    assertTrue(not srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}notnode_modules{SEP}b'))
    assertTrue(not srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}notnode_modules{SEP}'))
    assertTrue(not srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}notnode_modules'))
    assertTrue(not srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}node_modulesnot{SEP}b'))
    assertTrue(not srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}node_modulesnot{SEP}'))
    assertTrue(not srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}node_modulesnot'))
    assertTrue(srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}node_modules{SEP}b'))
    assertTrue(srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}node_modules{SEP}'))
    assertTrue(srss.SrssFileIterator.pathHasThisDirectory('node_modules', f'a{SEP}node_modules'))

#~ for i in range(ord('a'), ord('z')+1):
    #~ print(rf"softDeleteDirectory_{chr(i)}ColonBackslash={chr(i).upper()}:\data\local\trash")
if False:
    config = srssutil.SrssConfigReader()
    config.setSchemaForSection('main', {
        'tempEphemeralDirectory' : [str, ''],
        'tempDirectory' : [str, ''],
                'warnSoftDeleteBetweenDrives' : [bool, False],
        'softDeleteDirectoryAll' : [str, ''],
        'softDeleteDirectory_*' : [str, ''],})

    input3 = r'''
    tempEphemeralDirectory=G:\data\local\temp
    tempDirectory=D:\data\local\temp
    softDeleteDirectoryAll=D:\data\local\trash
    softDeleteDirectory_aColonBackslashb=a:\path2
    softDeleteDirectory_aColonBackslash=a:\pa
    th1
    warnSoftDeleteBetweenDrives=1
    '''
    config.parseText(input3)
    print(config.parsed.main.tempEphemeralDirectory)
    print(config.parsed.main.softDeleteDirectory_aColonBackslash)
    print(config.parsed.main.warnSoftDeleteBetweenDrives)
    print(config.findKeyForPath('a:\\tryone', 'softDeleteDirectory_'))
    print(config.findKeyForPath('a:\\b\\trytwo', 'softDeleteDirectory_'))

if False:
    loop = srss.SrssLooper(list(range(100)))
    loop.showPercentageEstimates()
    loop.addPauses(10, seconds=2)
    loop.waitUntilValueSeen(3)
    for number in loop:
        if number % 2 == 0:
            print('skipping even number', number)
            loop.flagDidNoMeaningfulWork()
        else:
            print('found an odd number', number)
#~ there must be a _winErrs with 'different drives'

if False:
    class SampleContextManager:
        def __enter__(self):
            print('entering SampleContextManager')
            return self

        def __exit__(self, exc_type, _exc_val, _exc_tb):
            print('exiting SampleContextManager')

    from contextlib import ExitStack
    with ExitStack() as cleanupTasks:
        cleanupTasks.push(SampleContextManager())
        cleanupTasks.callback(lambda: print('second'))
        cleanupTasks.callback(lambda: print('third'))