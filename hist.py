import numpy as np
from math import *
from statistics import *
import sys
import math

FLAG = 0
VALUE = 1
PROVIDED = 2
REQUIRED = 3
DESC = 4

# Script will histrogram a set of y values based of the x values
# First bins the x vlaues, and calcualtes the average y value in
# each of the bins using a delta basis set.

cmd_line_args = [["-in","None",False,True,"Input File"],
                ["-ou","None",False,False,"Output File" ],
                ["-bw","None",False,False,"Bin Width"],
                ["-basis","None",False,False,"Basis set: either Delta or Linear"]]

for i in range(len(sys.argv)-1):
  for j in range(len(cmd_line_args)):
    if (sys.argv[i] == cmd_line_args[j][FLAG]):
      cmd_line_args[j][VALUE] = sys.argv[i+1]
      cmd_line_args[j][PROVIDED] = True
      if (cmd_line_args[j][VALUE].replace(".","1").isdigit()): # test if argument is a floating point number
        cmd_line_args[j][VALUE] = float(sys.argv[i+1])

for i in range(len(sys.argv)):
  if (sys.argv[i] == "-h"):
    for j in range(len(cmd_line_args)):
      print("%s %s (req: %s)" % (cmd_line_args[j][FLAG],cmd_line_args[j][DESC],cmd_line_args[j][REQUIRED]))
    print("-h to display this table")
    exit()

kill = False
for arg in cmd_line_args:
  if (arg[REQUIRED] and not arg[PROVIDED]):
    print("ERROR: you did not provide required argument: %s" % (arg))
    kill = True
if (kill):
  exit()

fin = open(cmd_line_args[0][VALUE], 'r')
fout = open(cmd_line_args[1][VALUE], 'w')
bw = cmd_line_args[2][VALUE]
basis = cmd_line_args[3][VALUE]

xdata_array = []
ydata_array = []

for line in fin:
        line = ( line.strip() ).split()
        if ( len(line) == 2 and ( line[0].strip() )[0] != "#" and (line[0].strip())[0] != "@" ):
                x = line[0].strip()
                y = line[1].strip()

                xpoint = float(x)
                ypoint = float(y)
                xdata_array.append( xpoint )
                ydata_array.append( ypoint )

if (len(xdata_array) != len(ydata_array)):
        sys.exit('Error: the x and y dimensions are not the same')

min = math.floor(min(xdata_array))
max = math.ceil(max(xdata_array))

n_bins = int((max - min) / bw)

bin_count = [ 0 for i in range(0, n_bins+1)  ]
hist = [ [] for i in range(0, n_bins+1)  ]
hist_norm = [ [] for i in range(0, n_bins+1)  ]

for i in range(len(xdata_array)):
        bin_index = int((xdata_array[i] - min) / bw)

        if basis == "Delta":
                hist[bin_index].append(ydata_array[i])
                bin_count[bin_index] += 1               
        if basis == "Linear":
                LB = bin_index
                UB = bin_index + 1
                
                A = (xdata_array[i] - (min + LB*bw)) / bw
                B = 1 - A
                
                if (A + B > 1):
                        print(str(i) + '\n' + str(A) + '\n' + str(B))
                        sys.exit("Error: Something wrong with linear spline coefficients")
                
                hist[LB].append(ydata_array[i]*A)
                hist[UB].append(ydata_array[i]*B)
                bin_count[LB] += A
                bin_count[UB] += B

#if (sum(bin_count) != len(xdata_array)):
if (math.fabs(sum(bin_count)-len(xdata_array)) > 0.01):
        print("sum(bin_count): %.10f    len(xdata_array): %d" % (sum(bin_count),len(xdata_array)))
#        sys.exit("Error: the length of the x values does not match the length of the sum of the entries in each bin")


for i in range(len(hist)):
        
        if len(hist[i]) == 0:
                hist_norm[i] = 0
        else:
#                hist_norm[i] = mean(hist[i])
                hist_norm[i] = sum(hist[i]) / bin_count[i]
                
if (len(bin_count) == len(hist_norm)):
        for i in range(len(bin_count)):
                dist = min + (i*bw)
                fout.write(str(dist) + ' ' + str(hist_norm[i]) + '\n')

print("Complete")
