# Script for building docstring docs
pip install sphinx sphinx-markdown-builder sphinx-autodoc-typehints;

sphinx-apidoc -o Sphinx-docs ../src sphinx-apidoc --full -A 'Benjamin Barton'; cd Sphinx-docs;

echo "import os
import sys
sys.path.insert(0,os.path.abspath('../..'))
sys.path.insert(0, os.path.abspath('../../src'))

def skip(app, what, name, obj,would_skip, options):
    if name in ( '__init__',):
        return False
    return would_skip
def setup(app):
    app.connect('autodoc-skip-member', skip)
extensions.append('sphinx_autodoc_typehints')
" >> conf.py;

make markdown

cd ..
echo "All Module Structure
" >> module_structure.md
tail --lines=+13 ./Sphinx-docs/_build/markdown/index.md >> module_structure.md
#cp index.md index_full.md
#tail --lines=+13 ./Sphinx-docs/_build/markdown/index.md >> index_full.md
#echo "
#[Back to top](#pybdy-documentation)" >> index_full.md

rm ./Sphinx-docs/_build/markdown/index.md
mv ./Sphinx-docs/_build/markdown/*.md .
python format_docs.py

rm -rf Sphinx-docs
