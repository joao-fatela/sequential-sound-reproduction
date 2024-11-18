# Nspeakers.py
# 
# This program reproduces audio through a set of (N) speakers connected to the computer with the Portaudio driver. 
# Speakers are defined by a list of audio reproduction IDs (in an associated .ini file, or defined by user in a constant)
# and a reproduction mode set as a string argument to the python program call.
#
# Dependencies on the pyo (https://pypi.org/project/pyo/) and configparser (https://pypi.org/project/configparser/) libraries
# NOTE: dependency on pyo requires python<=3.10
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
# 18.11.2024
def import_or_install(package):
    try:
        __import__(package)
    except ImportError:
        pip.main(['install', package]) 


import pip
import_or_install('pyo')
import_or_install('termcolor')
import time
from pyo import *
import sys
from termcolor import cprint

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
MODE, DEVICE_IDS = inicio() 


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
        file = signal

    return file
        
def play(ID=0,signal='test',dur=1, wait=0):

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
            
        # no reproduction for <wait seconds>
        time.sleep(wait)
            
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
        
        # no reproduction for <wait seconds>
        time.sleep(wait)


# SIMPLE AUDIO REPRODUCTION ROUTINES
def sequential_reproduction(signal = 'test', duration = 1, wait=0):

    # plays selected audio through all devices individually 
    # in a sequential fashion 
    # ! <duration> in seconds respects to each individual reproduction

    for ID in DEVICE_IDS:
        play(ID, signal, duration, wait)

def run_test(test_dur = 30):

    # test reproduction
    # good for identifying speakers 
    # and placing them spatially / correcting order of ID list

    # plays output device ID on each device sequentially for 30 seconds

    timeout = time.time() + test_dur
 
    while time.time() < timeout:
        sequential_reproduction()


def audio_selection(audio_folder=".\\audio\\",audiopath=[]):

    cprint("current directory: \' "+audio_folder+"\\ \'",'yellow')
    print("Select audio file by writing the corresponding index number from the list below.\n" +
            "You may select multiple files to be played sequentially\n"+
            "by writing their indices in order separated by spaces.\n\n")

    # loop over subfolders
    for i,entry in enumerate(os.listdir(audio_folder)):
        outstr = "[" + str(i) + "] - " + entry
        outstr += (50-len(outstr))*" "
        if os.path.isdir(os.path.join(audio_folder,entry)):
            outstr += "(sub-directory)"
        elif os.path.isfile(os.path.join(audio_folder,entry)) and (entry.endswith(".wav") or entry.endswith(".mp3")):
            outstr += "(audio file)"
        else:
            outstr += "[UNSUPPORTED FORMAT]"
            
        print(outstr)
        
    inp = input("\n\nDesired input audio:")
    
    klist = [int(k) for k in inp.split()]
    for k in klist:
        if k >= len(os.listdir(audio_folder)):
            audiopath = audio_selection(audio_folder)
        else:
            if os.path.isfile(os.path.join(audio_folder, os.listdir(audio_folder)[k])):
                audiopath.append( os.path.join(audio_folder, os.listdir(audio_folder)[k]))
            elif os.path.isdir(os.path.join(audio_folder, os.listdir(audio_folder)[k])):
                audiopath = audio_selection(audio_folder=os.path.join(audio_folder, os.listdir(audio_folder)[k]), audiopath=audiopath)
            
    return audiopath
            
        
    
#######################################################################################################
# MAIN
#######################################################################################################
if __name__ == "__main__":
    if os.path.isdir("./audio/"):
        if str.lower(MODE) == 'test' or str.lower(MODE) == 't' or str.lower(MODE) == '':
            if os.path.isdir("./audio/test/"):
                run_test()
            else:
                IsADirectoryError("./audio/test/ folder removed or missing.")
                
        elif str.lower(MODE) == 'custom' or str.lower(MODE) == 'c':
            audiopaths = audio_selection()
            for audio in audiopaths:
                sequential_reproduction()
            
    else:
        IsADirectoryError("./audio/ folder removed or missing.")