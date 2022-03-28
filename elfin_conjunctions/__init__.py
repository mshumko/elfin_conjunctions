import warnings
import pathlib
import configparser

# Can add relative imports for your modules here. For example:
from elfin_conjunctions.library import hello
# will be avaliable to users as project.hello()

__version__ = '0.0.1'

# Load the configuration settings.
here = pathlib.Path(__file__).parent.resolve()
settings = configparser.ConfigParser()
settings.read(here / 'config.ini')

# Go here if config.ini exists (don't crash if the project is not yet configured.)
if 'Paths' in settings:  
    try:
        project_dir = settings['Paths']['project_dir']
        project_data_dir = settings['Paths']['project_data_dir']
    except KeyError as err:
        warnings.warn('The project package did not find the config.ini file. '
            'Did you run "python3 -m package config"?')

    config = {'project_dir': project_dir, 'project_data_dir': project_data_dir}