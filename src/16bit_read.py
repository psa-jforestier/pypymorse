import wave
import sys
import pprint

import pyaudio
import time
import random

# https://stackoverflow.com/questions/75920565/how-can-i-record-8-bit-audio-with-pyaudio

p = pyaudio.PyAudio()
inStream = p.open(format=pyaudio.paInt16, # read in 16 byte
                  channels=1,
                  rate=22050,
                  input=True,
                  input_device_index=4)

CHUNK = 1 # a CHUNK is the size of the audio sample (16b)
print(p.get_default_input_device_info())
print("Sample data from :")
print(p.get_default_input_device_info())
print("Will start in 1 second")
time.sleep(1)
SCREENWIDTH=80
while True:
    data = inStream.read(CHUNK, exception_on_overflow=False)
    high = data[1]
    low = data[0]
    sample16b = (high << 8) + low
    # sample16b is an unsigned integer varying from 0 to 65535.
    # Samples we got from the stream oscillates around -0.1/+0.1 by oscillating from 1 to 65535.
    # We need to convert them to a signed value
    sample = (sample16b ^ 0x8000) - 0x8000
    # now our sample is between -32768 and +32768


    # Oscilloscope part
    # 0.0 is centered at column SCREENWIDTH/2. 1 is at SCREENWIDTH, -1 is at 0
    s = int(sample * (SCREENWIDTH/0xffff)) # sample 0 to SCREENWIDTH    
    print(f"{sample:6}", end='')
    if (s == 0):
      print(
        "-" * (SCREENWIDTH // 2),
        "|", 
        "-" * (SCREENWIDTH // 2),
        sep='')
    elif (s > 0):
      print(
        "-" * (SCREENWIDTH // 2),
        "|",
        ":" * int(s), 
        "-" * int(SCREENWIDTH/2 - s),
        sep='')
    else:
      print(
        "-" * int((SCREENWIDTH // 2) + s),  
        ":" * int(-s), 
        "|",
        "-" * (SCREENWIDTH // 2),
        sep='')
    