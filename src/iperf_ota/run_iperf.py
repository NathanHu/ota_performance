import subprocess
import time
import csv
import datetime
import log_rssi
from threading import Thread


class IperfOTA:
    def __init__(self, controller, clients):
        #self._log_dir = configuration.test_results
        #self.test_dir = 'C:/Users/LCL-Spectrum-03/Desktop/OTA Results/code_test/PI19_bgw320/'
        self.test_dir = ''
        self.csv_header = ['time', 'interval', '', 'transfer', '', 'bandwidth', '']
        self.clients = clients
        self.server_addr = controller
        self.test_config = {
            'interval': 1,      # One second default data intervals
            'time': 75,         # Length of test
            'connections': 5    # Number of simultaneous connections to server
        }
        self.console_output = []

        ### OPTIONAL CONFIGURATION ###
        self.rssi_log = log_rssi.LogRSSI(clients)
        self.rssi_output = None
        self.parsed_data = None


    def run_test(self, server, file_name):
        self.parsed_data = None
        cnt = 0
        reads_to_capture = 5
        times = [0] * reads_to_capture
        lines = [''] * reads_to_capture
        tref = time.time()
        self.console_output = []
        process = subprocess.Popen(f"iperf3 -c {server} -f m \
                                    -P {self.test_config['connections']} \
                                    -i {self.test_config['interval']} \
                                    -t {self.test_config['time']}",
                                   encoding='utf-8',
                                   stdout=subprocess.PIPE)
        #self.parse_output(process.stdout.readline())
        while True:
            output = process.stdout.readline()
            """
            if cnt < reads_to_capture: # To avoid flooding the terminal, only print the first 5
                times[cnt] = time.time() - tref
                lines[cnt] = output
                cnt = cnt + 1
            """
            if output == '':
                rc = process.poll()
                if rc is not None:
                    break
            else:
                self.console_output.append(output)
        rc = process.poll()
        #for ii in range(reads_to_capture):
            #print(f'Readline {ii} returned after: {times[ii]} seconds, line was: {lines[ii].strip()}')
        print(self.console_output)
        self.parse_output(self.console_output, file_name)


    def run_reverse(self, server, file_name):
        cnt = 0
        reads_to_capture = 5
        times = [0] * reads_to_capture
        lines = [''] * reads_to_capture
        tref = time.time()
        #process = subprocess.Popen(f"iperf3 -c {server} -R -P 5 -f m \
        process = subprocess.Popen(f"iperf3 -c {server} -R -f m \
                                    -P {self.test_config['connections']} \
                                    -i {self.test_config['interval']} \
                                    -t {self.test_config['time']}",
                                   encoding='utf-8',
                                   stdout=subprocess.PIPE)
        #self.parse_output(process.stdout.readline())
        while True:
            output = process.stdout.readline()
            """
            if cnt < reads_to_capture: # To avoid flooding the terminal, only print the first 5
                times[cnt] = time.time() - tref
                lines[cnt] = output
                cnt = cnt + 1
            """
            if output == '':
                rc = process.poll()
                if rc is not None:
                    break
            else:
                self.console_output.append(output)
        rc = process.poll()
        #for ii in range(reads_to_capture):
        #print(f'Readline {ii} returned after: {times[ii]} seconds, line was: {lines[ii].strip()}')
        print(self.console_output)
        self.parse_output(self.console_output, file_name)


    def run_udp(self, server, file_name):
        cnt = 0
        reads_to_capture = 5
        times = [0] * reads_to_capture
        lines = [''] * reads_to_capture
        tref = time.time()
        process = subprocess.Popen(f"iperf3 -c {server} -u -b 2000m -f m \
                                            -i {self.test_config['interval']} \
                                            -t {self.test_config['time']}",
                                   encoding='utf-8',
                                   stdout=subprocess.PIPE)
        #self.parse_output(process.stdout.readline())
        while True:
            output = process.stdout.readline()
            """
            if cnt < reads_to_capture: # To avoid flooding the terminal, only print the first 5
                times[cnt] = time.time() - tref
                lines[cnt] = output
                cnt = cnt + 1
            """
            if output == '':
                rc = process.poll()
                if rc is not None:
                    break
            else:
                self.console_output.append(output)
        rc = process.poll()
        #for ii in range(reads_to_capture):
        #print(f'Readline {ii} returned after: {times[ii]} seconds, line was: {lines[ii].strip()}')
        print(self.console_output)
        self.parse_output(self.console_output, file_name)


    def run_udp_reverse(self, server, file_name):
        cnt = 0
        reads_to_capture = 5
        times = [0] * reads_to_capture
        lines = [''] * reads_to_capture
        tref = time.time()
        process = subprocess.Popen(f"iperf3 -c {server} -u -b 2000m -R -f m -i {self.test_config['interval']} \
                                        -t {self.test_config['time']}",
                                   encoding='utf-8',
                                   stdout=subprocess.PIPE)
        #self.parse_output(process.stdout.readline())
        while True:
            output = process.stdout.readline()
            """
            if cnt < reads_to_capture: # To avoid flooding the terminal, only print the first 5
                times[cnt] = time.time() - tref
                lines[cnt] = output
                cnt = cnt + 1
            """
            if output == '':
                rc = process.poll()
                if rc is not None:
                    break
            else:
                self.console_output.append(output)
        rc = process.poll()
        #for ii in range(reads_to_capture):
        #print(f'Readline {ii} returned after: {times[ii]} seconds, line was: {lines[ii].strip()}')
        print(self.console_output)
        self.parse_output(self.console_output, file_name)


    def parse_output(self, output, file_name, *args):
        #print('TEST OUTPUT:')
        #print(output)
        line_num = 0
        sec = 0
        # Skip first 3 lines for data
        data = []
        while line_num < len(output) and sec < self.test_config['time']:

            if self.test_config['connections'] == 1:
                if line_num > 2:
                    sec += 1
                    line = output[line_num].split()
                    #print([sec] + line[2:])
                    data.append([sec] + line[2:])    # Skip first two bracket elements

                #line_num += 1
            else:
                line = output[line_num].split()
                if line[0] == '[SUM]':
                    sec += 1
                    data.append([sec] + line[1:])
            line_num += 1
            """
            if line_num > 1 + 2 * self.test_config['connections']:
                sec += 1
                line = output[line_num].split()
                #print([sec] + line[2:])
                data.append([sec] + line[2:])    # Skip first two bracket elements
            if self.test_config['connections'] > 1:
                line_num += self.test_config['connections']
            else:
                line_num += 1
            """
        #print(data)
        #self.create_csv(data, file_name)
        self.parsed_data = data
        return data


    def run_test_rssi_dl(self, hw, server, file_name):
        self.rssi_log.rssi_output = None
        t2 = Thread(target=self.run_reverse, args=(server, file_name))
        t1 = Thread(target=self.rssi_log.rssi_cmd, args=('', hw, server))
        #rssi_data = Thread(target = self.rssi_log.rssi_multi_clients('', hw)).start()
        t2.start()
        t1.start()
        t2.join()
        t1.join()
        print('IPERF DATA: ', self.parsed_data)
        print('RSSI DATA: ', self.rssi_log.rssi_output)
        self.create_csv(self.parsed_data, file_name, 'rssi', self.rssi_log.rssi_output)


    def run_test_rssi_ul(self, hw, server, file_name):
        self.rssi_log.rssi_output = None
        t2 = Thread(target=self.run_test, args=(server, file_name))
        t1 = Thread(target=self.rssi_log.rssi_cmd, args=('', hw, server))
        #rssi_data = Thread(target = self.rssi_log.rssi_multi_clients('', hw)).start()
        t2.start()
        t1.start()
        t2.join()
        t1.join()
        print('IPERF DATA: ', self.parsed_data)
        print('RSSI DATA: ', self.rssi_log.rssi_output)
        self.create_csv(self.parsed_data, file_name, 'rssi', self.rssi_log.rssi_output)


    def create_csv(self, parsed_output, file_name, *args):
        #result_file = ''.join([self.test_dir, 'ota_iperf_test-1.csv'])
        date = datetime.datetime.now().strftime('%Y-%m-%d-%H%M')
        result_file = ''.join([self.test_dir, file_name, '_', date, '.csv'])
        
        if len(args) > 0:
            try:
                self.csv_header.append(args[0])
                for i in range(len(args[1])):
                    parsed_output[i].append(args[1][i])
            except:
                print('UNABLE TO RETRIEVE ADDITIONAL CSV DATA')
                pass
        
        with open(result_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.csv_header)    # Add header to .csv
            writer.writerows(parsed_output)
        print('********** CSV File Generated **********')



if __name__ == '__main__':
    # INPUT PC BEHIND AP IP AS STRING (ex. 192.168.1.50)
    controller = ''
    # INPUT CLIENT IP SEPARATE STRINGS WITH COMMAS (ex. '192.168.1.64', '192.168.1.65', ...)
    clients = {
        # CLIENTS
        'S20' : '192.168.1.30',
        'NOTE' : '192.168.1.31',
        'TAB' : '192.168.1.34',
        'S10' : '192.168.1.35',
        'IPHONESE' : '192.168.1.32',
        'IPADPRO' : '192.168.1.33',
        'IPHONE10' : '192.168.1.36',
        'IPHONE12' : '192.168.1.37',
        'MBP' : '192.168.1.40'
    }
    #test = IperfOTA(controller, clients)
    #test.rssi_log.duration = test.test_config['time']
    #test.rssi_log.interval = test.test_config['interval']
    ## SPECIFY OUTPUT DIRECTORY (ex. 'C:/Users/LCL-Spectrum-03/Desktop/OTA Results/code_test/PI19_bgw320/')
    #test.test_dir = 'C:/Users/LCL-Spectrum-03/Desktop/OTA Results/code_test/PI20_bgw320/'
    
    #print(test.rssi_log.client_ip_list)
    #test.rssi_log.map_client_list()
    #print(test.rssi_log.rssi_cmd('', 'nokia','192.168.1.202'))
    #print(test.rssi_log.rssi_multi_clients('', 'nokia'))
    #test.run_test_rssi('nokia', '192.168.1.67', '192.168.1.67')
    

    ### TEMP: Run script for each client in list ###
    """
    for client in test.clients:
        #test.run_test(client, client)
        #result_file = ''.join([test.test_dir, client, '.csv'])
        #print(result_file)
        test.run_test_rssi('nokia', client, client)
    """
    for k,v in clients.items():
        test = IperfOTA(controller, [v])
        test.rssi_log.duration = test.test_config['time']
        test.rssi_log.interval = test.test_config['interval']
        # SPECIFY OUTPUT DIRECTORY (ex. 'C:/Users/LCL-Spectrum-03/Desktop/OTA Results/code_test/PI19_bgw320/')
        test.test_dir = 'C:/Users/LCL-Spectrum-03/Desktop/OTA Results/code_test/PI20_bgw320/'
        #BGW320-500_MBP_TCP_DL_1P_3_19_5
        # FORMAT FILE NAME
        fn = ''.join([k, '_TCP_UL_HIGH'])
        test.run_test_rssi_ul('humax', v, fn)
        time.sleep(5)
