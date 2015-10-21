<p align="center"><a href="https://github.com/biologyguy/BuddySuite/wiki">
<img src="https://raw.githubusercontent.com/biologyguy/BuddySuite/master/images/BuddySuite-logo.gif" /></a></p>
<p align="center">
<a href="https://github.com/biologyguy/BuddySuite/wiki/SeqBuddy"><img src="https://raw.githubusercontent.com/biologyguy/BuddySuite/master/images/SeqBuddy-logo.gif" width=20%/></a>
<a href="https://github.com/biologyguy/BuddySuite/wiki/AlignBuddy"><img src="https://raw.githubusercontent.com/biologyguy/BuddySuite/master/images/AlignBuddy-logo.gif" width=25%/></a>
<a href="https://github.com/biologyguy/BuddySuite/wiki/DatabaseBuddy"><img src="https://raw.githubusercontent.com/biologyguy/BuddySuite/master/images/DBBuddy-logo.gif" width=20%/></a>
<a href="https://github.com/biologyguy/BuddySuite/wiki/PhyloBuddy"><img src="https://raw.githubusercontent.com/biologyguy/BuddySuite/master/images/PhyloBuddy-logo.gif" width=25%/></a>
</p>
<p align="center">Do fun stuff with biological data files. Seriously, biological data is fun stuff :)</p>
___
## Description
The BuddySuite modules are designed to be 'one-stop-shop' command line tools for common biological data file
 manipulations.

[SeqBuddy](https://github.com/biologyguy/BuddySuite/wiki/SeqBuddy) is the most mature BuddySuite tool, although
 [AlignBuddy](https://github.com/biologyguy/BuddySuite/wiki/AlignBuddy) and
 [PhyloBuddy](https://github.com/biologyguy/BuddySuite/wiki/PhyloBuddy) are also functional with a more limited number
 of commands. [DatabaseBuddy](https://github.com/biologyguy/BuddySuite/wiki/DatabaseBuddy) is a very different project,
 existing mostly as a 'live shell' for downloading sequences from GenBank, ENSEMBL, and UniProt. It definitely works,
 but has some bugs.

Being pure Python, the BuddySuite should be cross platform. Development and testing have been done on Linux
 and Mac OS X, however, so it is unclear if the Suite will work within Windows.

## Dependencies
This project has been written in Python3 and is not backwards compatible with Python2. If Python3 is not currently
 installed on your system, we highly recommend using the free [Anaconda manager](http://continuum.io/downloads#py34)
 from Continuum Analytics. Alternatively, the software can be downloaded directly from the
 [Python Software Foundation](https://www.python.org/downloads/).


The SeqBuddy blast, bl2seq, and purge functions require access to the blastp, blastn, and blastdbcmd binaries from the
 [NCBI C++ toolkit](http://www.ncbi.nlm.nih.gov/IEB/ToolBox/CPP_DOC/). If not already in your PATH the binaries will be
 downloaded by the installer. SeqBuddy.py will also attempt to download the binaries if any BLAST dependant functions
 are called and the programs are not found in PATH. AlignBuddy and PhyloBuddy can be used to launch a number of third
 party alignment/tree building programs, but the installation of these is up to you.
 
[BioPython](http://biopython.org/) is used heavily by the entire suite, and must be installed in your Python PATH to
 use the development version of the software. Furthermore, any BioPython versions earlier than 16.6 will cause unit
 tests to fail. PhyloBuddy requires [DendroPy](https://pythonhosted.org/DendroPy/) and version 3.0 (beta) of the
 [ETE toolkit](http://etetoolkit.org/download/). All of these dependencies are bundled with the installer, however, so
 _**no extra download is required**_ unless you are developing (or want the bleeding edge).
 
## Standalone installation 
#### This is still an Alpha version, but it seems to be working for Mac and Linux. It will not work on Windows.
[Download the graphical installer](https://raw.github.com/biologyguy/BuddySuite/master/BuddySuite.py)
 and run it from the command line
    
    $: cd /path/to/download/folder
    $: chmod +x BuddySuite.py
    $: ./BuddySuite.py

By default, the installer will place short form sym-links to the main tools in your PATH ('sb' for SeqBuddy, 'alb'
 for AlignBuddy, 'pb' for PhyloBuddy, and 'db' for DatabaseBuddy), so they can be accessed quickly ([examples in the
 wiki](https://github.com/biologyguy/buddysuite/wiki) use these short forms). The full names of each tool will also be
 added to PATH. If working outside the context of a graphical OS (on a cluster, for example), the installer may be run
 with the -cmd flag, which will walk you through the install processes directly from the command line.

Once out of alpha, the installer will only bundle stable release versions of the BuddySuite. If bugs are found they will
 be fixed, but the *expected* behavior will not be changed once the release is finalized. Likewise, new features added
 to the development versions will not become available in the installer until the next release. Versions of each tool or
 the installer can be displayed using the -v flag.

## Development version installation
All new features are developed in the 'workshop' versions of the buddy programs. These may be less stable than the
 official release versions, and may have extra dependencies. The easiest way to get the development version
 up and running is to [clone/fork](https://help.github.com/articles/fork-a-repo/) the repository.

    $: git clone https://github.com/biologyguy/BuddySuite.git

For further information on dependencies and how to contribute to the project, please see the
 [developer page](https://github.com/biologyguy/BuddySuite/wiki/Developers).

## Contact
Any comments you may have would be really appreciated. Please feel free to add issues in the GitHub issue tracker or
 contact me directly at [steve.bond@nih.gov](mailto:steve.bond@nih.gov)