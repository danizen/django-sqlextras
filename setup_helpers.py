"""
These helpers are external to setup.py to allow them to be debugged
and tested without running a setup.py
"""
import re
import os
import subprocess

# See https://www.python.org/dev/peps/pep-0440/#public-version-identifiers,  this is almost correct
VERSION_EXPR = '(\\d+!)?\\d+(\\.\\d+)*((a|b|rc)\\d+)?(\\.(post|dev)\d+)?'


def get_version():
    version = None
    if os.path.isdir('.git'):
        version = subprocess.check_output(['git', 'describe']).strip().decode('utf-8')
        with open('VERSION.txt', 'w') as f:
            f.write('%s\n' % version)
    if not version and os.path.isfile('VERSION.txt'):
        with open('VERSION.txt', 'r') as f:
            version = f.read().strip()
    if not version:
        version = '0.0.1'
    return version


def filter_dependencies(lines, exceptions=None):
    """
    Remove lines that are empty, for comments, imports or options,
    and parse the package name.
    :param lines: a list of lines
    :praam exceptions: a list of package names that should not have the version removed
    :return: a list of package names
    """
    if not exceptions:
        exceptions = []
    non_empty_lines = filter(lambda l: len(l) > 0, lines)
    non_comment_lines = filter(lambda l: not l.startswith('#'), non_empty_lines)
    package_lines = filter(lambda l: not l.startswith('-'), non_comment_lines)

    def package_name_from(line):
        nonlocal exceptions
        matches = [line.index(c) for c in '><=,' if c in line]
        if len(matches) > 0:
            name = line[:min(matches)]
            if name not in exceptions:
                line = name
        return line

    packages = [package_name_from(line) for line in package_lines]
    return packages


def get_dependencies(path, exceptions=None):
    """
    Parse requirements files using pip internals and return only the name of the requirement
    """
    lines = []
    with open(path, 'r') as f:
        lines = [l.strip() for l in f]
    return filter_dependencies(lines, exceptions)

