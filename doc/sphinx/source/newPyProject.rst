.. toctree::
   :maxdepth: 1

newPyProject
============

Creates a new python project template according to the given target project type. 
This project is supposed to be installed into standard project structure using pyProjectInstaller.  

* creates a default project structure
* creates a default sphinx documentation which will be generated from the documentation string of the main.py file
* initiates a git repository

Usage
-----

usage::

    newPyProject [-h] [-wrap script_path] [-ansaCheck] [-ansaButton] [-metaSession] projectName [project_path]
    
    positional arguments:
      projectName        Project name.
      project_path       New project location. (Default=Current directory)

    optional arguments:
      -h, --help         show this help message and exit
      -wrap script_path  Automatically wraps given executable script with a
                     newPyProject of given name. This project can be
                     directly installed using pyProjectInstaller.
      -ansaCheck         Creates an ANSA check template. Please be aware that in
                     order to use pyProjectInstaller the new created check
                     file name must contain a prefix: check_*.py
      -ansaButton        Creates an ANSA user script button template. This project
                     can be directly added to ANSA using pyProjectInstaller.
      -metaSession       Creates a META session template. This project can be
                     directly added to META using pyProjectInstaller.