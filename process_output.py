#!/usr/bin/python3

# this program reads the .f15 urqmd output files and returns:
# total multiplicity
# mean transverse momentum at midrapidity
# dN/dy at midrapidity
# (where midrapidity means -0.5<y<0.5)
# for:
# 211 -211 111 321 -321 2212 -2212 L+S0 a(L+S0) Xi- aXi- Om aOm

import math
import numpy as np
import os
import sys
import pickle

# rapdity cut
rap_cut = 0.5

hadrons = {"pion_plus":(0,"211"),\
           "pion_minus":(1,"-211"),\
           "pion_0":(2,"111"),\
           "kaon_plus":(3,"321"),\
           "kaon_minus":(4,"-321"),\
           "proton":(5,"2212"),\
           "anti-proton":(6,"-2212"),\
           "lambda_or_sigma0":(7,"L+S0"),\
           "anti_lambda_or_anti_sigma0":(8,"a(L+S0)"),\
           "Xi_minus":(9,"Xi-"),\
           "anti_Xi_minus":(10,"aXi"),\
           "Omega":(11,"Om"),\
           "anti_Omega":(12,"aOm"),\
           "any_other":(13,"any")\
          }

nh = len(hadrons)

dy = 2*rap_cut # the rapdity cut is symmetric around 0

results = np.zeros((nh,3),dtype=np.float64)

total_events = 0

enable_text_output_file = False

# format for quantities in output file
tf='{:7.3f}'
ff='{:16.12e}'
sp="    "

# if we want to print debugging messages or not (0=none,1=advancement infos)
verbose = 1

def extract_data_urqmd(infile,results):
    ifile = open(infile,"r")

    events_in_file = 0 
    results_event = np.zeros((nh,3),dtype=np.float64)

    first_cycle = True
    
    while True:
        try:
            if first_cycle:
                reference_urqmd_version = ifile.readline().split()[2]
                ifile.readline()
                ifile.readline()
                ifile.readline()
                collision_energy = ifile.readline().split()[5]
                for k in range(12):
                   ifile.readline()
                first_cycle = False
            else:
                for k in range(17):
                   ifile.readline()
            num_entries = int(ifile.readline().split()[0])
            #DBG print("entries: "+str(num_entries))
            ifile.readline()
            for line in range(num_entries):
                stuff = ifile.readline().split()
                #DBG print(str(stuff))
                En,px,py,pz = np.float64(stuff[4:8])
                if (((En - pz)*(En + pz)) <= 0):
                    continue
                itype = int(stuff[9])
                charge = int(stuff[11])
                rapidity = 0.5 * math.log((En+pz)/(En-pz))
                pt = math.sqrt(px**2+py**2)
                #DBG print(str(pt)+sp+str(itype)+sp+str(charge))
                if ((itype == 101) and (charge == 1)):
                    index = hadrons["pion_plus"][0]
                elif ((itype == 101) and (charge == -1)):
                    index = hadrons["pion_minus"][0]
                elif ((itype == 101) and (charge == 0)):
                    index = hadrons["pion_0"][0]
                elif ((itype == 106) and (charge == 1)):
                    index = hadrons["kaon_plus"][0]
                elif ((itype == -106) and (charge == -1)):
                    index = hadrons["kaon_minus"][0]
                elif ((itype == 1) and (charge == 1)):
                    index = hadrons["proton"][0]
                elif ((itype == -1) and (charge == -1)):
                    index = hadrons["anti-proton"][0]
                elif (((itype == 27) or (itype == 40)) and (charge == 0)):
                    index = hadrons["lambda_or_sigma0"][0]
                elif (((itype == -27) or (itype == -40)) and (charge == 0)):
                    index = hadrons["anti_lambda_or_anti_sigma0"][0]
                elif ((itype == 49) and (charge == -1)):
                    index = hadrons["Xi_minus"][0]
                elif ((itype == -49) and (charge == 1)):
                    index = hadrons["anti_Xi_minus"][0]
                elif (itype == 55):
                    index = hadrons["Omega"][0]
                elif (itype == -55):
                    index = hadrons["anti_Omega"][0]
                else:
                    index = hadrons["any_other"][0]

                #DBG print("index: "+str(index))
                results_event[index,0] += 1
                if abs(rapidity) < rap_cut:
                    results_event[index,1] += pt
                    results_event[index,2] += 1 
            results += results_event
            events_in_file += 1
            results_event = np.zeros((nh,3),dtype=np.float64)
        except:
            break

    return events_in_file, collision_energy, reference_urqmd_version

if (len(sys.argv)<3):
    print ('Syntax: ./process_output.py <output file name> <urqmd .f15 file 1> [urmqd .f15 file 2] ...')
    sys.exit(1)

if os.path.exists(sys.argv[1]):
    print("Output file "+sys.argv[1]+" already exists, I will not overwrite it. I stop here.")
    sys.exit(1)
else:
    outputfile = sys.argv[1]
    
for infile in sys.argv[2:]:
    if verbose > 0:
        print("Working on "+infile)
    new_events, new_collision_energy, new_urqmd_version = extract_data_urqmd(infile,results)
    if new_events == None:
        print("Warning, error detected when reading "+infile+", file discarded.")
        continue
    if new_events == 0:
        print("Warning, 0 events found in "+infile+", file discarded.")
        continue
    if infile == sys.argv[2]:
        reference_collision_energy = new_collision_energy
        reference_urqmd_version = new_urqmd_version
    else:
        if (new_collision_energy != reference_collision_energy):
            print("Error, discarding "+infile+" because collision energy "+new_collision_energy+" differs from reference "+reference_collision_energy)
            continue
        if (new_urqmd_version != reference_urqmd_version):
            print("Error, discarding "+infile+" because UrQMD version "+new_urqmd_version+" differs from reference "+reference_urqmd_version)
            continue
    total_events += new_events

if total_events == 0:
    print("Sorry, something went wrong, I collected 0 events...")
    sys.exit(2)
    
# now we print the results
if enable_text_output_file:
    if outputfile[-6:] == "pickle":
        text_outputfile = outputfile[:-6]+"txt"
    else:
        text_outputfile = outputfile+".txt"
    if verbose > 0:
        print("Writing the results in "+text_outputfile)
    outf = open(text_outputfile,"w")
    outf.write("# UrQMD version: "+reference_urqmd_version+"\n")
    outf.write("# events: "+str(total_events)+"\n")
    outf.write("# collision energy: "+reference_collision_energy+"\n")
    outf.write("# rapidity cut: "+'{:5.2f}'.format(rap_cut)+"\n")
    outf.write("# rows: 1) total multiplicity (no cuts)    2) sum(pT) (within the rapidity cut)    3) dN (within the rapidity cut)\n")
    outf.write("# to get <pT> at midrapidity one must divide (2) by the number of events\n")
    outf.write("# to get <dN/dy> at midrapidity one must divide (3) by the number of events and by (2*rapidty cut)\n")
    outf.write("# columns:")
    for v in hadrons.values():
        outf.write(sp+v[1])
    outf.write("\n")
    for i in range(3):
        for h in range(nh-1):
            outf.write(ff.format(results[h,i])+sp)
        outf.write(ff.format(results[h-1,i])+"\n")
    outf.close()

if outputfile[-6:] != "pickle":
    outputfile += ".pickle"

if verbose > 0:
    print("Writing the results in the pickled file "+outputfile)
with open(outputfile,"wb") as outf:
    info_results = "first index hadron type, second index: 0 total multiplicity (no cuts), 1 sum(pT) (within the rapidity cut), 2 dN (within the rapidity cut) "
    info_results += "to get <pT> at midrapidity one must divide (1) by the number of events, to get <dN/dy> at midrapidity one must divide (2) by the number of events and by (2*rapidty cut)"
    pickle.dump((total_events,reference_urqmd_version,reference_collision_energy,rap_cut,hadrons,info_results,results),outf)
