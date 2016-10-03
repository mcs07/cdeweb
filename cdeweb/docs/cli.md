# Command Line Interface

ChemDataExtractor includes a command line tool that can be accessed by typing `cde` at a command prompt.

## Using the Command Line

On a Mac, open the **Terminal** app, which you can find by searching or by looking in the **Utilities** folder in the 
**Applications** folder.

On Windows, use the **Command Prompt** or **PowerShell**.

For each of the commands below, type or paste the command, then press **Return** to run it.

For any command, add `--help` to the end to get information on how to use it.

## Downloading Data Files

In order to function, ChemDataExtractor requires a variety of data files, such as machine learning models, dictionaries,
and word clusters.

Data commands:

- `cde data download`: Download data files.
- `cde data clean`: Prune data that is no longer required.
- `cde data list`: List active data packages.
- `cde data where`: Print path to data directory.


## Reading documents

ChemDataExtractor processes each document input into a consistent internal format. To see what this looks like, run:

    cde read elements <path>
    
where `path` is the path to an input file in HTML, XML or PDF format. This will output a list of document elements.


