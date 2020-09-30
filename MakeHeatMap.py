# Python 3

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import sys
import math


def transpose_matrix(mat):
  n_orig_rows = len(mat)
  n_orig_cols = len(mat[0])
  newmat = [[mat[i][j] for i in range(n_orig_rows)] for j in range(n_orig_cols)]
  return newmat

LOG = False
SYM0 = False
TRIM = False
colorscheme = 'hot'
zlim_val = 0.0
for i in range(len(sys.argv)):
  if sys.argv[i] == "-h":
    print("Give the file to graph as the first command line argument.")
    print("optional command line args:")
    print("-log VAL : takes the absolute values of everything, and displays all values above VAL in a logscale")
    print("-trim    : trims leading/trailing rows/columns of 0s")
    print("-sym0    : use this if your data is both positive and negative and you want a distinction between the two")
    print("-cs VAL  : use this to use a colorscheme other than cool")
    print("-zlim VAL: use this to manually specify the limit of the color bar")
    exit()
  if sys.argv[i] == "-log":
    LOG = True
    logtrim = float(sys.argv[i+1])
  if sys.argv[i] == "-trim":
    TRIM = True
  if sys.argv[i] == "-sym0":
    SYM0 = True
  if (sys.argv[i] == "-cs"):
    colorscheme = sys.argv[i+1]
  if (sys.argv[i] == "-zlim"):
    zlim_val = float(sys.argv[i+1])
 
fp = open(sys.argv[1],'r')


x = -99
y = -99
z = -99

xmin = 999999
xmax = -999999
xmin0 = 999999
xmax0 = -999999
ymin = 999999
ymax = -999999
ymin0 = 999999
ymax0 = -999999
zmin = 999999
zmax = -999999
zmaxx = 0
zmaxy = 0
zminx = 0
zminy = 0

line = fp.readline()
matrix = []
matrix2 = []
lnum = 0
while (line[0] == "#"):
  line = fp.readline()
while (line != ""):
  tok = line.split()
  xprev = x
  x = float(tok[0])
  y = float(tok[1])
  z = float(tok[2])
  if (x < xmin):
    xmin = x
  if (x > xmax):
    xmax = x
  if (y < ymin):
    ymin = y
  if (y > ymax):
    ymax = y
  if (z > 0):
    if (x < xmin0):
      xmin0 = x
    if (x > xmax0):
      xmax0 = x
    if (y < ymin0):
      ymin0 = y
    if (y > ymax0):
      ymax0 = y
  if (x != xprev):
    matrix += [[]]
    matrix2 += [[]]
  matrix[-1] += [z]    
  matrix2[-1] += [math.fabs(z)]
  if (z < zmin):
    zmin = z
    zminx = x
    zminy = y
  if (z > zmax):
    zmax = z
    zmaxx = x
    zmaxy = y
  line = fp.readline()
fp.close()

dx = (xmax - xmin) / (len(matrix)-1)
dy = (ymax - ymin - 1) / (len(matrix[0])-1)

xvals = [xmin + i * dx for i in range(len(matrix))]
yvals = [ymin + i * dy for i in range(len(matrix[0]))]

if (SYM0):
  if (zmin + zmax < 0):
    zmax = -1 * zmin
  else:
    zmin = -1 * zmax


if (TRIM):
  x_trim_end = int((xmax - xmax0) / dx - 2)
  x_trim_beg = int((xmin0 - xmin) / dx - 2)
  y_trim_end = int((ymax - ymax0) / dy - 2)
  y_trim_beg = int((ymin0 - ymin) / dy - 2)
  for i in range(x_trim_end):
    del(matrix[-1])
    del(matrix2[-1])
  for i in range(x_trim_beg):
    del(matrix[0])
    del(matrix2[0])
  for j in range(y_trim_end):
    for i in range(len(matrix)):
      del(matrix[i][-1])
      del(matrix2[i][-1])
  for j in range(y_trim_beg):
    for i in range(len(matrix)):
      del(matrix[i][0])
      del(matrix2[i][0])
  xmin = xmin0
  ymin = ymin0
  xmax = xmax0
  ymax = ymax0

newmatrix = transpose_matrix(matrix)
newmatrix2 = transpose_matrix(matrix2)



if (zlim_val > 0.0):
  if (zlim_val > zmax):
    zmax = zlim_val
    zmin = -1.0 * zlim_val


if (SYM0 and LOG):
  plt.imshow(newmatrix, cmap='seismic', origin='lower', aspect='auto', interpolation='nearest', extent=[xmin,xmax,ymin,ymax], vmin=zmin, vmax=zmax, norm=matplotlib.colors.SymLogNorm(logtrim))
elif (SYM0):    
  plt.imshow(newmatrix, cmap='seismic', origin='lower', aspect='auto', interpolation='nearest', extent=[xmin,xmax,ymin,ymax], vmin=zmin, vmax=zmax)
elif (LOG):
  plt.imshow(newmatrix2, cmap=colorscheme, origin='lower', aspect='auto', interpolation='nearest', extent=[xmin,xmax,ymin,ymax], norm=matplotlib.colors.LogNorm(logtrim))
else:
  plt.imshow(newmatrix, cmap=colorscheme, origin='lower', aspect='auto', interpolation='nearest', extent=[xmin,xmax,ymin,ymax], vmin=zmin, vmax=zmax)
plt.colorbar()
plt.show()







