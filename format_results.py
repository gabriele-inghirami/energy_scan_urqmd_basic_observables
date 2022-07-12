#!/usr/bin/python3

# this program assembles the pickled data created by process_output.py 
# into a text file in the format expected by the python scripts that
# prepare energy scan comparison plots with SMASH

import math
import numpy as np
import os
import sys
import pickle


# format for quantities in output file
ff='{:7.5e}'
sp="  "

if (len(sys.argv)<3):
    print ('Syntax: ./format_results.py <output file label (pp, AuAuPbPb, etc)> <pickled data 1> <pickled data 2> ...')
    sys.exit(1)

label = sys.argv[1]

data={}

for inputfile in sys.argv[2:]:
    with open(inputfile,"rb") as infile:
        events, urqmd_version, collision_energy, rap_cut, hadrons, info_results, results = pickle.load(infile)
        if (inputfile == sys.argv[2]):
            reference_urqmd_version = urqmd_version
        else:
            if (urqmd_version != reference_urqmd_version):
                print("UrQMD version "+urqmd_version+" is different from reference version "+reference_urqmd_version)
                print("Skipping file "+inputfile)
                continue
        data[collision_energy] = (events,results)
        
key_order = sorted(data.keys(), key=lambda x:float(x))

nh = len(hadrons) # we do not check that hadrons is the same for all files, we do already in combine_processed_data.py
n_keys = len(key_order)

# now we print the results
outputfile = "meanpt_midrapidity_"+label+".txt"
with open(outputfile,"w") as outf:
    outf.write("!ecm")
    for i in list(hadrons.values())[:-1]:
        outf.write(sp+str(i[1]))
    outf.write("\n")
    for i in range(n_keys):
        ikey = key_order[i]
        entry_ecm = ikey
        nev = data[ikey][0]
        outf.write(entry_ecm)
        for j in range(nh-1):
            denominator = data[ikey][1][j][2]
            if (denominator > 0):
                meanpt = data[ikey][1][j][1]/denominator
            else:
                meanpt = 0.
            outf.write(sp+ff.format(meanpt))
        outf.write("\n")
    outf.write("# UrQMD version "+urqmd_version+"\n")

outputfile = "midrapidity_yield_"+label+".txt"
with open(outputfile,"w") as outf:
    outf.write("!ecm")
    for i in list(hadrons.values())[:-1]:
        outf.write(sp+str(i[1]))
    outf.write("\n")
    for i in range(n_keys):
        ikey = key_order[i]
        entry_ecm = ikey
        nev = data[ikey][0]
        outf.write(entry_ecm)
        for j in range(nh-1):
            midrap_yields = data[ikey][1][j][2]/(nev*2*rap_cut)
            outf.write(sp+ff.format(midrap_yields))
        outf.write("\n")
    outf.write("# UrQMD version "+urqmd_version+"\n")

outputfile = "total_multiplicity_"+label+".txt"
with open(outputfile,"w") as outf:
    outf.write("!ecm")
    for i in list(hadrons.values())[:-1]:
        outf.write(sp+str(i[1]))
    outf.write("\n")
    for i in range(n_keys):
        ikey = key_order[i]
        entry_ecm = ikey
        nev = data[ikey][0]
        outf.write(entry_ecm)
        for j in range(nh-1):
            tot_multiplicity = data[ikey][1][j][0]/nev
            outf.write(sp+ff.format(tot_multiplicity))
        outf.write("\n")
    outf.write("# UrQMD version "+urqmd_version+"\n")
