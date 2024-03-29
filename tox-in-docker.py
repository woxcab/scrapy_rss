#!/usr/bin/env python3

"""
Script accepts the same arguments as tox command.
This runs tox command in the specific docker containers
that's identified by environment list.

Script logs docker and tests standard output
to the logs/docker.log and logs/pytest.log files respectively.

Examples:
tox-in-docker.py --help
tox-in-docker.py
tox-in-docker.py --recreate
tox-in-docker.py -f py310 -f py39
tox-in-docker.py -e py38-scrapy260
tox-in-docker.py -e "py{37,38,39,310}-scrapy260"
"""

import os
import sys
import re
import subprocess
from collections import defaultdict
from itertools import chain
import tox
from tox.session import load_config


class UnknownEnvlist(ValueError):
    pass


class DuplicateOutput:
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    def __init__(self, file):
        self.file = file

    def write(self, text):
        print(text, end='\r')
        sys.stdout.flush()
        self.file.write(self.ansi_escape.sub('', text))
        self.file.flush()


def main(docker_logfile, pytest_logfile):
    deprecated_pythons = {'py27', 'py33', 'py34', 'py35'}
    upcoming_python = 'py311'
    nonparallel_pythons = {'py33', 'py34', 'py311'}
    nonstandard_pythons = deprecated_pythons | {upcoming_python}
    pyfactor2container = lambda pyfactor: pyfactor if pyfactor in nonstandard_pythons else 'py3'

    tox_config = load_config(sys.argv[1:])

    argv = iter(sys.argv[1:])
    filtered_argv = []
    for arg in argv:
        if arg not in {'-e', '-f'}:
            filtered_argv.append(arg)
        else:
            try:
                next(argv)
            except StopIteration:
                pass

    containers = defaultdict(list)
    for testenv, testenv_config in tox_config.envconfigs.items():
        if testenv in tox_config.envlist:
            for pyfactor in testenv_config.factors:
                if tox.PYTHON.PY_FACTORS_RE.match(pyfactor):
                    containers[pyfactor2container(pyfactor)].append(testenv)

    unknown_envlists = set(tox_config.envlist) - set(tox_config.envconfigs)
    if unknown_envlists:
        raise UnknownEnvlist('Environment lists ' + ', '.join(unknown_envlists)
                             + ' are not defined in the Tox configuration file')

    sysenv = os.environ.copy()
    sysenv["USERID"], sysenv["GROUPID"] = str(os.getuid()), str(os.getgid())

    summary = []
    summary_title = None
    congratulations_line = None
    failed = False
    return_code = 0

    pytest_logger = DuplicateOutput(pytest_logfile)

    for container, envlist in containers.items():
        up = subprocess.run(['docker-compose', 'up', '--build', container],
                            env=sysenv,
                            stdout=docker_logfile, text=True, bufsize=1)
        if up.returncode:
            continue

        specialargs = []
        if container in deprecated_pythons:
            specialargs.append('--sitepackages')
        if container not in nonparallel_pythons:
            specialargs.append('--parallel')
        envlist_args = chain.from_iterable(zip(['-e']*len(envlist), envlist))
        with subprocess.Popen(['docker-compose', 'run', container, 'tox',
                               *specialargs, *filtered_argv, *envlist_args],
                              env=sysenv,
                              stdout=subprocess.PIPE,
                              text=True,
                              bufsize=1) as container_process:
            summary_reached = False
            while container_process.poll() is None:
                line = container_process.stdout.readline()
                if summary_reached:
                    if 'congratulations' in line:
                        congratulations_line = line
                    else:
                        if re.search(r'(?:error|fail(?:ure|ed)?)\b', line, flags=re.I):
                            failed = True
                        summary.append(line)
                elif '__ summary __' in line:
                    summary_title = line
                    summary_reached = True
                else:
                    pytest_logger.write(line)
            if container_process.returncode:
                return_code = container_process.returncode

    if summary_title:
        pytest_logger.write(summary_title)
    for summary_line in summary:
        pytest_logger.write(summary_line)
    if not failed and congratulations_line:
        pytest_logger.write(congratulations_line)

    if containers:
        subprocess.run(['docker-compose', 'down'],
                       env=sysenv,
                       stdout=docker_logfile, text=True, bufsize=1)

    exit(return_code)

if __name__ == '__main__':
    with open(os.path.join('logs', 'docker.log'), 'wt') as docker_log, \
         open(os.path.join('logs', 'pytest.log'), 'wt') as pytest_log:
        main(docker_log, pytest_log)
