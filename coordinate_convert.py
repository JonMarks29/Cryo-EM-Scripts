#!/usr/bin/env python3

"""
author: Jonathan Machin (bsjma)

v0.1 - 23/12/20
v0.11 - 14/03/21
v0.12 - 19/05/21

v0.2 - 05/04/22
v0.21 - 07/04/22


notes:
micrograph order (NOT particle order) is randomised before writing files, comment out line 350 to stop this
.cbox file reading is assumed to be like .box reading - if x/y coordinates not in columns 1/2 this will fail
topaz file reading assumes a fixed file format as of v0.2.4...

writing star files with metadata from ctf file is slightly fudged and likley to bug if unusual micrographs_ctf.star file supplied

"""

import sys
import os
import numpy as np
import random
import argparse


ht = '''Converts between relion, cryolo and topaz particle formats
v0.21
'''

parser = argparse.ArgumentParser(description=ht)

parser.add_argument('-r', '--read', help="format to read: star, manpick, box, topaz", required=True)
parser.add_argument('-w', '--write', help="format to write: star, manpick, box, topaz", required=True)

parser.add_argument('-f', '--file', help="star/topaz file with particle coordinate information")
parser.add_argument('-d', '--dir', help="directory with *_manualpick.star or *.box files in")
parser.add_argument('-o', '--output', help="output location, defaults: box/manpick='.', topaz='particles.txt', star='particles.star'")
parser.add_argument('-ctf', '--ctf_mics', help="ctf_micrographs.star file to read optics group and ctf data from when writing out star files")

parser.add_argument('-b', '--boxsize', help="boxsize, needed for .box file writing")
parser.add_argument('-s', '--scale',  help="topaz coordinate scaling")

parser.add_argument('-max', '--max_particles', default=np.inf, help="total particles to write for *manualpick.star, *.box or topaz .txt files")
parser.add_argument('-cutoff', '--particle_count_cutoff', default=0, help="only write particles for micrographs that have strictly more than cutoff")
parser.add_argument('-max_mic', '--max_micrographs', default=np.inf, help="total number of micrographs to write for *manualpick.star, *.box or topaz .txt files")

        

def parse_star(file):
    particles = {}
    with open(file, 'r') as f:
        lines = f.readlines()
        
    pcount = 0
    in_data = False
    for line in lines:
        # check if in data block of star file, if not skip line
        if "data_particles" in line: 
            in_data = True
        if in_data == False:
            continue
        
        # extract column index of x/y coordinates and micrograph name
        if "_rlnCoordinateX" in line: 
            indexX = int(line.strip().split('#')[-1]) -1
        elif "_rlnCoordinateY" in line:
            indexY = int(line.strip().split('#')[-1]) -1
        elif "_rlnMicrographName" in line:
            indexMic = int(line.strip().split('#')[-1]) -1
        
        if line[0] == "_" or len(line) < 60:
            continue

        # parse data line into particle dictionary
        line = line.split() 
        x = line[indexX]
        y = line[indexY]
        micrograph = line[indexMic].split('/')[-1].split('.')[0]
                    
        if micrograph not in particles.keys():
            particles[micrograph] = [(x,y)]
        else:
            particles[micrograph].append((x,y))
        pcount += 1
                
    print(pcount, 'particles found in', file,'on', len(particles.keys()), 'unique micrographs')
    if pcount == 0:
        sys.exit("no particles found in "+file)
    
    return particles


def parse_manpick(directory):
    if directory[-1] != '/':
        directory += '/'
    particles = {}

    files = os.listdir(directory)
    pcount, mcount = 0, 0
    for fi in files:
        indexX, indexY = None, None
        if fi[-16:] == '_manualpick.star':
            micrograph = fi[:-16]
        elif fi[-5:] == '.star':
            micrograph = fi[:-5]
        else:
            print(fi, 'is not a star file, skipping')
            continue
        mcount += 1
        particles[micrograph] = []
        with open(directory+fi, 'r') as f:
            lines = f.readlines()
        for line in lines:
            if "_rlnCoordinateX" in line:
                indexX = int(line.strip().split('#')[-1]) -1
            elif "_rlnCoordinateY" in line:
                indexY = int(line.strip().split('#')[-1]) -1
            
            if line[0].isnumeric() or line[0] == ' ' and len(line) > 20:
                l = line.strip().split()
                pcount += 1
                try:
                    particles[micrograph].append((l[indexX],l[indexY]))
                except IndexError:
                    sys.exit("_rlnCoordinateX or _rlnCoordinateY not found in "+directory+file)
    
    print(pcount, 'particles found on', mcount, 'micrographs')
    if pcount == 0:
        sys.exit("no particles found in "+directory)
    return particles


def parse_box(directory, boxsize):
    if directory[-1] != '/':
        directory += '/'
    particles = {}
    files = os.listdir(directory)
     
    halfbox = int(boxsize)/2
    pcount, mcount = 0, 0
    for fi in files:
        if fi[-4:] == ".box":
            micrograph = fi[:-4]
        elif fi[-5:] == ".cbox":
            micrograph = fi[:-5]
        else:
            print(fi, 'is not a box file, skipping')
            continue
        mcount += 1
    
        particles[micrograph] = []
        with open(directory+fi, 'r') as f:
            lines = f.readlines()
        for line in lines:
            if line[0].isnumeric():
                l = line.strip().split()
                pcount += 1
                x = str(float(l[0])+int(halfbox))
                y = str(float(l[1])+int(halfbox))
                particles[micrograph].append((x,y))
   
    print(pcount, 'particles found on', mcount, 'micrographs')
    if pcount == 0:
        sys.exit("no particles found in "+directory) 
    return particles


# assuming standard topaz txt format, columns 1-4: micrograph, x, y, FOM  # correct as of v0.2.4
def parse_topaz(file, scale):
    with open(file,'r') as fi:
        data = fi.readlines()
    particles = {}

    pcount = 0
    scale = int(scale)
    for i in data[1:]:
        j = i.strip().split('\t')
        x = str(float(j[1])*scale)
        y = str(float(j[2])*scale)
        if j[0] in particles:
            particles[j[0]].append((x,y))
        else:
            particles[j[0]] = [(x,y)]
        pcount += 1
    print(pcount, 'particles found on', len(particles.keys()), 'micrographs')
    if pcount == 0:
        sys.exit("no particles found in "+file)
    return particles
            


def write_manpick(particles, output, particle_count_cutoff, total_particles, total_micrographs):
    pcount, mcount = 0, 0
    for micrograph, coor_list in particles.items():
        filename = micrograph+"_manualpick.star"
        if len(coor_list) < particle_count_cutoff:
            continue
        with open(output+filename, 'w') as manpick:
            manpick.write("# written by coordinate_convert.py\n\ndata_\n\nloop_\n_rlnCoordinateX #1\n_rlnCoordinateY #2")
            for coor in coor_list:
                x,y = coor
                manpick.write('\n'+x+'\t'+y)
                pcount += 1
        mcount += 1
        if pcount > total_particles:
            break
        if mcount > total_micrographs:
            break
    print('manualpick written for micrographs with more than', particle_count_cutoff, 'particles')
    print("written", pcount, "particles to", output)
        

def write_box(particles, output, boxsize, particle_count_cutoff, total_particles, total_micrographs):
    halfbox = int(boxsize)/2
    pcount, mcount = 0,0
    for micrograph, coor_list in particles.items():
        filename = micrograph+'.box'
        if len(coor_list) < particle_count_cutoff:
            continue
        with open(output+filename, 'w') as boxpick:
            mcount += 1
            for coor in coor_list:
                pcount += 1
                x,y = coor
                boxpick.write('\n'+str(int(float(x)-halfbox))+'\t'+str(int(float(y)-halfbox))+'\t'+str(boxsize)+'\t'+str(boxsize))
        if pcount > total_particles:
            break
        if mcount > total_micrographs:
            break
    print('boxfiles written for micrographs with more than', particle_count_cutoff, 'particles')
    print("written", pcount, "particles to", mcount, "boxfiles")


def write_topaz(particles, output, scale, particle_count_cutoff, total_particles, total_micrographs):
    pcount, mcount = 0,0
    scale = int(scale)
    with open(output, 'w') as t:
        t.write('image_name\tx_coord\ty_coord\tscore')
        for mic, coors in particles.items():
            if len(coors) < particle_count_cutoff:
                continue
            mcount += 1
            for coor in coors:
                x,y = str(int(coor[0].split('.')[0])/scale), str(int(coor[1].split('.')[0])/scale)
                t.write('\n'+mic+'\t'+x+'\t'+y+'\t2')
                pcount += 1
            if pcount > total_particles:
                break
            if mcount > total_micrographs:
                break
    print('coordinates written for micrographs with more than', particle_count_cutoff, 'particles')
    print('written ', pcount, 'particles from', mcount, 'micrographs to', output)    



def write_star(particles, output, particle_count_cutoff, total_particles, total_micrographs):
    pcount, mcount = 0, 0
    with open(output, 'w') as s:
        s.write("# written by coordinate_convert.py\n\ndata_particles\n\nloop_\n_rlnCoordinateX #1\n_rlnCoordinateY #2\n_rlnMicrographName #3")
        for mic, coors in particles.items():
            if len(coors) < particle_count_cutoff:
                continue
            mcount += 1
            for coor in coors:
                x,y = coor
                s.write('\n '+x+'\t'+y+'\t'+"MotionCorr/job002/Raw_data"+mic+".mrc")
                pcount += 1
            if pcount > total_particles:
                break
            if mcount > total_micrographs:
                break
        s.write('\n')
    print('coordinates written for micrographs with more than', particle_count_cutoff, 'particles')
    print("written", pcount, "particles from", mcount, "micrographs to", output)
    print("WARNING: optics group and defocus information is unknown and not written")
    print("WARNING: assumed micrographs in MotionCorr/job002/Raw_data")
    print("WARNING: it is usually better to supply this information explicity with the -ctf flag")



# transfer optics group and ctf information from a micrographs_ctf.star file to the new star file
def write_star_ctf(particles, ctf_file, output, boxsize, particle_count_cutoff, total_particles, total_micrographs):
    optics, header = [], []
    metadata = {}
    with open(ctf_file, 'r') as ctf:
        in_data, in_block = False, False
        for line in ctf:
            if "data_particles" in line or "data_micrographs" in line:
                in_block = True
            
            if in_block == False and in_data == False:
                optics.append(line)
            if len(line) < 130 and in_data == False and in_block == True:
                header.append(line)
            
            if in_block == True  and line[0:4] == "_rln":
                indexHigh = int(line.strip().split('#')[-1]) -1
            if "_rlnMicrographName" in line:
                indexMic = int(line.strip().split('#')[-1]) -1
            if len(line) > 100 and in_block == True:
                in_data == True
                mic = line.strip().split()[indexMic].split('/')[-1].split('.')[0]
                metadata[mic] = line.strip()

    new_optics = []
    for ind, line in enumerate(optics):
        if line[0:4] == "_rln" and optics[ind+1][0:4] != "_rln":
            new_optics.append(line)
            opticsHigh = int(line.strip().split('#')[-1]) -1
            new_optics.append("_rlnImageSize #"+str(opticsHigh+2)+'\n')
            new_optics.append("_rlnImageDimensionality #"+str(opticsHigh+3)+'\n')
            current_index = ind
            break
        else:
            new_optics.append(line)
    
    for line in optics[current_index+1:]:
        if len(line) > 25:
            new_optics.append(line.strip()+'\t'+str(boxsize)+'\t2\n')
        else:
            new_optics.append(line)


    pcount, mcount = 0, 0
    with open(output, 'w') as s:
        s.write("# written by coordinate_convert.py\n\n")
        for line in new_optics:
            s.write(line)
        for line in header:
            if "data_micrographs" in line:
                line = "data_particles\n"
            if line == header[-1]:
                line = line.strip()
            s.write(line)
        s.write("_rlnCoordinateX #"+str(indexHigh+2)+"\n")
        s.write("_rlnCoordinateY #"+str(indexHigh+3)+"\n")
        s.write("_rlnOriginXAngst #"+str(indexHigh+4)+"\n")
        s.write("_rlnOriginYAngst #"+str(indexHigh+5))


        for mic, coors in particles.items():
            if len(coors) < particle_count_cutoff:
                continue
            mcount += 1
            for coor in coors:
                x,y = coor
                s.write('\n '+metadata[mic]+'\t'+x+'\t'+y+'\t0\t0')
                pcount += 1
            if pcount > total_particles:
                break
            if mcount > total_micrographs:
                break
        s.write('\n')
    print('coordinates written for micrographs with more than', particle_count_cutoff, 'particles')
    print("written", pcount, "particles from", mcount, "micrographs to", output)
    print("optics groups and metadata read from", ctf_file)





# as of python 3.8 dictionaries are ordered, thus micrograph order needs explicitly randomising 
def randomise(particles):
    temp_items = list(particles.items())
    random.shuffle(temp_items)
    new_particles = {}
    for mic, parts in temp_items:
        new_particles[mic] = parts
    return new_particles



def main():
    args = parser.parse_args()
    inp = args.read
    out = args.write

    errors = []
    # check arguments against input requiremnts
    if inp == "star":
        if args.file == None:
            errors.append("--file required to read star file")
    elif inp == "manpick":
        if args.dir == None:
            errors.append("--dir required to read manpick directory")
    elif inp == "box":
        if args.dir == None:
            errors.append("--dir required to read box-file directory")
        if args.boxsize == None:
            errors.append("--boxsize required to read box-file directory")
    elif inp == "topaz":
        if args.file == None:
            errors.append("--file required to read topaz file")
        if args.scale == None:
            errors.append("--scale is required to read topaz file")
    else:
        errors.append("--read must be: star, manpick, box, topaz")

    # check arguements against output requirements
    if out == "star" and args.ctf_mics != None:
        if args.boxsize == None:
            errors.append("--boxsize required to write star file with metadata")
    elif out == "manpick":
        pass
    elif out == "box":
        if args.boxsize == None:
            errors.append("--boxsize required to write box-file directory")
    elif out == "topaz":
        if args.scale == None:
            errors.append("--scale is required to write topaz file")
    elif out == "star":
        pass
    else:
        errors.append("--write must be: star, manpick, box, topaz")

    # if parameter errors found print and exit
    if len(errors) != 0:
        for e in errors:
            print(e)
        sys.exit()

    # update the output to default values if not specified
    if args.output == None:
        if out == "star":
            args.output = "coordinates.star"
        elif out == "topaz":
            args.output = "coordinates.txt"
        elif out == "manpick" or out == "box":
            args.output = "./"
    if out == "manpick" or out == "box":
        if args.output[-1] != '/':
            args.output += '/'

    print('reading', inp, 'and writing', out)
    # parse input and write output as requested
    # micrograph order is randomised before writing output
    if inp == "star":
        particles = parse_star(args.file)
    elif inp == "topaz":
        particles = parse_topaz(args.file, args.scale)
    elif inp == "box":
        particles = parse_box(args.dir, args.boxsize)
    elif inp == "manpick":
        particles = parse_manpick(args.dir)

    particles = randomise(particles)
    

    cutoff = int(args.particle_count_cutoff)
    if args.max_particles == np.inf:
        total = np.inf
    else:
        total = int(args.max_particles)
    if args.max_micrographs == np.inf:
        total_mics = np.inf
    else:
        total_mics = int(args.max_micrographs)

    if out == "star" and args.ctf_mics == None:
        write_star(particles, args.output, cutoff, total, total_mics)
    elif out == "star":
        write_star_ctf(particles, args.ctf_mics, args.output, args.boxsize, cutoff, total, total_mics)
    elif out == "topaz":
        write_topaz(particles, args.output, args.scale, cutoff, total, total_mics)
    elif out == "box":
        write_box(particles, args.output, args.boxsize, cutoff, total, total_mics)
    elif out == "manpick":
        write_manpick(particles, args.output, cutoff, total, total_mics)
    

if __name__ == "__main__":
    main()




        
