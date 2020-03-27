.. toctree::
   :maxdepth: 1

doc
===

Tool that generates a IDIADA tool documentation overview using SPHINX

Usage
-----

usage::

    doc [-h] [-init] [-update] [-sync]

    optional arguments:
      -h, --help  show this help message and exit
      -init       Clones existing IDIADA tool documentation files from github
                  master repository and sets remote origin.
      -update     Creates documentation html content from source documentation
                  files.
      -sync       Synchonises source documentation files with the master
                  repository.