

Example Usage
=======================

Installation is as easy as running ``python -m pip install shinerainsevenlib``.

Then you can run a script like this,

.. code-block:: python

    from shinerainsevenlib.standard import *

    # iterate through files
    for f in files.recurseFileInfo('/path/to/files'):
        print(f.path)
        if getInputBool("Display the size of this file?"):
            print(f.size())

    # ask yes/no
    if srss.getInputBool('Convert file to jpg?'):
        files.run(['cjpeg', 'image.png'])
    

.. # convert a png to a jpg
.. retcode, stdout, stderr = files.run(['cjpeg', 'image.png'])
.. # get the crc32 of a file
.. crc32 = files.computeHash('file.txt', 'crc32')
