import pathlib

import pandas as pd

from elfin_conjunctions import config

sc_id = 'a'
# Merge the individual files from each THEMIS ASI into one file for ELFIN-A and one file
# for ELFIN-B
save_dir = pathlib.Path(config['project_dir'], 'data', 'conjunctions')
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