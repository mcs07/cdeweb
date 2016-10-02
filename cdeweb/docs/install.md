# Installation

To get up and running with ChemDataExtractor, you will need to install the python toolkit and then download the
data files.


## Installing the Toolkit

There are a couple of ways to download and install the ChemDataExtractor toolkit.

### Option 1: Use pip (recommended)

The easiest and recommended way to install is using pip. At the command line, run:

    pip install ChemDataExtractor

This will download the latest version of ChemDataExtractor, and place it in your `site-packages` folder so it is
automatically available to all your python scripts.

If you don't already have pip installed, you can 
[install it using get-pip.py](http://www.pip-installer.org/en/latest/installing.html):

    curl -O https://raw.github.com/pypa/pip/master/contrib/get-pip.py
    python get-pip.py

### Option 2: Download the Latest Release

Alternatively, [download the latest release](http://data.chemdataextractor.org/download) manually and install yourself 
by running::

    cd ChemDataExtractor-1.0.0
    python setup.py install

The setup.py command will install ChemDataExtractor in your `site-packages` folder so it is automatically available to
all your python scripts.

## Getting the Data Files

In order to function, ChemDataExtractor requires a variety of data files, such as machine learning models, dictionaries,
and word clusters. Get these by running:

    cde data download


This will download all the necessary data files to the data directory. Run `cde data where` to see where this is.

## Updating

Upgrade your installation to the latest version at any time using pip. Always remember to download any new data files
after doing this:


    pip install --upgrade ChemDataExtractor
    cde data download
