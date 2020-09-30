import sys, os, glob
import numpy as np

FLAG = 0
VALUE = 1
PROVIDED = 2
REQUIRED = 3
DESC = 4

cmd_line_args = []

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

def movingaverage(interval, window_size):
    window = np.ones(int(window_size))/float(window_size)
    #print(window_size, window)
    return np.convolve(interval, window, 'valid')

#################################################################################################################

# Create list of energy files in folder, extract interaction type
currdir = os.getcwd()

efilelist = []		#list of path/to/file for all outputfiles

for file in glob.glob('*energy*'):
    if (file.split('_')[0] != 'smooth' and file.split('_')[0] != 'trim'):
        efilelist.append(file)

print('There are ' + str(len(efilelist)) + ' energy files')

# Trim front off nb files, both ends of bonded files
# Smooth only the nb files
nb_init = 0.33
b_trim = 5
WD = 13

x = []
y = []

for i in range(len(efilelist)):
    with open(efilelist[i], 'r') as f:
        lines = f.read().splitlines() 

        for j in range(len(lines)):
                b = lines[j].split()
        
                if efilelist[i].split('_')[0] == 'pair':
                        if float(b[0]) < nb_init:
                            pass
                        else:
                            x.append(float(b[0]))
                            y.append(float(b[1]))
                else:
                    if (j >= b_trim and j <= (len(lines) - b_trim)):
                        x.append(float(b[0]))
                        y.append(float(b[1]))

    with open('trim_' + str(efilelist[i]), 'w') as g:
        for j in range(len(x)):
            g.write(str(x[j]) + ' ' + str(y[j]) + '\n') 
    
    if efilelist[i].split('_')[0] == 'pair':    

        temp = efilelist[i].split('_')[-1]
        inter = efilelist[i].split('_')[2] + '_' + temp.split('.')[0]
        
        trim_len = int(WD/2)
        del(x[0:trim_len])
        del(x[len(x)-trim_len:])

        temp = movingaverage(y, WD)
        y = list(temp)

        if len(x) == len(y):
            with open('smooth_' + str(efilelist[i]), 'w') as h:
                for j in range(len(x)):
                    h.write(str(x[j]) + ' ' + str(y[j]) + '\n')
        
        # Work to create nb Table Files
        
        x_init = float(x[0])
        x_final = float(x[-1])
        bw = round((x[2] - x[1]), 3)
        
        b_init = ((y[0] * x[1]) - (y[1] * x[0])) / (x[1] - x[0])
        m_init = (y[1] - b_init) / x[1]
        m_final = (y[-2] - y[-1]) / (x[-2] - x[-1]) # To be used to smooth end of curve to 0 rather than abrubtly switching to 0.0
       
        if m_final < 0:
            m_final = -m_final

        b_final = y[-1] - (m_final * x[-1])

        table_length = int(round((4.000 / bw), 0)) + 1
        table_start = int(round((x_init / bw), 0))
        table_final = int(round((x_final / bw), 0))

        mid = '  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  '
        
        with open('table_' + str(inter) + '.xvg', 'w') as p:
            for d in range(table_length):
                if (d < table_start):
                    value = (m_init * (d * bw)) + b_init
                    p.write('    ' + str('%.6f' % (d * bw)) + mid + '{:.6E}'.format(value) + '  ' + '{:.6E}'.format(0 - m_init) + '\n')
                
                elif (d < table_final):
                    value = y[d - table_start]
                    p.write('    ' + str('%.6f' % (d * bw)) + mid + '{:.6E}'.format(value) + '  ' + '{:.6E}'.format(0 - m_init) + '\n')
       
                elif (d >= table_final):
                    value = (m_final * (d * bw)) + b_final 
                    if (value < 0.0):
                        p.write('    ' + str('%.6f' % (d * bw)) + mid + '{:.6E}'.format(value) + '  ' + '{:.6E}'.format(0 - m_init) + '\n')
                    else:
                        p.write('    ' + str('%.6f' % (d * bw)) + mid + '{:.6E}'.format(0.000) + '  ' + '{:.6E}'.format(0.000) + '\n')
    
    elif efilelist[i].split('_')[0] == 'bond':
        
        x_init = float(x[0])
        x_final = float(x[-1])
        bw = round((x[2] - x[1]), 3)
    
        table_length = int(round((0.800 / bw), 0)) + 1
        table_start = int(round((x_init / bw), 0))
        table_final = int(round((x_final / bw), 0))
        
        with open('table_b0.xvg', 'w') as p:
            for d in range(table_length):
                if (d < table_start):
                    value = y[0]
                    p.write('    ' + str('%.6f' % (d * bw)) + ' ' + '{:.6E}'.format(value) + '  ' + '{:.6E}'.format(y[0]) + '\n')

                elif (d < table_final):
                    value = y[d - table_start]
                    p.write('    ' + str('%.6f' % (d * bw)) + ' ' + '{:.6E}'.format(value) + '  ' + '{:.6E}'.format(y[0]) + '\n')

                elif (d >= table_final):
                    value = y[-1]
                    p.write('    ' + str('%.6f' % (d * bw)) + ' ' + '{:.6E}'.format(value) + '  ' + '{:.6E}'.format(y[-1]) + '\n')
 
    elif efilelist[i].split('_')[0] == 'angle':

        x_init = float(x[0])
        x_final = float(x[-1])
        bw = round((x[2] - x[1]), 3)

        table_length = int(round((180.0 / bw), 0)) + 1
        table_start = int(round((x_init / bw), 0))
        table_final = int(round((x_final / bw), 0))

        with open('table_a0.xvg', 'w') as p:
            for d in range(table_length):
                if (d < table_start):
                    value = y[0]
                    p.write('    ' + str('%.6f' % (d * bw)) + ' ' + '{:.6E}'.format(value) + '  ' + '{:.6E}'.format(y[0]) + '\n')

                elif (d < table_final):
                    value = y[d - table_start]
                    p.write('    ' + str('%.6f' % (d * bw)) + ' ' + '{:.6E}'.format(value) + '  ' + '{:.6E}'.format(y[0]) + '\n')

                elif (d >= table_final):
                    value = y[-1]
                    p.write('    ' + str('%.6f' % (d * bw)) + ' ' + '{:.6E}'.format(value) + '  ' + '{:.6E}'.format(y[-1]) + '\n')

    elif efilelist[i].split('_')[0] == 'dihedral':

        x_init = float(x[0])
        x_final = float(x[-1])
        bw = round((x[2] - x[1]), 3)

        table_length = int(round((360 / bw), 0)) + 1
        table_start = int(round((x_init / bw), 0))
        table_final = int(round((x_final / bw), 0))

        with open('table_d0.xvg', 'w') as p:
            for d in range(table_length):
                if (d < table_start):
                    value = y[0]
                    p.write('    ' + str('%.6f' % (d * bw)) + ' ' + '{:.6E}'.format(value) + '  ' + '{:.6E}'.format(y[0]) + '\n')

                elif (d < table_final):
                    value = y[d - table_start]
                    p.write('    ' + str('%.6f' % (d * bw)) + ' ' + '{:.6E}'.format(value) + '  ' + '{:.6E}'.format(y[0]) + '\n')

                elif (d >= table_final):
                    value = y[-1]
                    p.write('    ' + str('%.6f' % (d * bw)) + ' ' + '{:.6E}'.format(value) + '  ' + '{:.6E}'.format(y[-1]) + '\n')





    x.clear()
    y.clear()
            
            

