"""
This program shows the user a list of audio devices connected to the local machine as detected by the driver Portaudio.
It then prompts the user to input a list of desired audiodevices


This program was designed with a specific procedure in mind and is part of a proto- software bundle.
It is not optimized for any uses outside its original purpose.

Author: João Fatela 
Contact: joao.garrettfatela@unicampania.it
Dipartimento di Architettura e Disegno Industriale, Università degli Studi della Campania 'Luigi Vanvitelli'
22.11.2024
"""
import configparser
from pyo import pa_list_devices
from termcolor import cprint

def main():
    CONFIG_FILENAME = 'config.ini'
    config_filepath='.\\lib\\'+CONFIG_FILENAME

    # listing devices connected through portaudio
    print("\n\n\n")
    pa_list_devices()

    #user prompt
    cprint("\n\n!READ THE LIST ABOVE CAREFULLY!",'yellow')
    print("You will be prompted for the ID# of the desired audio output devices.\n\n")
    IDs = input("Enter audio device IDs separated by spaces: ") # ! not resilient to misspellings/wrong input

    # reading the config file data
    read_config = configparser.ConfigParser()
    read_config.read(config_filepath)

    # temporarily storing data that may be deleted upon writing on config file
    python_path = read_config['paths']['python_path']


    repro = read_config['reproduction']

    # parser for writing on config file
    write_config = configparser.ConfigParser()

    write_config['paths'] = {}
    write_config['paths']['python_path'] = python_path.strip()
    write_config['devices'] = {}
    write_config['devices']['device_id'] = IDs.strip()
    write_config['reproduction']=repro

    # rewriting new device list and rewriting other config data
    with open(config_filepath, 'w') as configfile:
        write_config.write(configfile)

if __name__ == "__main__":
    main()