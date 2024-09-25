# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath('../../src/catframes'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Catframes'
copyright = '2022–2024, Устинов Г.М.'
author = 'Устинов Г.М.'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon'
]

language = 'ru'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_theme_options = {
    'description': 'catframes',
    'github_user': 'georgy7',
    'github_repo': 'catframes',
    'github_banner': True,
    'show_powered_by': False,
    'extra_nav_links': {
        'GitHub': 'https://github.com/georgy7/catframes',
    },
    'page_width': '940px',
    'sidebar_width': '220px',
    'fixed_sidebar': True,
}

html_static_path = ['_static']
html_css_files = ['custom.css']