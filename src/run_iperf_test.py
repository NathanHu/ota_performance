#!/usr/bin/env python3

import iperf3

class RunIperf:
    def __init__(self, server_addr, *args):
        self.iperf_path = 'C:/iperf-3.1.3-win64/iperf3.exe'    # CHECK PATH VALUE
        self.server_addr = server_addr
        self.clients = [arg for arg in args]


    def run_server(self):
        server = iperf3.Server(lib_name=self.iperf_path)
        server.bind_address = '10.10.10.10'
        server.port = 6969
        server.verbose = False
        while True:
            server.run()


    def run_client(self):
        client = iperf3.Client(lib_name=self.iperf_path)
        client.duration = 1
        client.bind_address = '192.168.1.40'
        client.server_hostname = '192.168.1.50'
        client.port = 5201
        client.blksize = 1234
        client.num_streams = 10
        client.zerocopy = True
        client.verbose = False
        client.reverse = True
        client.run()


    def run_udp(self):
        client = iperf3.Client()
        client.duration = 1
        client.server_hostname = '127.0.0.1'
        client.port = 5201
        client.protocol = 'udp'


        print('Connecting to {0}:{1}'.format(client.server_hostname, client.port))
        result = client.run()

        if result.error:
            print(result.error)
        else:
            print('')
            print('Test completed:')
            print('  started at         {0}'.format(result.time))
            print('  bytes transmitted  {0}'.format(result.bytes))
            print('  jitter (ms)        {0}'.format(result.jitter_ms))
            print('  avg cpu load       {0}%\n'.format(result.local_cpu_total))

            print('Average transmitted data in all sorts of networky formats:')
            print('  bits per second      (bps)   {0}'.format(result.bps))
            print('  Kilobits per second  (kbps)  {0}'.format(result.kbps))
            print('  Megabits per second  (Mbps)  {0}'.format(result.Mbps))
            print('  KiloBytes per second (kB/s)  {0}'.format(result.kB_s))
            print('  MegaBytes per second (MB/s)  {0}'.format(result.MB_s))


    def run_tcp(self):
        pass

    def get_results(self):
        pass


if __name__ == '__main__':
    test = RunIperf('test')
    #test.run_server()
    test.run_client()