"""
Main OTA TCP performance throughput class
Runs .exe file created with C++
"""
import argparse
import subprocess 
import string
import datetime
import ota_log as log
import client_data as topology
import plot_data as plot
import configuration
#import .report_ota as report

class RunOTA:
    def __init__(self, host):
        self._log_instance = log.LogOTA()
        self._topology = topology.ClientData(host)
        self._plotter = None
        self._console = configuration.test_console
        self._clients = configuration.test_clients
        self._client_data = configuration.test_data
        self._exe = configuration.test_exe
        self._streams = configuration.test_streams

        self._test_iterations = configuration.test_iterations
        self._test_info = {'build': 'Build-Missing', 'location': 'Loc-Missing'}    # Stores build, location


        date = datetime.datetime.now().strftime('%Y-%m-%d-%H%M')
        
        # For storing data of instance
        self._results = {}
        self._results_avg = {}
        #self._stats = {}
        #self._stats_avg = {}
    
    
    def run_client(self, e1, e2, num_streams):
        """
        Run .exe with arguments
        'run_ota.exe [endpoint1 addr] [endpoint2 addr][# stream pairs]'
        """
        cmd = ' '.join([self._exe, e1, e2, str(num_streams)])
        #print('\nRUNNING COMMAND: ' + cmd)
        #return subprocess.check_output('IxChariotPythonInterface 192.168.1.50 192.168.1.52 1', universal_newlines=True)
        # return subprocess.run('IxChariotPythonInterface 192.168.1.50 192.168.1.52 1',
                                        # shell=True,
                                        # universal_newlines=True)
        #c_run = subprocess.run(cmd, shell=True, universal_newlines=True)
        c_run = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        # while True:
            # output = c_run.stdout.readline()
            # if output == '' and c_run.poll() is not None:
                # break
            # if output:
                # print(output.strip())
            # rc = c_run.poll()
        stdout, stderr = c_run.communicate()
        print(stdout)
        #print(stdout.splitlines()[-3])
        c_result = stdout.splitlines()[-3]      # Hardcoded from system output
        #print(c_result)

        try:
            data = float(c_result.split(' ')[0])     
            return c_result.split(' ')
        except:
            return [0.0, 0.0, 0.0, 0.0]
        #return float(c_result.split(' '))


    def run_villa(self):
        """
        @param e1: Console IP
        @param e2: List of client IPs

        Run .exe with arguments
        'run_villa.exe [console addr] [client1 addr] [client2 addr] ... '
        """
        cmd = ' '.join([self._exe, self._console])
        # Append each client IP to execution cmd
        for e in self._clients.values():
            cmd = ' '.join([cmd, e])
        # print(cmd)

        c_run = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = c_run.communicate()
        print(stdout)
        #print(stdout.splitlines()[-3])
        c_result = stdout.splitlines()[-3]      # Hardcoded from system output
        #print(c_result)
        try:
            data = float(c_result.split(' ')[0])
            return c_result.split(' ')
        except:
            return [0.0, 0.0, 0.0, 0.0]

        #return float(c_result.split(' '))


    def run_test(self):
        """
        Run test permutation with clients.
        Iterations specifies how many times the full test is run.
        """
        # Get topology data
        print('\nInitial Topology Information: \n')
        try:
            print(self._topology.get_ap_info())
            print(self._topology.get_topology())
        except:
            pass
        
        # Initialize final results dictionary self._results { client : {stream : [iteration results]} }
        for client in self._clients: 
            self._results[client] = {}
            for stream in self._streams: 
                self._results[client][stream] = {}
                # for ap_info in init_ap_info:
                    # #self._results[client][stream][datapoint] = []
                    # self._results[client][stream][ap_info] = []
                for datapoint in self._client_data:
                    self._results[client][stream][datapoint] = []
        print(self._results)
        test_count = 1  # Counts the number of tests
        
        for iteration in range(self._test_iterations):
            print('\n\n********** TEST ITERATION ' + str(iteration + 1) + ' **********\n')
            
            for client in self._clients:             
                for stream in self._streams:
                    try:
                        run_ap = self._topology.get_ap_info()
                        run_topology = self._topology.get_topology()
                        #run_info = run_topology.update(run_ap)
                    except:
                        pass
                    print('\n---------- RUNNING TEST [ ' + str(test_count) + 
                            ' ]: Console -> ' + client + ' - ' + str(stream) + ' stream(s) ----------\n' )
                    
                    # Append topology information
                    for datapoint in self._client_data:
                        try:
                            if datapoint in run_ap:
                                self._results[client][stream][datapoint].append(run_ap[datapoint])
                            if datapoint in run_topology[client]:
                                self._results[client][stream][datapoint].append(run_topology[client][datapoint])
                        except:
                            continue
                            
                    output = self.run_client(self._console, self._clients[client], stream)
                    self._results[client][stream]['latency'].append(float(output[0]))
                    self._results[client][stream]['throughput'].append(float(output[1]))
                    test_count += 1
                # Save result 
                
        #self._results.add(iterations, iter_results)
        
    
    def calc_avg(self):
        for client in self._results:
            self._results_avg[client] = {}
            
            for stream in self._results[client]:
                self._results_avg[client][stream] = {}
                
                for datapoint in self._results[client][stream]:
                    s_sum = 0.0
                    s_count = 0
                    s_avg = 0.0                  
                    try:
                        for entry in self._results[client][stream][datapoint]:
                            if entry != 0.0:
                                s_sum += entry
                                s_count += 1
                            
                        if s_count > 0:
                            s_avg = s_sum/s_count
                            
                        self._results_avg[client][stream][datapoint] = s_avg
                    except:
                        continue


    def console_output(self):
        print('RUN DATA: ')
        for k, v in self._results.items():
            print(k, '\t--', v)
        print('\n')
        print('AVERAGE DATA: ')
        for k, v in self._results_avg.items():
            print(k, '\t\t--', v)


if __name__ == "__main__":
    test = RunOTA('192.168.1.251')
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-loc', action="store", dest="loc", help='client location')
    parser.add_argument('-build', action="store", dest="build", help='firmware build')
    args = parser.parse_args()
    try:
        test._test_info['build'] = args.build
        test._test_info['location'] = args.loc
    except:
        pass
    

    test._test_info['location'] = 'Test'
    test._test_info['build'] = 'TESTRUN'
    print(test._test_info['build'])
    print(test._test_info['location'])

    test._plotter = plot.PlotData(test._test_info['build'])
    out = test.run_test()
    test.calc_avg()

    #print('RUN DATA: ',test._results)
    #print('AVERAGE DATA: ', test._results_avg)
    # FORMATTED CONSOLE OUTPUT
    test.console_output()
    
    test._log_instance.log_test(test._test_info, test._results_avg, test._client_data)