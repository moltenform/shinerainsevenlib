

Editing this project
=======================

If you open this project in VSCode, there will be some defined tasks and launchors, to make it easy to run tests and attach a debugger.

To get full features editing this project, do the following:


.. code-block:: console

    (in a virtual environment,)
    python -m pip install pytest
    python -m pip install pylint
    python -m pip install ruff
    python -m pip install coverage
    python -m pip install sphinx
    code .
    (now vscode will have the correct context and path.)
    (when you open a .py file, an icon saying something 
    like "3.13" will appear in the lower right of vscode,
    click that icon and confirm that you are in the context
    of the virtual environment.)
    (you can now go to Run and Debug to run tests.)
    (you can now hit ctrl+shift+b and run a task like linting.)

Features of this project include,

* lint via pylint
* lint and autoformatting via ruff
* documentation via sphinx
* testing via pytest
* coverage via coverage
* github actions verify PRs by running tests
* can publish to pip


