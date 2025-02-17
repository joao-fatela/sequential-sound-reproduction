"""
This program reproduces audio through a set of (N) speakers connected to the computer with the Portaudio driver. 
Speakers are defined by a list of audio reproduction IDs (in an associated config.ini file)
and a reproduction mode set as a string argument to the python program call.

Author: João Fatela 
Contact: joao.garrettfatela@unicampania.it
Dipartimento di Architettura e Disegno Industriale, Università degli Studi della Campania 'Luigi Vanvitelli'
24.11.2024
"""
import os
import configparser
import time
import soundfile as sf
import sounddevice as sd
import numpy as np
import sys
from colorama import init
from termcolor import cprint
from write_device_list import main as write_devices
import threading

init()

current_frame=0

def streamfunc(stream,duration):
    stream.start()
    time.sleep(duration)
    stream.stop()

def organise_devices(s,l=[]):
    out = s.split("(",1)[0]
    for k in out.split():
        l.append([int(k)])
        
    if out != s:
        
        in_tail = s.split("(",1)[1]
        
        inn = in_tail.split(")",1)[0]
        tail = in_tail.split(")",1)[1]
            
        ll = []
            
        for kk in inn.split():
            ll.append(int(kk))
            
        l.append(ll)
        
        if "(" in tail :
            l = organise_devices(tail,l=l)
        else:
            for k in tail.split():
                l.append([int(k)])
        
    return l

def inicio(ini_file='.\lib\config.ini', global_sr = 192000):
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
        
        data = organise_devices(dd)
                
        if data == []:
            cprint("You must first select desired reproduction devices.\nInput the corresponding numerical IDs.","light_red", attrs=["bold"])
            write_devices()

    

    for idlist in data:
        for devID in idlist:
            devdata = sd.query_devices(device=devID)
            if devdata['default_samplerate'] < global_sr:
                global_sr = devdata['default_samplerate']

    repro = dict({"dur": None, "wait": 0.5, "lib": "audio/"})
    
    if 'reproduction' in read_config:
        if ('audio_duration' in read_config['reproduction']):
            if (read_config['reproduction']['audio_duration'] != ''):
                repro["dur"]=float(read_config['reproduction']['audio_duration'])
        
        if ('wait_duration' in read_config['reproduction']): 
            if (read_config['reproduction']['wait_duration'] != ''):
                repro["wait"]=float(read_config['reproduction']['wait_duration'])
                
        if ('sampling_rate' in read_config['reproduction']): 
            if (read_config['reproduction']['sampling_rate'] != ''):
                global_sr=float(read_config['reproduction']['sampling_rate'])

        if ('audio_library' in read_config['reproduction']): 
            if (read_config['reproduction']['audio_library'] != ''):
                repro["lib"]=read_config['reproduction']['audio_library']
                
                if not (repro["lib"].endswith("/") or repro["lib"].endswith('\\')):
                    repro["lib"] += "\\"

    # 'reproduction mode' from call arguments
    mode = sys.argv[1] 
    mode = mode.lower()
    return mode,data,repro,global_sr

# BASIC OPERATION FUNCTIONS
def select_test_file(dir = 0, signal='test', folder = '.\\audio\\' ):
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
        
def play(IDlist: list, data: np.ndarray, dur=1, wait=1,global_sr=44100,t0=0):
    """
    Reproduce a single signal for a fixed duration and device.

    """
    global current_frame
    current_frame=0
    
    def callback(outdata, frames, time, status):
        global current_frame
        if status:
            print(status)
        chunksize = min(len(data) - current_frame, frames)
        outdata[:chunksize] = data[current_frame:current_frame + chunksize]
        if chunksize < frames:
            outdata[chunksize:] = 0
            raise sd.CallbackStop()
        current_frame += chunksize
    
    
    jobs = []
    streamlist = []
    for i,ID in enumerate(IDlist):
        streamlist.append(sd.OutputStream(samplerate=global_sr,
                                callback=callback,
                                device=ID,
                                latency='low',
                                blocksize=1024)
        )

        jobs.append(threading.Thread(target=streamfunc,args=(streamlist[i],dur)))
    
    
    while time.time()-t0 < wait:
        pass
    
    for job in jobs:
        job.start()
        
    for job in jobs:
        job.join()
    
    return time.time()
    

        
# SIMPLE AUDIO REPRODUCTION ROUTINES
def sequential_reproduction(buffer:np.ndarray, signal = 'test', duration = 1., wait=0.5, device_IDs=[], global_sr=44100,t0=0):
    """
    Play selected audio through list of devices sequentially.
    
    """
    cprint("\nBegin \'" + signal + "\' signal output", 'light_blue')
    
    for i,ID in enumerate(device_IDs):
        string = "    " + str(i+1)+". Device(s) [ "
        for id in ID:
            string += str(id) + " "
        
        cprint(string+"]", "light_cyan")            
        t0 = play(ID, buffer, duration, wait, global_sr=global_sr, t0=t0)
        
    return t0


def run_test(test_dur = 30, device_IDs=[], global_sr=44100, t0=0):
    """
    Run special reproduction test routine.
    
    For a given duration, the devices play audio which assigns them 
    with a unique audio identifier.
    
    """
    bufferlist = []
    for i in range(len(device_IDs)):
        audio = "audio/test/"+str(i+1)+".wav"
        data,_ = sf.read(audio)
        if len(data.shape)==1:
            data = data.reshape(data.shape[0],1)
        bufferlist.append(data)

    cprint("\nBegin test signal output", 'light_blue')
    
    timeout = time.time() + test_dur

    while time.time() < timeout:        
        
        for i,ID in enumerate(device_IDs):
            string = "    " + str(i+1)+". Device(s) [ "
            for id in ID:
                string += str(id) + " "
            
            cprint(string+"]", "light_cyan")            
            t0 = play(ID, data=bufferlist[i], global_sr=global_sr, t0=t0)
        print()
        
    return t0


def audio_selection(audio_folder=".\\audio\\",audiopath=[]):
    """
    Prints compatible files and dirs, and stores user selection.

    """
    cprint("\nSelect audio file by writing the corresponding index number from the list below.",attrs=["bold"])
    cprint("You may select multiple files to be played sequentially\n"+
            "by writing their indices in order separated by spaces.\n",'dark_grey')
    cprint("current directory: \' "+audio_folder+" \'",'yellow',attrs=["dark"])
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
    
    t0 = 0
    
    mode, device_IDs, repro, global_sr = inicio()

    if os.path.isdir("./audio/"):
        
        if str.lower(mode) == 'test' or str.lower(mode) == 't':
            if os.path.isdir("./audio/test/"):
                _,sr=sf.read("./audio/test/1.wav")
                if sr<global_sr:
                    global_sr = sr
                run_test(device_IDs=device_IDs, global_sr=global_sr)
            else:
                IsADirectoryError("./audio/test/ folder removed or missing.")
                
        elif str.lower(mode) == 'custom' or str.lower(mode) == 'c' or mode == '':
            audiopaths = audio_selection(audio_folder=repro['lib'])
            
            bufferlist = []
            srlist = []
            
            for audio in audiopaths:
                data,sr=sf.read(audio)
                if sr<global_sr:
                    global_sr = sr
                if len(data.shape)==1:
                    data = data.reshape(data.shape[0],1)
                srlist.append(sr)
                bufferlist.append(data)
            
            cprint("\nReproduction sampling rate defaulted to " + str(global_sr) + " Hz.", "yellow", attrs=["dark"])
            
            durationlist = []
            if repro["dur"] is None:
                for i in range(len(audiopaths)):
                    durationlist.append(bufferlist[i].shape[0]/srlist[i])
                cprint("Reproduction duration defaulted to audio file durations.", "yellow", attrs=["dark"])
            else:
                for i in range(len(audiopaths)):
                    durationlist.append(repro["dur"])
                cprint("Reproduction duration: "+str(repro["dur"])+"s.", "yellow", attrs=["dark"])
                
            cprint("Wait time: "+str(repro["wait"])+"s.", "yellow", attrs=["dark"])
            input("\nPress Enter begin reproduction sequence...")
            
            for i in range(len(audiopaths)):                    
                t0 = sequential_reproduction(buffer=bufferlist[i], signal=audiopaths[i], duration=durationlist[i], wait=repro["wait"], device_IDs=device_IDs, global_sr=global_sr, t0=t0)

    else:
        IsADirectoryError("./audio/ folder removed or missing.")