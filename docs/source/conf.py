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

html_theme = "pydata_sphinx_theme"
# html_context["default_mode"] = "dark"
# html_theme_options["navbar_end"] = ["navbar-icon-links"]

html_context = {"default_mode": "light"}  # Set default color mode to light

html_theme_options = {
    # Remove all navbar items
    "navbar_start": [],
    "navbar_center": [],
    "navbar_end": [],
    "navbar_persistent": [],
    # Configure navigation behavior
    "navigation_depth": 2,
    "show_nav_level": 1,
    "navigation_with_keys": True,
    "collapse_navigation": True,  # Add this to collapse other sections
    "show_toc_level": 2,
    # Remove secondary sidebar
    "secondary_sidebar_items": [],
    # Configure the sidebar end section
    "primary_sidebar_end": ["theme-switcher"],
    # Footer configuration
    "footer_start": ["copyright"],
    "footer_end": [],
}

# Configure left sidebar with different components for different pages
html_sidebars = {
    "**": [  # Show minimal sidebar on all other pages
        "search-field.html",
        "navbar-nav.html",
        "sidebar-nav-bs.html",
    ]
}

html_static_path = ["_static"]


# Add custom CSS to change fonts
html_css_files = [
    "custom.css",
]

# html_theme = 'sphinx_rtd_theme'
# html_static_path = ['_static']
