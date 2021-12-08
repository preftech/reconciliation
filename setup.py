import json
import os
from setuptools import setup

with open('README.md') as f:
    long_description = f.read()
    
setup(
    name = 'reconciliation',         
    packages = ['reconciliation'],   
    version = '0.1',
    license='MIT',
    description = 'An OpenRefine Reconciliation Framework for Python',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author = 'patrick oleary',                   # Type in your name
    author_email = 'techops@preftech.com',      # Type in your E-Mail
    url = 'https://github.com/preftech/pyreconciliation',   # Provide either the link to your github or to your website
    keywords = ['reconcile', 'reconciliation', 'openrefine', 'cocoda'],   # Keywords that define your package best
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',      # Define that your audience are developers
        'Topic :: Text Processing',
        'Framework :: Flask',
        'License :: OSI Approved :: MIT License',   # Again, pick a license
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
)