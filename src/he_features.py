#from . import run_cmd
import telnet_rg
import time


class HEFeature:
    def __init__(self, ap_addr, radio, hef):
        self.ap_addr = ap_addr
        self.radio = radio
        self.he_code = hef
        self._telnet_rg = None
        self._telnet_cmd = ''


    def open_telnet(self):
        try:
            self._telnet_rg = telnet_rg.TelnetRG(self.ap_addr, 'admin', 'austin123', '4971')
            ret_val = self._telnet_rg.connect()
        except:
            print('FAILED TO TELNET INTO EXTENDER')

    def change_he(self):
        status = 0
        sta_output = ''
        log_failure = ''

        log = ''

        if not self._telnet_rg._connected:
            ret_val = self._telnet_rg.connect()
        if self._telnet_rg._connected:
            try:
                """
                Command:
                    1. wl -i wl1 down
                    2. wl -i wl1 he features (CODE)
                    3. wl -i wl1 up
                    4. wl -i wl1 he features
                """
                # 1
                cmd1 = 'wl -i wl' + str(self.radio) + ' down'
                self._telnet_rg.get_telnet_obj().write(cmd1.encode('ascii') + b'\r')
                time.sleep(5)
                # 2
                cmd2 = 'wl -i wl' + str(self.radio) + ' he features ' + str(self.he_code)
                self._telnet_rg.get_telnet_obj().write(cmd2.encode('ascii') + b'\r')
                time.sleep(5)
                # 3
                cmd3 = 'wl -i wl' + str(self.radio) + ' up'
                self._telnet_rg.get_telnet_obj().write(cmd3.encode('ascii') + b'\r')
                time.sleep(5)
                # 4 CHECK
                cmd4 = 'wl -i wl' + str(self.radio) + ' he features'
                self._telnet_rg.get_telnet_obj().write(cmd4.encode('ascii') + b'\r')
                time.sleep(.2)

                cmd_output = self._telnet_rg.get_telnet_obj().read_very_eager().decode('utf-8')
                self._telnet_rg.close_connection()
            except:
                print('Command Failed\n')
                sta_output = ''
                log = 'failed'

        print(cmd_output)
        #return cmd_output


    def check_hef(self):
        cmd_output =''
        self.open_telnet()
        if not self._telnet_rg._connected:
            ret_val = self._telnet_rg.connect()
        if self._telnet_rg._connected:
            try:
                self._telnet_rg.get_telnet_obj().write('sh'.encode('ascii') + b'\r')
                time.sleep(.2)
                cmd = 'wl -i wl' + str(self.radio) + ' he features'
                self._telnet_rg.get_telnet_obj().write(cmd.encode('ascii') + b'\r')
                time.sleep(.2)
                cmd_output = self._telnet_rg.get_telnet_obj().read_very_eager().decode('utf-8')
                #print(cmd_output)
            except:
                print('Command Failed\n')
            self._telnet_rg.close_connection()
        print(cmd_output)


if __name__ == '__main__':
    test = HEFeature('192.168.1.246', 2, 3)
    #test.check_hef()
    test.open_telnet()
    test.change_he()
    test.check_hef()
