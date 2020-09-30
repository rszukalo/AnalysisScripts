# Python


import sys
import math

def get_bin(value,min,max,step):
  i = 0
  test = min
  while ( value > min + (i + 1) * step + 0.000000000001):
    i += 1
  return i

def get_stdev(avg,list):
  stdev = 0
  for i in range(len(list)):
    stdev += (list[i] - avg) ** 2
  stdev /= (len(list)-1)
  stdev = stdev ** 0.5
  stdev = stdev / (len(list) ** 0.5)
  return stdev


PV = [[0,0]]

print("PV2.py constructs the PV EoS with error bars using a fixed bin width (specified with -bw, default 0.1)")



if (len(sys.argv) < 2):
  print("ERROR: specify the mode as a command line argument.")
  print("Acceptable modes are: LAMMPS GMX")
  exit()

MODE = sys.argv[1]

if (MODE == "LAMMPS"):
#  fp = open("pv_eos.dat",'r')
#  if (fp.closed):
    fvol = open("vol.dat",'r')
    fpress = open("press.dat",'r')
    if (fvol.closed):
      print("ERROR: with MODE = LAMMPS, I expect to find a file vol.dat")
      exit()
    if (fpress.closed):
      print("ERROR: with MODE = LAMMPS, I expect to find a file press.dat")
      exit()
    vline = fvol.readline()
    pline = fpress.readline()
    while (vline != ""):
      if (vline[0] == '#'):
        while (vline[0] == '#'):
          vline = fvol.readline()
      if (pline[0] == '#'):
        while (pline[0] == '#'):
          pline = fpress.readline()
      vtok = vline.split()
      ptok = pline.split()
      if (vtok[0] != ptok[0]):
        print("ERROR: The times in vol.dat and press.dat aren't the same.")
        print("vol.dat:   " + vtok[0])
        print("press.dat: " + ptok[0])
        exit()
      PV += [[float(vtok[1]),float(ptok[1])]] 
      vline = fvol.readline()
      pline = fpress.readline()  
    fvol.close()
    fpress.close()
#  else:
#    for line in fp:
#      if (line[0] != "#"):
#        tok = line.split()
#        PV += [[float(tok[0]),float(tok[1])]]
#    fp.close()
elif (MODE == "GMX"):
  infile = open("PV.xvg",'r')
  if (infile.closed):
    print("ERROR: with MODE = GMX I expect to find a file PV.xvg")
    print("PV.xvg should be generated with g_energy, and you should")
    print("select only the Pressure and Volume properties.")
    exit()
  line = infile.readline()
  while (line[0] == '#' or line[0] == '@'):
    line = infile.readline()
  while (line != ""):
    tok = line.split()
    PV += [[float(tok[2]),float(tok[1])]]
    line = infile.readline()
  infile.close()

PV.remove([0,0])

min_vol = 999999
max_vol = 0
for i in range(len(PV)):
  if (PV[i][0] < min_vol):
    min_vol = PV[i][0]
  if (PV[i][0] > max_vol):
    max_vol = PV[i][0]


BIN_WIDTH = 0.1

for i in range(len(sys.argv)):
  if sys.argv[i] == "-bw":
    BIN_WIDTH = float(sys.argv[i+1])
  if sys.argv[i] == "-h":
    print("first, give mode GMX or LAMMPS")
    print("cmd line args: -bw")
    exit()

print("Bin width: " + str(BIN_WIDTH))

n_bins = int((max_vol-min_vol)/BIN_WIDTH) + 2

volumes = []
pressures = []
counts = []
plists = [[] for i in range(n_bins)]
minv = min_vol - math.fmod(min_vol,BIN_WIDTH)
for i in range(n_bins):
  volumes += [minv + (i + 0.5) * BIN_WIDTH]
#  volumes += [min_vol + i * dV]
  pressures += [0]
  counts += [0]

print("Min vol: " + str(min_vol))
print("Max vol: " + str(max_vol))
print("Min bin: " + str(volumes[0]))
print("Max bin: " + str(volumes[-1]))

for i in range(len(PV)):
  bin = get_bin(PV[i][0],minv,max_vol,BIN_WIDTH)
  if (bin > n_bins-1):
    print("ERROR: bin = " + str(bin))
    print("max_vol = " + str(max_vol))
    print("volume = " + str(PV[i][0]))
    raw_input("Enter to continue.")
  pressures[bin] += PV[i][1]
  counts[bin] += 1
  plists[bin] += [PV[i][1]]
fnm = "PVcurve.bw." + str(BIN_WIDTH) + ".dat"
outfile = open(fnm,'w')
for i in range(n_bins):
  if (counts[i] > 0):
    pressures[i] /= counts[i]
    if len(plists[i]) > 1:  
      stdev = get_stdev(pressures[i],plists[i])
    else:
      stdev = 0
    outfile.write(str(volumes[i]) + " " + str(pressures[i]) + " " + str(stdev) + "\n")  
outfile.close()


