#!/usr/bin/python

import os
import matplotlib.pyplot as plt
import argparse

print('''Analysis of convergence of class3D iterations.
      Prints the model distribution of specified parameter per iteration in a tabublar format.
      If 10 or fewer classes plots the change in class distribuiton by iteration\n\n''')
      


parser = argparse.ArgumentParser()

parser.add_argument('-d', '--directory', help='Class3D directory to look at')
parser.add_argument('-plot', '--plot', default='dist', help='(dist) data to plot per class; dist=class distribution, ang=angular accuracy, res=resolution, trans=translational accuracy, fourier=fouriercompleteness')


 
dis_dict = {}
dis_list = {}

def process_data(directory):
    for filename in os.listdir(directory):
        if filename.endswith("_model.star"):
            temp = []
            f = directory + filename
            with open(f, 'r') as data:
                for line in data:
                    if line.strip()[0:7] == 'Class3D':
                        temp.append(line.split())
            classes = len(temp)
            
            iter_find_temp = temp[0][0]
            iter_ind = iter_find_temp.index('_it')
            iteration = ''
            for i in iter_find_temp[iter_ind+3:]:
                if i.isnumeric():
                    iteration += i
                else:
                    break
            iteration = int(iteration)
     
            #print(temp)
            good, good_list = {}, []
                  
            for line in temp:
                temp_short = [line[0][-12:-4].replace('0', '')]
                for i in line[1:]:
                    temp_short.append(i)
                #print(temp_short)

                if args.plot == 'dist': 
                    good[temp_short[0]] = temp_short[1]
                    good_list.append(temp_short[1])
                elif args.plot == 'ang': 
                    good[temp_short[0]] = temp_short[2]
                    good_list.append(temp_short[2])
                elif args.plot == 'trans': 
                    good[temp_short[0]] = temp_short[3]
                    good_list.append(temp_short[3])
                elif args.plot == 'res': 
                    good[temp_short[0]] = temp_short[4]
                    good_list.append(temp_short[4])
                elif args.plot == 'fourier': 
                    good[temp_short[0]] = temp_short[5]
                    good_list.append(temp_short[5])
                else:
                    print('invalid -plot arguement, acceptable (res, dist, ang, trans, fourier)')
                    
            dis_dict[str(iteration)] = good
            dis_list[str(iteration)] = good_list
    return dis_dict, dis_list, classes

def print_list(dis, classes):
    for it in range(0, len(dis)):
        print('Iteration', it, end=' ')
        for model in range(1, classes+1):
            print(dis[str(it)]['class' + str(model)], end=' ')
        print('\n')

def plot(dis_list, classes, directory):
    class_1, class_2, class_3, class_4, class_5, class_6, class_7, class_8, class_9, class_10 = [], [], [], [], [], [], [], [], [], []
    for it in range(0, len(dis_list)):
        try:     
            class_1.append(float(dis_list[str(it)][0]))
            class_2.append(float(dis_list[str(it)][1]))
            class_3.append(float(dis_list[str(it)][2]))
            class_4.append(float(dis_list[str(it)][3]))
            class_5.append(float(dis_list[str(it)][4]))
            class_6.append(float(dis_list[str(it)][5]))
            class_7.append(float(dis_list[str(it)][6]))
            class_8.append(float(dis_list[str(it)][7]))
            class_9.append(float(dis_list[str(it)][8]))
            class_10.append(float(dis_list[str(it)][9]))
        except IndexError:
            continue
    models = [class_1, class_2, class_3, class_4, class_5, class_6, class_7, class_8, class_9, class_10]

    x_data = range(0, len(dis_list))
    for dataset in models[0:classes]:
        plt.plot(x_data, dataset)
    plt.grid(c=(0.9,0.9,0.9,1))
    fig_name = directory +'_' + args.plot + 'converge_script_iteration_' + str(len(dis_list)-1) + '.png' 
    plt.savefig(fig_name)
    open_fig_name = 'eog ' + fig_name
    
    ################### Comment the below line to stop autoloading of plotted figure
    os.system(open_fig_name)
    #os.remove(fig_name)


    
args = parser.parse_args()

if args.directory[-1] == '/':
    directory = args.directory
else:
    directory = args.directory+'/'
                          
dis, dis_list, classes = process_data(directory)
print_list(dis, classes)
plot(dis_list, classes, directory)






