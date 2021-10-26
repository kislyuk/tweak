#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="tweak",
    version="1.0.4",
    url="https://github.com/kislyuk/tweak",
    license="Apache Software License",
    author="Andrey Kislyuk",
    author_email="kislyuk@gmail.com",
    description="Application configuration engine",
    long_description=open("README.rst").read(),
    packages=find_packages(exclude=["test"]),
    include_package_data=True,
    platforms=["MacOS X", "Posix"],
    test_suite="test",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
