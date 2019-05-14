#!/usr/bin/env python
from setup_helpers import (
    get_version,
    get_dependencies,
)

from setuptools import setup, find_packages


setup(
    name='django-sqlextras',
    version=get_version(),
    description='Easily manage custom SQL migrations in Django',
    author='Dan Davis',
    author_email='dan@danizen.net',
    url='https://github.com/danizen/django-sqlextras',
    packages=find_packages(),
    package_data={},
    include_package_data=True,
    tests_require=get_dependencies('requirements_test.txt'),
    install_requires=get_dependencies('requirements.txt'),
)
