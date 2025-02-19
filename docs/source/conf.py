# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
from pathlib import Path

package_path = os.path.abspath("../../src")
sys.path.insert(0, package_path)
print(f"Adding path {package_path}")

# Add template utils to Python path
template_path = Path(__file__).parent / '_templates'
sys.path.append(str(template_path))

from utils.generate_nav import generate_nav_template

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
    # Sidebar behavior
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    
    # Top of page buttons
    "top_of_page_button": None,
    
    # Light mode styling
    "light_css_variables": {
        # Brand colors
        "color-brand-primary": "#7f6cef",
        "color-brand-content": "#7f6cef",
        
        # Sidebar styling
        "color-sidebar-background": "#f8f9fb",
        "color-sidebar-item-background--hover": "#ebedf0",
        "color-sidebar-link": "#2b3137",
        "color-sidebar-link--hover": "#7f6cef",
        
        # TOC styling
        "toc-title-font-size": "1rem",
        "toc-spacing-vertical": "1.5rem",
        "toc-font-size": "0.9rem",
        
        # Content styling
        "font-size--normal": "1rem",
        "font-size--small": "0.9rem",
        "content-padding": "3rem",
        
        # Admonition styling
        "color-admonition-background": "#f8f9fb",
    },
    
    # Dark mode styling
    "dark_css_variables": {
        "color-brand-primary": "#9386f3",
        "color-brand-content": "#9386f3",
        "color-sidebar-background": "#1a1c1e",
        "color-sidebar-item-background--hover": "#2b2d2f",
    },
    
    # Footer configuration
    "footer_icons": [],
    
    # Other settings
    "announcement": None,
    "show_toc_level": 4
}

# Show copyright but hide sphinx
html_show_sphinx = False
html_show_copyright = True
html_show_sourcelink = False

# Update sidebar configuration
html_sidebars = {
    "**": [
        "sidebar/search.html",
        "sidebar/navigation.html",
    ]
}

html_static_path = ["_static"]


# Add custom CSS to change fonts
html_css_files = [
    "custom.css",
]

# html_theme = 'sphinx_rtd_theme'
# html_static_path = ['_static']

# Generate navigation template
generate_nav_template()
