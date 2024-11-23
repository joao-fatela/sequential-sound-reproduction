"""
This program reproduces audio through a set of (N) speakers connected to the computer with the Portaudio driver. 
Speakers are defined by a list of audio reproduction IDs (in an associated config.ini file)
and a reproduction mode set as a string argument to the python program call.

Author: João Fatela 
Contact: joao.garrettfatela@unicampania.it
Dipartimento di Architettura e Disegno Industriale, Università degli Studi della Campania 'Luigi Vanvitelli'
22.11.2024
"""
import os
import configparser
import time
import soundfile as sf
import sounddevice as sd
import sys
from termcolor import cprint
from write_device_list import main as write_devices

global_sr = 192000.0  

def inicio(ini_file='.\lib\config.ini', global_sr = global_sr):
    """
    Initialize reproduction parameters after config.ini file.

    Reads the audio reproduction mode from the command line call,
    and the audio reproduction IDs from the defined configurations (.ini) file.

    """
    data = []
    while data == []:
        # initialize .ini interpreter and read the file
        read_config = configparser.ConfigParser(inline_comment_prefixes="#") 
        read_config.read(ini_file)

        # extract output device IDs from the .ini file
        dd = read_config['devices']['device_id'] # string
        
        
        for x in dd.split(): 
            if x.isnumeric():
                data.append(int(x))
                
        if data == []:
            cprint("You must first select desired reproduction devices.\nInput the corresponding numerical IDs.","light_red", attrs=["bold"])
            write_devices()

    for devID in data:
        devdata = sd.query_devices(device=devID)
        if devdata['default_samplerate'] < global_sr:
            global_sr = devdata['default_samplerate']

    repro = dict()
    if read_config['reproduction']['audio_duration'] == '':
        repro["dur"]=None
    else:
        repro["dur"]=float(read_config['reproduction']['audio_duration'])
        
    if read_config['reproduction']['wait_duration'] == '':
        repro["wait"]=.5
    else:
        repro["wait"]=float(read_config['reproduction']['wait_duration'])

    # 'reproduction mode' from call arguments
    mode = sys.argv[1] 
    mode = mode.lower()
    return mode,data,repro

# BASIC OPERATION FUNCTIONS
def select_audio_file(dir = 0, signal='test', folder = '.\\audio\\' ):
    """
    Select audio file from audio library in input directory.

    Default file name formatting in directory '<signal>.wav'
    special exception if signal == 'test'
    see examples in default audio directory. 

    """
    if signal == 'test':
        # selects audio file from '.\<folder>\test\' subfolder
        # audio is a number assigned to output device ID ([dir] ection)
        signal_str = 'test\\' + str(dir)
        file = folder + signal_str + '.wav'
    else:
        # search for file in '<folder>' directory
        file = signal

    return file
        
def play(ID: int, f, dur=1, wait=0.5,t0=0):
    """
    Reproduce a single signal for a fixed duration and device.

    """
    
    data, _ = sf.read(f)
    
    sd.default.samplerate = global_sr
    sd.default.device = ID
    
    while time.time()-t0 < wait:
        pass
    
    sd.play(data)
    time.sleep(dur)
    sd.stop()
    
    return time.time()
    

        
# SIMPLE AUDIO REPRODUCTION ROUTINES
def sequential_reproduction(signal = 'test', duration = 1., wait=0.5, device_IDs=[], t0=0):
    """
    Play selected audio through list of devices sequentially.
    
    """
    cprint("\nBegin \'" + signal + "\' signal output", 'light_blue')
    
    if duration is None:
        dat,sr = sf.read(signal)
        duration = dat.shape[0]/sr
    
    for i,ID in enumerate(device_IDs):
        cprint("    - Device "+ str(i+1), "light_cyan")
        f=select_audio_file(i+1,signal) 
        t0 = play(ID, f, duration, wait, t0=t0)


def run_test(test_dur = 30, device_IDs=[]):
    """
    Run special reproduction test routine.
    
    For a given duration, the devices play audio which assigns them 
    with a unique audio identifier.
    
    """
    timeout = time.time() + test_dur
 
    while time.time() < timeout:
        sequential_reproduction(device_IDs=device_IDs)


def audio_selection(audio_folder=".\\audio\\",audiopath=[]):
    """
    Prints compatible files and dirs, and stores user selection.

    """
    cprint("\nSelect audio file by writing the corresponding index number from the list below.",attrs=["bold"])
    cprint("You may select multiple files to be played sequentially\n"+
            "by writing their indices in order separated by spaces.\n",'dark_grey')
    cprint("current directory: \' "+audio_folder+"\\ \'",'yellow',attrs=["dark"])
    print(" ")
    # loop over subfolders
    counter = 0
    paths = []
    for entry in os.listdir(audio_folder):
        outstr = "[" + str(counter) + "] - " + entry
        outstr += (40-len(outstr))*" "
        if os.path.isdir(os.path.join(audio_folder,entry)):
            outstr += "(sub-directory)"
            counter += 1
            paths.append(os.path.join(audio_folder,entry))
            cprint(outstr,'yellow')
    
    for entry in os.listdir(audio_folder):
        outstr = "[" + str(counter) + "] - " + entry
        outstr += (40-len(outstr))*" "
        if os.path.isfile(os.path.join(audio_folder,entry)) and (entry.endswith(".wav") or entry.endswith(".mp3")):
            outstr += "(audio file)"
            counter += 1
            paths.append(os.path.join(audio_folder,entry))
            cprint(outstr,'green')
    
    for entry in os.listdir(audio_folder):
        if not os.path.isdir(os.path.join(audio_folder,entry)) and not (entry.endswith(".wav") or entry.endswith(".mp3")):
            outstr = "[*] - " + entry
            outstr += (40-len(outstr))*" "
            outstr += "[UNSUPPORTED FORMAT]"
            cprint(outstr,'red')
        

    inp = input("\nDesired input audio:")
    
    klist = [k for k in inp.split()]
    for k in klist:
        if k.isnumeric():
            k=int(k)
            if k >= len(paths):
                audiopath = audio_selection(audio_folder)
            else:
                if os.path.isfile( paths[k] ):
                    audiopath.append( paths[k] )
                elif os.path.isdir( paths[k] ):
                    audiopath = audio_selection(audio_folder=paths[k], audiopath=audiopath)
        else:
            audiopath = audio_selection(audio_folder)
            
    return audiopath
            
            
#######################################################################################################
# MAIN
#######################################################################################################
if __name__ == "__main__":
    
    mode, device_IDs, repro = inicio()

    if os.path.isdir("./audio/"):
        
        if str.lower(mode) == 'test' or str.lower(mode) == 't':
            if os.path.isdir("./audio/test/"):
                run_test(device_IDs=device_IDs)
            else:
                IsADirectoryError("./audio/test/ folder removed or missing.")
                
        elif str.lower(mode) == 'custom' or str.lower(mode) == 'c' or mode == '':
            audiopaths = audio_selection()
            for audio in audiopaths:
                _,sr=sf.read(audio)
                if sr<global_sr:
                    global_sr = sr
                    
            cprint("\nReproduction sampling rate defaulted to " + str(global_sr) + " Hz.", "yellow", attrs=["dark"])
            input("Press Enter begin reproduction sequence...")
            
            for audio in audiopaths:
                sequential_reproduction(signal=audio, duration=repro["dur"], wait=repro["wait"], device_IDs=device_IDs, t0=0)

    else:
        IsADirectoryError("./audio/ folder removed or missing.")