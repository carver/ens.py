"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages
from io import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ens',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.4.0',

    description='Ethereum Name Service, made easy in Python',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/carver/ens.py',

    # Author details
    author='Jason Carver',
    author_email='ut96caarrs@snkmail.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Information Technology',
        'Topic :: Database :: Front-Ends',
        'Topic :: Internet :: Finger',
        'Topic :: Internet :: Name Service (DNS)',
        'Topic :: Security :: Cryptography',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Systems Administration :: Authentication/Directory',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords='ethereum eth web3 web3.py ENS web3utils',

    python_requires='>=3.5',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['tests', 'venv']),

    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['pytz', 'web3utils>=0.0.3,<1'],
)
