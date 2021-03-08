#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 09:54:40 2020
@author: jonathan

takes a run_data.star file and boxsize; outputs a set of relions _manualpick.star, or .box files (or topaz coordinate .txt file) that have a particle number above the specified particle count, 

"""

#--------------------
#PARAMETERS TO SET

file = 'run_data.star'
boxsize = (140,140)
particle_count_cutoff = 20  #for cryolo boxfile writing - only writes files if micrographs have stritcly more particles than the cutoff value

#--------------------

def parse_rundatastar(file):
    particles = {}
    with open(file, 'r') as f:
        lines = f.readlines()
        
    count = 0
    for line in lines:
        #if line[0] == '#' or line[0] == '\n' or line[0] == '_' or line[0]:
        if line[0] != ' ':
            continue
        line = line.split()
        if len(line) != 0:
            x = line[0]
            y = line[1]
            for ind, i in enumerate(line[6]):
                if i == '/':
                    cutoff_ind = ind
            micrograph = line[6][cutoff_ind+1:-4]
                    
            if micrograph not in particles.keys():
                particles[micrograph] = [(x,y)]
            else:
                particles[micrograph].append((x,y))
            count += 1
            
                
    print(count, 'particles found in run_data.star')
    print(len(particles.keys()), 'unique micrographs with particles')
    return particles
            

def write_manualpickstar(particles):
    for micrograph, coor_list in particles.items():
        filename = micrograph+'_manualpick.star'
        with open(filename, 'w') as manpick:
            manpick.write('\ndata_\n\nloop_\n_rlnCoordinateX #1\n_rlnCoordinateY #1\n_rlnClassNumber #3\n_rlnAnglePsi #4\n_rlnAutopickFigureOfMerit #5')
            for coor in coor_list:
                x,y = coor
                manpick.write('\n'+x+'\t'+y+'\t-999\t-999.0\t-999.0')
        print('written', len(coor_list), 'particles to', filename)
        
def write_cryolobox(particles, particle_count_cutoff):
    boxx, boxy = boxsize
    boxx, boxy = str(boxx), str(boxy)
    pcount, mcount = 0,0
    for micrograph, coor_list in particles.items():
        filename = micrograph+'.box'
        if len(coor_list) < particle_count_cutoff:
            continue
        with open(filename, 'w') as boxpick:
            mcount += 1
            for coor in coor_list:
                pcount += 1
                x,y = coor
                boxpick.write('\n'+str(int(float(x)-70))+'\t'+str(int(float(y)-70))+'\t'+boxx+'\t'+boxy)
        print('written', len(coor_list), 'particles to', filename)
    print('boxfiles written for all micrographs with more than', particle_count_cutoff, 'particles')
    print(mcount, 'micrographs, with', pcount, 'particles')

    
def write_topaztxt(particles, particle_count_cutoff):
    pcount, mcount = 0,0
    with open('topaz_coordinate_table.txt', 'w') as t:
        t.write('image_name\tx_coord\ty_coord\tscore')
        for mic, coors in particles.items():
            if len(coors) < particle_count_cutoff:
                continue
            mcount += 1
            for coor in coors:
                t.write('\n'+mic+'\t'+coor[0]+'\t'+coor[1]+'\t2')
                pcount += 1
    print('written ', pcount, 'particles from', mcount, 'micrographs to topaz_coordinate_table.txt')

    
    
                
particles = parse_rundatastar(file)


#--------------CHANGE HASHED LINE TO ALTER OUTPUT COORDINATE TYPE----------------#
#write_manualpickstar(particles)
#write_cryolobox(particles, particle_count_cutoff)
write_topaztxt(particles, particle_count_cutoff)



















        
