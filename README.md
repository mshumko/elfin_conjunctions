# Introduction
This is a Python project template with a configuration script that saves the data paths to `config.ini`. Publishing to PyPI (so you only have to install this via `python3 -m pip install elfin_conjunctions`) is a few extra steps and [this article](https://realpython.com/pypi-publish-python-package/) goes into the details.

I found this package format very useful for my data analysis projects so hopefully you will too. Feel free to copy/paste these files into your own repository and rename/delete all of the dummy names and modules.  

# Installation
- To install as a developer run:
  ```bash
    git clone git@github.com:mshumko/elfin_conjunctions.git
    cd elfin_conjunctions

    # Then one of these (see comment in requirement.txt):
    python3 -m pip install -e .
    ```
    or 
    ```bash
    python3 -m pip install -r requirements.txt 
    ```

# Configuration
After you install the project using the above commands, run `python3 -m elfin_asi_conjunctions config` to add the path to the ELFIN data. It will be saved to `elfin_asi_conjunctions/config.ini`. 

# Dependencies
You'll need to install [IRBEM](https://github.com/PRBEM/IRBEM) to use the `Conjunction` class in `conjunction.py`. You'll need to compile the fortran code and then install the Python wrapper.

# Structure
This folder (`project_template`):
- The `project_template` folder contains the auxiliary files required to install the `project` package (a folder). 
    - `setup.py`: Installs `project` using `setuptools`. It's formatting is [rapidly evolving](https://blog.pilosus.org/posts/2019/12/26/python-third-party-tools-configuration/), but a popular location to save the project metadata in `setup.cfg`. The `setup.cfg` metadata contains external dependencies that are installed via `python3 -m pip install -e .` (don't forget the period).
    - `requirements.txt`: the pinned project dependencies installed when you call `python3 -m pip install -r requirements.txt`.
- The `project` folder contains the package source code and the folder's name becomes the package name (imported via `import project`).
    - `__init__.py`: module is executed when you call `import project`. Here, it contains the code to load the `config.ini` file 
    - `__main__.py`: module creates the `config.ini` with the hard-coded paths. You can call it using `python3 -m project config`. **Techincal note: `__main__.py` is executed after `__init__.py`, so `__init__.py` includes an `if` statement to prevent a crash.**
    - `library.py`: A dummy project module that can be imported via `import project.library` or `from project import library`. The convention is that package source code contains functions and classes and no scripts. This is to avoid executing scripting code (code outside of any function or class) on import.
    - `a_script.py`: A dummy script that shows how to import `project` and call the `hello` function in `project/library.py`. Once `project` is installed, you can run `a_scipt.py` anywhere on your computer. 