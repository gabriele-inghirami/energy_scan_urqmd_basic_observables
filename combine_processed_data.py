#!/usr/bin/python3

# this program sums up the pickled data created by 
# process_output.py 

import math
import numpy as np
import os
import sys
import pickle


# format for quantities in output file
tf='{:7.3f}'
ff='{:16.12e}'
sp="    "

# if we are sure that the files are compatible, we try to force adding the results even if the infos are different
force_writing = True

if (len(sys.argv)<4):
    print ('Syntax: ./combine_processed_data.py <output file name> <pickled data 1> <pickled data 2> ...')
    sys.exit(1)

if os.path.exists(sys.argv[1]):
    print("Output file "+sys.argv[1]+" already exists, I will not overwrite it. I stop here.")
    sys.exit(1)

with open(sys.argv[2],"rb") as infile:
    total_events, reference_urqmd_version, reference_collision_energy, reference_rap_cut, reference_hadrons, info_results, results = pickle.load(infile)
    
for inputfile in sys.argv[3:]:
    with open(inputfile,"rb") as infile:
        new_events, new_urqmd_version, new_collision_energy, new_rap_cut, new_hadrons, new_info_results, new_results = pickle.load(infile)
        if (new_info_results != info_results):
            print("Information about data results in "+inputfile+" is different than in "+sys.argv[2]) 
            if force_writing:
                print("However, force_writing is set to True, therefore we carry on")
            else:
                continue
        if (new_collision_energy != reference_collision_energy):
            print("Mismatch between collision energy "+new_collision_energy+" and the reference value "+reference_collision_energy)
            print("Skipping file "+inputfile)
            continue
        if (new_urqmd_version != reference_urqmd_version):
            print("Mismatch between UrQMD version "+new_urqmd_version+" and the reference value "+reference_urqmd_version)
            print("Skipping file "+inputfile)
            continue
        if (new_rap_cut != reference_rap_cut):
            print("Mismatch between rapidity cut |y|< "+str(new_rap_cut)+" and the reference value "+str(reference_rap_cut))
            print("Skipping file "+inputfile)
            continue
        if (not(new_hadrons == reference_hadrons)):
            print("Mismatch between current hadron dictionary and the reference dictionary")
            print("Skipping file "+inputfile)
            continue

        total_events += new_events
        results += new_results
        
    
# now we print the results
outputfile=sys.argv[1]
if outputfile[-6:] != "pickle":
    outputfile += ".pickle"
with open(outputfile,"wb") as outf:
    pickle.dump((total_events,reference_urqmd_version,reference_collision_energy,reference_rap_cut,reference_hadrons,info_results,results),outf)
