
def reorderFilesWithPrefix(d, newOrder, prefix):
    newOrder = srss.strToList(newOrder)
    digitsNeeded = len(str(len(newOrder)))
    numberSpec = '%0' + str(digitsNeeded) + 'd'
    results = []
    for i, s in enumerate(newOrder):
        sWithoutPrefix = re.sub('^' + re.escape(prefix) + '[0-9]*', '', s)
        sNew = prefix + (numberSpec % i) + sWithoutPrefix
        if sNew != s:
            results.append([s, sNew])
            trace(f'Rename from {s} to {sNew}')
        else:
            trace(f'No need to rename {s}')


    if getInputBool('Do the renames now?'):
        for before, after in results:
            files.move(files.join(d, before), files.join(d, after), False, doTrace=True)
