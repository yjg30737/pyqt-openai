import toml

SETUP_FILENAME = '../pyproject.toml'

with open(SETUP_FILENAME, "r") as file:
    pyproject_data = toml.load(file)

# Even though constants are declared in the constants.py file
# For the sake of following the PEP8 standard, we will declare module-level dunder names here.

# PEP8 standard about dunder names: https://peps.python.org/pep-0008/#module-level-dunder-names

__version__ = pyproject_data["project"]["version"]
__author__ = pyproject_data["project"]["authors"][0]['name']

__all__ = ['__version__',
           '__author__']

