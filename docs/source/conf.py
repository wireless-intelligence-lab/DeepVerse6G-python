# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

package_path = os.path.abspath("../../src")
sys.path.insert(0, package_path)
print(f"Adding path {package_path}")

project = "DeepVerse6G"
copyright = "2025, Umut Demirhan, Abdelrahman Taha, Shuaifeng Jiang, Ahmed Alkhateeb"
author = "Umut Demirhan, Ahmed Alkhateeb"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # Core library for html generation from docstrings
    "sphinx.ext.autosummary",  # Create neat summary tables
    "nbsphinx",
]

templates_path = ["_templates"]
exclude_patterns = []

autosummary_generate = True

nbsphinx_allow_errors = True
nbsphinx_execute = "never"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# import maisie_sphinx_theme
# extensions.append("maisie_sphinx_theme")
# html_theme = 'maisie_sphinx_theme'
# html_theme_path = maisie_sphinx_theme.html_theme_path()

html_theme = "furo"
# html_context["default_mode"] = "dark"
# html_theme_options["navbar_end"] = ["navbar-icon-links"]

html_context = {"default_mode": "light"}  # Set default color mode to light

html_theme_options = {
    "sidebar_hide_name": False,
    "light_css_variables": {
        "color-brand-primary": "#7f6cef",
        "color-brand-content": "#7f6cef",
    },
    "dark_css_variables": {
        "color-brand-primary": "#9386f3",
        "color-brand-content": "#9386f3",
    },
    "footer_icons": [],
    "light_logo": "logo-light.png",  # Add this if you have light/dark logos
    "dark_logo": "logo-dark.png",    # Add this if you have light/dark logos
    "default_mode": "light"          # This is the correct way to set default mode in Furo
}

# Show copyright but hide sphinx
html_show_sphinx = False
html_show_copyright = True
html_show_sourcelink = False

# Simplify sidebar configuration for furo
html_sidebars = {
    "**": [
        "sidebar/search.html",
        "sidebar/scroll-start.html",
        "sidebar/navigation.html",
        "sidebar/scroll-end.html",
    ]
}

html_static_path = ["_static"]


# Add custom CSS to change fonts
html_css_files = [
    "custom.css",
]

# html_theme = 'sphinx_rtd_theme'
# html_static_path = ['_static']
