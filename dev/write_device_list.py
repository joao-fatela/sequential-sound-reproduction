# write_device_list.py
# 
# This program shows the user a list of audio devices connected to the local machine as detected by the driver Portaudio.
# It then prompts the user to input a list of desired audiodevices
#
# Dependencies on the pyo (https://pypi.org/project/pyo/) and configparser (https://pypi.org/project/configparser/) libraries
#
# This program was designed with a specific procedure in mind and is part of a proto- software bundle.
# It is not optimized for any uses outside its original purpose.
#
# This program is not resilient to user errors (such as different config file structures)
# and should be taken on an as-is-basis / corrected to suit the user's needs.
# Maintenance is not guaranteed.
#
# Author: João Fatela 
# Contact: joao.garrettfatela@unicampania.it
# Dipartimento di Architettura e Disegno Industriale, Università degli Studi della Campania 'Luigi Vanvitelli'
# 18.11.2024
def import_or_install(package):
    try:
        __import__(package)
    except ImportError:
        pip.main(['install', package]) 



import pip
import_or_install('pyo')
import_or_install('configparser')

from pyo import *


CONFIG_FILENAME = 'config.ini'
config_filepath='.\\lib\\'+CONFIG_FILENAME

# listing devices connected through portaudio
pa_list_devices()

#user prompt
print("\n\n!READ THE LIST ABOVE CAREFULLY!")
print("You will be prompted for the ID# of the desired audio output devices.\n\n")
IDs = input("Enter audio device IDs separated by spaces: ") # ! not resilient to misspellings/wrong input

# reading the config file data
read_config = configparser.ConfigParser()
read_config.read(config_filepath)

# temporarily storing data that may be deleted upon writing on config file
python_path = read_config['paths']['python_path']

# parser for writing on config file
write_config = configparser.ConfigParser()

write_config['paths'] = {}
write_config['paths']['python_path'] = python_path.strip()
write_config['devices'] = {}
write_config['devices']['device_id'] = IDs.strip()

# rewriting new device list and rewriting other config data
with open(config_filepath, 'w') as configfile:
  write_config.write(configfile)