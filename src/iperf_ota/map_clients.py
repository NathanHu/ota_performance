#!/usr/bin/env python3

import rg_telnet_cmd
#import device_ref


class MapClients:
    def __init__(self, clients):
        self.client_ip_list = clients
        self._rg_telnet = rg_telnet_cmd.RGTelnetCmd('linux', None)
        self.client_map = None
        self.ip_lan_headers = ['host', 'ip', 'mac', 'state', 'type', 'port']

    
    def show_ip_lan(self):
        # cshell -c "show ip lan" | grep [client IP]
        shell_output = []
        
        for client in self.client_ip_list:
            print(client)
            cmd = ''.join(['cshell -c "show ip lan" | grep ', client])
            line = self._rg_telnet.parse_single_output(self._rg_telnet.run_cmd(cmd))
            shell_output.append(line.split()) 
        #print(shell_output)
        return(shell_output)
        
    
    def map(self):
        client_raw = self.show_ip_lan()
        self.client_map = {}
        for i in range(len(self.client_ip_list)):
            self.client_map[self.client_ip_list[i]] = {k: v for k, v in zip(self.ip_lan_headers, client_raw[i])}
       

if __name__ == '__main__':
    test = MapClients(['192.168.1.202'])
    #test.show_ip_lan()
    test.map()
    print(test.client_map)