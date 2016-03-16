#!/usr/bin/env python
# Author:      Phil Westhart
# Created:     February 2016
import time
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import math

MAX_DIST_FROM_ORIG = 10 # farthest distance in x or y a point can be from the origin in meters
CELL_WIDTH = .1 # grid cell dimension in meters
ORIG_OFFSET = MAX_DIST_FROM_ORIG/CELL_WIDTH
map = np.zeros((2*MAX_DIST_FROM_ORIG/CELL_WIDTH,2*MAX_DIST_FROM_ORIG/CELL_WIDTH))
wiggle = 0.3 #margin of error in meters
found_signals = {}
ap_names = []

print "Initializing wifi-localization"

print "Loading configuration from ./ap.conf"
ap1 = {'ap_name':'NETGEAR52', 'x':0, 'y':0}
ap2 = {'ap_name':'NETGEAR52', 'x':3, 'y':0}
ap3 = {'ap_name':'NETGEAR52', 'x':0, 'y':8}

target_aps = [ap1, ap2, ap3]

def initialize_map():
    map = np.zeros((2*MAX_DIST_FROM_ORIG/CELL_WIDTH,2*MAX_DIST_FROM_ORIG/CELL_WIDTH))
    for t_ap in target_aps:
        map[(t_ap['x']/CELL_WIDTH + ORIG_OFFSET)-1, (t_ap['y']/CELL_WIDTH+ ORIG_OFFSET)-1] = -1
    

def scan_for_wifi():
    found_signals = {}
    ap_names = []
    print "Scanning for wifi..."
    out = subprocess.check_output(['sudo', './wavemon/wavemon'])
    out = out.split("\n")
    i = 0
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

def convert_db_to_m(dB):
    print "signal strength:" , dB
    #FSPL = 10*log(((4*pi*d*f)/c)**2)
    orig_strength = 20 #original signal strength in dB
    FSPL_dB = orig_strength - float(dB) + 30
    
    c = 2.9979e8 #m/s
    f = 2437 #MHz. assume channel 6
    k = -27.55
    d = 10**((FSPL_dB - 20*math.log(f,10) - k)/20)
    #FSPL = 10**(FSPL_dB/10)
    #d = (FSPL**0.5)*c/(4*np.pi*f)
    print "distance" , d , "m"
    return 2.5

def update_map():
    dist = 2.5
    for ap in ap_names:
        for t_ap in target_aps:
            if ap == t_ap['ap_name']:
                dist = convert_db_to_m(found_signals[ap])
                for x in np.arange(-(MAX_DIST_FROM_ORIG), MAX_DIST_FROM_ORIG,CELL_WIDTH):
                    for y in np.arange(-(MAX_DIST_FROM_ORIG), MAX_DIST_FROM_ORIG,CELL_WIDTH):
                        if(math.sqrt((t_ap['x'] - x)**2+ (t_ap['y'] - y)**2) <= dist + wiggle) and (math.sqrt((t_ap['x'] - x)**2+ (t_ap['y'] - y)**2) >= dist - wiggle) : 
#                            print "t_ap['x'], x, t_ap['y'], y"
#                            print t_ap['x'], x, t_ap['y'], y
#                            print "(x+MAX_DIST_FROM_ORIG)/CELL_WIDTH: " , (x+MAX_DIST_FROM_ORIG)/CELL_WIDTH
                            map[(x+MAX_DIST_FROM_ORIG)/CELL_WIDTH,(y+MAX_DIST_FROM_ORIG)/CELL_WIDTH] = map[(x+MAX_DIST_FROM_ORIG)/CELL_WIDTH,(y+MAX_DIST_FROM_ORIG)/CELL_WIDTH] + 1
                

def find_location():
    map_max = np.amax(map)
    print "max value in map: ", map_max
    count = 0
    x_total = 0
    y_total = 0
    for x in np.arange(-(MAX_DIST_FROM_ORIG), MAX_DIST_FROM_ORIG,CELL_WIDTH):
        for y in np.arange(-(MAX_DIST_FROM_ORIG), MAX_DIST_FROM_ORIG,CELL_WIDTH):
            if(map[(x+MAX_DIST_FROM_ORIG)/CELL_WIDTH,(y+MAX_DIST_FROM_ORIG)/CELL_WIDTH] == map_max):
                count = count + 1
                x_total = x_total + x
                y_total = y_total + y
    location_x = x_total / count
    location_y = y_total / count
    print "Calculated location as x:", location_x, ", y:" ,location_y
    map[(location_x+MAX_DIST_FROM_ORIG)/CELL_WIDTH,(location_y+MAX_DIST_FROM_ORIG)/CELL_WIDTH] = 5

while(True):
    initialize_map()
    scan_for_wifi()
    update_map()
    find_location()

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

    time.sleep(10)

