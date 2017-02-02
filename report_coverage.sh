#!/bin/bash

# Run tests, generate coverage report and open it on a browser
#
# Requires: coverage 3.3 or above from http://pypi.python.org/pypi/coverage

PYTHONPATH="$PWD:$PYTHONPATH" coverage run $(which trial) --reporter=text tests
coverage html -i
python -m webbrowser coverage_report/index.html
