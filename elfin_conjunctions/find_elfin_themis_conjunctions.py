
from datetime import datetime
import pathlib

import pandas as pd
import numpy as np
import asilib

from elfin_conjunctions.elfin_footprint import Elfin_footprint
from elfin_conjunctions.load.elfin import load_epd
from elfin_conjunctions import config

themis_imagers = asilib.themis_info()
themis_url = 'https://data.phys.ucalgary.ca/sort_by_project/THEMIS/asi/stream0/'

# Prepare the data/conjunction directory.
save_dir = pathlib.Path(config['project_dir'], 'data', 'conjunctions')
if not save_dir.exists():
    save_dir.mkdir(parents=True)
    print(f'Made {save_dir} directory.')
else:
    # Remove the csv files in the conjunction folder to avoid duplicate rows.
    for file in save_dir.glob('*.csv'):
        if file.is_file():
            file.unlink()
    print('Cleaned up the conjunction folder.')
        
for sc_id in ['a', 'b']:
    days = pd.date_range(start='2018-01-01', end=datetime.now(), freq='D')
    for day in days:
        # Look for an EPD file and skip the day if none exists.
        try:
            epd_time, epd = load_epd(sc_id, day)
        except (FileNotFoundError, ValueError) as err:
            if 'EPD files found at' in str(err):
                continue
            if 'No records found for variable' in str(err):
                continue
            else:
                raise
        
        print(f'Processing ELFIN-{sc_id.upper()} data on {day.date()}')
        # Calculate the ELFIN footprints in the LLA coordinates.
        footprint = Elfin_footprint(sc_id, day)
        footprint.map_footprint()

        # What ASI was below ELFIN?
        for location_code in themis_imagers['location_code']:
            try:
                imager = asilib.themis(location_code, time=day, load_images=False)
            except Exception as err:
                if 'Invalid SIGNATURE' in str(err):  # Poorly formatted save file.
                    continue
            c2 = asilib.Conjunction(imager, footprint.time, footprint.lla)
            conjunction_df = c2.find()
            conjunction_df['epd_data'] = False
            conjunction_df['asi_data'] = False

            for index, row in conjunction_df.iterrows():
                # Was there EPD data during this conjunction?
                idx = np.where(
                    (epd_time > row['start']) &
                    (epd_time < row['end'])
                )[0]
                if len(idx):
                    conjunction_df.loc[index, 'epd_data'] = True

                # Was there ASI data during this conjunction?
                download = asilib.io.download.Downloader(themis_url)
                url_subdirectories = [
                    str(day.year), 
                    str(day.month).zfill(2), 
                    str(day.day).zfill(2), 
                    f'{location_code.lower()}*', 
                    f'ut{str(row["start"].hour).zfill(2)}', 
                    ]
                filename = row["start"].strftime(f'%Y%m%d_%H%M_{location_code.lower()}*.pgm.gz')
                try:
                    asi_url = download.find_url(subdirectories=url_subdirectories, filename=filename)
                except FileNotFoundError as err:
                    if 'does not contain any hyper references containing' in str(err):
                        continue
                if len(asi_url):
                    conjunction_df.loc[index, 'asi_data'] = True
                
                # Save to file.
                save_name = f'elfin_{sc_id.lower()}_themis_{location_code.lower()}_conjunctions.csv'
                save_path = save_dir / save_name

                if save_path.exists():
                    conjunction_df.to_csv(save_path, mode='a', header=False, index=False)
                else:
                    conjunction_df.to_csv(save_path, index=False)


    # Finally merge the conjunction files with ELFIN-X into one.
    file_paths = save_dir.rglob(f'elfin_{sc_id.lower()}_themis_*_conjunctions.csv')
    merged_conjunctions = pd.DataFrame(columns=['start', 'end', 'epd_data', 'asi_data', 'asi'])

    for file_path in file_paths:
        df = pd.read_csv(file_path)
        df['asi'] = file_path.name.split('_')[3]

        merged_conjunctions = pd.concat([merged_conjunctions, df])

    # Sort the conjunctions by time.
    merged_conjunctions['start'] = pd.to_datetime(merged_conjunctions['start'])
    merged_conjunctions = merged_conjunctions.sort_values('start')
    merged_conjunctions.to_csv(save_dir.parents[0] / f'elfin_{sc_id.lower()}_themis_asi_conjunctions.csv', 
        index=False)

    filtered_conjunctions = merged_conjunctions[
        (merged_conjunctions['asi_data'] == True) & (merged_conjunctions['epd_data'] == True)
        ]
    filtered_conjunctions.to_csv(save_dir.parents[0] / f'elfin_{sc_id.lower()}_themis_asi_conjunctions_filtered.csv', 
        index=False)