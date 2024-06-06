

# add the most-commonly-used items to the top scope
from .core import alert, warn, trace, assertTrue, assertEq, tracep, softDeleteFile, getRandomString, jslike, Bucket

# the rest can be accessed via `srss`
from . import core as srss

# add modules where it's only one class that people need to access
from .plugins import plugin_configreader as _plugin_configreader
from .plugins import plugin_store as _plugin_store

# add other modules
from .plugins import plugin_compression as SrssCompression
from .plugins import plugin_imageutil as SrssImageUtil
from .plugins import plugin_fileexts as SrssFileExts
from . import files

SrssConfigReader = _plugin_configreader.SrssConfigReader
SrssStore = _plugin_store.SrssStore
