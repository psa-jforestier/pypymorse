#!/usr/bin/env python3 -u

def getNumberFromString(s: str, bad = -1):
  e = s[-1:]
  m = 1
  if (e == 'M'):
    m = 1_000_000
  elif (e == 'K' or e == 'k'):
    m = 1_000
  if (m != 1):
    n = s[0:-1]
  else:
    n = s
  try:
    return float(float(n) * m)
  except:
    return bad
    
    
  
if __name__ == "__main__":
  print(getNumberFromString(''))
  print(getNumberFromString('123'))
  print(getNumberFromString('123.456'))
  print(getNumberFromString('123M'))
  print(getNumberFromString('123.456M'))
  print(getNumberFromString('123.456K'))
  print(getNumberFromString('123.456k'))
  print(getNumberFromString('0.1k'))
  print(getNumberFromString(b'868M'.decode(), -1))
  
