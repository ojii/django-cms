#!/bin/sh
cd examples
python bootstrap.py
bin/buildout -c simple.cfg
bin/django syncdb --all
bin/django migrate --fake
bin/django runserver $*
cd ..
