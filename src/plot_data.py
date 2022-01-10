# """ Plot Test Results
#
# Author: Nathan Hu
# Plot the results
#
# """
import matplotlib.pyplot as plt
import numpy as np
import csv
import os
#import .csv_extract as extract
import glob
import argparse

class PlotData:

    def __init__(self, build):
        self._data_path = 'C:/Users/LCL-Spectrum-03/Desktop/OTA Results/Test Runs/'
        self._run_dir = ''.join([self._data_path, build, '/'])
        self._dict_reader = None
        self._plot_folder = 'Dataplots/'
        self._current_file = ''
        self._data = []
        
    
    def extract_data(self, csv_file, *args, **kwargs):
        """
        Take the extracted data of the .csv file in dictionary format
        Specify datapoints and labels in arguments
        """
        self._current_file = csv_file.split('.',1)[0]
        csv_path = ''.join([self._run_dir, csv_file])
        
        self._data = []
        
        try:
            csv_data = open(csv_path, 'r')
        except:
            print('ERROR WITH .CSV FILE!')
            return
        
        with csv_data:
            reader = csv.DictReader(csv_data)       
            if args and kwargs is None:
                for row in reader:
                    temp = {}
                    for arg in args:
                        try:
                            temp[arg] = row[arg]
                        except:
                            continue
                    self._data.append(temp)
            elif kwargs:
                for row in reader:
                    conditions = True
                    for key, value in kwargs.items(): 
                        conditions = key in row and row[key] == value         
                    if conditions:
                        if args:
                            temp = {}
                            temp['client'] = row['client'] # Always have client, build, and loc
                            temp['build'] = row['build']
                            temp['location'] = row['location']
                            for arg in args:
                                try:
                                    temp[arg] = row[arg]
                                except:
                                    continue
                            self._data.append(temp)
                        else:    
                            self._data.append(row)
            else:
                for row in reader:
                    self._data.append(row)
                    
        return reader
        
    
    def plot_dir(self, *args):
        dir_data = {}   
        
        try:
            os.mkdir(''.join([self._run_dir, self._plot_folder]))
        except:
            pass
        
        for file in os.scandir(self._run_dir):
            if file.path.endswith('.csv') and file.is_file():
                #print(file.path)
                format_file = str(file.path).split('/')[-1]
                try:
                    self.extract_data(format_file)
                    dir_data[format_file] = self._data
                except:
                    continue
        
        #dir_data = sorted(dir_data)
        
        self._current_file = 'all_files'
        plot_file = ''.join([self._run_dir, self._plot_folder, self._current_file, '_throughput', '.pdf'])    
        
        #plotter = [(row['client'], row['throughput'], row['rssi'], row['phy']) for row 
                            #in self._data]
        plotter_label = ['client', 'throughput', 'rssi', 'phy']
        num_plots = len(plotter_label) - 1    
        
        fig, ax = plt.subplots(num_plots)
        plt.subplots_adjust(hspace=1)
        
        max_data = {}
        for p in range(1, num_plots+1):
            file_count = 1
            max_data[p] = {}
            for file_data in dir_data:
                max_data[p][file_data] = {}
                plotter = [(row['client'], row['build'], row['location'], 
                            #row['stream(s)'],
                            row['throughput'], row['rssi'], row['phy']) for row in dir_data[file_data]]

                x0 = [('-'.join([x[2],x[0],str(file_count),'\n',x[1]])) for x in plotter] 
                y0 = [(float(x[p+2])) for x in plotter]
                
                for label in x0:
                    max_data[p][file_data][label] = 0
                #x0 = x0.sort()                
                #run_count += 1
                #ax[p-1].plot(x0, y0, marker='.')
                ax[p-1].bar(x0, y0, width=.4)
                
                #ax[0].text(1, 1, str(y0), label=y0, va='top')
                #ax[p-1].set_ylabel('Mbps')
                ax[p-1].set_title(plotter_label[p])
                for i, v in zip(x0,y0):
                    if v < 0:
                        max_data[p][file_data][i] = min(max_data[p][file_data][i], v)
                    else:
                        max_data[p][file_data][i] = max(max_data[p][file_data][i], v)
                    # ann = '   {}\n'.format(str(v))
                    # ax[p-1].annotate(ann, xy=(i, v),
                                        # fontsize=6,
                                        # rotation=45,                                        
                                        # ha='left', 
                                        # va='top')
                    # if pt_count % 2 == 0:
                        # ax[p-1].annotate(v, xy=(i,  1.1*v),
                                    # fontsize=6,
                                    # #rotation=45,
                                    # ha='left', 
                                    # va='bottom')
                    # else:
                        # ax[p-1].annotate(v, xy=(i, v), xytext=(i, 1.1*v),
                                    # fontsize=6,
                                    # #rotation=45,
                                    # ha='right', 
                                    # va='top')
                    # pt_count += 1
                #print(max_data)
                #print('\n')
                for label, value in max_data[p][file_data].items():
                    #for key in max_data[file_data][file].keys():
                    ax[p-1].annotate(value, xy=(label, 1*value),
                                fontsize=7, rotation=90, 
                                weight='bold',
                                ha='center', va='center')
                
                file_count += 1
                
            ax[p-1].set_yticks(np.arange(min(y0), max(y0)+1, 100))
                #ax[p-1].autoscale_view()
            for tick in ax[p-1].get_xticklabels():
                tick.set_rotation(45)
                tick.set_fontsize(5)
            ax[p-1].grid()  
        
        plt.savefig(plot_file)
        plt.show()  
        
            
    def plot_data(self, *args):
        #self._data = []
        
        try:
            os.mkdir(''.join([self._run_dir, self._plot_folder]))
        except:
            pass
            
        #try:
        if args:
            for arg in args:
                plotter = [(row['location'], row['client'], row[arg]) for row 
                            in self._data]
                
                plot_file = ''.join([self._run_dir, self._plot_folder, self._current_file, '_', arg, '.png'])
                fig = plt.figure()
                ax = fig.add_subplot(111)
                ax.set_title(arg)
                ax.plot([x[0] for x in plotter], [float(x[1]) for x in plotter], color='tab:blue')
     
                plt.grid()
                plt.show()
                fig.savefig(plot_file)
                
        else:   # DEFAULT: Throughput vs Client
            
            plotter = [(row['client'], row['throughput'], row['rssi'], row['phy']) for row 
                            in self._data]
            plotter_label = ['client', 'throughput', 'rssi', 'phy']
            
            plot_file = ''.join([self._run_dir, self._plot_folder, self._current_file, '_throughput', '.png'])            
            # fig = plt.figure()
            # ax = fig.add_subplot(111)
            # ax.set_title('Throughput (Mbps)')
            # ax.plot([x[0] for x in plotter], [float(x[1]) for x in plotter], color='tab:blue')
            #fig = plt.figure()
            #plt.title('Test')
            num_plots = len(plotter[0]) - 1
            fig, ax = plt.subplots(num_plots)
            plt.subplots_adjust(hspace=.5)
            
            for p in range(1, num_plots+1):
                x0 = [(x[0]) for x in plotter] 
                y0 = [(float(x[p])) for x in plotter]
                ax[p-1].plot(x0, y0, marker='.')
                #ax[0].text(1, 1, str(y0), label=y0, va='top')
                #ax[p-1].set_ylabel('Mbps')
                ax[p-1].set_title(plotter_label[p])
                for i, v in zip(x0,y0):
                    ax[p-1].annotate(str(v), xy=(i, v), fontsize=8)
                ax[p-1].set_yticks(np.arange(min(y0), max(y0)+1, 100))
                #ax[p-1].autoscale_view()
                ax[p-1].grid()                
            
            plt.savefig(plot_file)
            plt.show()       
        
        # except:
            # print('ERROR WITH DATA!')
            # return
            
            
    def get_text_positions(x_data, y_data, txt_width, txt_height):
        a = zip(y_data, x_data)
        text_positions = y_data.copy()
        for index, (y, x) in enumerate(a):
            local_text_positions = [i for i in a if i[0] > (y - txt_height)
                                and (abs(i[1] - x) < txt_width * 2) and i != (y,x)]
            if local_text_positions:
                sorted_ltp = sorted(local_text_positions)
                if abs(sorted_ltp[0][0] - y) < txt_height: #True == collision
                    differ = np.diff(sorted_ltp, axis=0)
                    a[index] = (sorted_ltp[-1][0] + txt_height, a[index][1])
                    text_positions[index] = sorted_ltp[-1][0] + txt_height
                    for k, (j, m) in enumerate(differ):
                        #j is the vertical distance between words
                        if j > txt_height * 1.5: #if True then room to fit a word in
                            a[index] = (sorted_ltp[k][0] + txt_height, a[index][1])
                            text_positions[index] = sorted_ltp[k][0] + txt_height
                            break
        return text_positions
    

def plot_fn(x_data, y_data, text_positions, axis,txt_width,txt_height):
    for x,y,t in zip(x_data, y_data, text_positions):
        axis.text(x - .03, 1.02*t, '%d'%int(y),rotation=0, color='blue', fontsize=13)
        if y != t:
            axis.arrow(x, t+20,0,y-t, color='blue',alpha=0.2, width=txt_width*0.0,
                       head_width=.02, head_length=txt_height*0.5,
                       zorder=0,length_includes_head=True)
                       

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--build', action="store", dest="build", help='firmware build')
    args = parser.parse_args()
    
    test = PlotData(args.build)
    test_dict = test.extract_data('test.csv', 'client', 'throughput', 'rssi', 'phy', stream='3')
    #print(test._data)
    #test.plot_data()
    test.plot_dir()
    # for row in test._data:
        # print(row)
    

    # test.plot_data('rssi')









    