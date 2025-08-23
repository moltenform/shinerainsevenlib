
# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv2.1 License

# don't add these broad imports to __init__.py, otherwise a module in
# a directory that imported ..otherdir would bring in the entire project.

# add the most-commonly-used items to the top scope
from .core import (
    alert,
    warn,
    trace,
    tracep,
    assertTrue,
    assertEq,
    softDeleteFile,
    getRandomString,
    getInputString,
    getInputBool,
    Bucket
)

from .core import m6_jslike as jslike

# the rest can be accessed via `srss`
from . import core as srss

# add modules where it's only one class that people need to access
from .plugins.plugin_configreader import SrssConfigReader
#~ from .plugins.plugin_store import SrssStore

#~ # add other modules
#~ from .plugins import plugin_compression as SrssCompression
from .plugins import plugin_fileexts as SrssFileExts
from .plugins import plugin_media as SrssMedia
from .plugins import tools_any_project as tools_any_project
from . import files
