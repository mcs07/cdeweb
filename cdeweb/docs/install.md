# Installation

To get up and running with ChemDataExtractor, you will need to install the python toolkit and then download the
data files.

## Installing the Toolkit

There are a few different ways to download and install the ChemDataExtractor toolkit.

### Option 1: Use conda

This method is recommended for all Windows users, as well as beginners on all platforms who don't already have Python
installed. [Anaconda Python](https://www.continuum.io/anaconda-overview) is a self-contained Python environment that is
particularly useful for scientific applications.

Start by installing [Miniconda](http://conda.pydata.org/miniconda.html), which includes a complete Python distribution
and the conda package manager, or [Anaconda](https://www.continuum.io/downloads), which additionally includes many
pre-installed packages. Choose the Python 3.5 version, unless you have a particular reason why you must use Python 2.7.

Once installed, at the command line, run:

    conda install -c chemdataextractor chemdataextractor
    
This command installs the `chemdataextractor` package from the `chemdataextractor` 
[conda channel](http://conda.anaconda.org/chemdataextractor).

### Option 2: Use pip

If you already have Python installed, it's easiest to install the ChemDataExtractor package using `pip`. At the 
command line, run:

    pip install ChemDataExtractor

On Windows, this will require the 
[Microsoft Visual C++ Build Tools](http://landinghub.visualstudio.com/visual-cpp-build-tools) to be installed. If you 
don't already have pip installed, you can 
[install it using get-pip.py](http://www.pip-installer.org/en/latest/installing.html).

### Option 3: Download the Latest Release

Alternatively, [download the latest release](http://data.chemdataextractor.org/download) manually and install yourself 
by running:

    python setup.py install

The setup.py command will install ChemDataExtractor in your `site-packages` folder so it is automatically available to
all your python scripts. 

You can also get the unstable development version by cloning the 
[git source code repository](https://github.com/mcs07/ChemDataExtractor).

## Getting the Data Files

In order to function, ChemDataExtractor requires a variety of data files, such as machine learning models, dictionaries,
and word clusters. Get these by running:

    cde data download

This will download all the necessary data files to the data directory. Run `cde data where` to see where this is.

## Updating

Upgrade your installation to the latest version at any time using conda or pip, matching the method you used originally 
to install it. For conda, run:

    conda update -c chemdataextractor chemdataextractor

For pip, run:

    pip install --upgrade ChemDataExtractor

Either way, always remember to download any new data files after doing this:

    cde data download
