# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'shinerainsevenlib'
copyright = '2025, Ben Fisher'
author = 'Ben Fisher'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
extensions = [
    'autoapi.extension'
]

autoapi_dirs = ['../src/shinerainsevenlib']
autoapi_type = "python"

def custom_skip(app, what, name, obj, skip, options):
    # name is fully qualified, get only the last part
    lastPartOfName = name.split(".")[-1]
    if lastPartOfName.startswith("_"):
        skip = True
    return skip

def setup(sphinx):
    sphinx.connect("autoapi-skip-member", custom_skip)

