# -*- coding: utf-8 -*-
import re
from setuptools import setup
 
 
version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('smommit/smommit.py').read(),
    re.M
).group(1)
 
# Opening readme
with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")
f.close()

# Opening requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()
 
setup(
    name="smommit",
    packages=["smommit"],
    entry_points={"console_scripts": ['smommit = smommit.smommit:main']},
    version=version,
    python_requires='>=3',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    
    description="The CLI tool for forgetful gits.",
    long_description=long_descr,
    long_description_content_type='text/markdown',
    
    author="Jakab Zeller",
    author_email="jakabzeller0@gmail.com",
    url="https://github.com/andygello555/smommit",
)