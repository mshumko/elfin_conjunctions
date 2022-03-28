# A library module.

import elfin_conjunctions

def hello():
    print('In the project.library.hello() function.')

    print(f'Saving data to {elfin_conjunctions.config["project_data_dir"]}!')

    return