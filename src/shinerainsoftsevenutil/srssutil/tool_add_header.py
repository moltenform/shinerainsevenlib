# ruff: noqa

# ~ def goAll(root):
# ~ for f, short in files.recursefiles(root):
# ~ if files.getext(f) == 'py':
# ~ goOne(f)

# ~ def goOne(f):
# ~ code = files.readall(f)
# ~ expected = standardNewlines(r'''
# ~ # ShineRainSevenCommon(Ben Fisher)
# ~ # Useful python helpers
# ~ # Released under the MIT License
# ~ ''')
# ~ expectedAll = expected
# ~ if files.getname(f).startswith('layer') and not files.getname(f).startswith('layer'):
# ~ lowerLayer = getLowerLayer(f)
# ~ if lowerLayer:
# ~ expectedAll += '\n

# ~ def getLowerLayer(f):
# ~ curLayer = files.getname(f).replace('layer', '').split('_')[0]
# ~ if intOrNone(curLayer)
