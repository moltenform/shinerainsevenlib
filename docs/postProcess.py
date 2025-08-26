
import os
import sys
import re

if not os.path.exists('pyproject.toml'):
    print('Please run this script where current directory = the root of the project')
    sys.exit(1)

sys.path.append('./src')
from shinerainsevenlib.standard import *

def postProcessReplace(path, search, replace, useRe=False, optional=False):
    if not path.startswith('./docs'):
        path = './docs/_build/html/' + path
    
    oldTxt = files.readAll(path)
    if useRe:
        txt = re.sub(search, replace, oldTxt)
    else:
        txt = oldTxt.replace(search, replace)
    
    if not optional:
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
<li class="toctree-l1"><a class="reference internal" href="files/m0_files_wrappers/index.html">Files section 0, wrappers</a></li>
<li class="toctree-l1"><a class="reference internal" href="files/m1_files_listing/index.html">Files section 1, iteration</a></li>
<li class="toctree-l1"><a class="reference internal" href="files/m2_files_higher/index.html">Files section 2, higher-level utils</a></li>
</ul>
</div>
</section>
<section id="submodulesplugins">
<h2>Plugins<a class="headerlink" href="#submodulesplugins" title="Link to this heading">¶</a></h2>
<div class="toctree-wrapper compound">
<ul>
<li class="toctree-l1"><a class="reference internal" href="plugins/plugin_fileexts/index.html">fileexts</a></li>
<li class="toctree-l1"><a class="reference internal" href="plugins/plugin_media/index.html">media</a></li>

'''
)

notyet = '''
<li class="toctree-l1"><a class="reference internal" href="plugins/plugin_configreader/index.html">configreader</a></li>
<li class="toctree-l1"><a class="reference internal" href="plugins/plugin_compression/index.html">compression</a></li>
<li class="toctree-l1"><a class="reference internal" href="plugins/plugin_store/index.html">store (database utils)</a></li>
</ul>
</div>
</section>
<section id="submodulestools">
<h2>Tools<a class="headerlink" href="#submodulestools" title="Link to this heading">¶</a></h2>
<div class="toctree-wrapper compound">
<ul>
<li class="toctree-l1"><a class="reference internal" href="files/xxxx/index.html">tool</a></li>
'''

postProcessReplace('autoapi/shinerainsevenlib/index.html', '<h2>Submodules<a class="headerlink',
                   '<h2>Core<a class="headerlink')

postProcessReplace('autoapi/index.html',
                     r'<li class="toctree-l[2-9]">.*', '', useRe=True)

def postProcessSubFile(pathFragment):
    path = 'autoapi/shinerainsevenlib/' + pathFragment + '/index.html'
    rgx = re.compile(r'<table class="autosummary longtable docutils align-default">.*?</table>', re.DOTALL)
    postProcessReplace(path, rgx, '', useRe=True)
    rgx = re.compile(r'<h1>.*?</h1>', re.DOTALL)
    postProcessReplace(path, rgx, '', useRe=True)
    mname = pathFragment.split('/')[1]
    
    if 'core' in pathFragment:
        rgx = re.escape(f'<span class="pre">shinerainsevenlib.core.{mname}.</span>')
        postProcessReplace(path, rgx, 'srss.', useRe=True)
    elif 'files' in pathFragment:
        rgx = re.escape(f'<span class="pre">shinerainsevenlib.files.{mname}.</span>')
        postProcessReplace(path, rgx, 'files.', useRe=True)
    elif 'plugins/plugin_media' in pathFragment:
        rgx = re.escape(f'<span class="pre">shinerainsevenlib.plugins.{mname}.</span>')
        postProcessReplace(path, rgx, 'SrssMedia.', useRe=True)
    elif 'plugins/plugin_fileexts' in pathFragment:
        rgx = re.escape(f'<span class="pre">shinerainsevenlib.plugins.{mname}.</span>')
        postProcessReplace(path, rgx, 'SrssFileExts.', useRe=True)

    # add extra whitespace
    postProcessReplace(path, f'<dl class', '<br/><br/><br/><dl class')
    # mark as optional
    postProcessReplace(path, f'_m2_core_data_structures.DefaultVal', '(Optional)', optional=True)
    # hide titles
    postProcessReplace(path, '<h2>Functions<a class="headerlink" href="#functions" title="Link to this heading">¶</a></h2>', '', optional=True)
    postProcessReplace(path, '<h2>Classes<a class="headerlink" href="#classes" title="Link to this heading">¶</a></h2>', '', optional=True)
    postProcessReplace(path, '<h2>Exceptions<a class="headerlink" href="#exceptions" title="Link to this heading">¶</a></h2>', '', optional=True)
    postProcessReplace(path, '<h2>Attributes<a class="headerlink" href="#attributes" title="Link to this heading">¶</a></h2>', '', optional=True)
    # leave 'module contents'
    # add periods
    rgx = re.compile(r'<dd>(.*?[^\.\?])</p>', re.DOTALL)
    postProcessReplace(path, rgx, r'<dd>\1.</p>', useRe=True, optional=True)
    

subFiles = srss.strToList('''
core/m0_text_io
core/m1_core_util
core/m2_core_data_structures
core/m3_core_nonpure
core/m4_core_ui
core/m5_batch_util
core/m6_jslike
files/m0_files_wrappers
files/m1_files_listing
files/m2_files_higher
plugins/plugin_fileexts
plugins/plugin_media
                          ''')
for subFile in subFiles:
    print(f'processing {subFile}')
    postProcessSubFile(subFile)

for f, short in files.recurseFiles('./docs/_build/html'):
    print(f)
    if short.endswith('.html'):
        if f.replace('\\', '/').endswith('_build/html/index.html'):
            rgx = re.compile(r'(\|.*?Powered by.*?)\|.*?<a href="_sources.*?Page source</a>', re.DOTALL)
            postProcessReplace(f, rgx, r'\1', useRe=True, optional=True)
        else:
            rgx = re.compile(r'\|.*?Powered by.*?Page source</a>', re.DOTALL)
            postProcessReplace(f, rgx, '', useRe=True, optional=True)
            postProcessReplace(f, '&#169;2025, Ben Fisher.', '&#169;2025, Ben Fisher, LGPLv2.1', optional=True)


