import starfile
import subprocess
import os
import pandas as pd
import xml.etree.ElementTree as ET
import re
import sys

def parse_xml(f):
    tree = ET.parse(f)
    root = tree.getroot()

    # The <Movie> tag is the root in your case
    movie_tag = root

    # Extract the attributes
    ctf_resolution = movie_tag.attrib.get('CTFResolutionEstimate')
    mean_frame_movement = movie_tag.attrib.get('MeanFrameMovement')
    
    ctf_block = root.find("CTF")
    defocus_value = None

    # Search for Param with Name="Defocus"
    for param in ctf_block.findall('Param'):
        if param.attrib.get('Name') == 'Defocus':
            defocus_value = float(param.attrib['Value'])
            break


    return ctf_resolution, defocus_value, mean_frame_movement



def write_position_starfile(tomostar_file):
    star = starfile.read(tomostar_file)
     
    df = pd.DataFrame()

    df["rlnTomoNominalStageTiltAngle"] = star["wrpAngleTilt"]
    df["rlnTomoNominalTiltAxisAngle"] = star["wrpAxisAngle"]
    df["rlnMicrographPreExposure"] = star["wrpDose"]

    remove_starter_string_n = tomostar_file.count("/")
    pattern = '^' + r'\.\./' * remove_starter_string_n

    mic = []
    ctfmaxres, motion_average, defocus = [],[],[]
    for ind, row in star.iterrows():
        mrcfile = row["wrpMovieName"]
        xmlfile = re.sub(pattern, '', mrcfile)
        xmlfile = xmlfile[:-4]+".xml"

        ctfres, defocus_val, movement = parse_xml(xmlfile)
        ctfmaxres.append(ctfres)
        motion_average.append(movement)
        defocus.append(defocus_val)
        mrcfile_average = frame_average_dir+mrcfile.split("/")[-1]
        mic.append(mrcfile_average)

    df['rlnMicrographName']  = mic
    df["rlnDefocusU"] = defocus
    df["rlnDefocusV"] = defocus
    df["rlnDefocusAngle"] = 0
    df["rlnAccumMotionTotal"] = motion_average
    df["rlnCtfMaxResolution"] = ctfmaxres


    data_name = tomostar_file.split("/")[-1].split(".")[0]
    data = {data_name: df}
    starfile.write(data, outdir+data_name+".star", overwrite=True)




def write_relion_starfiles(pixel_size):
    df = pd.DataFrame()
    tomos = []
    tomo_tilt_star = []
    for tomostar in os.listdir(tomostar_dir):
        if ".tomostar" not in tomostar:
            continue
        write_position_starfile(tomostar_dir+tomostar)
        tomoname = tomostar.split(".")[0]
        tomos.append(tomoname)
        tomo_tilt_star.append(outdir+tomoname+".star")

    df["rlnTomoName"] = tomos
    df["rlnVoltage"]  = [300]*len(tomos)
    df["rlnSphericalAberration"] = [2.7]*len(tomos)
    df["rlnAmplitudeContrast"] = [0.1]*len(tomos)
    df["rlnMicrographOriginalPixelSize"] = [pixel_size]*len(tomos)
    df["rlnOpticsGroupName"] = ["optics1"]*len(tomos)
   # df["rlnTomoTiltSeriesPixelSize"] = [bin_pixel_size]*len(tomos)

    df["rlnTomoTiltSeriesStarFile"] = tomo_tilt_star

    data = {"global": df}
    starfile.write(data, "RLN_tilt_series.star", overwrite=True)

    print("written relion star files needed for ExcludeTilts job")
    print("   tilt series star file:   RLN_tilt_series.star")
    print("   position star files in directory:  ", outdir)
    


def write_warp_tomostar():
    output_tilts = []
    star_tiltseries = starfile.read(relion_output+"selected_tilt_series.star")
    selected_tomo_name = star_tiltseries["rlnTomoName"].tolist()


    for f in os.listdir(relion_output+"tilt_series"):
        if f[-5:] != ".star":
            continue
        tomo_name = f[:-5]
        if tomo_name not in selected_tomo_name:
            continue

        rln_tilt = starfile.read(relion_output+"tilt_series/"+f)
        warp_orig = starfile.read(tomostar_dir + f.split(".")[0]+".tomostar")

        warp_filt = warp_orig[warp_orig['wrpAngleTilt'].isin(rln_tilt['rlnTomoNominalStageTiltAngle'])]

        starfile.write(warp_filt, tomostar_dir_new+f.split(".")[0]+".tomostar", overwrite=True)

    print("written warp tomostar files from output of relion ExcludeTilts job")
    print("   new tomostar files in directory:  ", tomostar_dir_new)
    print()
    print("NOTE: you may want to rename ", tomostar_dir_new, " to ", tomostar_dir, " to provide continuity with WarpTools .settings files")
        
        
helptext = '''Converts warp .tomostar to relion format for running ExcludeTilts in relion, and then converts back to warp tomostar for aligning/reconstruction in WarpTools
Usage:
        python3 relion_exclude_tilts_handler.py <option> <pixel_size>

option:
        warp2relion
        relioncommand
        relion2warp 

pixel_size is of original, raw images

        '''

# VARIABLES
# ------- these are WarpTools default naming, only change if not using standard naming conventions
tomostar_dir = "tomostar_all_warp/"
frame_average_dir = "warp_frameseries/average/"

# ------ these are output directory names, only change if you don't like how the script names its outputs
tomostar_dir_new = "tomostar_exclude/"
relion_output = "RLN_exclude_tilts/"  # this must match the value used for --output_directory in the relion command
outdir = "RLN_tomostar/"
# END VARIABLES


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(helptext)
        sys.exit()

    option = sys.argv[1]
    if option not in ["warp2relion", "relioncommand", "relion2warp"]:
        print(helptext)
        sys.exit()

    pixel_size = float(sys.argv[2])

    if option == "warp2relion":
        os.makedirs(outdir, exist_ok=True)
        write_relion_starfiles(pixel_size)


    elif option == "relioncommand":
        print("add a relion5 executable to your PATH, then:")
        print("   relion_python_tomo_exclude_tilt_images --tilt-series-star-file RLN_tilt_series.star --output-directory "+relion_output+" --cache-size 5 &")
        print(" NOTE: --output_directory  must match the value set in the scipt (relion_output)")

    
    elif option == "relion2warp":
        os.makedirs(tomostar_dir_new, exist_ok=True)
        write_warp_tomostar()









