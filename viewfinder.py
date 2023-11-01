# correlate particle counts per micrographs to location on grid
# Jonathan Machin (j.m.machin@leeds.ac.uk)
# v0.2: 27/09/22 - tidied and updated code


import sys
sys.path.append("/astbury/Users/bsjma/scripts/")  # needed for local copy of xmltodict, starfile
sys.path.append("/astbury/Users/bsjma/scripts/starfile")

import numpy as np
import matplotlib.pyplot as plt
import xmltodict
import os
import random
import starfile

# force xmltodict location and confirm it has imported properly
xmltodict.__file__ = "/astbury/Users/bsjma/scripts/xmltodict/xmltodict.py"
print(xmltodict.__file__)


plt.rcParams['figure.dpi'] = 300

text = '''
Plots the grid x-y coordinates of micrographs with particles in them (particle count represented by blue-green color gradient)
outputs: png files of the plots (same name as input starfile), all_xml.key (list of micrographs and their grid x-y coordinates), overlay.png (overlay plot of data from all individual star files)
x-y position corresponds to the stage at time of collection 

Usage:
python3 viewfinder.py raw_data_directory particle_starfile1, particle_starfile2...
eg: python3 viewfinder.py /astbury/Data/Krios2-F4/bsijh/05082022_54msKtrA/Images-Disc1/ particles.star

assumes that the xml files remain in the EPU raw data directory structure (i.e. GridSquare/Data/*xml)
can handle an arbitrary number of particles.star files, but these should all have different names

'''


# base class to store data for each starfile requested        
class Dataset:
    def __init__(self):
       pass

    # reads starfile (v3.1)
    # returns a dictionary keyed to micrograph names and valued with the number of particles in that micrograph (micrograph name has no file extension)
    # replaces previous manual reading of the starfile with pandas based starfile module
    def add_starfile_new(self, file):
        self.starfile = file
        particles = {}
        particle_table = starfile.read(file)["particles"]
        
        if len(particle_table) == 0:
            sys.exit("no particles found in "+file)

        for i in range(len(particle_table)):
            name = particle_table.loc[i, "rlnMicrographName"].split("/")[-1].split(".")[0]
            if name in particles:
                particles[name] += 1
            else:
                particles[name] = 1
        
    
        print(len(particle_table), 'particles found in', file,'on', len(particles.keys()), 'unique micrographs')
        self.micrographs = particles


    # grab the grid X and Y coordinates for a given micrograph
    def get_xy(self, mic):
        with open(mic, 'r') as f:
            xmlstring = f.read()
            data = xmltodict.parse(xmlstring)
            position = data['MicroscopeImage']['microscopeData']['stage']['Position']
            x = float(position['X'])
            y = float(position['Y'])
        return x, y

    
    
    # get the xml file location for each micrograph stored in the self.xml_dict
    # find the x,y coordinates of all micrographs and write to all_xml.key file
    # parse this file to get the x,y coordinates and count - stored as tuples (x,y,count) in self.data
    def read_xml(self, metadatad):
        if metadatad[-1] != '/':
            metadatad += '/'
        
        self.xml_dict = {}
        for gridsquare in os.listdir(metadatad):
            if not os.path.isdir(metadatad + gridsquare):
                continue
            try:
                for f in os.listdir(metadatad+gridsquare+'/Data'):
                    if f[-3:] == 'xml':
                        self.xml_dict[f.split('.')[0]+"_EER"] = metadatad+gridsquare+'/Data/'+f
            except FileNotFoundError:
                print("no data found for gridsquare", gridsquare, "- skipping")

        c = 0
        if "all_xml.key" not in os.listdir('.'):
            print(" writing all_xml.key ")
            out = open("all_xml.key", 'w')
            for mic, xml in self.xml_dict.items():
                x, y = self.get_xy(xml)
                out.write(mic+ " " + str(x) + " " + str(y) + "\n")
                c += 1
                if c %1000 == 0:
                    print(c)
            out.close

            print("written all_xml.key")

        all_xml = {}
        with open("all_xml.key", 'r') as f:
            print("all_xml.key already exists, reading micrograph data from here")
            print("WARNING: the existing all_xml.key file must correspond to the dataset in the analysed starfiles")
            for line in f:
                l = line.strip().split()
                all_xml[l[0]] = (float(l[1]), float(l[2]))

        c = 0
        # store micrograph data as tuple of ( x, y, count)
        self.data = []
        for mic, count in self.micrographs.items():
            if mic in all_xml.keys():
                x,y = all_xml[mic]
                self.data.append((x,y,count))
            else:
                try:
                    xml_name = self.xml_dict[mic]
                    x, y = self.get_xy(xml_name)
                    self.data.append((x, y, count))
                    all_xml[mic] = (x,y)
                except KeyError:
                    print("no xml data found for", mic, "- skipping")
            c += 1
            if c %1000 == 0:
                print('...read', c, 'xmls')
       

    # plot the x/y coordinates of all micrographs with particles as dots
    # transition color based on particle count from blue to green
    # plot saved as the name of the starfile.png
    def plot(self):
        print("plotting")
        random.shuffle(self.data)
        collated_positions = {}
        for xi,yi,ci in self.data:
            if (xi, yi) in collated_positions:
                collated_positions[(xi,yi)] += ci
            else:
                collated_positions[(xi, yi)] = ci
        
        print(len(self.data), "micrographs have", len(collated_positions), "stage_positions")
        x, y, count = [],[],[]
        for coor, ci in collated_positions.items():
            xi, yi = coor
            x.append(xi)
            y.append(yi)
            count.append(ci)
         
        print("max/min particles counts:", max(count), min(count))

        x = np.array(x)*1000
        y = np.array(y)*1000
        count = np.array(count)

        mi = min(count)
        ma = max(count)

        color = []
        for i in count:
            # color.append((0, i/ma, 1-i/ma,1)) # adjust here to change the color gradient
            transparency = (sum(count)/(2*ma))*(i/sum(count))
            color.append((0,0,1, transparency))

        fig, ax = plt.subplots(1,1, figsize=(6,6))
        ax.scatter(x,y, s=0.25, color=color)
        ax.set_title(self.starfile.split('.')[0])
        ylow, yhigh = ax.get_ylim()
        xlow, xhigh = ax.get_xlim()

        if yhigh-ylow > xhigh-xlow:
            difference = yhigh-ylow - xhigh-xlow
            ax.set_ylim(ylow, yhigh)
            ax.set_xlim(xlow-difference/4, xhigh+difference/4)

        elif yhigh-ylow < xhigh-xlow:
            difference = xhigh-xlow - yhigh-ylow
            ax.set_xlim(xlow, xhigh)
            ax.set_ylim(ylow-difference/4, yhigh+difference/4)

        ax.set_xlabel("x (mm)")
        ax.set_ylabel("y (mm)")
        plt.savefig(self.starfile.split('.')[0]+".png")
        plt.show()
        plt.close()
    

# plot all datasets (i.e. all particle.star files) on top of each other
def plot_overlay(all_datasets):
    print("plotting overlay")
    fig, ax = plt.subplots(1,1, figsize=(6,6))

    base_colors = [(1,0,0),(0,1,0),(0,0,1),(1,1,0),(1,0,1),(0,1,1)]*10
    for ind, d in enumerate(all_datasets):
        collated_positions = {}
        for xi,yi,ci in d.data:
            if (xi, yi) in collated_positions:
                collated_positions[(xi,yi)] += ci
            else:
                collated_positions[(xi, yi)] = ci

        x, y, count = [],[],[]
        for coor, ci in collated_positions.items():
            xi, yi = coor
            x.append(xi)
            y.append(yi)
            count.append(ci)


        x = np.array(x)*1000
        y = np.array(y)*1000
        count = np.array(count)

        color = []
        r,g,b = base_colors[ind]
        for i in count:
            transparency = (sum(count)/(2*max(count)))*(i/sum(count))
            color.append((r,g,b, transparency))

        ax.scatter(x,y,s=0.25, color=color, label=d.starfile.split('.')[0])
    
    ylow, yhigh = ax.get_ylim()
    xlow, xhigh = ax.get_xlim()

    if yhigh-ylow > xhigh-xlow:
        difference = yhigh-ylow - xhigh-xlow
        ax.set_ylim(ylow, yhigh)
        ax.set_xlim(xlow-difference/4, xhigh+difference/4)

    elif yhigh-ylow < xhigh-xlow:
        difference = xhigh-xlow - yhigh-ylow
        ax.set_xlim(xlow, xhigh)
        ax.set_ylim(ylow-difference/4, yhigh+difference/4)


    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.legend()
    plt.show()
    plt.savefig("overlay.png")



 
# reads each supplied starfile separately and generates individual plots, and then makes an overlay plot of all starfiles
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(text)
        sys.exit()
    
    all_datasets = []
    raw_data_dict = sys.argv[1]
    if raw_data_dict[-1] != '/':
        raw_data_dict += '/'

    for f in sys.argv[2:]:
        d = Dataset()
        d.add_starfile_new(f)
        d.read_xml(raw_data_dict)
        d.plot()
        all_datasets.append(d)

    plot_overlay(all_datasets)





