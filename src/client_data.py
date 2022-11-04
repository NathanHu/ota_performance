from . import ap4971_cmd as ap4971
from . import configuration
import re

class ClientData:
    def __init__(self, host):
    #def __init__(self, host, user, pwd, ap_type):
        self._extender = ap4971.AP4971Cmd(host)
        self._select_info = ['memory_usage', 'cpu_usage']
        
        self._ap_info = {}
        self._topology = {}
 
    def get_data(self):
        client_data = {}
        convert_data = {}   # Convert from 'str' to 'int' for ease of use
        status, ap_info, sess_op_topology, timestamp = self._extender.get_ap_topology_txt()
        #print(sess_op_topology)
        #print(ap_info)
        
        for select in self._select_info:
            try:
                self._ap_info[select] = float(ap_info[select].strip('%'))/100
            except:
                self._ap_info[select] = ap_info[select]

        
        x = sess_op_topology.split(',mac=')
        #print(x)
        # Get channel information from line 1 of Topology.txt
        # TODO: STILL HARD-CODED
        # mac=d4:11:a3:6d:72:bd,qual=780,band=52,nss=2,rxpr=6,txpr=780,mrxpr=866700,mtxpr=866700,rssi=-630,snr=0,bss=0,
        channel_info = x[0].split(',')
        self._ap_info['channel'] = int(channel_info[11].split('=',1)[1])
        self._ap_info['cca'] = float(channel_info[16].split('=',1)[1])
        
        # Get client information
        try:
            for line in range(1, len(x)):
                line_split = x[line].split(',') 
                #print('\n')
                #print(line_split)
                #if line_split[0] in self._ota_devices:
                    #client = self._ota_devices[line_split[0]]
                if line_split[0] in configuration.ota_clients:
                    client = configuration.ota_clients[line_split[0]]
                    client_data[client] = {}
                    client_data[client]['phy'] = line_split[1].split('=',1)[1]
                    client_data[client]['band'] = line_split[2].split('=',1)[1]
                    client_data[client]['nss'] = line_split[3].split('=',1)[1]
                    client_data[client]['rssi'] = int(line_split[8].split('=',1)[1])/10
                    client_data[client]['snr'] = line_split[9].split('=',1)[1]
                    client_data[client]['bss'] = line_split[10].split('=',1)[1]
                    
            # Conversion to float for usage
            for client in client_data:
                self._topology[client] = dict((datapoint, int(value)) for datapoint, value in client_data[client].items())
            #self._topology = convert_data
        except:
            pass
    
    def print_data(self):
        client_data = {}
        convert_data = {}   # Convert from 'str' to 'int' for ease of use
        status, ap_info, sess_op_topology, timestamp = self._extender.get_ap_topology_txt()
        print(sess_op_topology)
        #print(ap_info)
    
    
    def get_ap_info(self):
        #if not self._ap_info:
        self.get_data()
        return self._ap_info
        
        #return self._ap_info
        
    
    def get_topology(self):
        #if not self._topology:
        #self.get_data()
        return self._topology
        
        #return self._topology

        
if __name__ == "__main__":
    #test = ClientData('192.168.1.254', 'admin', 'austin123', '4971')
    test = ClientData('192.168.1.254')
    test.print_data()
    test_ap = test.get_ap_info()
    test_topology = test.get_topology()
    print(test_ap)
    print(test_topology)
    # for client in test_dict:
        # print(client, test_dict[client])
