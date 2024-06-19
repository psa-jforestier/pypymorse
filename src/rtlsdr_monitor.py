#!/usr/bin/env python3 -u
# -*- coding: utf-8 -*-
# encoding is important because we use here some non standard char
# This demo get sample from rtl-sdr and create a waterfall in the console.
# it uses NCURSES to handle console, colors, and keyboard inputs.
# Keys : 
#  ESC : quit
#  Left, right arrow : move frequency by 100kHz
#  Up, Down arrow : move frequency by 1MHz
#  g : change gain
#  s : change sample rate
#  ENTER : enter a frequency

"""
pip install pyrtlsdr pyrtlsdrlib matplotlib

Doc : https://pyrtlsdr.readthedocs.io/en/latest/

good info : https://pysdr.org/content/rtlsdr.html
"""

import time
import numpy
import pprint
import screen
import traceback
import matplotlib.pyplot as plt
from rtlsdr import RtlSdr
#        	░▒▓█
#       0    1     2    3    4    5    6    7    8
GRAPH4=[' ', '░', '▒', '▓', '█']
GRAPH8=[' ', '·', '•', '▪', '■', '░', '▒', '▓', '█']
GRAPH8Col = [
  [246, '░'],
  [247, '░'],
  [246, '▒'],
  [247, '▒'],
  [246, '▓'],
  [247, '▓'],
  [246, '█'],
  [247, '█'],
]
devs = RtlSdr.get_device_serial_addresses()
print("rtl-sdr devices id : ", devs)
sdr = RtlSdr(serial_number=devs[0])

gains = sdr.valid_gains_db # Gains in dB
gains.append('auto')
print("Gains:", gains)
# configure device

frequency = 466_050_000
samplerates = [250_000, 1000_000, 2000_000, 3000_000]
samplerate_idx = 0
sdr.sample_rate = samplerates[samplerate_idx]  # Hz
sdr.center_freq = frequency     # Hz
#sdr.freq_correction = 60   # PPM
gain_idx = len(gains) - 1
sdr.gain = gains[gain_idx]
sdr.set_bandwidth(100)
#sdr.gain = 30

sampling_duration = 0.01 # in second = 500 
fft_size = 160 # 512
num_rows = 50
#num_rows = int(sampling_duration * samplerate / 250 / 2)
datasize = fft_size*num_rows
#sdr.read_samples(2048) # get rid of initial empty samples

"""
while(True):
  print('Get data for ',sampling_duration)
  sample = sdr.read_samples(datasize)
  print('Compute')
  spectrogram = numpy.zeros((num_rows, fft_size))
  for i in range(num_rows):
    s = 10*numpy.log10(numpy.abs(numpy.fft.fftshift(numpy.fft.fft(sample[i*fft_size:(i+1)*fft_size])))**2)
    mi = min(s)
    ma = max(s)
    s = 10 * ((s - mi) / (ma - mi))    
    spectrogram[i,:] = s
  extent = [(sdr.center_freq + sdr.sample_rate/-2),
            (sdr.center_freq + sdr.sample_rate/2),
            len(sample)/sdr.sample_rate, 
            0]
  #print(spectrogram)
  plt.imshow(spectrogram, aspect='auto', extent=extent)
  plt.xlabel("Frequency [MHz]")
  plt.ylabel("Time [s]")
  plt.show()
  plt.show()
  quit()

"""
"""
while(True):
  sample = sdr.read_samples(fft_size)
  i = 0
  spectrogram = 10*numpy.log10(numpy.abs(numpy.fft.fftshift(numpy.fft.fft(sample[i*fft_size:(i+1)*fft_size])))**2)
  extent = [(sdr.center_freq + sdr.sample_rate/-2),
            (sdr.center_freq + sdr.sample_rate/2),
            len(sample)/sdr.sample_rate, 
            0]
  
  mi = min(spectrogram)
  ma = max(spectrogram)
  scaled_spectro = 4 * ((spectrogram - mi) / (ma - mi))
  for i in range(0, len(scaled_spectro)):
    #print(GRAPH[int(scaled_spectro[i])], sep='', end='')
    j = scaled_spectro[i]
    if (numpy.isnan(j)):
      j = 0
    print(GRAPH[int(j)], sep='', end='')
  print()
"""
try:
  screen.init()
  screen.nodelay(True) # do not block when waiting for a key
  screen.clrscr()
  screen.curses.start_color()
  screen.curses.use_default_colors()
  screen.curses.init_pair(246, 5, -1)
  screen.curses.init_pair(247, 13, -1)
  terminate = False
  hold = False
  statusrefresh = True
  
  spectrogram = numpy.zeros((num_rows, fft_size))
  
  mini = 0
  maxi = 0
  while(not terminate): 
    T = time.time()
    sample = sdr.read_samples(datasize)    
    if (not hold):
      for i in range(num_rows):
        s = 10*numpy.log10(numpy.abs(numpy.fft.fftshift(numpy.fft.fft(sample[i*fft_size:(i+1)*fft_size])))**2)
        spectrogram[i,:] = s
      mi = numpy.min(spectrogram)
      ma = numpy.max(spectrogram)
      if (mi < mini):
        mini = mi
      if (ma > maxi):
        maxi = ma
      for i in range(num_rows):
        s = spectrogram[i]
        s = 7 * ((s - mi) / (ma - mi))
        for j in range(0, len(s)):
          v = s[j]
          if (numpy.isnan(v)):
            v = 0                    
          screen.printfxyc(j, i+1, GRAPH8Col[int(v)][0], "%c", GRAPH8Col[int(v)][1])
    if (statusrefresh == True):
      screen.printfxy((len(s)-(40)) // 2,0,"%s < %s > %s ", 
        f'{int(sdr.center_freq + sdr.sample_rate/-2)+1:_}', 
        f'{sdr.center_freq:_}', 
        f'{int(sdr.center_freq + sdr.sample_rate/2):_}')      
      screen.printfxy(1, 0, "Gain : %4s | Smp %9s ", str(gains[gain_idx]), f'{int(sdr.sample_rate):_}')
      statusrefresh = False
    T = time.time() - T
    screen.printfxy(30, 0, "T=%1.3f mi=%06.1f ma=%06.1f ", T, mi, ma)
    screen.refresh()
    extent = [(sdr.center_freq + sdr.sample_rate/-2),
              (sdr.center_freq + sdr.sample_rate/2),
              len(sample)/sdr.sample_rate, 
              0]
    if (screen.iskeypressed()):
      k = screen.getlastkeypressed()
      print("You press ", k, "which is ", screen.curses.keyname(k) )
      if (k == 27):
        terminate = True
      elif (k == ord('h')):
        hold = not hold
        print("Hold", hold)
      elif (k == screen.curses.KEY_LEFT):
        sdr.center_freq = sdr.center_freq - 100_000
        statusrefresh = True
      elif (k == screen.curses.KEY_DOWN):
        sdr.center_freq = sdr.center_freq - 1_000_000
        statusrefresh = True
      elif (k == screen.curses.KEY_RIGHT):
        sdr.center_freq = sdr.center_freq + 100_000
        statusrefresh = True
      elif (k == screen.curses.KEY_UP):
        sdr.center_freq = sdr.center_freq + 1_000_000
        statusrefresh = True
      elif (k == ord('g')):      
        statusrefresh = True
        gain_idx = (gain_idx + 1) % len(gains)
        sdr.gain = gains[gain_idx]
      elif (k == ord('s')):
        statusrefresh = True
        samplerate_idx = (samplerate_idx + 1) % len (samplerates)
        sdr.sample_rate = samplerates[samplerate_idx]
      elif (k == 10):
        oldfreq = sdr.center_freq
        newfreq = screen.promptxy(1,1,"Frequency : ")
        mini = maxi = 0
        try:
          sdr.center_freq = newfreq
        except Exception as error:
          print(traceback.format_exc())
        statusrefresh = True
except Exception as error:
  screen.deinit()    
  print(traceback.format_exc())
finally:
  screen.deinit()

quit()
while(True):
  print('Get data for ',sampling_duration)
  sample = sdr.read_samples(datasize)
  print('Compute')
  spectrogram = numpy.zeros((num_rows, fft_size))
  for i in range(num_rows):
    s = 10*numpy.log10(numpy.abs(numpy.fft.fftshift(numpy.fft.fft(sample[i*fft_size:(i+1)*fft_size])))**2)
    mi = min(s)
    ma = max(s)
    s = 10 * ((s - mi) / (ma - mi))    
    spectrogram[i,:] = s
  extent = [(sdr.center_freq + sdr.sample_rate/-2),
            (sdr.center_freq + sdr.sample_rate/2),
            len(sample)/sdr.sample_rate, 
            0]
  #print(spectrogram)
  plt.imshow(spectrogram, aspect='auto', extent=extent)
  plt.xlabel("Frequency [MHz]")
  plt.ylabel("Time [s]")
  plt.show()
  plt.show()
  quit()