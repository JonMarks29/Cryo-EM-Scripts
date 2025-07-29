# Cryo-EM-Scripts
Short scripts for EM data

**relion_exclude_tilts_handler.py**
Converts WarpTools directory tomostar to relion starfile and directory structure for running ExcludeTilts in relion, and then converts back to WarpTools tomostar for aligning/reconstruction without the excluded tilt views. 
Usage: python3 relion_exclude_tilts_handler.py <option> <pixel_size>


**class3d_parameter_converge.py**

Reads the model.star file of all iterations in Class3D directory and exracts asked for model parameter. Prints table of iterations by class number to console and generates plot of how the asked for parameter changes over iterations for each model.
Usage: class3d_parameter_converge.py [-h] [-d DIRECTORY] [-plot PLOT]



**coordinate_convert.py**

Facilitates the conversion between .star, manualpick.star, box files and topaz .txt particle coordinate formats. Provides options for thresholding the particles written out based on number of micrographs, number of particles and particle count per micrograph
usage: coordinate_convert.py [-h] -r READ -w WRITE [-f FILE] [-d DIR] [-o OUTPUT] [-ctf CTF_MICS] [-b BOXSIZE] [-s SCALE] [-max MAX_PARTICLES] [-cutoff PARTICLE_COUNT_CUTOFF]  [-max_mic MAX_MICROGRAPHS]


**viewfinder.py**

Plots the grid x-y coordinates (corresponds to the stage at time of collection) of micrographs with particles in them (particle count represented by blue-green color gradient). 
outputs: png files of the plots (same name as input starfile), all_xml.key (list of micrographs and their grid x-y coordinates), overlay.png (overlay plot of data from all individual star files)

Usage:
python3 viewfinder.py raw_data_directory particle_starfile1, particle_starfile2...

eg: python3 viewfinder.py /astbury/Data/Krios2-F4/bsijh/05082022_54ms/Images-Disc1/ particles.star

Assumes that the xml files remain in the EPU raw data directory structure (i.e. GridSquare/Data/*xml) and can handle an arbitrary number of particles.star files, but these should all have different names
