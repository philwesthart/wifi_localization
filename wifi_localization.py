#!/usr/bin/env python
# Author:      Phil Westhart
# Created:     February 2016

import subprocess
import numpy as np
import matplotlib.pyplot as plt
import math

MAX_DIST_FROM_ORIG = 10 # farthest distance in x or y a point can be from the origin in meters
CELL_WIDTH = 1 # grid cell dimension in meters
ORIG_OFFSET = MAX_DIST_FROM_ORIG/CELL_WIDTH
map = np.zeros((2*MAX_DIST_FROM_ORIG/CELL_WIDTH,2*MAX_DIST_FROM_ORIG/CELL_WIDTH))


print "Initializing wifi-localization"

print "Loading configuration from ./ap.conf"
ap1 = {'ap_name':'NETGEAR52', 'x':0, 'y':0}
ap2 = {'ap_name':'NETGEAR52', 'x':5, 'y':0}
ap3 = {'ap_name':'NETGEAR52', 'x':0, 'y':5}

target_aps = [ap1, ap2, ap3]

for t_ap in target_aps:
    map[(t_ap['x'] + ORIG_OFFSET)-1, (t_ap['y']+ ORIG_OFFSET)-1] = -1
    

def scan_for_wifi():
    print "Scanning for wifi..."
    out = subprocess.check_output(['sudo', './wavemon/wavemon'])
    out = out.split("\n")
    i = 0
    found_signals = {}
    ap_names = []
    for line in out:
        if len(line) > 0:
            i = i + 1
            ap_name = line[:-11]
            ap_name = ap_name.rstrip()
            ap_names.append(ap_name)
            signal_strength = line[-11:-2]
        #        print ap_name, signal_strength, "dB"
            found_signals[ap_name] = signal_strength

    print i, "access points found"
    dist = 2.5
    for ap in ap_names:
        for t_ap in target_aps:
            if ap == t_ap['ap_name']:
                for x in np.arange(-(MAX_DIST_FROM_ORIG), MAX_DIST_FROM_ORIG,CELL_WIDTH):
                    for y in np.arange(-(MAX_DIST_FROM_ORIG), MAX_DIST_FROM_ORIG,CELL_WIDTH):
                        if(math.sqrt((t_ap['x'] - x)**2+ (t_ap['y'] - y)**2) <= dist) : 
#                            print "t_ap['x'], x, t_ap['y'], y"
#                            print t_ap['x'], x, t_ap['y'], y
#                            print "(x+MAX_DIST_FROM_ORIG)/CELL_WIDTH: " , (x+MAX_DIST_FROM_ORIG)/CELL_WIDTH
                            map[(x+MAX_DIST_FROM_ORIG)/CELL_WIDTH,(y+MAX_DIST_FROM_ORIG)/CELL_WIDTH] = map[(x+MAX_DIST_FROM_ORIG)/CELL_WIDTH,(y+MAX_DIST_FROM_ORIG)/CELL_WIDTH] + 1
                


scan_for_wifi()

fig = plt.figure(figsize=(6, 3.2))

ax = fig.add_subplot(111)
ax.set_title('colorMap')
plt.imshow(map)
ax.set_aspect('equal')

cax = fig.add_axes([0.12, 0.1, 0.78, 0.8])
cax.get_xaxis().set_visible(False)
cax.get_yaxis().set_visible(False)
cax.patch.set_alpha(0)
cax.set_frame_on(False)
plt.colorbar(orientation='vertical')
plt.show()


