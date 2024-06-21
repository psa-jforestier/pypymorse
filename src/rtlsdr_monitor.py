#!/usr/bin/env python3 -u
# -*- coding: utf-8 -*-

"""
I want to do a kind of frequency monitoring program, using rtl-sdr wrapper in python and numpy. This program must run in console mode, no graphic interface. I do not want to have a dependency with matplotlib or scipy , so I'm looking for a pure python and numpy solution.
I know how to read data from the rtl-sdr dongle (for example, centered at 446MHz with a sample rate of 250kHz should give me a spectrum from 445,875MHz to 446,125MHz).
But how to get this spectrum view ? How to compute the power of 80 linear bands in this range (freq resolution will be 3,125kHz) on data sampled for 100ms ?
I know I have to read 25000 samples (100ms at 250kHz), but I do not know how to compute the frequency power in numpy only.
Here is my skeleton code. the get_spectrum() function is what I want to do, but all the attempt I made with numpy (based on fft) where probably wrong because results were inconsistent (nothing special happends when I transmit on this frequency)

https://stackoverflow.com/questions/78646082/get-spectrum-value-with-numpy-only/

"""

import time
import numpy as np
import pprint
import traceback
import screen
import utils
from rtlsdr import RtlSdr

global window_cache
window_cache = 0
global WINDOW
def psd(data, nfft=80, overlap=0.5):
  """
  A Welch's method-based power spectrum function purely using
  numpy for complex input. This returns the averaged power not
  the power spectral density (although that just requires an
  an additional normalisation factor).
  https://stackoverflow.com/questions/78646082/get-spectrum-value-with-numpy-only/78646609#78646609
  """
  global window_cache
  global WINDOW
  # number of samples to overlap consecutive FFTs
  noverlap = int(nfft * overlap)

  if (window_cache != nfft):
    # create a window function
    #WINDOW = np.hanning(nfft)
    WINDOW = np.blackman(nfft)

  # generate ffts
  fftpower = np.zeros(nfft)
  idx = 0
  count = 0
  while True:
    inputdata = data[idx: idx + nfft]

    if len(inputdata) < nfft:
        # zero pad the final piece
        inputdata = np.pad(inputdata, ((0, nfft - len(inputdata))))

    # perform FFT on windowed data
    fftdata = np.fft.fft(inputdata * WINDOW)
    #fftdata = np.fft.fft(inputdata)

    # sum FFT power
    
    fftpower += 10*np.log10(
      np.abs(np.fft.fftshift(fftdata))**2
    )
    
    #fftpower += np.abs(np.fft.fftshift(fftdata))**2

    # move on index
    idx += nfft - noverlap
    count += 1

    if idx >= len(data):
        break

  # get the average power
  fftpower /= count

  return fftpower
    
# f is the requested frequency
# signal is the time series data
# Fs is the sampling frequency in Hz
def Sxx(f, signal, Fs):
    t = 1/Fs # Sample spacing
    T = len(signal) # Signal duration
    
    s = np.sum([signal[i] * np.exp(-1j*2*np.pi*f*i*t) for i in range(T)])
    
    return t**2 / T * np.abs(s)**2

def init_status():
  screen.printfxy(0,0,"Gain : ")
  screen.printfxy(16,0,"Samplerate : ")
  screen.printfxy(41,0,"Sample duration : ")
  screen.printfxy(0,1,"╒")
  screen.printfxy(screen.curses.COLS-1,1,"╕")
def update_status(sdr):
  screen.printfxy(1,1, "%s", f'{int(sdr.center_freq + sdr.sample_rate/-2)+1:11_}')
  screen.printfxy((screen.curses.COLS-12) // 2,1, "%s", f'{int(sdr.center_freq):11_}')
  screen.printfxy(screen.curses.COLS-12,1, "%s", f'{int(sdr.center_freq + sdr.sample_rate/2):11_}')
  screen.printfxy(7,0,"%s ", sdr.gain)
  screen.printfxy(16+13,0,"%9s", f'{int(sdr.sample_rate):_}')
  screen.printfxy(41+18,0,"%1.3fs", sdr.duration)
  
def handle_key(k, sdr):
  samplerates = [250_000, 1000_000, 2000_000, 3000_000]
  durations = [0.001, 0.005, 0.010, 0.050, 0.100, 0.500, 1.000]
  gains = sdr.valid_gains_db # Gains in dB
  
  if (k == 27):
    return True
  elif (k == screen.curses.KEY_UP):
    sdr.center_freq = sdr.center_freq + 100_000
  elif (k == screen.curses.KEY_DOWN):
    sdr.center_freq = sdr.center_freq - 100_000
  elif (k == screen.curses.KEY_PPAGE):
    sdr.center_freq = sdr.center_freq + 1_000_000
  elif (k == screen.curses.KEY_NPAGE):
    sdr.center_freq = sdr.center_freq - 1_000_000
  elif (k == ord('s')):
    idx = samplerates.index(int(sdr.sample_rate))
    idx = (idx + 1) % len (samplerates)
    sdr.sample_rate = samplerates[idx]
  elif (k == ord('S')):
    idx = samplerates.index(int(sdr.sample_rate))
    idx = (idx - 1) % len (samplerates)
    sdr.sample_rate = samplerates[idx]    
  elif (k == ord('g')):
    idx = gains.index(sdr.gain)
    idx = (idx + 1) % len (gains)
    sdr.gain = gains[idx]
  elif (k == ord('G')):
    idx = gains.index(sdr.gain)
    idx = (idx - 1) % len (gains)
    sdr.gain = gains[idx]
  elif (k == 10):
    newfreq = screen.promptxy(70,0,"Frequency : ", clear=True)
    try:
      f = utils.getNumberFromString(newfreq.decode(), -1)
      sdr.center_freq = int(f)
    except Exception as error:
      print(traceback.format_exc())
  elif (k == ord('d')):
    idx = durations.index(sdr.duration)
    idx = (idx + 1) % len(durations)
    sdr.duration = durations[idx]
  elif (k == ord('D')):
    idx = durations.index(sdr.duration)
    idx = (idx - 1) % len(durations)
    sdr.duration = durations[idx]
  return False

def main():
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
  try:
    screen.init()
    screen.nodelay(True) # do not block when waiting for a key
    screen.clrscr()
    if (screen.curses.LINES < 25 or screen.curses.COLS < 80):
      raise Exception("Terminal must be at least 25x80")
    screen.curses.start_color()
    screen.curses.use_default_colors()
    screen.curses.init_pair(246, 5, -1)
    screen.curses.init_pair(247, 13, -1)
    
    screen.printfxy(0,0, "Init...")
   
    screen.refresh()
    sdr = RtlSdr()
    sdr.sample_rate = 1000_000
    sdr.center_freq = 190_000_000
    sdr.gain = 50
    # new properties added to RtlSdr
    sdr.duration = 0.100
    init_status()
    update_status(sdr)
    screen.refresh()
    line_idx = 0
    nbins = screen.curses.COLS
    old_spectrum = [0.0] * nbins
    waterfall = [(0,15)] * 10
    terminate = False
    smin_val = -3
    smax_val = +3    
    while(not terminate):
      samples = sdr.read_samples(sdr.duration * sdr.sample_rate)
      # mockup data
      # samples = np.random.randn(int(sdr.duration * sdr.sample_rate)) + 1j * np.random.randn(int(sdr.duration * sdr.sample_rate))      
      T_FFT = time.time()
      power = psd(samples, nfft=nbins)
      min_val = np.min(power)
      max_val = np.max(power)
      if (min_val < smin_val):
        smin_val = min_val
      if (max_val > smax_val):
        smax_val = max_val
      smin_val = min_val
      smax_val = max_val
      scaled_data = (15 * ((power - smin_val) / (smax_val - smin_val))).astype(int)      
      T_DRAW = time.time()
      T_FFT = T_DRAW - T_FFT
      # draw the spectrum
      X = 0
      Y = 3 + 15
      # remove old spectrum
      for i in range(0, len(old_spectrum)):
        v = int(old_spectrum[i])        
        for j in range(0,v) :
          screen.printfxy(X+i, Y - v + j, " ")
      old_spectrum = scaled_data
      # print new
      for i in range(0, len(scaled_data)):
        v = int(scaled_data[i])        
        for j in range(0,v + 1) :
          screen.printfxy(X+i, Y - v + j, "█")
        screen.printfxy(X+i, Y - v, "▓")
      # draw the waterfall
      waterfall[line_idx] = scaled_data
      for i in range(0, 10):
        j = (line_idx - i) % 10
        w = waterfall[j]
        for k in range(0,len(w) - 1):
          v = int(w[k])
          screen.printfxyc(X+k, Y + 1 + i, GRAPH8Col[int(v) // 2][0], "%c", GRAPH8Col[int(v) // 2][1])
      line_idx = (line_idx + 1)
      if (line_idx >= 10): 
        line_idx = 0      
      T_DRAW = time.time() - T_DRAW
      screen.printfxy(0,Y+11, "min  = %6.3f,  max=%7.3f T_FFT=%1.3f T_DRAW=%1.3f", min_val, max_val, T_FFT, T_DRAW)
      screen.printfxy(0,Y+12, "smin = %6.3f, smax=%7.3f", smin_val, smax_val)
      screen.refresh()
      if (screen.iskeypressed()): # key detected outside the sample loop, so it may not be very reactive with high duration
        k = screen.getlastkeypressed()
        print("You press ", k, "which is ", screen.curses.keyname(k) )
        terminate = handle_key(k, sdr)
        update_status(sdr)
        screen.refresh()

  except Exception as error:
    screen.deinit()    
    print(traceback.format_exc())
  finally:
    screen.deinit()
  quit()
    

if __name__ == "__main__":
  main()
