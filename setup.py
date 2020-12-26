#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'python-dotenv>=0.5.1',
    'pbkdf2>=1.3',
    'pycryptodome>=3.9.9'
]

setup_requirements = [
    'pytest-runner',
    # TODO(blueogive): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]

setup(
    name='pyncrypt',
    version='0.3.0',
    description="Create, maintain, and use encrypted key-value stores",
    long_description=readme + '\n\n' + history,
    author="Mark Coggeshall",
    author_email='mark.coggeshall@gmail.com',
    url='https://github.com/blueogive/pyncrypt',
    packages=find_packages(include=['pyncrypt']),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='pyncrypt',
    classifiers=[
        'Development Status :: 3 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
