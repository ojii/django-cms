#!/bin/sh
cd examples
python bootstrap.py
bin/buildout -c simple.cfg
bin/django setup_cms_example
bin/django runserver $*
cd ..