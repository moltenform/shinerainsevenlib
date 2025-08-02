

Example Usage
=======================

Installation is as easy as running ``pip install shinerainsevenlib``.

Then you can run a script like this,

.. code-block:: python

    from shinerainsevenlib import *

    for f in files.recurseFileInfo('/path/to/files'):
        print(f.path)
        if getInputBool("Display the size of this file?"):
            print(f.size())

    # convert a png to a jpg
    retcode, stdout, stderr = files.run(['cjpeg', 'image.png'])

    # get the crc32 of a file
    crc32 = files.computeHash('file.txt', 'crc32')

