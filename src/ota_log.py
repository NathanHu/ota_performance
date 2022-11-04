import sys
import csv
import datetime
import os
from . import configuration

class LogOTA:
    def __init__(self):
        self._log_dir = configuration.test_results

    # TEST INPUT
    # data_dict = {'MBP':{'1':10,'3':30}, 'iPad':{'1':15,'3':325}}
    # info_dict = {'build' : 'BGW320-2.10.1', 'location' : 'L0'}
    
    def log_test(self, test_info, test_data, client_data):
        # Create Directory
        build = ''
        location = ''
        
        if test_data is None:
            print('\nERROR: TEST DATA IS EMPTY/INVALID\n')
            return
            
        try:
            build = test_info['build']
            location = test_info['location']
        except:
            pass
            
        path = self._log_dir + build + '/'
        
        try:
            os.mkdir(path)
        except:
            pass
        """
        Desired .csv format)
            build | location | stream(s) | client_1 | rssi | phy | throughput |client_2 | rssi | phy | throughput |
                                         | mbp      |
        """
        log_date = datetime.datetime.now().strftime('%Y-%m-%d-%H%M')
        #log_date = datetime.datetime.now().strftime('%Y-%m-%d')
        log_file = ''.join([path, location, '_', log_date, '_OTA_Run.csv'])
        #client_data = ['rssi', 'phy', 'throughput']    # Modifiable

        with open(log_file, 'w', newline='') as csvfile:
            fnames = ['build', 'location', 'stream', 'client']
            for datapoint in client_data:
                    fnames.append(datapoint)
            # for client in data_dict:
                # fnames.append(client)
                # # TODO: Make dynamic
                # for stat in client_stats:
                    # fnames.append(stat)
                # # for stream in data_dict[client]:
                    # # fnames.append(stream)
                
            writer = csv.DictWriter(csvfile, fieldnames=fnames, restval='')
            writer.writeheader()
            
            #cl_list = list(data_dict.keys())
            
            for client in test_data:
                row_dict = {}
                row_dict['build'] = build
                row_dict['location'] = location
                row_dict['client'] = client
                
                for stream in test_data[client]:
                    row_dict['stream'] = stream    
                    for datapoint in client_data:
                        row_dict[datapoint] = test_data[client][stream][datapoint]
                    writer.writerow(row_dict)
                
        print('\n- Data file created -\n')

#2if __name__ == "__main__":

    # data_dict = {'MBP':{'1':10,'3':30}, 'iPad':{'1':15,'3':325}}
    # info_dict = {'build':'BGW320-2.10.1', 'location':'L0'}
    
    # test = LogOTA()
    # test.log_test(info_dict, data_dict)
    