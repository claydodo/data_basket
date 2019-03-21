#!/bin/sh

python setup.py sdist bdist_wheel
python3 setup.py bdist_wheel

VERSION=`cat setup.py | grep 'version=' | grep -o '[0-9]*\.[0-9]*\.[0-9]*'`

twine upload dist/*${VERSION}*
