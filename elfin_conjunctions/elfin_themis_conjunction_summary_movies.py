"""
Make movies of ELFIN-THEMIS ASI conjunctions.
"""
import pathlib
from datetime import datetime, date, timedelta

import pandas as pd
import numpy as np
import asilib
import matplotlib.pyplot as plt

from elfin_conjunctions import config, elfin_footprint
import pad 

alt = 110  # km
box = (10, 10)  # km
# options: 'THEMIS-ASI', 'TREx RGB', 'TREx NIR', 'REGO'
asis = ['THEMIS-ASI']

conjunction_dir = pathlib.Path(config['project_dir'], 'data')
conjunction_path = conjunction_dir / '2019_2023_elfin_themis_rego_trex_conjunctions.csv'

conjunction_list = pd.read_csv(conjunction_path)
conjunction_list['Start Time (UTC)'] = pd.to_datetime(conjunction_list['Start Time (UTC)'])
conjunction_list['End Time (UTC)'] = pd.to_datetime(conjunction_list['End Time (UTC)'])

conjunction_list['asi_array'] = [row.split()[0] for row in conjunction_list['Conjunction Between'].to_numpy()]

for _, row in conjunction_list.iterrows():
    time_range = (
        row['Start Time (UTC)']-timedelta(minutes=3), 
        row['End Time (UTC)']+timedelta(minutes=3)
        )
    sc_id = row['Conjunction Between'].split('and')[-1][-1]
    pad_obj = pad.EPD_PAD(sc_id, time_range, start_pa=90)
    
    # fig, ax = plt.subplots(7, 1, sharex=True, figsize=(7, 9))
    # ax[0].set_title(
    #     f'ELFIN-{sc_id.upper()} | {time_range[0]}-{time_range[1]}'
    #     f'\nElectron Pitch Angle Distributions'
    #     )
    # pad_obj.plot_omni(ax[0])
    # pad_obj.plot_pad_scatter(ax[1])
    # pad_obj.plot_pad_spectrogram(ax[2])
    # pad_obj.plot_pad_spectrogram(ax[3], energy=520)
    # pad_obj.plot_pad_spectrogram(ax[4], energy=1081)
    # pad_obj.plot_pad_spectrogram(ax[5], energy=2121)
    # pad_obj.plot_blc_dlc_ratio(ax[-1])
    # pad_obj.plot_position(ax[-1])
    # plt.subplots_adjust(bottom=0.127, right=0.927, top=0.948, hspace=0.133)
    # plt.show()
    print(f'Processing {row["start"]}')

    # Create an Imager object
    img = asilib.themis(row['asi'], time_range=time_range, alt=alt)
    # Load, filter, and map the ELFIN footprint
    footprint = elfin_footprint.Elfin_footprint(sc_id, row['start'])
    footprint_idx = np.where(
        (footprint.time >= time_range[0]) &
        (footprint.time <= time_range[1])
    )[0]
    footprint.time = footprint.time[footprint_idx]
    footprint.lla = footprint.lla[footprint_idx, :]
    footprint.map_footprint(alt=alt)

    c = asilib.Conjunction(img, footprint.time, footprint.lla)
    c.resample()
    sat_azel, asi_pixels = c.map_lla_azel()
    equal_area_gen = c.equal_area_gen(box=box)
    mask_gen = c.equal_area_gen(box=(10, 10))

    mean_asi_intensity = -np.ones(c.sat.shape[0])
    for i, ((_, image), mask) in enumerate(zip(img, equal_area_gen)):
        mean_asi_intensity[i] = np.nanmean(image*mask)
    
    fig, ax = plt.subplots(3, gridspec_kw={'height_ratios':[3, 1, 1]}, figsize=(6, 10))
    ax[1].sharex(ax[2])  # Connect the two subplots to remove the extra time axis.
    epd_idx = np.where(
        (epd_time >= time_range[0]) &
        (epd_time <= time_range[1])
    )[0]
    assert len(epd_idx), f'No EPD data found in {time_range=}'
    epd_time_flt = epd_time[epd_idx]
    epd_counts = epd.varget(f'el{sc_id.lower()}_pef')[epd_idx, :]

    img_gen = img.animate_fisheye_gen(ax=ax[0], overwrite=True)
    mask_gen = c.equal_area_gen(box=box)

    for i, ((image_time, image, _, im), mask) in enumerate(zip(img_gen, mask_gen)):
        ax[1].clear()
        ax[2].clear()
        ax[1].xaxis.set_visible([])

        ax[0].plot(asi_pixels[:, 0], asi_pixels[:, 1], 'r:')
        ax[0].scatter(asi_pixels[i, 0], asi_pixels[i, 1], s=10, c='r')

        # Plot the equal area
        mask[np.isnan(mask)] = 0  # To play nice with plt.contour()
        ax[0].contour(mask, levels=[0.99], colors=['yellow'])

        ax[1].plot(c.sat.index, mean_asi_intensity, color='k')
        for ch in range(epd_counts.shape[1]):
            ax[2].plot(epd_time_flt, epd_counts[:, ch], color=plt.cm.hsv(ch/16))
        ax[1].axvline(image_time, c='k')
        ax[2].axvline(image_time, c='k')
        ax[1].set_ylabel(f'Mean ASI intensity\n{box} km area')
        ax[2].set_ylabel(f'ELFIN PEF')
        ax[2].set_xlabel(f'Time')
        ax[2].set_xlim(*time_range)
        ax[2].set_yscale('log')
        plt.suptitle(
            f"Conjunction between ELFIN-{sc_id.upper()} & THEMIS-{row['asi'].upper()}\n"
            f'{img._data["time_range"][0].strftime("%Y-%m-%d")} '
            f'{img._data["time_range"][0].strftime("%T")} - '
            f'{img._data["time_range"][1].strftime("%T")}\n'
            f'{alt} km footprint'
            )
        plt.tight_layout()

    plt.close()