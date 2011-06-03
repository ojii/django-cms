#!/bin/bash
find . -name '*.pyc' -delete


if [[ ! `which Xfvb &> /dev/null` ]]; then
    echo "Could not find Xfvb, cannot run selenium tests"
    exit 1
fi
cd tests

python bootstrap.py
bin/buildout -c selenium.cfg

Xfvb :99
export DISPLAY=:99

bin/django selenium_tests
