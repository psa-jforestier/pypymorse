# PyPyMorse
Morse decoder program. Use audio input from soundcard. In Python. Work under Windows. From an old code fftmorse.c . Use PyAudio and NCurses

## Original C code
The original C code, by François JALBERT, is under the fftmorse.c folder. This program has been written for MSDOS with a SoundBlaster 8 sound card, and is not working anymore on 64 bits OS.

## Porting to Python
I rewrite the C code to Python, make it compatible with all OS supporting Python 3, the PyAudio sound library, and the NCurses library. I developed it under Windows 64 bits.

### Installation
- install dependecies : Python3 and libraries by using `python -m pip install pyaudio windows-curses` (change curses if you use an other OS)
- binary install : a standalone Windows binary will be provided



