import curses
import sys
import time
import pprint
import platform

global stdscr



def isWindows():
  return platform.system() == "Windows"
  
def clrscr():
  stdscr.clear()
  stdscr.refresh()
  
def pokeb(memoryseg: int, xy: int, char):
  x = xy >> 1
  y = int((xy - x) / 160)
  y = int(xy / 160)
  x = int((xy - (160 * y)) / 2)
  stdscr.addch(y, x, char)
  return

def printfxy(x: int, y: int, format: str, *args):
  stdscr.addstr(y, x,  format % args)
  
def refresh():
  stdscr.refresh()
  
def gotoxy(x: int,y: int):
  global XPOS
  global YPOS
  XPOS=x
  YPOS=y

def printf(format: str, *args):
  sys.stdout.write(format % args)

def cprintf(format: str, *args):
  global XPOS
  global YPOS
  stdscr.addstr(YPOS, XPOS, format % args)
  
def nodelay(flag: bool):
  stdscr.nodelay(flag)
  
def getlastkeypressed():
  global lastkeypressed
  return lastkeypressed
  
def iskeypressed():
  global lastkeypressed
  lastkeypressed = stdscr.getch()  
  return lastkeypressed != curses.ERR

def init():
  global stdscr
  stdscr = curses.initscr()
  curses.noecho()
  curses.curs_set(False)
  if curses.has_colors():
    curses.start_color()  
  stdscr.keypad(True)
  
def deinit():
  global stdscr
  curses.nocbreak()
  curses.echo()
  curses.curs_set(True)
  curses.endwin()

if __name__ == "__main__":

  #curses.noecho()
  #curses.cbreak()
  #curses.curs_set(False)
  init()
  stdscr.addstr(0, 0, "Hello, world from curses!")
  print("Hello world with print")
  
  stdscr.getch()
  nodelay(True)
  while(not iskeypressed()):
    #print("in the loop...")
    time.sleep(0.1)
  k = getlastkeypressed()
  print("You quit with ", k, "which is ", curses.keyname(k) )
  
  
  
  # BEGIN ncurses shutdown/deinitialization...
  # Turn off cbreak mode...
  curses.nocbreak()

  # Turn echo back on.
  curses.echo()

  # Restore cursor blinking.
  curses.curs_set(True)

  # Turn off the keypad...
  # stdscr.keypad(False)

  # Restore Terminal to original state.
  curses.endwin()
  