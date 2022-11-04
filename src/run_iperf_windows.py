import subprocess
import time
import csv
import configuration


class IperfOTA:
    def __init__(self, server_addr, *args):
        #self._log_dir = configuration.test_results
        self.test_dir = 'C:/Users/LCL-Spectrum-03/Desktop/OTA Results/code_test/PI19_bgw320-2/'
        self.csv_header = ['time', 'interval', '', 'transfer', '', 'bandwidth', '']
        self.clients = [arg for arg in args]
        self.server_addr = server_addr
        self.test_config = {
            'interval': 1,      # One second default data intervals
            'time': 75,         # Length of test
            'connections': 5    # Number of simultaneous connections to server
        }
        self.console_output = []


    def run_test(self, server, file_name):
        cnt = 0
        reads_to_capture = 5
        times = [0] * reads_to_capture
        lines = [''] * reads_to_capture
        tref = time.time()
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


    def parse_output(self, output, file_name):
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
        self.create_csv(data, file_name)


    def create_csv(self, parsed_output, file_name):
        #result_file = ''.join([self.test_dir, 'ota_iperf_test-1.csv'])
        result_file = ''.join([self.test_dir, file_name, '.csv'])
        with open(result_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.csv_header)    # Add header to .csv
            writer.writerows(parsed_output)
        print('*** CSV File Generated ***')



if __name__ == '__main__':
    # TEMP
    clients = { 'S20' : '192.168.1.30',
                'NOTE' : '192.168.1.31',
                'IPHONESE' : '192.168.1.32',
                'IPADPRO' : '192.168.1.33',
                'TAB' : '192.168.1.34',
                'S10' : '192.168.1.35',
                'IPHONE10' : '192.168.1.36',
                'IPHONE12' : '192.168.1.37',
                }
    """
    for k, v in clients.items():
        #print(k, v)
        test = IperfOTA(v, '192.168.1.50')

        #filename = ''.join(k, '_TCP_UL')
        filename = k + '_TCP_UL'
        #print(filename)
        test.run_reverse(test.server_addr, filename)
    """

    #test = IperfOTA('192.168.1.50', '192.168.1.40')
    #test = IperfOTA('192.168.1.40', '192.168.1.50') # MBP
    #test = IperfOTA('192.168.1.33', '192.168.1.50') # IPADPRO
    #test = IperfOTA('192.168.1.30', '192.168.1.50') # S20
    #test = IperfOTA('192.168.1.31', '192.168.1.50') # NOTE
    test = IperfOTA('192.168.1.32', '192.168.1.50') # IPHONESE
    #test = IperfOTA('192.168.1.34', '192.168.1.50') # TAB
    #test = IperfOTA('192.168.1.35', '192.168.1.50') # S10
    #test = IperfOTA('192.168.1.36', '192.168.1.50') # IPHONE10
    #test = IperfOTA('192.168.1.37', '192.168.1.50') # IPHONE12


    #test.run_test(test.clients[0])
    #test.run_test(test.server_addr)
    #test.run_reverse(test.server_addr)

    #test.run_test(test.server_addr, 'MBP_TCP_CHECK')
    #test.run_reverse(test.server_addr, 'MBP_TCP_CHECK')

    #test.run_test(test.server_addr, 'BGW320-500_MBP_TCP_DL_1P_3_19_5')
    #test.run_reverse(test.server_addr, 'BGW320-500_MBP_TCP_UL_1P_3_19_5')

    ################# CLIENTS ##################
    ### IPAD PRO
    #test.run_test(test.server_addr, 'IPADPRO_TCP_DL')
    #test.run_reverse(test.server_addr, 'IPADPRO_TCP_UL')
    ### GALAXY S20
    #test.run_test(test.server_addr, 'S20_TCP_DL')
    #test.run_reverse(test.server_addr, 'S20_TCP_UL')
    ### NOTE
    #test.run_test(test.server_addr, 'NOTE_TCP_DL')
    #test.run_reverse(test.server_addr, 'NOTE_TCP_UL')
    ### IPHONE SE
    #test.run_test(test.server_addr, 'IPHONESE_TCP_DL')
    #test.run_reverse(test.server_addr, 'IPHONESE_TCP_UL')
    ### TAB
    #test.run_test(test.server_addr, 'TAB_TCP_DL')
    #test.run_reverse(test.server_addr, 'TAB_TCP_UL')
    ### S10
    #test.run_test(test.server_addr, 'S10_TCP_DL')
    #test.run_reverse(test.server_addr, 'S10_TCP_UL')
    ### IPHONE10
    #test.run_test(test.server_addr, 'IPHONE10_TCP_DL')
    #test.run_reverse(test.server_addr, 'IPHONE10_TCP_UL')
    ### IPHONE12
    #test.run_test(test.server_addr, 'IPHONE12_TCP_DL')
    #test.run_reverse(test.server_addr, 'IPHONE12_TCP_UL')