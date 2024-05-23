/*
    FFT Morse Code Decoder Version 1.0
    Copyright (c) 1992 Fran‡ois Jalbert (jalbert@IRO.UMontreal.CA)

    Sound-Blaster (c) 1989-1991 Creative Labs Inc
    Turbo-C 2.0 (c) 1988 Borland International
    Sound-Blaster C Library BLAST13 (c) 1991 Joel Lucsy
    LZEXE 0.91 (c) 1989 Fabrice Bellard

    Turbo-C flags used: -mt -1 -d -f- -A -K -G -O -w

    Warning! This source file contains IBM extended ASCII characters.
             Some source lines are slightly longer than 80 characters.
*/
/*
#define DEBUG
#define FFTDEBUG
*/
#include <direct.h> /* BLAST13 */
#include <stdlib.h>
#include <stdio.h>
#include <conio.h>
#include <dos.h>

#define TRUE  1
#define FALSE 0
#define N 16 /* number of FFT terms, do not change this!!! See also LOG2N */

static unsigned int videoseg=0xB800; /* assume color */

/*----------------------------------- FFT ------------------------------------*/

#define S0  0 /* corresponds to 0.0 */
#define S1  3
#define S2  6
#define S3  9 /* sin() table with 4 bit precision */
#define S4 11 /* increasing precision will cause short integer overflows... */
#define S5 13 /* too bad, I really would have liked more precision */
#define S6 15
#define S7 16
#define S8 16 /* corresponds to 1.0 */
#define SCALE 11 /* scale FFT with 2**SCALE from big values to low */

#ifdef DEBUG
static int s[N+N],c[N+N];
#endif
static int FFTenable=FALSE; /* Maximum sampling rate for initial SW tuning */
static int waitfactor=3; /* Best initial sampling rate for my 12MHz 286 */
static int fft[N],oldfft[N];

void FFT(void)
{ /* compute fast short integer FT */
#ifdef DEBUG
  static int data,kl,a[N],b[N],fff[N];
#endif
  static int k,l,f[N+N];
  static int level,oldlevel,line,column;
  static int f16p0,f17m1,f17p1,f18m2,f18p2,f19m3,f19p3;
  static int f20m4,f20p4,f21m5,f21p5,f22m6,f22p6,f23m7,f23p7;
  static int f24p8,f25m9,f25p9,f26m10,f26p10,f27m11,f27p11;
  static int f28m12,f28p12,f29m13,f29p13,f30m14,f30p14,f31m15,f31p15;
  static int f25m9Mf23m7,f25m9Pf23m7,f26m10Mf22m6,f26m10Pf22m6;
  static int f27m11Pf21m5,f29m13Mf19m3,f29m13Pf19m3,f27m11Mf21m5;
  static int f30m14Mf18m2,f30m14Pf18m2,f31m15Mf17m1,f31m15Pf17m1;
  static int f24p8Pf16p0,f25p9Mf23p7,f25p9Pf23p7,f26p10Mf22p6,f26p10Pf22p6;
  static int f27p11Mf21p5,f27p11Pf21p5,f28p12Pf20p4,f29p13Mf19p3;
  static int f29p13Pf19p3,f30p14Mf18p2,f30p14Pf18p2,f31p15Mf17p1,f31p15Pf17p1;
  static int f29Mf19Pf27Mf21,f29Pf19Mf27Pf21,f29Mf19Mf27Mf21;
  static int f31Mf17Pf25Mf23,f31Pf17Mf25Pf23,f31Mf17Mf25Mf23;
  static int s4Mf28f20,s4Pf28f20;
  static int s4Mf30f18f26f22,s4Pf30f26f22f18,s4Mf31f29f27f25,s4Pf31f29f27f25;
  static int s8Mf30f18f26f22,s8Pf28f24f20f16,s8Mf24f16,s8Mf28f20,s8f16,s8f24;
  static int s4Mf30f26Ms8Mf28,s4Mf30f26Ps8Mf28;
  static int s4Pf30f22Ms8Mf24,s4Pf30f22Ps8Mf24;
  static int s6Mf31f25Ms2Mf29f27,s6Mf29f27Ps2Mf31f25;
  static int s6Pf29f27Ms2Pf31f25,s6Pf31f25Ps2Pf29f27;
  static int s1Mf25s3f27s5f29s7f31,s1Pf25s3f27s5f29s7f31;
  static int s1Mf27s3f31s5f25s7f29,s1Pf27s3f31s5f25s7f29;
  static int s1Mf29s3f25s5f31s7f27,s1Pf29s3f25s5f31s7f27;
  static int s1Mf31s3f29s5f27s7f25,s1Pf31s3f29s5f27s7f25;
  static int s2Mf26Ps6Mf30,s2Pf26Ms6Pf30,s2Mf30Ms6Mf26,s2Pf30Ps6Pf26;
  static int s4Mf28Ps8f16,s4Mf28Ms8f16,s4Pf28Ps8f24,s4Pf28Ms8f24;
  static int s2Mf26Ps4f28s6f30Ms8f16,s2Mf26Ms4f28s6f30Ps8f16;
  static int s2Pf26Ms4f28s6f30Ps8f24,s2Pf26Ps4f28s6f30Ms8f24;
  static int s2Mf30Ps4f28s6f26Ps8f16,s2Mf30Ms4f28s6f26Ms8f16;
  static int s2Pf30Ps4f28s6f26Ps8f24,s2Pf30Ms4f28s6f26Ms8f24;

  for (k=0 ; k<(N+N) ; k++) {
    for (l=1 ; l<waitfactor ; l++) read_data(); 
    f[k]=read_data()-128;
  }
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
  s2Mf26Ps6Mf30=S2*f26m10Mf22m6+S6*f30m14Mf18m2;;
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
  fft[1]=(abs(s1Mf25s3f27s5f29s7f31+s2Mf26Ps4f28s6f30Ms8f16)>>SCALE)+
         (abs(s1Pf31s3f29s5f27s7f25+s2Pf30Ps4f28s6f26Ps8f24)>>SCALE);
  fft[2]=(abs(s6Pf31f25Ps2Pf29f27+s4Pf30f22Ms8Mf24)>>SCALE)+
         (abs(s6Mf29f27Ps2Mf31f25+s4Mf30f26Ps8Mf28)>>SCALE);
  fft[3]=(abs(s2Mf30Ms4f28s6f26Ms8f16-s1Mf29s3f25s5f31s7f27)>>SCALE)+
         (abs(s2Pf26Ms4f28s6f30Ps8f24-s1Pf27s3f31s5f25s7f29)>>SCALE);
  fft[4]=(abs(s4Pf31f29f27f25-s8Pf28f24f20f16)>>SCALE)+
         (abs(s4Mf31f29f27f25+s8Mf30f18f26f22)>>SCALE);
  fft[5]=(abs(s1Mf27s3f31s5f25s7f29-s2Mf30Ps4f28s6f26Ps8f16)>>SCALE)+
         (abs(s2Pf26Ps4f28s6f30Ms8f24-s1Pf29s3f25s5f31s7f27)>>SCALE);
  fft[6]=(abs(s6Pf29f27Ms2Pf31f25+s4Pf30f22Ps8Mf24)>>SCALE)+
         (abs(s6Mf31f25Ms2Mf29f27+s4Mf30f26Ms8Mf28)>>SCALE);
  fft[7]=(abs(s1Mf31s3f29s5f27s7f25-s2Mf26Ms4f28s6f30Ps8f16)>>SCALE)+
         (abs(s1Pf25s3f27s5f29s7f31-s2Pf30Ms4f28s6f26Ms8f24)>>SCALE);
  fft[8]=(abs(S8*(f30p14Pf18p2+f26p10Pf22p6-f28p12Pf20p4-f24p8Pf16p0))>>SCALE)+
         (abs(S8*(f31Mf17Mf25Mf23-f29Mf19Mf27Mf21))>>SCALE);
  fft[9]=(abs(s1Mf31s3f29s5f27s7f25+s2Mf26Ms4f28s6f30Ps8f16)>>SCALE)+
         (abs(s1Pf25s3f27s5f29s7f31+s2Pf30Ms4f28s6f26Ms8f24)>>SCALE);
  fft[10]=(abs(s6Pf29f27Ms2Pf31f25-s4Pf30f22Ps8Mf24)>>SCALE)+
          (abs(s4Mf30f26Ms8Mf28-s6Mf31f25Ms2Mf29f27)>>SCALE);
  fft[11]=(abs(s1Mf27s3f31s5f25s7f29+s2Mf30Ps4f28s6f26Ps8f16)>>SCALE)+
          (abs(s1Pf29s3f25s5f31s7f27+s2Pf26Ps4f28s6f30Ms8f24)>>SCALE);
  fft[12]=(abs(s8Pf28f24f20f16+s4Pf31f29f27f25)>>SCALE)+
          (abs(s8Mf30f18f26f22-s4Mf31f29f27f25)>>SCALE);
  fft[13]=(abs(s1Mf29s3f25s5f31s7f27+s2Mf30Ms4f28s6f26Ms8f16)>>SCALE)+
          (abs(s1Pf27s3f31s5f25s7f29+s2Pf26Ms4f28s6f30Ps8f24)>>SCALE);
  fft[14]=(abs(s4Pf30f22Ms8Mf24-s6Pf31f25Ps2Pf29f27)>>SCALE)+
          (abs(s4Mf30f26Ps8Mf28-s6Mf29f27Ps2Mf31f25)>>SCALE);
  fft[15]=(abs(s2Mf26Ps4f28s6f30Ms8f16-s1Mf25s3f27s5f29s7f31)>>SCALE)+
          (abs(s2Pf30Ps4f28s6f26Ps8f24-s1Pf31s3f29s5f27s7f25)>>SCALE);
#ifdef DEBUG
  for (l=1 ; l<N ; l++) a[l]=b[l]=0;
  for (k=0 ; k<(N+N) ; k++) 
    for (l=1 ; l<N ; l++) {
      kl=(l*k)%(N+N);
      a[l]+=f[k]*c[kl];
      b[l]+=f[k]*s[kl];
    }
  for (l=1 ; l<N ; l++) {
    fff[l]=(abs(a[l])>>SCALE)+(abs(b[l])>>SCALE);
    if (fff[l]!=fft[l]) printf("l:%2d fft:%3d fff:%3d\n",l,fft[l],fff[l]);
  }
#endif
#ifdef FFTDEBUG
  gotoxy(1,1);
  for (l=1 ; l<N ; l++) printf("%2d %7d\n",l,fft[l]);
#endif
  for (l=1,line=0 ; l<N ; l++,line+=160) {
    oldlevel=oldfft[l];
    level=oldfft[l]=fft[l];
    for (k=1,column=2 ; k<=level ; k++,column+=2) 
      pokeb(videoseg,80+line+column,'þ');
    for (k=level+1 ; k<=oldlevel ; k++,column+=2)  
      pokeb(videoseg,80+line+column,' ');
  }
}

/*------------------------------ FFT to Tone ---------------------------------*/

#define FLIP 5 /* levels above average sufficient to trigger tone detected */
#define LOG2N 4 /* Adjust according to N way above */ 

static int tonedetected=FALSE; /* indicates a tone is currently present */
static int freqm2,freqm1,freqp1,freqp2,freq=(N>>1); /* interesting frequency */

void FFT2tone(void)
{ /* determines whether a morse tone is present or not */
  static int old3active,old2active=FALSE,old1active=FALSE,active=FALSE; 
  static int average,l,limit,oldtonedetected;

  average=0;
  for (l=1 ; l<N ; l++) average+=fft[l];
  average>>=LOG2N;
  limit=FLIP+(5*average);
  old3active=old2active;
  old2active=old1active;
  old1active=active;
  active=( (fft[freqm2]+fft[freqp2]+fft[freqm1]+fft[freqp1]+fft[freq])>=limit );
  oldtonedetected=tonedetected;
  tonedetected=(active || old1active || old2active || old3active);
  if (tonedetected && !oldtonedetected) pokeb(videoseg,158,'Û');
  else if (oldtonedetected && !tonedetected) pokeb(videoseg,158,'þ');
}

/*----------------------------- Tone to Morse --------------------------------*/

#define M 8 /* number of elements used to compute average element */
#define LOG2M 3 /* adjust according to M above */

static int reset=TRUE;
static int counterdots=0,counterdashes=0;
static int sumdots=0,sumdashes=0;
static int avrgdot=0,avrgdash=0;
static int dots[M],dashes[M];
static int dot=FALSE,dash=FALSE,space=FALSE;
static int oncounter=0,offcounter=0;
static int firsttone=0;

void learn(void)
{ /* learn dot and dash duration out of tone detection */

  if (tonedetected) oncounter+=waitfactor;
  else 
    if (oncounter>0) {
      /* tone oncounter long just completed */
      if (counterdots==0) { /* not one of each yet, must be starting to learn */
        if (firsttone==0) firsttone=oncounter;
        else /* make sure tones are different enough, ie dot and dash */
          if (firsttone>oncounter) { /* which is dash and which is dot? */
            if (firsttone>(oncounter<<1)) { /* firsttone=dash oncounter=dot */
              dashes[0]=sumdashes=avrgdash=firsttone;
              dots[0]=sumdots=avrgdot=oncounter;
              counterdashes=counterdots=1;
            } else firsttone=oncounter; /* not different enough */
          } else {
            if (oncounter>(firsttone<<1)) { /* oncounter=dash firsttone=dot */
              dashes[0]=sumdashes=avrgdash=oncounter;
              dots[0]=sumdots=avrgdot=firsttone;
              counterdashes=counterdots=1;
            } else firsttone=oncounter; /* not different enough */
          }
      } else { /* at least one instance of dot and dash encountered so far */
        if (oncounter>((avrgdot+avrgdash)>>1)) {
          if (counterdashes<M) { /* still some to learn about dashes */
            dashes[counterdashes]=oncounter;
            sumdashes+=oncounter;
            counterdashes++;
            avrgdash=sumdashes/counterdashes;
          }
        } else {
          if (counterdots<M) { /* still some to learn about dots */
            dots[counterdots]=oncounter;
            sumdots+=oncounter;
            counterdots++;
            avrgdot=sumdots/counterdots;
          }
        }
        if ((counterdots==M) && (counterdashes==M)) { /* enough learning */
          counterdots=counterdashes=0;
          reset=FALSE;
        }
      }
      oncounter=0;
    }
}

void tone2morse(void)
{ /* deduces dot or dash or space out of tone detection */

  if (tonedetected) {
    oncounter+=waitfactor;
    if (offcounter>0) {
      /* silence offcounter long just completed */
      if (offcounter>((avrgdot+avrgdot+avrgdot+avrgdash)>>2)) space=TRUE;
      offcounter=0;
    }
  } else {
    offcounter+=waitfactor;
    if (oncounter>0) {
      /* tone oncounter long just completed */
      if (oncounter>((avrgdot+avrgdash)>>1)) {
        dash=TRUE;
        sumdashes-=dashes[counterdashes];
        dashes[counterdashes]=oncounter;
        sumdashes+=oncounter;
        avrgdash=(sumdashes>>LOG2M);
        if (counterdashes==(M-1)) counterdashes=0;
        else counterdashes++;
      } else {
        dot=TRUE;
        sumdots-=dots[counterdots];
        dots[counterdots]=oncounter;
        sumdots+=oncounter;
        avrgdot=(sumdots>>LOG2M);
        if (counterdots==(M-1)) counterdots=0;
        else counterdots++;
      }
      oncounter=0;
    }
  }
}

/*----------------------------- Morse to Text --------------------------------*/

void morse2text(void)
{ /* outputs text on the screen */
  static int code=0,mask=1,x=1,y=1,y160=160,punctuation;
  static char c;

  if (dot) {
    code+=mask;
    mask<<=1;
    dot=FALSE;
  } else
    if (dash) {
      mask<<=1;
      dash=FALSE;
    } else
      if (space) {
        code+=mask;
        switch (code) {
          case 2:c='T'; punctuation=FALSE; break;
          case 3:c='E'; punctuation=FALSE; break;
          case 4:c='M'; punctuation=FALSE; break;
          case 5:c='A'; punctuation=FALSE; break;
          case 6:c='N'; punctuation=FALSE; break;
          case 7:c='I'; punctuation=FALSE; break;
          case 8:c='O'; punctuation=FALSE; break;
          case 9:c='W'; punctuation=FALSE; break;
          case 10:c='K'; punctuation=FALSE; break;
          case 11:c='U'; punctuation=FALSE; break;
          case 12:c='G'; punctuation=FALSE; break;
          case 13:c='R'; punctuation=FALSE; break;
          case 14:c='D'; punctuation=FALSE; break;
          case 15:c='S'; punctuation=FALSE; break;
          case 17:c='J'; punctuation=FALSE; break;
          case 18:c='Y'; punctuation=FALSE; break;
          case 19:c='š'; punctuation=FALSE; break;
          case 20:c='Q'; punctuation=FALSE; break;
          case 21:c='Ž'; punctuation=FALSE; break;
          case 22:c='X'; punctuation=FALSE; break;
          case 23:c='V'; punctuation=FALSE; break;
          case 24:c='™'; punctuation=FALSE; break;
          case 25:c='P'; punctuation=FALSE; break;
          case 26:c='C'; punctuation=FALSE; break;
          case 27:c='F'; punctuation=FALSE; break;
          case 28:c='Z'; punctuation=FALSE; break;
          case 29:c='L'; punctuation=FALSE; break;
          case 30:c='B'; punctuation=FALSE; break;
          case 31:c='H'; punctuation=FALSE; break;
          case 32:c='0'; punctuation=FALSE; break;
          case 33:c='1'; punctuation=FALSE; break;
          case 35:c='2'; punctuation=FALSE; break;
          case 36:c='¥'; punctuation=FALSE; break;
          case 39:c='3'; punctuation=FALSE; break;
          case 41:c=''; punctuation=FALSE; break;
          case 47:c='4'; punctuation=FALSE; break;
          case 48:c='9'; punctuation=FALSE; break;
          case 54:c='/'; punctuation=FALSE; break;
          case 56:c='8'; punctuation=FALSE; break;
          case 59:c=''; punctuation=FALSE; break;
          case 60:c='7'; punctuation=FALSE; break;
          case 62:c='6'; punctuation=FALSE; break;
          case 63:c='5'; punctuation=FALSE; break;
          case 76:c=','; punctuation=TRUE; break;
          case 82:c='|'; punctuation=FALSE; break;
          case 85:c='.'; punctuation=TRUE; break;
          case 94:c='-'; punctuation=FALSE; break;
          case 106:c=';'; punctuation=TRUE; break;
          case 115:c='?'; punctuation=TRUE; break;
          case 120:c=':'; punctuation=TRUE; break;
          default:c='þ'; punctuation=FALSE; break;
        }
        pokeb(videoseg,(x<<1)+y160,c);
        x++;
        if (x==35) {
          y++; y160+=160;
          if (y==24) {y=1; y160=160;}
          for (x=1 ; x<35 ; x++) pokeb(videoseg,(x<<1)+y160,' ');
          x=1;
        }
        if (punctuation) {
          pokeb(videoseg,(x<<1)+y160,' ');
          x++;
          if (x==35) {
            y++; y160+=160;
            if (y==24) {y=1; y160=160;}
            for (x=1 ; x<35 ; x++) pokeb(videoseg,(x<<1)+y160,' ');
            x=1;
          }
        }
        pokeb(videoseg,(x<<1)+y160,'_');
        code=0; mask=1;
        space=FALSE;
      }
}

/*-------------------------------- Keyboard ----------------------------------*/

void updatecursor(char c1, char c2)
{ /* displays selected frequency cursor */
  freqp1=freq+1; freqm1=freq-1; freqp2=freq+2; freqm2=freq-2;
  pokeb(videoseg,(74-160)+(160*freqm2),c1);
  pokeb(videoseg,(74-160)+(160*freqm1),c1);
  pokeb(videoseg,(74-160)+(160*freq),c1);
  pokeb(videoseg,(74-160)+(160*freqp1),c1);
  pokeb(videoseg,(74-160)+(160*freqp2),c1);
  pokeb(videoseg,(76-160)+(160*freqm2),c2);
  pokeb(videoseg,(76-160)+(160*freqm1),c2);
  pokeb(videoseg,(76-160)+(160*freq),c2);
  pokeb(videoseg,(76-160)+(160*freqp1),c2);
  pokeb(videoseg,(76-160)+(160*freqp2),c2);
}

#include <bios.h>

#define UPKEY     0x4800
#define SUPKEY    0x4838
#define SFIVEKEY  0x4C35
#define DOWNKEY   0x5000   
#define SDOWNKEY  0x5032
#define ESCKEY    0x011B
#define PLUSKEY   0x4E2B
#define PLUSKEY2  0x0D2B
#define MINUSKEY  0x4A2D
#define MINUSKEY2 0x0C2D
#define SPACEKEY  0x3920
#define STARKEY   0x372A
#define STARKEY2  0x092A
#define OFFSTRING "Toggle FFT On/Off with Space  (now off)"
#define ONSTRING  "Toggle FFT On/Off with Space  (now on) "
#define WAITSTRING "S-Blaster DSP Mixture Ratio 1:%d  (+/-) "

void handlekey(int *done)
{ /* read key pressed and act accordingly */
  updatecursor(' ',' ');
  switch (bioskey(0)) {
    case UPKEY:if (freq>3) freq--; break;
    case DOWNKEY:if (freq<(N-3)) freq++; break;
    case SUPKEY:freq=3; break;
    case SDOWNKEY:freq=N-3; break;
    case SFIVEKEY:freq=(N>>1); break;
    case PLUSKEY:
    case PLUSKEY2:waitfactor++; gotoxy(40,25);
                  cprintf(WAITSTRING,waitfactor);
                  break;
    case MINUSKEY:
    case MINUSKEY2:if (waitfactor>1) {
                     waitfactor--; gotoxy(40,25);
                     cprintf(WAITSTRING,waitfactor);
                   }
                   break;
    case SPACEKEY:FFTenable=!FFTenable; 
                  gotoxy(40,20);
                  if (FFTenable) cprintf(ONSTRING); 
                  else cprintf(OFFSTRING);
                  break;
    case STARKEY:
    case STARKEY2:reset=TRUE; 
                  counterdots=counterdashes=0;
                  sumdots=sumdashes=0;
                  avrgdot=avrgdash=0;
                  firsttone=0;
                  break;
    case ESCKEY:*done=TRUE; break;
  }
  updatecursor('=','>');
}

/*------------------------------- Initialize ---------------------------------*/

#ifdef DEBUG
#include <math.h>
#endif

#ifdef DEBUG
#define CTEPI (3.14159265358979323846/(float)N)
#define TRIG  16 /* trig table lookup precision compatible with S? way above */
#endif
#define COPYSTRING "FFT Morse (c) 1992 Fran‡ois Jalbert"
#define FREQSTRING "Lock Frequency with Up and Down Arrows"
#define EXITSTRING "Exit with Esc"

void begin(void)
{ /* initializes screen, data & SB */
#ifdef DEBUG
  static float xx,ss,cc;
  static int k;
#endif
  static int l,line,xx,yy;
  static struct text_info info;

  clrscr();
  if (reset_dsp()!=SBOK) {
    printf("Ne peut pas initialiser DSP!\7\n\n");
    exit(1);
  }
  gettextinfo(&info);
  if (info.currmode==7) videoseg=0xB000;
  for (xx=1 ; xx<=34 ; xx++) pokeb(videoseg,(xx<<1),'Ä');
  for (xx=1 ; xx<=34 ; xx++) pokeb(videoseg,(xx<<1)+(160*24),'Ä');
  for (yy=1 ; yy<=23 ; yy++) pokeb(videoseg,(160*yy),'³');
  for (yy=1 ; yy<=23 ; yy++) pokeb(videoseg,(35<<1)+(160*yy),'³');
  pokeb(videoseg,0,'Ú');
  pokeb(videoseg,(35<<1),'¿');
  pokeb(videoseg,(160*24),'À');
  pokeb(videoseg,(35<<1)+(160*24),'Ù');
  gotoxy(40,17); cprintf(COPYSTRING);
  gotoxy(40,19); cprintf(FREQSTRING);
  gotoxy(40,20); if (FFTenable) cprintf(ONSTRING); else cprintf(OFFSTRING);
  gotoxy(40,21); cprintf(EXITSTRING);
  gotoxy(40,25); cprintf(WAITSTRING,waitfactor);
  updatecursor('=','>');
  for (l=1,line=0 ; l<N ; l++,line+=160) {
    fft[l]=0;
    pokeb(videoseg,80+line,'ð');
  }
#ifdef DEBUG
  for (k=0 ; k<(N+N) ; k++) {
    xx=CTEPI*k;
    ss=TRIG*sin(xx);
    cc=TRIG*cos(xx);
    if (ss>0.0) ss+=0.5; else ss-=0.5;
    if (cc>0.0) cc+=0.5; else cc-=0.5;
    s[k]=(int)ss; /* truncate */
    c[k]=(int)cc; /* truncate */
  }
#endif
}

/*---------------------------------- main ------------------------------------*/

#include <time.h>

#define KCHECK 64 /* ratio of key pressed checks versus FFT cycles  */
#define SCHECK 16 /* ratio of sampling rate checks versus key checks */
#define SAMPSTRING "%d S-Blaster Samples per Second  "
#define STATSTRING "Avrg Dot:%d  Avrg Dash:%d (* resets) "

void main(void)
{
  static int done=FALSE,counter=0;
  static int kloop,sloop,delta,k;
  static long int start,current;

  begin();
  time(&start);
  speaker_on();
  while (!done) {
    for (sloop=1 ; sloop<=SCHECK ; sloop++) {
      if (FFTenable) 
        for (kloop=1 ; kloop<=KCHECK ; kloop++) {
          FFT();
          FFT2tone();
          if (reset) learn();
          else {
            tone2morse();
            morse2text(); 
          }
        }
      else
        for (kloop=1 ; kloop<=KCHECK ; kloop++)
          for (k=0 ; k<(N+N) ; k++) read_data();
      if (bioskey(1)!=0) {
        handlekey(&done);
        if (done) goto abortit; /* get out quickly, facultative statement */
      }
    }
    counter+=(N+N);
    time(&current);
    delta=(int)(current-start);
    if (delta>2) {
      gotoxy(40,24);
      cprintf(SAMPSTRING, counter*((KCHECK*SCHECK)/delta) );
      start=current;
      counter=0;
    } 
    gotoxy(40,23);
    cprintf(STATSTRING,avrgdot,avrgdash);
  }
  abortit:
  speaker_off();
  gotoxy(1,24);
}
