#!/usr/bin/env python3

import time
import rg_telnet_cmd
import map_clients
import device_ref


class LogRSSI:
    def __init__(self, clients):
        # Constructor based on RG Telnet
        self._rg_telnet = rg_telnet_cmd.RGTelnetCmd('linux', '')
        self._client_mapper = map_clients.MapClients(clients)
        self._client_map = None
        #self._mode = 'linux'
        self.client_ip_list = clients
        self.duration = 10
        self.interval = 1
        self.rssi_output = None
        
    
    def format_cmd(self, client_mac, radio):
        # Format shell command values based on:
        # wl -i wl[radio] sta_info [MAC of client] | grep smoothed
        return ''.join(['wl -i ', radio, ' sta_info ', client_mac, ' | grep smoothed'])
    
    
    def map_client_list(self):
        #time.sleep(1)
        while self._client_map is None:
            try:
                self._client_mapper.map()
                #time.sleep(.1)
                self._client_map = self._client_mapper.client_map
                print(self._client_map)
            except:
                pass

    
    
    def rssi_cmd(self, option, hw, client):
        self.rssi_output = None
        if not self._client_map:
            self.map_client_list()
            time.sleep(.1)
        try:
            mac = self._client_map[client]['mac']
            radio = device_ref.radio_ref[hw][self._client_map[client]['port']]
            #print(mac, radio)
            if option == 'single':
                raw = self._rg_telnet.run_cmd(self.format_cmd(mac, radio))
                self.rssi_output = self._rg_telnet.parse_single_output(raw).split(' ')[-1]
            else:
                raw = self._rg_telnet.run_duration(self.interval, self.duration, self.format_cmd(mac, radio))
                parsed = self._rg_telnet.parse_duration_output(raw)
                self.rssi_output = [int(parsed[i].split(' ')[-1]) for i in range(len(parsed)) if i%2 == 1]
            return self.rssi_output
        except:
            print('ERROR RUNNING COMMAND')
            
    
    def rssi_multi_clients(self, option, hw):
        self.rssi_output = None
        if len(self.client_ip_list) > 1:
            rssi_list = []
            for client in self.client_ip_list:
                rssi_list.append(self.rssi_cmd(option, hw, client))
            return rssi_list            
        else:
            try:
                self.rssi_cmd(option, hw, self.client_ip_list[0])
            except:
                print('NO CLIENTS IN LIST')
                
    
    def print_ref(self):
        print(device_ref.radio_ref)
   
    
    
if __name__ == '__main__':
    #test = LogRSSI(['192.168.1.202'])
    #test = LogRSSI(['192.168.1.205', '192.168.1.67'])
    #print(test.format_cmd('7e:c3:79:a7:0c:bd', 'wl1'))
    #print(test.rssi_cmd('', 'nokia', '192.168.1.202'))
    #test.test()
    #for client in test.client_ip_list:
        #print(test.rssi_cmd('', 'nokia', client))
    print(test.rssi_multi_clients('', 'nokia'))