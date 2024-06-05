
*welcome to shinerainsoftsevenutil*

Useful unadorned utilities for powerful Python programming.


By design, there are no required dependencies for this project. It's designed to be simple to add to your code, either by pip, or just by adding a shinerainsoftesvenutil.zip file next to your code and importing it.

There are some optional dependencies to enable a few unimportant features,

* module `Send2Trash`, to send files to OS trash location
* module `crc64iso`, to get the crc64 of a file
* module `xxhash`, to get the xxhash of a file
* module `apsw`, for `srss_db` database helpers
* module `dateparser`, for the `EnglishDateParserWrapper` class
* module `parse`, for the `ParsePlus` class
* module `pyperclip`, for accessing the clipboard
* module `pytest`, to run this project's tests

## Project information

There are vscode tasks for this project. To run a task, hit `Cmd+Shift+P`, then type "Tasks: run task", then choose a task from the list.

There are tasks for:
* Linting the project
* Autoformatting the project
* Running tests

## Configuration

Place a file named `shinerainsoftsevenutil.cfg` into the `core` directory.

Example contents,

```
[main]
tempEphemeralDirectory=G:\data\local\temp
tempDirectory=D:\data\local\temp
softDeleteDirectory=D:\data\local\trash

```

## Python 2

A Python2 compatible version of this library can be found here, https://github.com/moltenform/scite-with-python/tree/main/src/scite/scite/bin/tools_internal/ben_python_common
