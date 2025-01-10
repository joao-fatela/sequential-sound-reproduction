# INTRO
The code in this repository runs an audio reproduction routine over a set of output devices connected to the machine via Portaudio driver (http://www.portaudio.com/)

The package includes:
- a sample audio library, 
- a configuration file,
- a python program for audio device listing and assignment, 
- a python program which runs the reproduction routine, and 
- a simplified batch file which allows basic users to run and control limited aspects of the routine.

This program is optimized for a specific audio reproduction routine on a given number of speakers.
In order to introduce changes in the routine or create a new one, the source code can be adapted (see section **.\dev\Nspeakers.py**). This, however, cannot be guaranteed to provide consistent results.

### Disclaimer
**This code is provided on an *as-is basis*.**  
It aims to provide a very basic solution to a very basic problem. By nature it has low resilience to user error, since its intended use is very limited.
Maintenance  is not guaranteed.

### Author
João Garrett Fatela | joao.garrettfatela@unicampania.it

_Dipartimento di Architettura e Disegno Industriale_ | Università degli Studi della Campania *Luigi Vanvitelli*



# GETTING STARTED:
### Requirements:
- Machine with active [Portaudio](http://www.portaudio.com/) driver 
- Python (**version <ins>3.10 or 3.11</ins>**) environment with 
	- [numpy](https://pypi.org/project/numpy/)
	- [soundfile](https://pypi.org/project/soundfile/)
	- [sounddevice](https://pypi.org/project/sounddevice/)
	- [configparser](https://pypi.org/project/configparser/) 
	- [termcolor](https://pypi.org/project/termcolor/libraries)

Generally, an automated routine will attempt to install them before the program is run.
If you wish to run the program with a different python distribution, you can install these dependencies manually and remove lines 23-26 of `sequential_sound_reproduction.bat`.

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
     - **BETA**: you can play the audio in more than one device simultaneously by writing the desired device IDs between parentheses. **The reproductions are not perfectly synchronous.**
8. Run `'test'` routine (write `'test'`, `'t'`, or simply hit the return key)

The devices should output a text-to-speech (TTS) voice numbering them one at a time. 
Check that all desired devices are numbered in the order defined by the user. 

**TIP**: If you wish to change the ordering of the devices, or repeat reproduction in a given device, this should be hard coded in the input sequence of devices. This order can always be changed directly in the configuration file `lib/config.ini` for convenience.

### Troubleshooting
 
- **No audio output:** Re-run `sequential_sound_reproduction.bat`. Write `'y'` upon first prompt. Double check that the device IDs respect to *output devices*. Double check that the IDs respect to the *desired* devices. Double check that desired ID numbers are separated by *empty spaces*. Run the `'test'` reproduction mode again.
- **The reproduction order of the output devices is incorrect:** Make sure that the output devices are connected to the computer and outputting at the desired volume. Re-run `sequential_sound_reproduction.bat`. Write `'y'` upon first prompt. Input the device IDs in the order that you wish them to play the audio. Run the `'test'` reproduction mode again.
- **incompatible sampling rate error message:** The program automatically defaults the audio reproduction to the lowest sampling rate necessary for artifact-less reproduction. This is based on the sampling rate of the selected audios, as well as available sampling rate on the selected devices. However, certain audio APIs may still cause issues. You can try selecting a different API for your desired devices in the device selection menu, or defining a lower sampling rate by hand in the configuration file. It's recommended to use the same audio API for all of your devices.

# Program structure
## User interface
### sequential_sound_reproduction.bat
Batch file. It helps the user to operate the output device assignment and the audio reproduction routine.
Its operation is described below.

#### **First prompt:**  
- By inputting 'y', 'Y', or 'yes', the list of devices connected to Portaudio is output.
	- A second prompt asks the user for a list of desired output device IDs, separated by empty spaces. Any sequence of devices can be input, separated by spaces. 
	
	**BETA**: you can play the audio in more than one device simultaneously by writing the desired device IDs between parentheses. **The reproductions are not perfectly synchronous.**
	- The user input is stored in the configuration file.
	
- By hitting any other key, the connected device list is not shown and the ID assignment step is not performed
	- The output device IDs are loaded directly from the configuration file (which may be empty).
	
#### **Second prompt:** 
- By hitting the return key, 't' key, or typing 'test', the 'test' reproduction mode is activated.
	- A TTS voice numbers the different devices one at a time. (Up to 9 devices. This can be expanded for any N number of devices by expanding the audio library)
- By typing **'c'** or **'custom'**, a new menu shows all available audio signals in the library `audio/`. 
	- Any signals or subdirectories can be selected by choosing the correct signal index in the menu.
	- Multiple audios can be played in sequence by writing multiple indices separated by empty spaces.

**warning**: the audio file and device loop have a fixed hierarchy. Each audio loops through all devices in the sequence before the next audio is played. The audio duration and wait times is fixed, set in the configuration file. See pseudocode below.

	 for each audio_file {
			for each output_device {
				play_audio( audio_file , output_device)
				# with constant audio duration and wait times
			}
	 }

## Configuration
### lib\ config.ini
Configuration file. Stores relevant information for the correct operation of the audio reproduction routine.
- `[paths]`
	- `python_path` -> the path to the desired python executable

- `[devices]`
	- `device_id` -> portaudio id of reproduction devices. Mind the sampling rate, since it must match the chosen signals!

- `[reproduction]`
	- `audio_duration` -> audio duration in seconds. Default is the total duration of the selected audio file.  
	- `wait_duration` -> wait time after each reproduction in second. Default 0.5s. It's recommended to include some wait_duration >= 0.1s, in order to compensate for potential program latency.
	- `audio_library` -> path to audio files to use in routines. default `audio/`
	- `sampling_rate` -> desired reproduction sampling rate. default 192000 Hz. May be overwritten by selected audio file or devices sampling rates.

## Audio signal library
### audio\
Audio file library for the reproduction routines.
- `audio\white_noise_5s.wav`: 5s white noise audio clip.
- `audio\pink_noise_5s.wav`: 5s pink noise audio clip.
- `audio\brown_noise_5s.wav`: 5s brown noise audio clip.

#### audio\test\
contains audio signals for the 'test' routine
- `audio\test\<number>.wav`:
Audio clip of TTS voice enunciating the [number] in the filename. Relevant for numbering the output devices in the 'test' routine.


**NOTE:** This library can be freely expanded by adding .mp3 or .wav files to the `audio\` folder. Creation of subfolders is also supported.

## Source code
### dev\ 
"Developer" folder. Contains Python source code.

### .\dev\ list_devices.py
Lists devices connected to machine via Portaudio Driver. Prompts user for output device IDs. Stores device IDs on config.ini file.
Further details of its operation are commented in the source code.

### .\dev\ Nspeakers.py
Performs audio reproduction routines, given a **reproduction mode** or routine ID (as argument) and a **list of output device IDs** (in `.\lib\config.ini` under the field `device_id`).

