#!/usr/bin/env python3 -u
# -*- coding: utf-8 -*-
# encoding is important because we use here some non standard char
# like the vertical bar (│) or the semi-caret(■)
"""
https://www.codeconvert.ai/c-to-python-converter

Massive usage of PyAudio : https://pypi.org/project/PyAudio/
  python -m pip install pyaudio windows-curses

https://stackoverflow.com/questions/4623572/how-do-i-get-a-list-of-my-devices-audio-sample-rates-using-pyaudio-or-portaudio


stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=FRAMES_PER_BUFFER,
    input_device_index=1 <---- 

)

based on https://archive.org/details/fftmorse
"""
import pyaudio
import pprint
import argparse
import time
import sys
import random

import screen
def print_input_device_info(idev):
  print('id:' + str(idev['index']) + ' ' + idev['name'] + ' ')
  
def print_input_devices():
  p = pyaudio.PyAudio()
  print("  Default input device :")
  print_input_device_info(p.get_default_input_device_info())
  print("  Other available input devices :")
  info = p.get_host_api_info_by_index(0)
  for i in range(info.get('deviceCount')):
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
      print_input_device_info(p.get_device_info_by_host_api_device_index(0, i))

# Global var
FFTenable = False
N = 16
waitfactor = 3
fft = [0] * (N)
oldfft = [0] * (N)

COPYSTRING="FFT Morse (c) 1992 François Jalbert"
FREQSTRING="Lock Frequency with Up and Down Arrows"
EXITSTRING="Exit with Esc"
OFFSTRING ="Toggle FFT On/Off with Space  (now off)"
ONSTRING  ="Toggle FFT On/Off with Space  (now on) "
WAITSTRING="S-Blaster DSP Mixture Ratio 1:%d  (+/-) "
SAMPSTRING = "%d S-Blaster Samples per Second  "
STATSTRING = "Avrg Dot:%d  Avrg Dash:%d (* resets)   "

FLIP=5 # /* levels above average sufficient to trigger tone detected */
LOG2N=4 # /* Adjust according to N way above */ 

# from FFT2tone
old3active = False
old2active = False
old1active = False
active = False
tonedetected = False  # indicates a tone is currently present
freqm2 = freqm1 = freqp1 = freqp2 = 0
freq = (N // 2)  # interesting frequency
freq = 3

  
def FFT(stream):
  S0=0 #/* corresponds to 0.0 */
  S1=3
  S2=6
  S3=9  #/* sin() table with 4 bit precision */
  S4=11 #/* increasing precision will cause short integer overflows... */
  S5=13 #/* too bad, I really would have liked more precision */
  S6=15
  S7=16
  S8=16 #/* corresponds to 1.0 */
  SCALE=11 #/* scale FFT with 2**SCALE from big values to low */

  nbread = 0
  chunk = 1
  
  f = [0] * (N+N)
  
  
  for k in range(0, N+N):
    #for l in range (1, waitfactor):
    #  read_data(stream) 
    if (waitfactor > 1): read_data_buffer(stream, waitfactor - 1)
    f[k] = (read_data(stream) ^ 0x80) - 128
  # print samples
  #for k in range(0, N+N - 4):
  #  screen.printfxy(3 + (5 * k), 0, "%+03d  ", f[k])
  
  # The infamous fft
  f17m1 =f[17]-f[1];  f17p1 =f[17]+f[1];
  f18m2 =f[18]-f[2];  f18p2 =f[18]+f[2];
  f19m3 =f[19]-f[3];  f19p3 =f[19]+f[3];
  f20m4 =f[20]-f[4];  f20p4 =f[20]+f[4];
  f21m5 =f[21]-f[5];  f21p5 =f[21]+f[5];
  f22m6 =f[22]-f[6];  f22p6 =f[22]+f[6];
  f23m7 =f[23]-f[7];  f23p7 =f[23]+f[7];
  f16p0 =f[16]+f[0];  f24p8 =f[24]+f[8];
  f25m9 =f[25]-f[9];  f25p9 =f[25]+f[9];
  f26m10=f[26]-f[10]; f26p10=f[26]+f[10];
  f27m11=f[27]-f[11]; f27p11=f[27]+f[11];
  f28m12=f[28]-f[12]; f28p12=f[28]+f[12];
  f29m13=f[29]-f[13]; f29p13=f[29]+f[13];
  f30m14=f[30]-f[14]; f30p14=f[30]+f[14];
  f31m15=f[31]-f[15]; f31p15=f[31]+f[15];
  f25m9Mf23m7 =f25m9 -f23m7; f25m9Pf23m7 =f25m9 +f23m7;
  f26m10Mf22m6=f26m10-f22m6; f26m10Pf22m6=f26m10+f22m6; 
  f27m11Mf21m5=f27m11-f21m5; f27m11Pf21m5=f27m11+f21m5; 
  f29m13Mf19m3=f29m13-f19m3; f29m13Pf19m3=f29m13+f19m3;
  f30m14Mf18m2=f30m14-f18m2; f30m14Pf18m2=f30m14+f18m2; 
  f31m15Mf17m1=f31m15-f17m1; f31m15Pf17m1=f31m15+f17m1;
  f25p9Mf23p7 =f25p9 -f23p7; f25p9Pf23p7 =f25p9 +f23p7;
  f26p10Mf22p6=f26p10-f22p6; f26p10Pf22p6=f26p10+f22p6;
  f27p11Mf21p5=f27p11-f21p5; f27p11Pf21p5=f27p11+f21p5;
  f24p8Pf16p0 =f24p8 +f16p0; f28p12Pf20p4=f28p12+f20p4;
  f29p13Mf19p3=f29p13-f19p3; f29p13Pf19p3=f29p13+f19p3; 
  f30p14Mf18p2=f30p14-f18p2; f30p14Pf18p2=f30p14+f18p2;
  f31p15Mf17p1=f31p15-f17p1; f31p15Pf17p1=f31p15+f17p1; 
  f29Mf19Pf27Mf21=f29p13Mf19p3+f27p11Mf21p5;
  f29Pf19Mf27Pf21=f29p13Pf19p3-f27p11Pf21p5;
  f29Mf19Mf27Mf21=f29p13Mf19p3-f27p11Mf21p5;
  f31Mf17Pf25Mf23=f31p15Mf17p1+f25p9Mf23p7;
  f31Pf17Mf25Pf23=f31p15Pf17p1-f25p9Pf23p7;
  f31Mf17Mf25Mf23=f31p15Mf17p1-f25p9Mf23p7;
  s4Mf30f18f26f22=S4*(f30p14Mf18p2+f26p10Mf22p6);
  s4Pf30f26f22f18=S4*(f30p14Pf18p2-f26p10Pf22p6);
  s4Mf31f29f27f25=S4*(f31Mf17Mf25Mf23+f29Mf19Mf27Mf21);
  s4Pf31f29f27f25=S4*(f31p15Pf17p1+f25p9Pf23p7-f29p13Pf19p3-f27p11Pf21p5);
  s8Mf30f18f26f22=S8*(f30p14Mf18p2-f26p10Mf22p6);
  s8Pf28f24f20f16=S8*(f28p12Pf20p4-f24p8Pf16p0);
  s8Mf24f16=S8*(f24p8-f16p0); 
  s8Mf28f20=S8*(f28p12-f20p4);
  s4Mf30f26Ms8Mf28=s4Mf30f18f26f22-s8Mf28f20;
  s4Mf30f26Ps8Mf28=s4Mf30f18f26f22+s8Mf28f20;
  s4Pf30f22Ms8Mf24=s4Pf30f26f22f18-s8Mf24f16;
  s4Pf30f22Ps8Mf24=s4Pf30f26f22f18+s8Mf24f16;
  s6Mf31f25Ms2Mf29f27=S6*f31Mf17Pf25Mf23-S2*f29Mf19Pf27Mf21;
  s6Mf29f27Ps2Mf31f25=S6*f29Mf19Pf27Mf21+S2*f31Mf17Pf25Mf23;
  s6Pf29f27Ms2Pf31f25=S6*f29Pf19Mf27Pf21-S2*f31Pf17Mf25Pf23;
  s6Pf31f25Ps2Pf29f27=S6*f31Pf17Mf25Pf23+S2*f29Pf19Mf27Pf21;
  s1Mf25s3f27s5f29s7f31=S1*f25m9Mf23m7+S3*f27m11Mf21m5+S5*f29m13Mf19m3+S7*f31m15Mf17m1;
  s1Pf25s3f27s5f29s7f31=S1*f25m9Pf23m7-S3*f27m11Pf21m5+S5*f29m13Pf19m3-S7*f31m15Pf17m1;
  s1Mf27s3f31s5f25s7f29=S1*f27m11Mf21m5+S3*f31m15Mf17m1+S5*f25m9Mf23m7-S7*f29m13Mf19m3;
  s1Pf27s3f31s5f25s7f29=S1*f27m11Pf21m5+S3*f31m15Pf17m1-S5*f25m9Pf23m7+S7*f29m13Pf19m3;
  s1Mf29s3f25s5f31s7f27=S1*f29m13Mf19m3+S3*f25m9Mf23m7-S5*f31m15Mf17m1+S7*f27m11Mf21m5;
  s1Pf29s3f25s5f31s7f27=S1*f29m13Pf19m3+S3*f25m9Pf23m7+S5*f31m15Pf17m1-S7*f27m11Pf21m5;
  s1Mf31s3f29s5f27s7f25=S1*f31m15Mf17m1-S3*f29m13Mf19m3+S5*f27m11Mf21m5-S7*f25m9Mf23m7;
  s1Pf31s3f29s5f27s7f25=S1*f31m15Pf17m1+S3*f29m13Pf19m3+S5*f27m11Pf21m5+S7*f25m9Pf23m7;
  s2Mf26Ps6Mf30=S2*f26m10Mf22m6+S6*f30m14Mf18m2;
  s2Pf26Ms6Pf30=S2*f26m10Pf22m6-S6*f30m14Pf18m2;
  s2Mf30Ms6Mf26=S2*f30m14Mf18m2-S6*f26m10Mf22m6;
  s2Pf30Ps6Pf26=S2*f30m14Pf18m2+S6*f26m10Pf22m6;
  s4Mf28f20=S4*(f28m12-f20m4); s4Pf28f20=S4*(f28m12+f20m4);
  s8f16=S8*(f[16]-f[0]); s8f24=S8*(f[24]-f[8]);
  s4Mf28Ps8f16=s4Mf28f20+s8f16;
  s4Mf28Ms8f16=s4Mf28f20-s8f16;
  s4Pf28Ps8f24=s4Pf28f20+s8f24;
  s4Pf28Ms8f24=s4Pf28f20-s8f24;
  s2Mf26Ps4f28s6f30Ms8f16=s2Mf26Ps6Mf30+s4Mf28Ms8f16;
  s2Mf26Ms4f28s6f30Ps8f16=s2Mf26Ps6Mf30-s4Mf28Ms8f16;
  s2Pf26Ms4f28s6f30Ps8f24=s2Pf26Ms6Pf30-s4Pf28Ms8f24;
  s2Pf26Ps4f28s6f30Ms8f24=s2Pf26Ms6Pf30+s4Pf28Ms8f24;
  s2Mf30Ps4f28s6f26Ps8f16=s2Mf30Ms6Mf26+s4Mf28Ps8f16;
  s2Mf30Ms4f28s6f26Ms8f16=s2Mf30Ms6Mf26-s4Mf28Ps8f16;
  s2Pf30Ps4f28s6f26Ps8f24=s2Pf30Ps6Pf26+s4Pf28Ps8f24;
  s2Pf30Ms4f28s6f26Ms8f24=s2Pf30Ps6Pf26-s4Pf28Ps8f24;
  fft[1]=(abs(s1Mf25s3f27s5f29s7f31+s2Mf26Ps4f28s6f30Ms8f16)>>SCALE)+(abs(s1Pf31s3f29s5f27s7f25+s2Pf30Ps4f28s6f26Ps8f24)>>SCALE);
  fft[2]=(abs(s6Pf31f25Ps2Pf29f27+s4Pf30f22Ms8Mf24)>>SCALE)+(abs(s6Mf29f27Ps2Mf31f25+s4Mf30f26Ps8Mf28)>>SCALE);
  fft[3]=(abs(s2Mf30Ms4f28s6f26Ms8f16-s1Mf29s3f25s5f31s7f27)>>SCALE)+(abs(s2Pf26Ms4f28s6f30Ps8f24-s1Pf27s3f31s5f25s7f29)>>SCALE);
  fft[4]=(abs(s4Pf31f29f27f25-s8Pf28f24f20f16)>>SCALE)+(abs(s4Mf31f29f27f25+s8Mf30f18f26f22)>>SCALE);
  fft[5]=(abs(s1Mf27s3f31s5f25s7f29-s2Mf30Ps4f28s6f26Ps8f16)>>SCALE)+(abs(s2Pf26Ps4f28s6f30Ms8f24-s1Pf29s3f25s5f31s7f27)>>SCALE);
  fft[6]=(abs(s6Pf29f27Ms2Pf31f25+s4Pf30f22Ps8Mf24)>>SCALE)+(abs(s6Mf31f25Ms2Mf29f27+s4Mf30f26Ms8Mf28)>>SCALE);
  fft[7]=(abs(s1Mf31s3f29s5f27s7f25-s2Mf26Ms4f28s6f30Ps8f16)>>SCALE)+(abs(s1Pf25s3f27s5f29s7f31-s2Pf30Ms4f28s6f26Ms8f24)>>SCALE);
  fft[8]=(abs(S8*(f30p14Pf18p2+f26p10Pf22p6-f28p12Pf20p4-f24p8Pf16p0))>>SCALE)+(abs(S8*(f31Mf17Mf25Mf23-f29Mf19Mf27Mf21))>>SCALE);
  fft[9]=(abs(s1Mf31s3f29s5f27s7f25+s2Mf26Ms4f28s6f30Ps8f16)>>SCALE)+(abs(s1Pf25s3f27s5f29s7f31+s2Pf30Ms4f28s6f26Ms8f24)>>SCALE);
  fft[10]=(abs(s6Pf29f27Ms2Pf31f25-s4Pf30f22Ps8Mf24)>>SCALE)+(abs(s4Mf30f26Ms8Mf28-s6Mf31f25Ms2Mf29f27)>>SCALE);
  fft[11]=(abs(s1Mf27s3f31s5f25s7f29+s2Mf30Ps4f28s6f26Ps8f16)>>SCALE)+(abs(s1Pf29s3f25s5f31s7f27+s2Pf26Ps4f28s6f30Ms8f24)>>SCALE);
  fft[12]=(abs(s8Pf28f24f20f16+s4Pf31f29f27f25)>>SCALE)+(abs(s8Mf30f18f26f22-s4Mf31f29f27f25)>>SCALE);
  fft[13]=(abs(s1Mf29s3f25s5f31s7f27+s2Mf30Ms4f28s6f26Ms8f16)>>SCALE)+(abs(s1Pf27s3f31s5f25s7f29+s2Pf26Ms4f28s6f30Ps8f24)>>SCALE);
  fft[14]=(abs(s4Pf30f22Ms8Mf24-s6Pf31f25Ps2Pf29f27)>>SCALE)+(abs(s4Mf30f26Ps8Mf28-s6Mf29f27Ps2Mf31f25)>>SCALE);
  fft[15]=(abs(s2Mf26Ps4f28s6f30Ms8f16-s1Mf25s3f27s5f29s7f31)>>SCALE)+(abs(s2Pf30Ps4f28s6f26Ps8f24-s1Pf31s3f29s5f27s7f25)>>SCALE);

  for l in range(1, N):
    line = 160 * l
    oldlevel = oldfft[l]
    level = oldfft[l] = fft[l]
    for k in range(1, level+1):
      column = 2 * k
      screen.pokeb(0, 80+line+column, '■')
    for k in range(level+1, oldlevel+1):
      column = 2 * k
      screen.pokeb(0, 80 + line + column, ' ')
  screen.refresh()
  
def begin():
  screen.clrscr()
  for xx in range(1, 35):    screen.pokeb(0,(xx<<1),'─');
  for xx in range(1, 35):    screen.pokeb(0,(xx<<1)+(160*24),'─');
  for yy in range(1,24):     screen.pokeb(0,(160*yy),'│');
  for yy in range(1, 24):    screen.pokeb(0,(35<<1)+(160*yy),'│');
  screen.pokeb(0,0,'┌');
  screen.pokeb(0,(35<<1),'┐');
  screen.pokeb(0,(160*24),'└');
  screen.pokeb(0,(35<<1)+(160*24),'┘');
  screen.gotoxy(40,17); screen.cprintf(COPYSTRING);
  screen.gotoxy(40,19); screen.cprintf(FREQSTRING);
  screen.gotoxy(40,20); 
  if (FFTenable): screen.cprintf(ONSTRING)
  else: screen.cprintf(OFFSTRING);
  screen.gotoxy(40,21); screen.cprintf(EXITSTRING);
  screen.gotoxy(40,25); screen.cprintf(WAITSTRING, waitfactor);
 
  updatecursor('=','>')
  line = 0
  for l in range(1, N):
    line += 160
    fft[l]=0
    screen.pokeb(0,80+line,'­');
  screen.refresh()
  return

def FFT2tone():
  # /* determines whether a morse tone is present or not */
  global old3active
  global old2active
  global old1active
  global active
  global tonedetected
  average = 0
  for l in range(1, N):
    average += fft[l]
  average = average >> LOG2N
  limit = FLIP+(5*average)
  old3active = old2active
  old2active = old1active
  old1active = active
  active=( (fft[freqm2]+fft[freqp2]+fft[freqm1]+fft[freqp1]+fft[freq])>=limit )
  
  oldtonedetected = tonedetected
  tonedetected = (active or old1active or old2active or old3active)
  #screen.pokeb(0, 158, '?')
  if tonedetected and not oldtonedetected:
    screen.pokeb(0, 158, '█')
  elif oldtonedetected and not tonedetected:
    screen.pokeb(0, 158, '■')
  screen.refresh()    
  return

# /*----------------------------- Tone to Morse --------------------------------*/

M=8 # /* number of elements used to compute average element */
LOG2M=3 # /* adjust according to M above */


reset = True
counterdots=0
counterdashes=0
sumdots=0
sumdashes=0
avrgdot=int(0)
avrgdash=int(0)
dots = [0] * (M)
dashes = [0] * (M)
dot = False
dash = False
space = False
oncounter = 0
offcounter = 0
firsttone = 0

def learn():
  global oncounter
  global firsttone
  global avrgdot
  global avrgdash
  global sumdots
  global sumdashes
  global counterdots
  global counterdashes
  global reset
  # /* learn dot and dash duration out of tone detection */
  if (tonedetected): oncounter+=waitfactor
  else:
    if (oncounter>0):
      # /* tone oncounter long just completed */
      if (counterdots==0): # /* not one of each yet, must be starting to learn */
        if (firsttone==0): firsttone=oncounter;
        else: # /* make sure tones are different enough, ie dot and dash */
          if (firsttone>oncounter): # /* which is dash and which is dot? */
            if (firsttone>(oncounter<<1)): # { /* firsttone=dash oncounter=dot */
              dashes[0]=sumdashes=avrgdash=firsttone
              dots[0]=sumdots=avrgdot=oncounter
              counterdashes=counterdots=1              
            else: firsttone=oncounter # /* not different enough */
          else:
            if (oncounter>(firsttone<<1)): # { /* oncounter=dash firsttone=dot */
              dashes[0]=sumdashes=avrgdash=oncounter;
              dots[0]=sumdots=avrgdot=firsttone;
              counterdashes=counterdots=1;
            else: firsttone=oncounter #; /* not different enough */
      else: # /* at least one instance of dot and dash encountered so far */
        if (oncounter>(int(avrgdot+avrgdash)>>1)):
          if (counterdashes<M):
            dashes[counterdashes]=oncounter
            sumdashes+=oncounter
            counterdashes+=1
            avrgdash=sumdashes // counterdashes
        else:
          if (counterdots < M): # /* still some to learn about dots */        
            dots[counterdots]=oncounter
            sumdots+=oncounter
            counterdots+=1
            avrgdot=sumdots // counterdots
        if ((counterdots==M) and (counterdashes==M)): # { /* enough learning */
          counterdots=counterdashes=0
          reset=False
      oncounter=0;
          
  return

def tone2morse():
  # /* deduces dot or dash or space out of tone detection */
  global tonedected
  global offcounter
  global oncounter
  global avrgdot
  global avrgdash
  global space
  global dash
  global dot
  global sumdots
  global sumdashes
  global counterdots
  global counterdashes
  
  if (tonedetected):
    oncounter += waitfactor
    if (offcounter>0):
      # /* silence offcounter long just completed */
      if (offcounter>(int(avrgdot+avrgdot+avrgdot+avrgdash)>>2)): space=True
      offcounter=0; 
  else:
    offcounter+=waitfactor;
    if (oncounter>0) :
      # /* tone oncounter long just completed */
      if (oncounter>(int(avrgdot+avrgdash)>>1)):
        dash=True
        sumdashes-=dashes[counterdashes]
        dashes[counterdashes]=oncounter
        sumdashes+=oncounter;
        avrgdash=int(sumdashes>>LOG2M)
        if (counterdashes==(M-1)): counterdashes=0
        else: counterdashes+=1
      else:
        dot=True
        sumdots-=dots[counterdots]
        dots[counterdots]=oncounter
        sumdots+=oncounter
        avrgdot=(sumdots>>LOG2M)
        if (counterdots==(M-1)): counterdots=0
        else: counterdots+=1
      oncounter=0;      
  return
  
# /*----------------------------- Morse to Text --------------------------------*/

code = 0
mask = 1
x = y = 1
y160 = 160

def morse2text():  
  global code
  global mask
  global x
  global y
  global y160
  global dot
  global dash
  global space
  
  if (dot == True):
    code = code + mask
    mask = mask << 1
    dot = False
  else:
    if (dash == True):
      mask = mask << 1
      dash = False
    else:
      if (space == True):
        code += mask
        if (code == 2):
          c='T'; punctuation=False
        elif (code == 3):
          c='E'; punctuation=False
        elif (code == 4):
          c='M'; punctuation=False
        elif (code == 5):
          c='A'; punctuation=False
        elif (code == 6):
          c='N'; punctuation=False
        elif (code == 7):
          c='I'; punctuation=False
        elif (code == 8):
          c='O'; punctuation=False
        elif (code == 9):
          c='W'; punctuation=False
        elif (code == 10):
          c='K'; punctuation=False
        elif (code == 11):
          c='U'; punctuation=False
        elif (code == 12):
          c='G'; punctuation=False
        elif (code == 13):
          c='R'; punctuation=False
        elif (code == 14):
          c='D'; punctuation=False
        elif (code == 15):
          c='S'; punctuation=False
        elif (code == 17):
          c='J'; punctuation=False
        elif (code == 18):
          c='Y'; punctuation=False
        elif (code == 19):
          c='Ü'; punctuation=False
        elif (code == 20):
          c='Q'; punctuation=False
        elif (code == 21):
          c='Ä'; punctuation=False
        elif (code == 22):
          c='X'; punctuation=False
        elif (code == 23):
          c='V'; punctuation=False
        elif (code == 24):
          c='Ö'; punctuation=False
        elif (code == 25):
          c='P'; punctuation=False
        elif (code == 26):
          c='C'; punctuation=False
        elif (code == 27):
          c='F'; punctuation=False
        elif (code == 28):
          c='Z'; punctuation=False
        elif (code == 29):
          c='L'; punctuation=False
        elif (code == 30):
          c='B'; punctuation=False
        elif (code == 31):
          c='H'; punctuation=False
        elif (code == 32):
          c='0'; punctuation=False
        elif (code == 33):
          c='1'; punctuation=False
        elif (code == 35):
          c='2'; punctuation=False
        elif (code == 36):
          c='ą'; punctuation=False
        elif (code == 39):
          c='3'; punctuation=False
        elif (code == 41):
          c='Ć'; punctuation=False
        elif (code == 47):
          c='4'; punctuation=False
        elif (code == 48):
          c='9'; punctuation=False
        elif (code == 54):
          c='/'; punctuation=False
        elif (code == 56):
          c='8'; punctuation=False
        elif (code == 59):
          c='É'; punctuation=False
        elif (code == 60):
          c='7'; punctuation=False
        elif (code == 62):
          c='6'; punctuation=False
        elif (code == 63):
          c='5'; punctuation=False
        elif (code == 76):
          c=','; punctuation=True
        elif (code == 82):
          c='|'; punctuation=False
        elif (code == 85):
          c='.'; punctuation=True
        elif (code == 94):
          c='-'; punctuation=False
        elif (code == 106):
          c=';'; punctuation=True
        elif (code == 115):
          c='?'; punctuation=True
        elif (code == 120):
          c=':'; punctuation=True
        else:
          c='■'; punctuation=False
        print(c, end='')
        sys.stdout.flush()
        screen.pokeb(0,(x<<1)+y160,c);
        x = x + 1
        
        if (x == 35):
          y = y + 1
          y160 += 160
          if (y == 24):
            y = 1
            y160 = 160
          for x in range(1, 35):
            screen.pokeb(0, (x<<1)+y160,' ')
          x = 1
        if (punctuation):
          screen.pokeb(0, (x<<1)+y160,' ')
          x = x + 1
          if (x == 35):
            y = y + 1
            if (y == 24):
              y = 1
              y160 = 160
            for x in range(1, 35):
              screen.pokeb(0, (x<<1)+y160,' ')
            x = 1
        screen.pokeb(0,(x<<1)+y160,'_')
        code = 0
        mask = 1
        space = False
    
  return

def read_data(stream):  
  buf = stream.read(1) # Return a 16 bits buffers
  high = buf[1]
  return high

def read_data_buffer(stream, size):
  buf = stream.read(size)
  return buf
def updatecursor(c1, c2): # /* displays selected frequency cursor */
  global freq
  global freqm1
  global freqm2
  global freqp1
  global freqp2
  freqp1=freq+1
  freqm1=freq-1
  freqp2=freq+2
  freqm2=freq-2
  # need +1 because cursor is shifted (bug?)
  screen.pokeb(0,(74-160)+(160*(freqm2 + 1)),c1);
  screen.pokeb(0,(74-160)+(160*(freqm1 + 1)),c1);
  screen.pokeb(0,(74-160)+(160*(freq   + 1)),c1);
  screen.pokeb(0,(74-160)+(160*(freqp1 + 1)),c1);
  screen.pokeb(0,(74-160)+(160*(freqp2 + 1)),c1);
  screen.pokeb(0,(76-160)+(160*(freqm2 + 1)),c2);
  screen.pokeb(0,(76-160)+(160*(freqm1 + 1)),c2);
  screen.pokeb(0,(76-160)+(160*(freq   + 1)),c2);
  screen.pokeb(0,(76-160)+(160*(freqp1 + 1)),c2);
  screen.pokeb(0,(76-160)+(160*(freqp2 + 1)),c2);

def handlekey(key):
  global FFTenable
  global freq
  global waitfactor
  global reset
  global counterdots
  global counterdashes
  global sumdots
  global sumdashes
  global avrgdot
  global avrgdash
  global firsttone
  updatecursor(' ',' ')
  ch = screen.getlastkeypressed()
  if (ch == 27): return True # ESC
  elif (ch == screen.curses.KEY_UP):
    if (freq > 3): freq = freq - 1
  elif (ch == screen.curses.KEY_DOWN):
    if (freq<(N-3)): freq = freq + 1
  elif (ch in [ screen.curses.KEY_SUP, screen.curses.KEY_PPAGE]): freq = 3
  elif (ch in [ 548, screen.curses.KEY_NPAGE]): freq = N-3 # Shift+DOWN
  elif (ch in [screen.curses.KEY_HOME, ord('5')]): freq=(N>>1)
  elif (ch == ord('+')):
    waitfactor = waitfactor + 1
    screen.gotoxy(40,25)
    screen.cprintf(WAITSTRING,waitfactor)
  elif (ch == ord('-')):
    if (waitfactor>1):
      waitfactor = waitfactor - 1
      screen.gotoxy(40,25)
      screen.cprintf(WAITSTRING,waitfactor)
  elif (ch == ord(' ')):
    FFTenable = not FFTenable; 
    screen.gotoxy(40,20);
    if (FFTenable): screen.cprintf(ONSTRING); 
    else: screen.cprintf(OFFSTRING);
  elif (ch == ord('*')):
    reset = True
    counterdots=counterdashes=0
    sumdots=sumdashes=0
    avrgdot=avrgdash=0
    firsttone=0
  updatecursor('=','>');
  
  return False
  
def getTimeS():
  return int(time.time())

def main():
  global avrgdot
  global avrgdash
  global FFTenable
  global counterdots
  global counterdashes
  global M
  global reset
  global oncounter
  global offcounter
  global dots
  global dashes
  global sumdots
  global sumdashes
  global firsttone
  parser = argparse.ArgumentParser(description='Morse decoder')
  parser.add_argument('-i', '--input',
    default=-1, metavar='ID', type=int,
    help='Set input device (use --devices to enumerate existing devices)')
  parser.add_argument('--avrgdot',
    default = 0, metavar='N', type = int,
    help='Set default dot sample count and avoid learning phase')
  parser.add_argument('--avrgdash',
    default = 0, metavar='N', type = int,
    help='Set default dash sample count and avoid learning phase')
  parser.add_argument('--autostart',
    action='store_true',
    help='Start decoding automatically (no need to press SPACE)')
  parser.add_argument('--devices',
    action='store_true',
    help='Enumerate and print existing devices and their ID to use with -i')
  args = vars(parser.parse_args())
  pprint.pprint(args)
  
  inputdeviceid = 0
  p = pyaudio.PyAudio()
  if (args['devices'] == True):
    print_input_devices()
    exit()
  if (args['input'] == -1):
    inputdeviceid  = p.get_default_input_device_info()['index']
  else:
    inputdeviceid = int(args['input'])
  inputdevice = p.get_device_info_by_index(inputdeviceid)
  print("Using device audio ID", inputdeviceid, ":\"", inputdevice.get('name'),"\"")
  print("  sample rate :", inputdevice.get('defaultSampleRate'), "; input channels :", inputdevice.get('maxInputChannels'))
  
  stream = p.open(input=True, output = False,
    channels=1,
    rate=44100,
    format=pyaudio.paInt16, # PaAudio do not work with 8bit samples
    input_device_index=inputdeviceid)
  screen.init()
  screen.nodelay(True) # do not block when waiting for a key
  
  # Decoder settings
  if (args['avrgdot'] != 0):
    avrgdot = args['avrgdot']
  if (args['avrgdot'] != 0):
    avrgdash = args['avrgdash']
  if (args['autostart'] == True):
    FFTenable = True
    reset = False
    sumdots = avrgdot * M
    sumdashes = avrgdash * M
    dots = [75] * M
    dashes = [235] * M
  """
  Start C code conversion
  """
  
  KCHECK = 64
  SCHECK = 16

  done = False
  counter = 0 # int
  kloop = sloop = delta = k = 0 # int
  start = current = 0 # longint
 
  
  begin();
  start = getTimeS()
  while (not done) :
    for sloop in range(1, SCHECK + 1):
      """
      screen.gotoxy(0,29);
      screen.cprintf("dots  =%s   ", dots)
      screen.gotoxy(0,30);
      screen.cprintf("dashes=%s   ", dashes)
      screen.gotoxy(40,23);
      screen.cprintf(STATSTRING,avrgdot,avrgdash);
      screen.gotoxy(0,26);
      screen.cprintf("counterdots=%d counterdashes=%d sumdots=%d sumdashes=%d     ", counterdots, counterdashes, sumdots, sumdashes);
      screen.gotoxy(0,27);
      screen.cprintf("avrgdot=%d avrgdash=%d firsttone=%d      ", avrgdot, avrgdash, firsttone);
      screen.gotoxy(0,28);
      screen.cprintf("oncounter=%d offcounter=%d  reset=%s ", oncounter, offcounter, reset)
      """
      if (FFTenable):
        for kloop in range(1, KCHECK+1):
          FFT(stream)
          FFT2tone()
          if (reset):
            learn()
          else:
            tone2morse()
            morse2text()
      else:
        
        #for kloop in range(1, KCHECK+1): # can be optimized by reading a longer buffer
        #  for k in range(0, N+N):
        #    read_data(stream)
        read_data_buffer(stream, KCHECK * (N + N))
      if (screen.iskeypressed()):
        key = screen.getlastkeypressed()
        done = handlekey(key)
        if (done): quit()
    counter = counter + (N+N);
    current = getTimeS()
    delta = (current-start);
    if (delta > 2):
      screen.gotoxy(40, 24)
      screen.cprintf(SAMPSTRING, counter*((KCHECK*SCHECK)/delta) )
      start = current
      counter = 0
    
    
    screen.refresh()
  
  p.terminate()

if __name__ == "__main__":
    main()
