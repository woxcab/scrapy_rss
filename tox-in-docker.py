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
tox-in-docker.py -m latest  # run tests with latest Scrapy on each Python version
tox-in-docker.py -m deprecated_latest  # run tests with latest Scrapy on each deprecated Python version
tox-in-docker.py -m actual_latest  # run tests with latest Scrapy on each actual Python version
tox-in-docker.py -m single_latest  # run tests with latest Scrapy on latest Python version
tox-in-docker.py -e py38-scrapy260
tox-in-docker.py -e py38-scrapy260,py310-scrapy290
tox-in-docker.py -e py312-scrapy2.13.0 -e py313-scrapy2.13.0
tox-in-docker.py -e py38-scrapy260 -- tests/test_exporter.py
tox-in-docker.py -e py38-scrapy260 -- -vv tests/elements/test_repr.py
"""

import os
import sys
import re
import subprocess
from collections import defaultdict
from tox.tox_env.python.api import PY_FACTORS_RE
from tox.run import setup_state


class UnknownEnvlist(ValueError):
    pass

class UnknownFactor(ValueError):
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
    deprecated_pythons = {'py27', 'py33', 'py34', 'py35', 'py36', 'py37', 'py38'}
    upcoming_python = 'py314'
    nonparallel_pythons = {'py27', 'py33', 'py34'}
    nonstandard_pythons = deprecated_pythons | {upcoming_python}
    pyfactor2container = lambda pyf: pyf if pyf in nonstandard_pythons else 'py3'

    tox_config = setup_state(sys.argv[1:])
    default_tox_config = setup_state([])
    default_tox_envs = set(default_tox_config.envs.iter())
    argv = iter(sys.argv[1:])
    filtered_argv = []
    double_dashed = False
    filtered_pytest_argv = []
    for arg in argv:
        if double_dashed:
            filtered_pytest_argv.append(arg)
        elif arg == '--':
            double_dashed = True
        elif arg in {'-e', '-f', '-m'}:
            try:
                next(argv)
            except StopIteration:
                pass
        else:
            filtered_argv.append(arg)

    containers = defaultdict(list)
    envs = set(tox_config.envs.iter())
    for testenv in envs:
        pyfactor = testenv.split('-', 1)[0]
        if not PY_FACTORS_RE.match(pyfactor):
            raise UnknownFactor(pyfactor)
        containers[pyfactor2container(pyfactor)].append(testenv)

    unknown_envlists = envs - default_tox_envs
    unknown_envlists = {e for e in unknown_envlists if not e.startswith(upcoming_python)}
    if unknown_envlists:
        raise UnknownEnvlist('Environment lists ' + ', '.join(unknown_envlists)
                             + ' are not defined in the Tox configuration file')
    sysenv = os.environ.copy()
    sysenv["USERID"], sysenv["GROUPID"] = str(os.getuid()), str(os.getgid())

    summary = []
    summary_title = None
    failed = False
    return_code = 0

    pytest_logger = DuplicateOutput(pytest_logfile)

    for container, envlist in containers.items():
        up = subprocess.run(['docker', 'compose', 'up', '--build', '--remove-orphans', container],
                            env=sysenv,
                            stdout=docker_logfile, text=True, bufsize=1)
        if up.returncode:
            continue

        specialargs = []
        pytest_ini = ''
        if container in {'py27', 'py33', 'py34'}:
            pytest_ini = 'pytest-sync-only.ini'
        if container in deprecated_pythons:
            specialargs.append('--sitepackages')
        if container not in nonparallel_pythons:
            specialargs.extend(['-p', 'auto'])
        pytest_args = filtered_pytest_argv
        if pytest_ini:
            pytest_args = ['-c', pytest_ini] + pytest_args
        with subprocess.Popen(['docker', 'compose', 'run', '--remove-orphans', container, 'tox',
                               *specialargs, *filtered_argv, '-e', ','.join(envlist),
                               '--', *pytest_args],
                              env=sysenv,
                              stdout=subprocess.PIPE,
                              text=True,
                              bufsize=1) as container_process:
            try:
                summary_reached = False
                while container_process.poll() is None:
                    line = container_process.stdout.readline()
                    if re.search(r'(congratulations|evaluation failed)', line):
                        continue
                    if summary_reached:
                        if re.search(r'(?:error|fail(?:ure|ed)?)\b', line, flags=re.I):
                            failed = True
                        if not re.search(r'(: commands\[|: exit | summary )', line):
                            summary.append(line)
                        pytest_logger.write(line)
                    elif re.search(r'(__ summary __|: (OK|FAIL).*=setup.*\+cmd)', line):
                        summary_title = os.linesep + ' SUMMARY '.center(80, '=') + os.linesep
                        summary_reached = True
                        if ' FAIL ' in line:
                            failed = True
                        if '=setup' in line:
                            summary.append(line)
                        if ' summary ' not in line:
                            pytest_logger.write(line)
                    else:
                        pytest_logger.write(line)
                if container_process.returncode:
                    return_code = container_process.returncode
            except KeyboardInterrupt as e:
                subprocess.run(['docker', 'compose', 'kill', '-s', 'SIGKILL', container],
                               env=sysenv,
                               stdout=docker_logfile, text=True, bufsize=1)
                raise e from e

        pytest_logger.write(os.linesep + os.linesep)


    if summary_title:
        pytest_logger.write(summary_title)
    for summary_line in summary:
        pytest_logger.write(summary_line)
    pytest_logger.write('evaluation failed :(\n' if failed else 'congratulations :)\n')

    if containers:
        subprocess.run(['docker-compose', 'down'],
                       env=sysenv,
                       stdout=docker_logfile, text=True, bufsize=1)

    exit(return_code)


if __name__ == '__main__':
    with open(os.path.join('logs', 'docker.log'), 'wt') as docker_log, \
         open(os.path.join('logs', 'pytest.log'), 'wt') as pytest_log:
        main(docker_log, pytest_log)
