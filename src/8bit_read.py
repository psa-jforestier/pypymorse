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
                  rate=8000,
                  input=True,
                  input_device_index=4)

CHUNK = 1 # a CHUNK is the size of the audio sample (16b)
sample8b = [0] * (CHUNK) # Each data will be in 8bits, from  0 to 255, where 0 is at 127
print("Sample data from :")
print(p.get_default_input_device_info())
print("Will start in 1 second")
time.sleep(1)
SCREENWIDTH=80
while True:
    data = inStream.read(CHUNK, exception_on_overflow=False)
    high = data[1] # use only the high part of the 16b sample
    # sample16b is an unsigned integer varying from 0 to 65535.
    # Samples we got from the stream oscillates around -0.1/+0.1 by oscillating from 1 to 65535.
    # We need to convert them to a signed value
    
    sample8b = (high ^ 0x80) - 0x80
    
    # now our sample is between -127 and +127
    
    # Oscilloscope part
    # 0.0 is centered at column SCREENWIDTH/2. 1 is at SCREENWIDTH, -1 is at 0
    s = int(sample8b * (SCREENWIDTH/255)) # sample 0 to SCREENWIDTH    
    print(f"{sample8b:6}", end='')
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
    