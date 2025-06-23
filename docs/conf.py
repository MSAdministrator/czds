"""Sphinx configuration."""

project = "CZDS"
author = "Josh Rickard"
copyright = "2023, Josh Rickard"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
