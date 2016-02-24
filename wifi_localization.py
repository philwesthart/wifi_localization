#!/usr/bin/env python
# Author:      Phil Westhart
# Created:     February 2016

import subprocess

print "Initializing wifi-localization"

print "Loading configuration from ./ap.conf"



print "Scanning for wifi..."
out = subprocess.check_output(['sudo', './wavemon'])
out = out.split("\n")
i = 0
found_signals = {}
for line in out:
    if len(line) > 0:
        i = i + 1
        ap_name = line[:-11]
        ap_name = ap_name.rstrip()
        signal_strength = line[-11:-2]
        print ap_name, signal_strength, "dB"
        found_signals[ap_name] = signal_strength

print i, "access points found"




