#!/usr/bin/env python
from distutils.core import setup
setup(
    name = "django-ticket",
    packages = ["issues"],
    version = "1.0.0",
    description = "Issue tracker using django",
    author = "Daniel Snider",
    author_email = "mrdanielsnider@gmail.com",
    url = "http://github.com/mostateresnet/django-ticket",
    download_url = "https://github.com/mostateresnet/django-ticket/zipball/master",
    keywords = ["django", "ticket", "issue", "bug"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Bug Tracking",
        ],
    )

