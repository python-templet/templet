#!/usr/bin/env python3

from distutils.core import setup

setup(
    name='python_templet',
    version='4.0.0',
    description='Lightweight string templating via function decorator.',
    long_description=open('README.md', 'r').read(),
    author='David Bau',
    author_email='david.bau@gmail.com',
    url='https://github.com/python-templet/templet',
    packages=[],
    py_modules=['templet', 'test_templet'],
    scripts=[],
    license='BSD',
    keywords="simple string template decorator",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries",
        "Topic :: Text Processing :: General",
    ]
)
