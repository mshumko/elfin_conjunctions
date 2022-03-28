# A script showing how this package is imported into a script.

import elfin_conjunctions

# Can also put this in __init__.py so it is imported as package.hello
from elfin_conjunctions.library import hello

print('In a_script.py!')
print(f'Configuration paths: {elfin_conjunctions.config}')

hello()