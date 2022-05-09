
from datetime import datetime

import pandas as pd
import asilib

from elfin_conjunctions.elfin_footprint import Elfin_footprint
from elfin_conjunctions.load.elfin import _find_epd

themis_imagers = asilib.themis_info()
themis_url = 'https://data.phys.ucalgary.ca/sort_by_project/THEMIS/asi/stream0/'

for sc_id in ['a', 'b']:
    for day in pd.date_range(start='2018-01-01', end=datetime.now(), freq='D'):
        # Look for an EPD file and skip the day if none exists.
        try:
            _find_epd(sc_id, day)
        except FileNotFoundError as err:
            if 'EPD files found at' in str(err):
                continue
            else:
                raise

        # Calculate the ELFIN footprints in the LLA coordinates.
        footprint = Elfin_footprint(sc_id, day)
        footprint.map_footprint()

        # Pass off the footprints to asilib
        for location_code in themis_imagers['location_code']:
            imager = asilib.themis(location_code, time=day, load_images=False)
            c2 = asilib.Conjunction(imager, footprint.time, footprint.lla)
            conjunction_df = c2.find()
            pass
            
            # Check that ASI data was avaliable then.

            # Save the conjunction list to elfin_conjunctions/data.

        # download = asilib.io.download.Downloader(themis_url)
        #     url_subdirectories = [
        #         str(day.year), 
        #         str(day.month).zfill(2), 
        #         str(day.day).zfill(2), 
        #         f'{location_code.lower()}*', 
        #         f'ut{str(time.hour).zfill(2)}', 
        #         ]
        # filename = time.strftime(f'%Y%m%d_%H%M_{location_code.lower()}*.pgm.gz')
        # # file_paths will only contain one path.
        # file_paths = [_manager.find_file(filename, subdirectories=url_subdirectories, overwrite=overwrite)]
        #     download.find_url(subdirectories=subdirectories, filename=filename)