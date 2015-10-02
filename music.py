#-----------------------------------------------------
# DEPENDENCY: pygame library
import wave, struct, sys
import pygame

nchannels=0
sampwidth=0
framerate=0
nframes=0
comptype=0
compname=0

#-----------------------------------------------------
# LIST MANIPULATION METHODS

def everyOther (v, offset=0):
   return [v[i] for i in range(offset, len(v), 2)]

# ls0 and ls1 are 0- and 1-offset halves respectively
# makes assumption that lists are same length (safe in this context)
def repack(ls0, ls1):
	tor = []
	for i in range(0, len(ls0)):
		tor.append(ls0[i])
		tor.append(ls1[i])
	return tor

def subtract(l1, l2):
   tor = []
   items = len(l1)
   for i in range(0, items):
      tor.append(l1[i] - l2[i])
   return tor

# Removes amplitude values |x| > 32000 since struct.pack can only process short values
def flatten(ls):
   tor=[]
   for item in ls:
      if(item< -32000):
         tor.append(-32000)
      elif(item>32000):
         tor.append(32000)
      else:
         tor.append(item)
   return tor

#-----------------------------------------------------

# Returns tuple of (wave object, left frame buffer, right frame buff)
def wavExtract (fname):
   print("Extracting left/right channels...")
   wav = wave.open (fname, "r")
   global nchannels
   global sampwidth
   global framerate
   global nframes
   global comptype
   global compname
   (nchannels, sampwidth, framerate, nframes, comptype, compname) = wav.getparams()
   frames = wav.readframes (nframes * nchannels)

   # CONVERTS FROM WAV TO LIST
   out = struct.unpack_from ("%dh" % nframes * nchannels, frames)

   # CONVERTS FROM LIST BACK TO WAV 
   orig = struct.pack('%sh' % (nframes * nchannels), *out)
   # Convert 2 channles to arrays
   if nchannels == 2:
       left = list (everyOther (out, 0))
       right = list  (everyOther (out, 1))

   return (wav, left, right)

# Distance to right -> positive nframes value
# Distance to left -> negative nframes value
def delay(nframes, left, right):
   # Right needs shifted backward (0's to end) -> Left forward (0's to beginning)
   print("Delaying channels...")
   size = len(left)
   return_l = []
   return_r = []
   for i in range(0, nframes):
      return_l.append(0)
   for i in range(0, size):
      return_r.append(right[i])
      return_l.append(left[i])
   for i in range(0, nframes):
      return_r.append(0)
   return (return_l, return_r)

def negdelay(nframes, left, right):
   print("Delaying channels...")
   size = len(left)
   return_l = []
   return_r = []
   for i in range(0, nframes):
      return_r.append(0)
   for i in range(0, size):
      return_l.append(left[i])
      return_r.append(right[i])
   for i in range(0, nframes):
      return_l.append(0)
   return (return_l, return_r)

# Converts left/right int arrays to WAV file
def framesToWAV(orig_wav, lframes, rframes, delay):
   print("Converting new frames to WAV...")
   outp = wave.open(sys.argv[2], "w")
   outp.setnchannels(orig_wav.getnchannels())
   outp.setsampwidth(orig_wav.getsampwidth())
   outp.setframerate(orig_wav.getframerate())
   frames = struct.pack('%sh' % 2*len(lframes), *repack(lframes, rframes))
   outp.writeframes(frames)
   outp.close()

# Plays WAV file
def play(filename):
   print("Playing final song...")
   pygame.mixer.init()
   pygame.mixer.music.load(filename)
   pygame.mixer.music.play()
   while pygame.mixer.music.get_busy() == True:
      continue 

(wav, left, right) = wavExtract(sys.argv[1])
diff = int(sys.argv[3])
if(diff<0):
   (newl, newr) = negdelay(int(sys.argv[3]), left, right)
else:
   (newl, newr) = delay(int(sys.argv[3]), left, right)

(newl, newr) = (left, right)
subt = flatten(subtract(newr, newl))

framesToWAV(wav, subt, subt, int(sys.argv[3]))
play(sys.argv[2])



