
import os
import sys
import re

if not os.path.exists('pyproject.toml'):
    print('Please run this script where current directory = the root of the project')
    sys.exit(1)

sys.path.append('./src')
from shinerainsevenlib.standard import *

def postProcessReplace(path, search, replace, useRe=False):
    path = './docs/_build/html/' + path
    oldTxt = files.readAll(path)
    if useRe:
        txt = re.sub(search, replace, oldTxt)
    else:
        txt = srss.replaceMustExist(oldTxt, search, replace)
    
    assertTrue(txt != oldTxt, search, replace)
    files.writeAll(path, txt)


postProcessReplace('autoapi/shinerainsevenlib/index.html',
r'''<li class="toctree-l1"><a class="reference internal" href="core/index.html">shinerainsevenlib.core</a></li>
<li class="toctree-l1"><a class="reference internal" href="files/index.html">shinerainsevenlib.files</a></li>
<li class="toctree-l1"><a class="reference internal" href="plugins/index.html">shinerainsevenlib.plugins</a></li>''',
r'''
<li class="toctree-l1"><a class="reference internal" href="core/m0_text_io/index.html">Section 0, text io</a></li>
<li class="toctree-l1"><a class="reference internal" href="core/m1_core_util/index.html">Section 1, core utils</a></li>
<li class="toctree-l1"><a class="reference internal" href="core/m2_core_data_structures/index.html">Section 2, data structures</a></li>
<li class="toctree-l1"><a class="reference internal" href="core/m3_core_nonpure/index.html">Section 3, non-pure utils</a></li>
<li class="toctree-l1"><a class="reference internal" href="core/m4_core_ui/index.html">Section 4, ui utils</a></li>
<li class="toctree-l1"><a class="reference internal" href="core/m5_batch_util/index.html">Section 5, batch processing utils</a></li>
<li class="toctree-l1"><a class="reference internal" href="core/m6_jslike/index.html">Section 6, javascript-like utils</a></li>
<li class="toctree-l1">Files section 0, wrappers</li>
<li class="toctree-l1">Files section 1, iteration</li>
<li class="toctree-l1">Files section 2, higher-level utils</li>
'''

)
postProcessReplace('autoapi/index.html',
                     r'<li class="toctree-l[2-9]">.*', '', useRe=True)

def postProcessSubFile(pathFragment):
    path = 'autoapi/shinerainsevenlib/' + pathFragment + '/index.html'
    rgx = re.compile(r'<table class="autosummary longtable docutils align-default">.*?</table>', re.DOTALL)
    postProcessReplace(path, rgx, '', useRe=True)
    rgx = re.compile(r'<h1>.*?</h1>', re.DOTALL)
    postProcessReplace(path, rgx, '', useRe=True)
    #~ re.escape('<span class="pre">shinerainsevenlib.core.m0_text_io.</span>')
    mname = pathFragment.split('/')[1]
    rgx = re.escape(f'<span class="pre">shinerainsevenlib.core.{mname}.</span>')
    postProcessReplace(path, rgx, 'srss.', useRe=True)
    # add extra whitespace
    postProcessReplace(path, f'<dl class', '<br/><dl class')
    

subFiles = srss.strToList('''
core/m0_text_io
core/m1_core_util
core/m2_core_data_structures
core/m3_core_nonpure
core/m4_core_ui
core/m5_batch_util
core/m6_jslike''')
for subFile in subFiles:
    postProcessSubFile(subFile)
