"""
Make movies of ELFIN-THEMIS ASI conjunctions.
"""
import pathlib
from datetime import datetime, date, timedelta

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import asilib
import asilib.asi

from elfin_conjunctions import config
import pad 

alt = 110  # km
box = (10, 10)  # km
asis = ['TREx RGB']  # other options: 'THEMIS-ASI', 'TREx RGB', 'TREx NIR', 'REGO'
save_progress=True
conjunction_dir = pathlib.Path(config['project_dir'], 'data')
progress_path = conjunction_dir / 'elfin_conjunctions_progress.txt'
conjunction_input_path = conjunction_dir / '2019_2023_elfin_themis_rego_trex_conjunctions.csv'
conjunction_output_path = conjunction_dir / f'2019_2023_elfin_{asis[0].lower().replace(" ", "_")}_conjunctions_data.csv'

# Load the conjunction list and identify the ASI array and ASI location_code.
conjunction_list = pd.read_csv(conjunction_input_path)
conjunction_list['Start Time (UTC)'] = pd.to_datetime(conjunction_list['Start Time (UTC)'])
conjunction_list['End Time (UTC)'] = pd.to_datetime(conjunction_list['End Time (UTC)'])
conjunction_list['asi_array_and_id'] = [row.split('and')[0] for row in conjunction_list['Conjunction Between'].to_numpy()]
conjunction_list['asi_array'] = [' '.join(row.split()[:-1]) for row in conjunction_list['asi_array_and_id'].to_numpy()]
conjunction_list['asi'] = [row.split()[-1] for row in conjunction_list['asi_array_and_id'].to_numpy()]

if save_progress and progress_path.exists():
    last_processed = pd.Timestamp(progress_path.read_text())
    conjunction_list = conjunction_list.loc[conjunction_list["Start Time (UTC)"] > last_processed, :]

idx = []
for i, row in enumerate(conjunction_list['asi_array'].to_numpy()):
    for _asi in asis:
        if _asi in row:
            idx.append(i)
conjunction_list = conjunction_list.iloc[idx, :]
if conjunction_output_path.exists():
    good_conjunctions = pd.read_csv(conjunction_output_path)
else:
    good_conjunctions = pd.DataFrame(columns=conjunction_list.columns)

n = conjunction_list.shape[0]
for row_i, (_, row) in enumerate(conjunction_list.iterrows()):
    print(f'\rProcessing {row["Start Time (UTC)"]} ({row_i}/{n}).')
    time_range = (
        row['Start Time (UTC)']-timedelta(minutes=1), 
        row['End Time (UTC)']+timedelta(minutes=1)
        )
    sc_id = row['Conjunction Between'].split('and')[-1][-1]
    try:
        pad_obj = pad.EPD_PAD(
            sc_id, time_range, start_pa=0, lc_exclusion_angle=0, min_counts=0, accumulate=1
            )
    except (FileNotFoundError, ValueError) as err:
        if (
            ('left keys must be sorted' in str(err)) or
            ('right keys must be sorted' in str(err)) or 
            (f'No level 2 ELFIN-{sc_id} electron EPD files found' in str(err)) or
            (f'No ELFIN-{sc_id} L2 data between' in str(err)) or
            (f'does not contain any hyper references containing the match' in str(err))
            ):
            if save_progress:
                progress_path.write_text(str(row["Start Time (UTC)"]))
            continue
        else:
            raise
    
    fig, ax = plt.subplots(4, gridspec_kw={'height_ratios':[3, 1, 1, 1]}, figsize=(6, 10))
    ax[0].set_title(
        f'ELFIN-{sc_id.upper()} {row["asi_array_and_id"]} Conjunction\n'
        f'{time_range[0]}-{time_range[1]}'
        )
    pad_obj.plot_omni(ax[2], colorbar=False)
    pad_obj.plot_blc_dlc_ratio(ax[3], colorbar=False)
    pad_obj.plot_position(ax[3])
    plt.subplots_adjust(bottom=0.127, right=0.927, top=0.948, hspace=0.133)
    # plt.show()

    if row['asi_array'] == 'TREx RGB':
        asi = asilib.asi.trex_rgb(row['asi'], time_range=time_range, alt=alt)
    elif row['asi_array'] == 'THEMIS-ASI':
        asi = asilib.asi.themis(row['asi'], time_range=time_range, alt=alt)
    elif row['asi_array'] == 'REGO':
        asi = asilib.asi.rego(row['asi'], time_range=time_range, alt=alt)
    else:
        raise NotImplementedError

    conjunction_obj = asilib.Conjunction(asi, pad_obj.transformed_state.drop(columns='mlat'))
    conjunction_obj.interp_sat()
    conjunction_obj.lla_footprint(alt)
    sat_azel, sat_azel_pixels = conjunction_obj.map_azel()
    nearest_pixel_intensity = conjunction_obj.intensity(box=None)
    
    gen = asi.animate_fisheye_gen(
        ax=ax[0], azel_contours=True, overwrite=True, cardinal_directions='news', color_bounds=[10, 105]
    )
    ax[1].plot(conjunction_obj.sat.index, nearest_pixel_intensity, color='k')

    for i, (image_time, image, _, im) in enumerate(gen):
        ax[0].xaxis.set_visible([])
        ax[0].plot(sat_azel_pixels[:, 0], sat_azel_pixels[:, 1], 'r:')
        ax[0].scatter(sat_azel_pixels[i, 0], sat_azel_pixels[i, 1], s=10, c='r')

        if 'guide_lines' in locals():
            for guide_line in guide_lines:
                guide_line.remove()
        guide_lines = []
        for ax_i in ax[1:]:
            guide_lines.append(ax_i.axvline(image_time, c='k', ls=':'))
            ax_i.set_xlim(*time_range)

        ax[1].set_ylabel(f'Mean ASI intensity\nnearest pixel')
        # plt.tight_layout()

    plt.close()

    good_conjunctions = pd.concat([good_conjunctions, row.to_frame().T], ignore_index=True)
    good_conjunctions.to_csv(conjunction_output_path, index=False)
    if save_progress:
        progress_path.write_text(str(row["Start Time (UTC)"]))
    
if progress_path.exists():
    progress_path.unlink()  # Clean up after the loop is complete.