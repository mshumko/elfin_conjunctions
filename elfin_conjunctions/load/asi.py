import pathlib

import pandas as pd

from elfin_conjunctions import config

def load_locations(array=None, location_code=None):
    """
    Loads the asi_locations.csv file.

    Parameters
    ----------
    array: str
        Optionally filter by the ASI array.
    location_code: str
        Optionally filter by the ASI location_code.
    """
    path = pathlib.Path(config['project_dir']) / 'data' / 'asi_locations.csv'
    locations = pd.read_csv(path)
    if array is not None:
        locations = locations[locations['array'] == array.upper()]
    if location_code is not None:
        locations = locations[locations['location_code'] == location_code.upper()]
    return locations

if __name__ == '__main__':
    all_asi = load_locations()
    print('ALL:\n', all_asi)
    themis_asi = load_locations(array='themis')
    print('THEMIS:\n', themis_asi)
    rego_asi = load_locations(array='rego')
    print('REGO:\n', rego_asi)