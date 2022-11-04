import telnet_rg
import time


class WlData:
    def __init__(self, ap_addr, radio):
        self.ap_addr = ap_addr
        self.radio = radio
        self._telnet_rg = None
        self._telnet_cmd = ''


    def open_telnet(self):
        try:
            self._telnet_rg = telnet_rg.TelnetRG(self.ap_addr, 'admin', 'austin123', 'rg')
            ret_val = self._telnet_rg.connect()
            print('TELNET SESSION OPENED')
        except:
            print('FAILED TO TELNET INTO EXTENDER')


    def wl_muinfo(self):
        cmd_output =''

        if not self._telnet_rg._connected:
            ret_val = self._telnet_rg.connect()
        if self._telnet_rg._connected:
            try:
                self._telnet_rg.get_telnet_obj().write('magic'.encode('ascii') + b'\r')
                time.sleep(.2)
                self._telnet_rg.get_telnet_obj().write('!'.encode('ascii') + b'\r')
                time.sleep(.2)
                cmd = 'wl -i wl' + str(self.radio) + ' muinfo'
                self._telnet_rg.get_telnet_obj().write(cmd.encode('ascii') + b'\r')
                time.sleep(.2)
                cmd_output = self._telnet_rg.get_telnet_obj().read_very_eager().decode('utf-8')
                #print(cmd_output)
            except:
                print('Command Failed\n')
            #self._telnet_rg.close_connection()
        print(cmd_output)


    def wl_bs_data(self):
        cmd_output =''

        if not self._telnet_rg._connected:
            ret_val = self._telnet_rg.connect()
        if self._telnet_rg._connected:
            try:
                self._telnet_rg.get_telnet_obj().write('magic'.encode('ascii') + b'\r')
                time.sleep(.2)
                self._telnet_rg.get_telnet_obj().write('!'.encode('ascii') + b'\r')
                time.sleep(.2)
                cmd = 'wl -i wl' + str(self.radio) + ' bs_data'
                self._telnet_rg.get_telnet_obj().write(cmd.encode('ascii') + b'\r')
                time.sleep(.2)
                cmd_output = self._telnet_rg.get_telnet_obj().read_very_eager().decode('utf-8')
                #print(cmd_output)
            except:
                print('Command Failed\n')
            #self._telnet_rg.close_connection()
        print(cmd_output)


    def close_telnet(self):
        if self._telnet_rg._connected:
            self._telnet_rg.close_connection()
            print('TELNET SESSION CLOSED')


if __name__ == '__main__':
    test = WlData('192.168.1.254', 1)
    test.open_telnet()
    test.wl_muinfo()
    test.wl_bs_data()
    test.close_telnet()