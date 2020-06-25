# Installation

To get up and running with ChemDataExtractor, you will need to install the python 
toolkit and then download the data files.

## Installing the Toolkit

There are a few different ways to download and install the ChemDataExtractor toolkit. 
We recommended using conda.

[Anaconda Python](https://www.anaconda.com) is a self-contained Python environment that 
is particularly useful for scientific applications. Start by installing 
[Miniconda](https://docs.conda.io/en/latest/miniconda.html), which includes a complete 
Python  distribution and the conda package manager, or 
[Anaconda](https://www.anaconda.com/products/individual), which additionally includes 
many pre-installed packages. Either way, choose the Python 3 version.

Once installed, at the command line, run:

    conda config --add channels conda-forge
    conda install chemdataextractor
    
The first command adds the `conda-forge` channel as a package source, then the second 
command installs the `chemdataextractor` package from this channel.

## Getting the Data Files

In order to function, ChemDataExtractor requires a variety of data files, such as 
machine learning models, dictionaries, and word clusters. Get these by running:

    cde data download

This will download all the necessary data files to the data directory. Run 
`cde data where` to see where this is.

## Updating

Upgrade your installation to the latest version at any time using conda:

    conda update chemdataextractor

Remember to download any new data files after doing this:

    cde data download
