import ast

def parsePythonModuleIntoListOfFunctionsAndClasses(contents):
    # use real ast parsing. otherwise it is hard to know where classes end.
    # and we can get tripped up by multiline strings.
    def _getMethods(node):
        return [item.name for item in node if isinstance(item, ast.FunctionDef)]

    results = []
    parsed = ast.parse(contents)
    
    # do not use walk because we only want top level, not nested, functions
    for item in parsed.body:
        if isinstance(item, ast.FunctionDef):
            results.append(Bucket(type='fn', name=item.name))
        elif isinstance(item, ast.ClassDef):
            results.append(Bucket(type='cls', name=item.name, methods=_getMethods(item.body)))
    
    return results

def getTopLevelConstantsAndImportFroms(filename):
    showNodeInfo = False
    lns = files.readAll(filename).replace('\r\n', '\n').split('\n')
    trace(filename)

    with open(filename, encoding='utf-8') as file:
        tree = ast.parse(file.read())
        if showNodeInfo:
            import astunparse
            print(astunparse.dump(tree))

        for node in tree.body: # don't walk, we only want top levels
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        ret = Bucket(linecontext = files.getName(filename) +':'+ lns[node.lineno - 1])
                        ret.type = 'global'
                        ret.symbolname = target.id
                        yield ret
                    
            if isinstance(node, ast.ImportFrom):
                for name in node.names:
                    if isinstance(name, ast.alias):
                        ret = Bucket(linecontext = files.getName(filename) +':'+ lns[node.lineno - 1])
                        if name.name == '*' or name.asname == '*':
                            continue
                        ret.type = 'importfrom'
                        if name.asname:
                            ret.symbolname = name.asname
                        else:
                            ret.symbolname = name.name
                        yield ret