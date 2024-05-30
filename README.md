# PyPyMorse
Morse decoder program. Use audio input from soundcard. In Python. Work under Windows too, but every OS with Pyhton should work. From an old code fftmorse.c . Use PyAudio and NCurses

## Original C code
The original C code, by François JALBERT, is under the `src/fftmorse.c/` folder. This program has been written for MSDOS with a SoundBlaster 8 sound card, and is not working anymore on 64 bits OS.

## Porting to Python
I rewrite the C code to Python, make it compatible with all OS supporting Python 3, the PyAudio sound library, and the NCurses library. I developed it under Windows 64 bits.

### Installation
- install dependecies : Python3 and libraries by using `python -m pip install pyaudio windows-curses` (change curses if you use an other OS).
- binary install : a standalone Windows binary will be provided.

### Usage

- Basic usage : `python pypymorse.py`

  Act exactly like the good old DOS program. It uses the default sound input from your system. By default, Morse decoding is not enable, you must press SPACE bar to start. See key binding bellow. Your terminal window must have at least 80x25 chars.
  
  Special note for Windows : if you are running it under Git Bash, replace all `python` by `winpty python` or you will have "Redirection is not supported.".
  
- Advanced generic usage : `python pypymorse.py [A lot of cool parameters]`

  Use the `--help` switch to display new options and features of the Morse decoder.
  
- Specify the sound input : use `python pypymorse.py --devices` to list all available devices. Then use `python pypymorse.py -i ID` with the ID number you got from the previous command. Yes, it can use "Digital Stereo Mix" or "Virtual Audio Cable" to work with local audio (from a SDR software for example). *TODO* it is possible to use standard input STDIN to get sample from a piped command.

- Automatically start Morse decoder : `python pypymorse.py --autostart`. It will start the decoder in learning mode without having to press the SPACE bar.

- No GUI : `python pypymorse.py --nogui`. Start the program in command line mode, the (old) user interface is not displayed. Imply `--autostart`. Press Ctrl+C to quit.

- Skip learning phase by specifying dot and dash sample duration : `python pypymorse.py --avrgdot 100 --avrgdash 300`. You can get the value on the GUI from a previous run. They depends of the sampling rate, and the speed of the operator, and your CPU power (100/300 are for 10 WPM at ~12KHz).

- Specify the frequency : `python pypymorse.py --freq F`. Indicate which frequency to lock to use to find signal. This value vary from 0 (low freq) to 10 (high freq), and depends of the sampling rate.

- Specify the mixture ratio : `python pypymorse.py --mix M`. Indicate how many sample to discard. Basically, it allows to change the sample frequency from full speed (M=1 : 44smp/s) to low speed (M=10 : 4smp/s). It is supposed to change the CPU usage, but there is no real difference.

- Change input sample rate : `python pypymorse.py --irate F`. Modify the sample rate of the input device, only to use for unusual sound card that are not compatible with the default 44100 sampling rate.

- Change audio gain : `python pypymorse.py --gain N`. Modify the audio multiplier. N is a float value. Default is 1.

#### Key bindings

The keys of the Python versions are almost the same as the good old DOS version :

```
<space> This toggles FFT on and off. Morse decoding requires the FFT option to 
        be active. This switch was added to make it possible for you to get a 
        very good sampling rate while tuning your short-wave receiver. A high 
        sampling rate improves the quality of the sound coming out ot the 
        Sound-Blaster. Once you have an interesting station, you should toggle 
        FFT back on to start decoding the incoming morse code. On fast 
        computers, this key is probably not very useful.

<+> These change the mixture ratio by throwing away samples every now and then. 
<-> This makes it possible to move the signal up and down the FFT display until 
    it is located more or less in the middle. This is where I suspect the 
    Fourier analysis is at its best. These are only operational if the FFT is 
    enabled. Too high a value (say 10) is not desirable since this throws away 
    too much information and slows down everything since the Sound-Blaster can 
    only supply 15Kb of information per second at best.

<*> Used to toggle learn mode where the program will accumulate statistics 
    about typical dot and dash lengths. After a while, morse decoding will 
    resume on its own. Use this whenever you switch station or after 
    encountering a lot of noise which may have confused the program. Indeed, 
    the program continuously slowly adapts to changes of rhythm in the morse 
    code received.
 
<Up Arrow>         Used to move the frequency window of interest up and down. This is 
<Shift Up><PgUp>   very useful in case the current tone frequency is not exactly in 
<Shift 5><Home>    the middle of the FFT display, or if several morse signals of 
<Shift Down><PgDn> different tone frequencies are active at the same time. In the 
<Down Arrow>       latter case, you can isolate the signal of interest for you.
<g><G>  Increase or reduce the audio gain.
```



