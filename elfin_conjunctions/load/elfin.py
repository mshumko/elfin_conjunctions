# The ELFIN data loaders

import pathlib
from datetime import datetime, date
import dateutil.parser

import cdflib
import numpy as np

from elfin_conjunctions import config


def load_state(sc_id, day):
    """
    Loads the ELFIN state (ephemeris) data.

    Parameters
    ----------
    sc_id: str
        The spacecraft id, either "A" or "B". Case insensitive.
    day: str or datetime.datetime
        A string specifying the 
    
    Returns
    -------
    np.array
        The epochs (time stamps) for that state file.
    cdflib.CDF
        The CDF object handle with the data not yet loaded. See the example on how
        to access variables managed by this object
    
    Example
    -------
    sc_id = 'A'
    day = '2020-01-01'
    state_times, state = load_state(sc_id, day)
    print(state.cdf_info())
    print(state.cdf_info()['zVariables'])
    print(state.varget('ela_att_gei').shape)
    print(state.varget('ela_att_gei'))
    """
    if isinstance(day, str):
        day = dateutil.parser.parse(day)
    # Find the file
    path = pathlib.Path(config['elfin_data_dir'], f'el{sc_id.lower()}', 'l1', 'state', 'defn')
    file_pattern = f'el{sc_id.lower()}_l1_state_defn_{day.strftime("%Y%m%d")}_v01.cdf'
    file_paths = list(path.rglob(file_pattern))
    assert len(file_paths) == 1, (f"{len(file_paths)} state files found at {path} "
        f"(and subdirectories) that match : {file_pattern}")
    # Load file
    state_obj = cdflib.CDF(file_paths[0])
    epoch = np.array(
        cdflib.cdfepoch.to_datetime(state_obj.varget(f'el{sc_id.lower()}_state_time'))
        )
    return epoch, state_obj

def epd(sc_id, day):
    raise NotImplementedError

if __name__ == '__main__':
    sc_id = 'A'
    day = '2020-01-01'
    state_times, state = load_state(sc_id, day)
    print(state.cdf_info())
    print(state.cdf_info()['zVariables'])
    print(state.varget('ela_att_gei').shape)
    print(state.varget('ela_att_gei'))