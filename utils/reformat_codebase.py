"""
    Small code util help reformat all code base with black and isort
"""

import fnmatch
import os

import isort

START_FOLDER = "/app/"
EXCLUDE_FOLDERS = [
    ".mypy_cache",
    ".vscode",
    "_conf",
    "media",
    "local",
    "assets",
    "static",
    ".git",
    "__pycache__",
    "migrations",
    "node_modules",
    "templates",
]

for root, dirnames, filenames in os.walk(START_FOLDER):
    if any([i in root for i in EXCLUDE_FOLDERS]):
        continue

    for filename in fnmatch.filter(filenames, "*.py"):
        f_name = os.path.join(root, filename)
        isort.file(f_name)
        os.system(f"black {f_name}")
