# Cryo-EM-Scripts
Short scripts for EM data

class3d_parameter_converge.py: Reads the model.star file of all iterations in Class3D directory and exracts asked for model parameter. Prints table of iterations by class number to console and generates plot of how the asked for parameter changes over iterations for each model.
Usage: class3d_parameter_converge.py [-h] [-d DIRECTORY] [-plot PLOT]

defocus_particle_filter.py: Reads a particle.star file and generates a new file with only the particles in the specified defocus window.
Usage: defocus_particle_filter.py [-h] [-f RUNFILE] [-cutoff DEFOCUS_CUTOFF]

run_data_to_coor.py: Takes a run_data.star file and boxsize; outputs a set of relions manualpick.star, or .box files that have a particle number above the specified particle count. File, boxsize, particle number cut-off are defined at top of script
