import telnet_rg
import time
import os
"""
TODO:
console display option
hello message monitoring
disassociation 
"""

class RunCMD:
    
    def __init__(self, host, user, pwd, ap_type):
        self._host = host
        self._ap_type = ap_type
        self._telnet_rg = telnet_rg.TelnetRG(host, user, pwd, ap_type)
        self._telnet_cmd = ''
        
        # OPTIONAL CLIENT INFORMATION
        self._client_mac = ''
        self._client_name = ''
        
        # OPTIONAL LOG INFORMATION
        self._build = ''
        self._log_path = ''
        self._log_type = ''
        self._file_name = ''
        
        # Custom Inputs
        self.yes = ('y', 'yes', 'Y', 'YES', 'Yes')
        self.quit = ('q', 'quit', 'Q', 'QUIT', 'Quit')
        
    def input_prompt(self):
        print('\nInput Command: ')
        self._telnet_cmd = input('# ')
        print('\n')
 
 
    def create_log(self):
        file_path = ''.join([self._log_dir, self._build, '/'])
        self._file_name = ''.join([file_path, self._client_name, self._log_type])
        #self._telnet_cmd = ''.join([self._telnet_cmd, self._client_mac])       
        try:
            os.mkdir(file_path + '/')
        except:
            pass
        print('File Location: ' + self._file_name)
        
        
    def run_cmd(self):
        status = 0
        sta_output = ''
        log_failure = ''

        log = ''
        
        if not self._telnet_rg._connected:
            ret_val = self._telnet_rg.connect()
            if self._telnet_rg._connected:
                try:
                    self._telnet_rg.get_telnet_obj().write(self._telnet_cmd.encode('ascii') + b'\r')
                    #self._telnet_rg.get_telnet_obj().write(self._telnet_cmd.encode('ascii'))
                    time.sleep(.2)
                    cmd_output = self._telnet_rg.get_telnet_obj().read_very_eager().decode('utf-8')
                    self._telnet_rg.close_connection()
                except:
                    print('Command Failed\n')
                    sta_output = ''
                    log = 'failed'

        self._telnet_rg.close_connection()
        #print(cmd_output)
        return cmd_output

    def run_qtn(self, input):
        if not self._telnet_rg._connected:
            ret_val = self._telnet_rg.connect()
            self._telnet_rg.telnet_qtn()
        if self._telnet_rg._connected:
            try:
                self._telnet_rg.get_telnet_obj().write(input.encode('ascii') + b'\r')
                # self._telnet_rg.get_telnet_obj().write(self._telnet_cmd.encode('ascii'))
                time.sleep(.2)
                cmd_output = self._telnet_rg.get_telnet_obj().read_very_eager().decode('utf-8')
                self._telnet_rg.close_connection()
            except:
                print('Command Failed\n')
                sta_output = ''
                log = 'failed'

        self._telnet_rg.close_connection()
        # print(cmd_output)
        return cmd_output


    def run_interface(self):
        log = input('Log outputs? y or n: ')
        if log in self.yes:
            print('\nEnter file name: ')
            script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
            self._file_name = input()
            self._log_path = os.path.join(script_dir, self._file_name)

        count = 0
        print("\nType 'q' or 'quit' to exit")
        while self._telnet_cmd not in self.quit:
            if self._telnet_cmd in self.quit:
                break
            #self.input_prompt()
            if count > 0:
                cmd_output = self.run_cmd()
                 
                print(cmd_output)
                time.sleep(.2)
                if log in self.yes:
                    try:
                        f = open(self._log_path, "a")
                        #f.write(cmd_output)
                        for line in cmd_output:
                            f.write(line.rstrip('\n'))
                        f.close()                    
                    except:
                        print('UNABLE TO OPEN LOG FILE\n')
                        pass  
            self.input_prompt()
            count += 1
        # Run finished
        print('EXITING')    
    
        
if __name__ == "__main__":  
    prompt = RunCMD('192.168.3.254', 'admin', 'austin123', 'rg')
    #prompt._telnet_cmd = 'call_qcsapi get_csw_records wifi0'
    print(prompt.run_qtn('call_qcsapi get_csw_records wifi0'))


    #prompt._telnet_cmd = 'uptime'
    print(prompt.run_qtn('uptime'))
    #prompt.run_interface()
    
