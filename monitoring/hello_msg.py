import telnet_rg
import time
import datetime
import run_cmd
#import os
"""
--------------------------------------------------------
** BGW210 Check "Hello" msg for MESH Health

quantenna # cat /proc/mesh-ng-topology | grep hello

while [ 1 ]; do date; cat /proc/mesh-ng-topology | grep hello; sleep 10; done
--------------------
**************** BGW320 Check "Hello" msg for MESH Health *************

NOS/N93FA9FJ000364/DEBUG/MAGIC> !

# cat /proc/mesh-ng-topology | grep hello
      - 008-f4:17:b8:b5:30:d9, age: 0s, flags: DSH, hello: 22012
      - 008-f4:17:b8:b5:32:37, age: 0s, flags: DSH, hello: 21971
      - 008-f4:17:b8:b5:32:05, age: 0s, flags: DSH, hello: 22132

TODO:
Fix time of error
Track Reset count
Add if fails 

Upon failure:
1. Check QTN reset
2. Check channel change

"""

class HelloLog:
    
    cmd_hello_msg = 'cat /proc/mesh-ng-topology | grep hello'
    cmd_qtn_telnet = 'telnet 203.0.113.2'
    
    def __init__(self, host, user, pwd, ap_type):
        self._enable_hello = False
        self._enable_log = False
        self._check_interval = 10        # Default check every 30 seconds
        self._ip_list = []              # Needs to be filled with the AP IPs
        self._host = host
        self._ap_type = ap_type
        self._telnet_rg = telnet_rg.TelnetRG(host, user, pwd, ap_type)
        self._run_cmd = run_cmd.RunCMD(host, user, pwd, ap_type)
        self._cmd_hello_msg = 'cat /proc/mesh-ng-topology | grep hello'
        
        start_date = datetime.datetime.now().strftime('%Y-%m-%d-%H%M')

        # Tracking variables
        self._hello_log = {}
        self._prev_entry = {}
        self._cmd_output = ''
        self._prev_ap_count = 0
        self._ap_count = 0

        # OPTIONAL CLIENT INFORMATION
        self._client_mac = ''
        self._client_name = ''
        
        # OPTIONAL LOG INFORMATION
        self._build = ''
        self._log_path = ''
        self._log_type = '_hello_log.txt'
        self._file_name = start_date + self._log_type
        
        # Custom Inputs
        self.yes = ('y', 'yes', 'Y', 'YES', 'Yes', 'yES', 'YEs')
        self.quit = ('q', 'quit', 'Q', 'QUIT', 'Quit', 'exit', 'Exit', 'EXIT')
        self.on = ('on', 'On', 'ON', 'oN')
        self.off = ('off', 'Off', 'OFF', 'oFf', 'OFf', 'OfF', 'ofF') 
    
    
    def enable_hello(self):
        self._enable_hello = True
        self.run_hello()
    
    
    def create_log(self):
        #print(self._file_name)
        if not self._enable_log:
            print("Logging of hello messages not enabled")
        else:
            print("Logging of hello messages is enabled")
            #file_path = ''.join([self._log_dir, self._build, '/'])
            #self._file_name = ''.join([self._log_path, self._file_name])       
            try:
                #os.mkdir(os.path.join(sys.path[0], self._file_name))
                f = open(self._file_name, "a")
                #print('Initial Hello Information')
                output = test.get_hello()
                self.parse_hello()
                
                f.write("------------------------------\n" \
                        "      HELLO MESSAGE LOG       \n" \
                        "------------------------------\n" \
                        "Check interval: " + str(self._check_interval) + " sec(s)\n" \
                        "Initial AP Count: " + str(len(self._hello_log)) + "\n\n")
                f.close()
                
                print('File Location: ' + self._file_name + '\n')
            except:
                print('ERROR: Unable to create log')
                
        
    def get_hello(self):
        #cmd_hello_msg = 'cat /proc/mesh-ng-topology | grep hello'
           
        if not self._telnet_rg._connected:
            ret_val = self._telnet_rg.connect()
            self._telnet_rg.telnet_qtn()
        if self._telnet_rg._connected:
            try:
                self._telnet_rg.get_telnet_obj().write(self._cmd_hello_msg.encode('ascii') + b'\r')
                time.sleep(.2)
                self._cmd_output = self._telnet_rg.get_telnet_obj().read_very_eager().decode('utf-8')
                
                self._telnet_rg.close_connection()
            except:
                print('Command Failed\n')
                self._cmd_output = ''
        else:
            print('Hello Msg QTN Telnet Failed\n')

        self._telnet_rg.close_connection()
        #print(self._cmd_output)
        return self._cmd_output
        
        
    def parse_hello(self):
        # 001-f4:17:b8:b5:32:1a, age: 0s, flags: DSH, hello: 113556
        if len(self._hello_log.keys()) > 0:
            for key in self._hello_log.keys():
                self._prev_entry[key] = self._hello_log[key]['hello']

        #self._prev_entry = self._hello_log
        try:
            aps = self._cmd_output.split('\r\n')    # Split lines for each ap_type
            for line in range(1, len(aps)-1):       # Ignore first and last line
                line_split = aps[line].split(', ')
                #line_split[0] = line_split[0].lstrip('- ')
                line_split[0] = line_split[0].split('-')[2]
                if line_split[0] not in self._hello_log.keys():
                    self._hello_log[line_split[0]] = {}
                
                for statistic in range(1, len(line_split)):
                    data = line_split[statistic].split(': ')
                    self._hello_log[line_split[0]][data[0]] = data[1] 
                
                if 'err_count' not in self._hello_log[line_split[0]].keys():
                    self._hello_log[line_split[0]]['err_count'] = 0
                
                # Update AP counts
                self._prev_ap_count = self._ap_count
                self._ap_count = len(self._hello_log)
        except:
            print('Unable to parse hello messages from the following output:')
            print(self._cmd_output)
        #print(self._hello_log)

        
    def print_hello(self):
        try:
            for ap_key in self._hello_log.keys():
                #print(ap_key)
                ap_string = 'AP: '+ ap_key
                for key, value in self._hello_log[ap_key].items():
                    ap_string += '    ' + key + ': ' + str(value)

                print(ap_string)
            # print('\n')
        except:
            print('Error printing hello message info')
    
    
    def check_hello(self):
        error_flag = False
        error_log_entry = ''

        if self._prev_entry is not None:
            try: 
                #if self._enable_log:
                    #with open(self._file_name, 'a') as logfile:
                        #logfile.write('\n')
                # AP count check
                self.check_ap_count()
                # Hello count check
                for ap_key in self._hello_log.keys():
                    if self._prev_entry[ap_key] is not None:
                        try:
                            if int(self._hello_log[ap_key]['hello']) < int(self._prev_entry[ap_key]):
                                error_flag = True
                                self._hello_log[ap_key]['err_count'] += 1
                                error_date = datetime.datetime.now().strftime('%Y-%m-%d at %H:%M:%S')
                                #print('break 1')
                                error_log_entry += 'Hello Message Error detected on ' + error_date + '\n' \
                                'Previous ' + ap_key + ' count: ' + self._prev_entry[ap_key] + '    ' + \
                                'Current  ' + ap_key + ' count: ' + self._hello_log[ap_key]['hello'] + '    ' + \
                                'Error Count: ' + str(self._hello_log[ap_key]['err_count']) + '\n'
                                #print('break 2')
                                #logfile.write(error_log_entry)
                                print(error_log_entry)
                                self.custom_error()
                                #logfile.write(self.custom_error())
                                #time.sleep(.2)
                                #print('break 3')
                            else:
                                print(ap_key + ': No errors detected on ' 
                                      + datetime.datetime.now().strftime('%Y-%m-%d at %H:%M:%S'))
                            # Display current and previous hello packet counts
                            print('Current: ' + self._hello_log[ap_key]['hello'] +
                                  '    Previous: ' + self._prev_entry[ap_key])
                        except:
                            print(ap_key + ' does not exist in the previous check.\n')

                    else:
                        pass
                if error_flag:
                    if self._enable_log:
                        with open(self._file_name, 'a') as logfile:
                            logfile.write('\n')
                            logfile.write(error_log_entry)
                            check = self.custom_error()
                            for line in check:
                                logfile.write(line.rstrip('\n'))
                            logfile.write('\n')
                print('\n')
            except:
                print('Error while running hello message check.\n')
                    

    def check_ap_count(self):
        if self._ap_count < self._prev_ap_count:
            error_date = datetime.datetime.now().strftime('%Y-%m-%d at %H:%M:%S')

            count_err_msg = 'AP Count Error detected at ' + error_date + '\n'\
                            'Counts - Previous: ' + self._prev_ap_count + \
                            '    Current: ' + self._ap_count + '\n'
            print(count_err_msg)

            if self._enable_log:
                with open(self._file_name, 'a') as logfile:
                    logfile.write(count_err_msg)
        else:
            print('AP Count: ' + str(self._ap_count))


    def check_hello_all(self):
        pass
        
    
    def hello_input(self, input):
        if input in self.on:
            if self._enable_hello is False:
                self.run_hello()
            else:
                self._enable_hello = True
                print('Hello Message Logging is ON\n')
        elif input in self.off:
            self._enable_hello = False
            print('Turning Hello Message Logging OFF\n')
        else:
            print("Invalid 'hello' command\n")
    
        
    def run_hello(self):
        self._enable_hello = True
        self._enable_log = True
        self.create_log()
        
        while self._enable_hello:
            ouput = self.get_hello()
            self.parse_hello()
            self.print_hello()
            self.check_hello()
            time.sleep(self._check_interval)
        
        print('Hello Message logging has ended\n')


    def custom_error(self):
        output = ''
        commands = ['call_qcsapi get_csw_records wifi0',
                    'uptime']

        for cmd in commands:
            output += self._run_cmd.run_qtn(cmd) + '\n'

        #print(output)
        return output


        
if __name__ == "__main__":  
    test = HelloLog('192.168.3.254', 'admin', 'austin123', 'rg')
    # output = test.get_hello()
    # test.custom_error()
    #test.check_ap_count()
    # test._enable_log = True
    # test.create_log()
    # test.parse_hello()
    # test.print_hello()
    test.run_hello()
    
