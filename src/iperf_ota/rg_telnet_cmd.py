import telnetlib
import re
import time
import datetime
import subprocess


class RGTelnetCmd:
    # Constructor
    def __init__(self, mode, cmd):
        self._telnet_obj = telnetlib.Telnet()
        self.mode = mode
        self.cmd = cmd
        self._ap_host = '192.168.1.254'
        self._ap_user = 'admin'
        self._ap_password = 'austin123'
        
        self._qtn_host = '203.0.113.2'
        self._qtn_user = 'root'
        
        self._connected = False
        self._debug = False
        self._magic = False
        self._qtn = False
        self._linux = False
        
        self._error_log = ''
        self._output = []


    # _telnet_obj getter
    def get_telnet_obj(self):
        return self._telnet_obj


    def ping_re_connect(self):
        result = subprocess.run(['ping', '-n', '1', self._ap_host], stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        print('ping output:{}\n'.format(output))
        print(datetime.datetime.now().strftime('%Y-%m-%d %A  %H:%M:%S.%f'))
        match = re.search(r'Approximate round trip times in milli-seconds:', output)
        if match:
            try:
                self._telnet_obj.open(self._ap_host)
            except IOError:
                print('IO Error in ping_re_connect')
                print(datetime.datetime.now().strftime('%Y-%m-%d %A  %H:%M:%S.%f'))
                return 1
            except:
                print('Other error in ping_re_connect')
                print(datetime.datetime.now().strftime('%Y-%m-%d %A  %H:%M:%S.%f'))
                return 1
        else:
            return 1
        return 0


    # Telnet to RG
    def connect(self):
        try:
            self._telnet_obj.open(self._ap_host)
        except IOError:
            print('IO Error')
            ret_val = self.ping_re_connect()
            if ret_val:
                return ret_val
        except:
            print('Other Error')
            ret_val = self.ping_re_connect()
            if ret_val:
                return ret_val
        self._telnet_obj.read_until(b'login: ')
        self._telnet_obj.write(self._ap_user.encode('ascii') + b'\r')
        self._telnet_obj.read_until(b'Password:')
        self._telnet_obj.write(self._ap_password.encode('ascii') + b'\r')
        time.sleep(.2)
        self._connected = True
        return 0
     

    # Enter debug mode
    def enter_debug(self):
        if not self._connected:
            self.connect()
        # Enter debug mode
        if not self._debug:
            time.sleep(.2)
            self._telnet_obj.write(b'debug\r')
            time.sleep(.2)
            self._debug = True


    # Enter Magic mode
    def enter_magic(self):
        if not self._connected:
            self.connect()
        # Enter magic mode
        if not self._magic:
            time.sleep(.2)
            self._telnet_obj.write(b'magic\r')
            _, ret_str, _ = self._telnet_obj.expect([b'Warning'], 5)
            time.sleep(.1)
            self._magic = True


    # Enter magic and then enter Linux xhell
    def enter_linux(self):
        if not self._connected:
            ret_val = self.connect()
        # Enter magic mode
        if not self._magic:
            time.sleep(.2)
            self._telnet_obj.write(b'magic\r')
            _, ret_str, _ = self._telnet_obj.expect([b'Warning'], 5)
            time.sleep(.1)
            self._magic = True
        # Enter linux shell
        if not self._linux:
            time.sleep(.2)
            self._telnet_obj.write(b'!\r')
            _, ret_str, _ = self._telnet_obj.expect([b'#'], 5)
            time.sleep(.1)
            self._linux = True


    # Telnet to QTN chip
    def telnet_qtn(self):
        if not self._connected:
            self.connect()
        if not self._qtn:
            telnet_qtn_cmd = 'telnet ' + self._qtn_host
            time.sleep(.2)
            self._telnet_obj.write(telnet_qtn_cmd.encode('ascii') + b'\r')
            self._telnet_obj.read_until(b'BGW210 login:')
            time.sleep(.1)
            self._telnet_obj.write(self._qtn_user.encode('ascii') + b'\r')
            self._telnet_obj.read_until(b'quantenna #')
            time.sleep(.1)
            self._qtn = True


    # Exit QTN chip
    def exit_qtn(self):
        if self._qtn:
            self._telnet_obj.write(b'exit\n')
            self._qtn = False
            time.sleep(.2)


    def start_session(self):
        if not self._connected:
            self.connect()
        if self.mode == 'debug' and not self._debug:
            self.enter_debug()
        if self.mode == 'magic' and not self._magic:
            self.enter_magic()
        if self.mode == 'linux' and not self._linux:
            self.enter_linux()
        if self.mode == 'qtn' and not self._qtn:
            self.telnet_qtn()


    # Close telnet connection
    def close_connection(self):
        time.sleep(.1)
        if self._qtn:
            self._telnet_obj.write(b'exit\n')
            self._qtn = False
            time.sleep(.2)
        if self._linux:
            self._telnet_obj.write(b'exit\n')
            self._linux = False
            time.sleep(.2)
        if self._magic:
            self._telnet_obj.write(b'exit\n')
            self._telnet_obj.write(b'exit\n')
            self._magic = False
            time.sleep(.2)
        if self._debug:
            self._telnet_obj.write(b'exit\n')
            self._debug = False
            time.sleep(.2)
        if self._connected:
            self._telnet_obj.write(b'exit\n')
            self._connected = False
            time.sleep(.2)
        self._telnet_obj.close()


    def run_cmd(self, *cmd):
        if not self._connected:
            self.start_session()
            
        cmd_input = ''       
        if cmd:
            cmd_input = cmd[0]
        else:
            cmd_input = self.cmd          
        try:
            self.get_telnet_obj().write(cmd_input.encode('ascii') + b'\r')
            #self._telnet_rg.get_telnet_obj().write(self._telnet_cmd.encode('ascii'))
            time.sleep(.2)
            cmd_output = self.get_telnet_obj().read_very_eager().decode('utf-8')
            #self.close_connection()
        except:
            print('Command Failed\n')
            sta_output = ''
            log = 'failed'
        self.close_connection()
        #print(cmd_output)
        return cmd_output
        
    
    def run_duration(self, interval, duration, *cmd):
        if not self._connected:
            self.start_session()
            
        cmd_input = ''       
        if cmd:
            cmd_input = cmd[0]
        else:
            cmd_input = self.cmd         
        try:
            while duration > 0:
                duration -= 1
                self.get_telnet_obj().write(cmd_input.encode('ascii') + b'\r')
                #self._telnet_rg.get_telnet_obj().write(self._telnet_cmd.encode('ascii'))
                time.sleep(interval)
            cmd_output = self.get_telnet_obj().read_very_eager().decode('utf-8')
                #self.close_connection()
        except:
            print('Command Failed\n')
            sta_output = ''
            log = 'failed'
        self.close_connection()
        #print(cmd_output)
        return cmd_output
        
    
    def parse_single_output(self, raw_output):
        #parsed = [line for line in raw_output]
        parsed = raw_output.splitlines()[:-1]
        return parsed[1]
        
    
    def parse_duration_output(self, raw_output):     
        parsed = raw_output.splitlines()[:-1]
        return parsed
    

if __name__ == "__main__":  
    test = RGTelnetCmd('linux', 'wl -i wl1 sta_info 7e:c3:79:a7:0c:bd | grep smoothed')
    #test.cmd = 'wl -i wl1 sta_info 7e:c3:79:a7:0c:bd | grep smoothed'
    #print(test.cmd)
    
    #raw = test.run_cmd()
    #parsed = test.parse_single_output(raw)
    #print(parsed)
    
    raw = test.run_duration(1, 10)
    parsed = test.parse_duration_output(raw)
    print(parsed)