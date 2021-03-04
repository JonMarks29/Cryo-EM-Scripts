#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 09:54:40 2020
@author: jonathan 

reads a particle.star file and generates a new file with only the particles in the specified defocus window

"""


#--------------------
# particle_count_cutoff = 20  #for cryolo boxfile writing - only writes files if micrographs have stritcly more particles than the cutoff value
#--------------------

import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-f', '--runfile', default='particles.star', help='(particles.star) particles.star file to consider particles from')
parser.add_argument('-cutoff', '--defocus_cutoff', default=17.5, help='(17.5) cutoff defocus value in uM, maximum threshold for defocus')



def parse_particle(filename, cutoff):
    header, footer = [], []
    particles = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        
    count, good_defocus_count = 0, 0
    for line in lines:
        #if line[0] == '#' or line[0] == '\n' or line[0] == '_' or line[0]:
        if line[0] != ' ' and count==0:
            header.append(line)
            continue
        if line[0] != ' ' and count>0:
            footer.append(line)
            continue
        linesplit = line.split()
        if len(linesplit) != 0:
            defocusu = float(linesplit[9])
            defocusv = float(linesplit[10])
            #print(defocusu, defocusv)
            defocus = (defocusu+defocusv)/2000
            if defocus <= float(cutoff):
                particles.append(line)
                good_defocus_count +=1
            count += 1
            
                
    print(count, 'particles found')
    print(good_defocus_count, 'particles found with defocus values less than the cutoff value (', cutoff, ')')
    
    with open('particles_defocus_filtered.star', 'w') as f:
        for i in header:
            f.write(i)
        for j in particles:
            f.write(j)
        for k in footer:
            f.write(k)


args = parser.parse_args()
particles = parse_particle(args.runfile, args.defocus_cutoff)






















        
