# INTRO
The code in this folder runs an audio reproduction routine over a set of output devices connected to the machine via Portaudio driver (http://www.portaudio.com/)
It is provided as a proto- software bundle to make its use more practical and intuitive.
The bundle includes:
- a sample audio library, 
- a configuration file,
- a python program for audio device listing and assignment, 
- a python program which runs the reproduction routine, and 
- a simplified batch file which allows basic users to run and control limited aspects of the routine.

This program is optimized for a specific audio reproduction routine on an N number of speakers.
In order to introduce changes in the routine or create a new one, the source code can be adapted (see section **.\dev\Nspeakers.py**). This, however, cannot be guaranteed to provide consistent results.

### Disclaimer
**This code is provided on an *as-is basis*.**  
It aims to provide a very basic solution to a very basic problem. By nature it has low resilience to user error, since its intended use is very limited.
Maintenance  is not guaranteed.

### Author
João Garrett Fatela
joao.garrettfatela@unicampania.it
_Dipartimento di Architettura e Disegno Industriale_
Università degli Studi della Campania *Luigi Vanvitelli*



# GETTING STARTED:
### Prerequisites:
- Machine with active [Portaudio](http://www.portaudio.com/) driver 
- Python (3.9<=version<=3.11) environment with 
	- [pyo](https://pypi.org/project/pyo/)
	- [configparser](https://pypi.org/project/configparser/) 
	- [termcolor](https://pypi.org/project/termcolor/libraries)

in case of absence of any of these libraries, an automated routine will attempt to install them before the program is run.

**Notice for basic users:**
! _Do not change folder and file structure or file names_ !
(except for adapting source code for own audio reproduction routine)

## Setup
1. Open the `lib` folder.
2. Open the configuration file `config.ini` in a text editor. In section `[paths]` you'll find the field `python_path=`. 
3. Replace `<your-python-path>` with the path pointing to the python executable (`python.exe`) of your environment. It should look something like `C:\user\path-to-folder\python.exe`. 
**Make sure that the dependencies are installed in the same environment, or that you're ok with the dependencies being automatically installed in the same location.**
4. Done!

## First test
1. Connect the desired output devices to the machine.
2. Increase the volume of the output devices as desired. No gains are applied to the signals in the audio folder.
3. Double click on `sequential_sound_reproduction.bat`.
4. Write `'y'` upon first prompt . (This step can be skipped on following reproductions, unless new devices are connected/disconnected).
5. Read list of devices and select desired audio devices.
6. Input ID numbers of desired audio output devices separated by spaces. You can input any order desired.
7. Run `'test'` routine (write `'test'`, `'t'`, or simply hit the return key)

The devices should output a text-to-speech (TTS) voice numbering them one at a time. 
Check that all desired devices are numbered in the order by which they were input in the batch prompt input by the user. 

**TIP**: If you wish to change the ordering of the devices, or repeat reproduction in a given device, this should be hard coded in the input sequence of devices. Remeber: this order can always be changed directly in the configuration file `lib/config.ini` for convenience.

### Troubleshooting
- **Command line outputs message 'Impossible to find defined path' or similar:** Make sure to replace the python_path variable to a path in your own machine. 
- **Command line outputs message 'ModuleNotFoundError: No module named 'module-name'':** Make sure that you have installed the required python modules, and check that the `python_path` variable in the configuration file points to the environment where the modules are installed. 
- **No audio output:** Re-run `sequential_sound_reproduction.bat`. Write `'y'` upon first prompt. Double check that the device IDs respect to *output devices*. Double check that the IDs respect to the *desired* devices. Double check that desired ID numbers are separated by *empty spaces*. Run the `'test'` reproduction mode again.
- **The reproduction order of the output devices is incorrect:** Make sure that the output devices are connected to the computer and outputting at the desired volume. Re-run `sequential_sound_reproduction.bat`. Write `'y'` upon first prompt. Input the device IDs in the order that you wish them to play the audio. Run the `'test'` reproduction mode again.


# FILE STRUCTURE AND DESCRIPTION
### .\sequential_sound_reproduction.bat
Batch file. It helps the user to operate the output device assignment and the audio reproduction routine.
Its operation is described below.

#### **First prompt:**  
- By inputting 'y', 'Y', or 'yes', the list of devices connected to Portaudio is output.
	- A second prompt asks the user for a list of desired output device IDs, separated by empty spaces. Any sequence of devices can be input.
	- The user input is stored in the configuration file.
	- **warning**: the device sampling rate and audio sampling rate must match.
- By hitting any other key, the connected device list is not shown and the ID assignment step is not performed
	- The output device IDs are loaded directly from the configuration file.
	
#### **Second prompt:** 
- By hitting the return key, 't' key, or typing 'test', the 'test' reproduction mode is activated.
	- A TTS voice numbers the different devices one at a time. (Up to 9 devices. This can be expanded for any N number of devices by expanding the audio library)
- By typing **'c'** or **'custom'**, a new menu shows all available audio signals in the library `audio/`. 
	- Any signals or subdirectories can be selected by choosing the correct signal index in the menu.
	- Multiple audios can be played in sequence by writing multiple indices separated by empty spaces.

**warning**: the audio file and device loop have a fixed hierarchy. Each audio loops through all devices in the sequence before the next audio is played. The audio duration and wait times is fixed, set in the configuration file. See below.

	 for each audio_file {
			for each output_device{
				play_audio( audio_file , output_device)
				# with constant audio duration and wait times
			}
	 }


### .\lib\ config.ini
Configuration file. Stores relevant information for the correct operation of the audio reproduction routine.
- `[paths]`
	- `python_path` -> the path to the desired python executable

- `[devices]`
	- `device_id` -> portaudio id of reproduction devices. Mind the sampling rate, since it must match the chosen signals!

- `[reproduction]`
	- `audio_duration` -> audio duration in seconds. Default 1s. Mind the duration of the input signals!
	- `wait_duration` -> wait time after each reproduction in second. Default 0s. Note that the real wait time may be slightly longer, due to the processing time of the routine. 
  


## .\dev\ 
"Developer" folder. Contains Python source code.

### .\dev\ list_devices.py
Lists devices connected to machine via Portaudio Driver. Prompts user for output device IDs. Stores device IDs on config.ini file.
Further details of its operation are commented in the source code.

### .\dev\ Nspeakers.py
Performs audio reproduction routines, given a **reproduction mode** or routine ID (as argument) and a **list of output device IDs** (in `.\lib\config.ini` under the field `device_id`).


## .\audio\
Audio file library for the `.\dev\Nspeakers.py` routines.
### .\audio\ WN.wav
5s white noise audio clip.
### .\audio\ PN.wav
5s pink noise audio clip.
### .\audio\ BN.wav
5s brown noise audio clip.
### .\audio\test\
Audio file library for the Nspeakers.py routines.
#### .\audio\test\ [number].wav
Audio clip of TTS voice enunciating the [number] in the filename. Relevant for numbering the output devices in the 'test' routine of `.\dev\Nspeakers.py`.


This library can be freely expanded by adding .mp3 or .wav files to the `.\audio\` folder. Creation of subfolders is also supported.