# Nspeakers.py
# 
# This program reproduces audio through a set of (N) speakers connected to the computer with the Portaudio driver. 
# Speakers are defined by a list of audio reproduction IDs (in an associated .ini file, or defined by user in a constant)
# and a reproduction mode set as a string argument to the python program call.
#
# Dependencies on the pyo (https://pypi.org/project/pyo/) and configparser (https://pypi.org/project/configparser/) libraries
#
# This program was designed with a specific procedure in mind. Hence, it is not optimized for uses outside basic reproduction modes.
# It can, however, be changed to suit any of the user's needs: basic functions for simple reproduction routines are provided
# and can be combined for a specific use. User-input audio sources are also supported.
#
# This program is not resilient to user errors and should be taken on an as-is-basis.
# Maintenance is not guaranteed.
#
# Author: João Fatela 
# Contact: joao.garrettfatela@unicampania.it
# Dipartimento di Architettura e Disegno Industriale, Università degli Studi della Campania 'Luigi Vanvitelli'
# 4.4.2023

import time
from pyo import *
import sys

# INITIALIZATION via config file
def inicio(ini_file='.\lib\config.ini'):

    # initializes the sound distribution main functions
    # It reads the audio reproduction mode from the command line call,
    # and the audio reproduction IDs from the defined configurations (.ini) file
    
    import configparser
    
    # initialize .ini interpreter and read the file
    read_config = configparser.ConfigParser() 
    read_config.read(ini_file)

    # extract output device IDs from the .ini file
    dd = read_config['devices']['device_id'] # string
    data = [int(x) for x in dd.split()] # list of integers

    # 'reproduction mode' from call arguments
    mode = sys.argv[1] 
    mode = mode.lower()
    return mode,data

##########################################################################################################################################
#      CONSTANTS
# ! default (config file)
MODE, DEVICE_IDS = inicio() 

# ! debug (user input)
# MODE = <reproduction mode> # 'test', 'w', 'p', 'b', <custom>
# DEVICE_IDS = <list of device IDs> # integer list of device IDs as detected by Portaudio driver

##########################################################################################################################################

# BASIC OPERATION FUNCTIONS
def select_audio_file(dir = 0, signal='test', folder = '.\\audio\\' ):
    
    # selects audio file from audio library in <folder> directory
    # default file name formatting in directory '<signal>.wav'
    # special exception if signal == 'test'
    # see examples in default directory .\audio\

    if signal == 'test':
        # selects audio file from '.\<folder>\test\' subfolder
        # audio is a number assigned to output device ID ([dir] ection)
        signal_str = 'test\\' + str(dir)
        file = folder + signal_str + '.wav'
    else:
        # search for file in '<folder>' directory
        signal_str = signal
        file = folder + signal_str + '.wav'

    return file
        
def play(ID=0,signal='test',dur=1):

    # reproduces a single signal given <signal> flag 
    # for duration of <dur> seconds
    # on output device(s) with Portaudio ID number <ID> 
    # ID can be an integer (single device) [or a list of integers (multiple devices at same time) NOT IMPLEMENTED]

    server_verbosity = 1

    # initialize list of servers
    S = []

    if type(ID)==list:
        # multiple output devices
        for id in ID:

            # in case of 'test' output, <dir> is relevant for audio reproduction 
            dir = DEVICE_IDS.index(id)+1

            # initialize server
            s = Server(duplex=0,buffersize=256)
            s.setVerbosity(server_verbosity)
            s.setOutputDevice(id)
            s.boot()
            f=select_audio_file(dir,signal) 

            # output channel definition
            num_channels = pa_get_output_max_channels(ID)
            Outp=[]
            for i in range(0,num_channels):
                Outp.append( SfPlayer(f, speed=1,loop=True, mul=.8).out(i))
            s.start()   # !reproduction of multiple sources not perfectly synchronized!

            # append server to list of servers
            S.append(s)

        # hold reproduction for <dur seconds>
        time.sleep(dur)

        # stop audio reproduction
        for i in range(0,len(ID)-1):
            S[i].stop()
            
    else:
        
        # equivalent to previous for single output device

        dir = DEVICE_IDS.index(ID)+1

        s = Server(duplex=0,buffersize=256)
        s.setVerbosity(server_verbosity)
        s.setOutputDevice(ID)
        s.boot()
        f=select_audio_file(dir,signal) 

        num_channels = pa_get_output_max_channels(ID)
        Outp=[]
        for i in range(0,num_channels):
            Outp.append( SfPlayer(f, speed=1,loop=True, mul=.8).out(i))
       
        s.start()   
        print("Output in device ", dir )    

        time.sleep(dur)

        s.stop()


# SIMPLE AUDIO REPRODUCTION ROUTINES
def sequential_reproduction(signal = 'test', duration = 1):

    # plays selected audio through all devices individually 
    # in a sequential fashion 
    # ! <duration> in seconds respects to each individual reproduction

    for ID in DEVICE_IDS:
        play(ID, signal, duration)

def play_all_devices(signal='BN', duration = 1):

    # NOT YET IMPLEMENTED: Portaudio parallel reproduction likely not possible
    # future option: set ASIO4ALL as output device and connect multiple outputs to the ASIO driver


    # plays selected audio on all output devices at the same time 

    play(DEVICE_IDS, signal, duration)

def run_test(test_dur = 30):

    # test reproduction
    # good for identifying speakers 
    # and placing them spatially / correcting order of ID list

    # plays output device ID on each device sequentially for 30 seconds

    timeout = time.time() + test_dur
 
    while time.time() < timeout:
        sequential_reproduction()




#######################################################################################################
# MAIN
#######################################################################################################
if MODE == 'test' or MODE == 't':
    run_test()
elif MODE == 'white' or MODE == 'w':
    print("\nSequential reproduction -- white noise")
    sequential_reproduction('WN',3)
elif MODE == 'pink' or MODE == 'p':
    print("\nSequential reproduction -- pink noise")
    sequential_reproduction('PN',3)
elif MODE == 'brown' or MODE == 'b':
    print("\nSequential reproduction -- brown noise")
    sequential_reproduction('BN',3)
elif MODE == 'all' or MODE == 'a':
    print("\nSequential reproduction -- white noise")
    sequential_reproduction('WN',3)
    print("\nSequential reproduction -- pink noise")
    sequential_reproduction('PN',3)
    print("\nSequential reproduction -- brown noise")
    sequential_reproduction('BN',3)

