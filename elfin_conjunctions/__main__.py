import sys
import pathlib
import configparser

import elfin_conjunctions

# Run the configuration script with
# python3 -m elfin_asi_conjunctions [init, initialize, config, or configure]

here = pathlib.Path(__file__).parent.resolve()

if (len(sys.argv) > 1) and (sys.argv[1] in ['init', 'initialize', 'config', 'configure']):
    print('Running the configuration script.')
    s = f'Where is your ELFIN data directory?'
    elfin_data_dir = input(s)

    if elfin_data_dir != '':
        if not pathlib.Path(elfin_data_dir).exists():
            pathlib.Path(elfin_data_dir).mkdir(parents=True)
            print(f'Made ELFIN data directory at {pathlib.Path(elfin_data_dir)}.')
        else:
            print(f'The ELFIN data directory at {pathlib.Path(elfin_data_dir)} already exists.')
    else:
        raise ValueError('No ELFIN directory was provided.')

    # Create a configparser object and add the user configuration.
    config = configparser.ConfigParser()
    config['Paths'] = {
        'project_dir':here,
        'elfin_data_dir': elfin_data_dir
        }

    with open(here / 'config.ini', 'w') as f:
        config.write(f)

else:
    print(
        'This is a configuration script to set up config.ini file. The config '
        'file contains the ELFIN data directory and the directory of the source '
        'code. To configure this package, run python3 -m elfin_asi_conjunctions config.'
    )