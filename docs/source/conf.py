# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
# Go up two directory levels to reach the SDA-Proj folder
sys.path.insert(0, os.path.abspath('../../'))
project = 'GDP Analysis'
copyright = '2026, Ahmad Rehan and Asjad Raza'
author = 'Ahmad Rehan and Asjad Raza'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',     # Automatically extract docstrings
    'sphinx.ext.napoleon',    # Allows Sphinx to read Google-style docstrings (highly recommended)
    'sphinx.ext.autosummary',
]

html_theme = 'sphinx_rtd_theme'  # Use the beautiful Read the Docs theme

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ['_static']
