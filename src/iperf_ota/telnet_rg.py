
import telnetlib
import re
import time
import datetime
import subprocess


class TelnetRG:

    ap_user_prompt_pool = {
        'bgw210': b'login: ',
        '4920': b'Air4920-4 login: '
    }

    ap_password_prompt_pool = {
        'bgw210': b'Password:'
    }

    qtn_host = '203.0.113.2'
    qtn_user = 'root'

    # Constructor
    def __init__(self, ap_host, ap_user, ap_pwd, ap_type):
        self._telnet_obj = telnetlib.Telnet()
        self._ap_host = ap_host
        self._ap_user = ap_user
        self._ap_password = ap_pwd
        self._ap_type = ap_type
        self._connected = False
        self._debug = False
        self._magic = False
        self._qtn = False
        self._linux = False
        self._error_log = ''

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
        if self._ap_type == 'rg':
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

        elif (self._ap_type == '4920') or (self._ap_type == '4921'):

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

            # Wait to get a match of prompt
            _, ret_str, _ = self._telnet_obj.expect([b'Air492.*login:'], 5)
            self._telnet_obj.write(self._ap_user.encode('ascii') + b'\r')
            _, ret_str, _ = self._telnet_obj.expect([b'.*built-in commands.*'], 5)
            time.sleep(.1)

            self._connected = True

            return 0

        elif self._ap_type == '4971':

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

            # Wait to get a match of prompt
            try:
                _, ret_str, _ = self._telnet_obj.expect([b'Login:'], 5)
                self._telnet_obj.write(self._ap_user.encode('ascii') + b'\r')
                _, ret_str, _ = self._telnet_obj.expect([b'Password:'], 5)
                time.sleep(.1)
                self._telnet_obj.write(self._ap_password.encode('ascii') + b'\r')
                _, ret_str, _ = self._telnet_obj.expect([b' >'], 5)
                self._telnet_obj.write('sh'.encode('ascii') + b'\r')
                time.sleep(.1)
            except EOFError:
                print('EOFError: telnet connection closed')
                return 1

            self._connected = True

            return 0

        else:
            print('I am here')
            return 1

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
            telnet_qtn_cmd = 'telnet ' + TelnetRG.qtn_host

            time.sleep(.2)

            self._telnet_obj.write(telnet_qtn_cmd.encode('ascii') + b'\r')
            self._telnet_obj.read_until(b'BGW210 login:')
            time.sleep(.1)
            self._telnet_obj.write(TelnetRG.qtn_user.encode('ascii') + b'\r')
            self._telnet_obj.read_until(b'quantenna #')
            time.sleep(.1)

            self._qtn = True

    # Exit QTN chip
    def exit_qtn(self):
        if self._qtn:
            self._telnet_obj.write(b'exit\n')
            self._qtn = False
            time.sleep(.2)

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
            if self._ap_type == '4971':
                self._telnet_obj.write(b'exit\n')
                time.sleep(.1)
            self._telnet_obj.write(b'exit\n')
            self._connected = False
            time.sleep(.2)

        self._telnet_obj.close()
