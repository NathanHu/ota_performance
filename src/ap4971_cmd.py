
import time
import datetime
import re
import telnet_rg
import common_functions



class AP4971Cmd:

    cmd_cat_topology_txt = 'cat /tmp/topology.txt'
    cmd_cat_friendly_info_txt = 'cat /tmp/friendly-info.txt'
    cmd_get_uptime = 'uptime'
    cmd_top_cpu = 'top -n 1 -d 3'

    def __init__(self, ap_host_ip):
        self._ap_host_ip = ap_host_ip
        self._telnet_rg = telnet_rg.TelnetRG(self._ap_host_ip, 'admin', 'austin123', '4971')


    # Get friendly-info.txt file output
    def get_ap_friendly_info_txt(self):
        status = 0
        sess_op = ''
        log_failure = ''

        log = ''

        if not self._telnet_rg._connected:
            ret_val = self._telnet_rg.connect()

        if self._telnet_rg._connected:
            try:
                self._telnet_rg.get_telnet_obj().write(AP4971Cmd.cmd_cat_friendly_info_txt.encode('ascii') + b'\r')
                _, ret_str, _ = self._telnet_rg._telnet_obj.expect([b'own'], 5)
                time.sleep(.2)
                sess_op = self._telnet_rg.get_telnet_obj().read_very_eager().decode('utf-8')
                self._telnet_rg.close_connection()
            except:
                sess_op = ''
                # log = '### Can telnet to AP; cannot get friendly-info file from 4920 telnet, #{}\n\n'
                # log = self._telnet_rg._error_log + log
                log = 'failed'
        else:
            sess_op = ''
            # log = '### Cannot telnet to AP; cannot get friendly-info file from 4920 telnet, #{}\n\n'
            # log = self._telnet_rg._error_log + log
            log = 'failed'

        if not log:
            if re.search(r'.*addr=', sess_op):
                log_failure = ''
                # break
            else:
                # log_failure = log_failure + '### Empty friendly-info file, #{}\n\n'
                log_failure = 'failed'
        else:
            # log_failure = log_failure + log
            log_failure = 'failed'

        # time.sleep(5)

        # Get time stamp for calculating streaming throughput. No use for friendly-info file.
        timestamp = int(time.mktime(datetime.datetime.now().timetuple()))

        # If there is connection or getting file error, print out log to console.
        if log_failure:
            print(log_failure)

        return status, sess_op, timestamp

    # Get topology.txt file output
    def get_ap_topology_txt(self):
        status = 0
        sess_op_topology = ''
        log_failure = ''
        ap_info = {}

        # Pattern for parsing chipset uptime, memory usage, and CPU usage
        patt_uptime = r'.*up (.*),\s+load.*'
        patt_memory = r'.*m: (\d*)K used, (\d*)K free.*'
        # For CPU, it uses floating number
        patt_cpu = r'.*CPU:.*nic (.*)% idle.*'
        # For radio and FW, from topology file
        patt_radio_fw = r'channel2g=(\d+),channel=(\d+),channel52g=(\d+),cca2g=(.*),cca=(.*),cca52g=(.*),' \
                        r'fwversion=(.*),apibuild'

        log = ''
        # ap_info = {}

        # Try telnet to AP
        if not self._telnet_rg._connected:
            ret_val = self._telnet_rg.connect()

        # If telnet is successful, get info from AP
        # Otherwise, reports telnet error.
        if self._telnet_rg._connected:
            try:
                # Get AP uptime
                self._telnet_rg.get_telnet_obj().write(AP4971Cmd.cmd_get_uptime.encode('ascii') + b'\r')

                # Expect current time string like: 09:34:37
                self._telnet_rg.get_telnet_obj().expect([b'[0-2][0-9]:[0-5][0-9]:[0-5][0-9]'], 10)
                time.sleep(.2)
                sess_op_uptime = self._telnet_rg.get_telnet_obj().read_very_eager().decode('utf-8')
                uptime_results = re.search(patt_uptime, sess_op_uptime)
                uptime = uptime_results.group(1) if uptime_results else 'NA'

                # Read from socket, get memory and CPU usage.
                self._telnet_rg.get_telnet_obj().write(AP4971Cmd.cmd_top_cpu.encode('ascii') + b'\r')
                self._telnet_rg.get_telnet_obj().expect([b'Me'], 10)
                time.sleep(.3)
                sess_op_cpu_mem = self._telnet_rg.get_telnet_obj().read_very_eager().decode('utf-8')

                memory_usage, cpu_usage = common_functions.cal_mem_cpu_usage(sess_op_cpu_mem, '4971')

                # patterns_chip = [patt_memory, patt_cpu]
                # search_results = [re.search(patt, sess_op_cpu_mem) for patt in patterns_chip]
                #
                # memory = search_results[0].groups() if search_results[0] else ('', '')
                # cpu_idle = search_results[1].group(1) if search_results[1] else ''
                # # print('cpu_idle:{}'.format(cpu_idle))
                #
                # memory_usage = str(int(int(memory[0]) / (int(memory[0]) + int(memory[1])) * 100)) + '%' \
                #     if memory[0] != '' and memory[1] != '' else 'NA'
                # cpu_usage = str(int((1 - float(cpu_idle) / 100) * 100)) + '%' if cpu_idle != '' else 'NA'

                # [uptime, memory_usage, cpu_usage]
                ap_info = {'uptime': uptime, 'memory_usage': memory_usage, 'cpu_usage': cpu_usage}
                # print('4920 AP info: {}\n'.format(ap_info))

                self._telnet_rg.get_telnet_obj().write(AP4971Cmd.cmd_cat_topology_txt.encode('ascii') + b'\r')
                _, ret_str, _ = self._telnet_rg._telnet_obj.expect([b'own'], 10)
                time.sleep(.4)
                sess_op_topology = self._telnet_rg.get_telnet_obj().read_very_eager().decode('utf-8')
                self._telnet_rg.close_connection()

                # Process topology to get info regarding radio and FW version
                match = re.search(patt_radio_fw, sess_op_topology)

                if match:
                    radio_fw = {'fw': match.group(7),
                                '2.4_channel': match.group(1), '2.4_ch_cca': match.group(4),
                                '5_hi_channel': match.group(2), '5_hi_ch_cca': match.group(5),
                                '5_lo_channel': match.group(3), '5_lo_ch_cca': match.group(6)}
                    log = 'success'
                else:
                    radio_fw = {'fw': 'NA',
                                '2.4_channel': 'NA', '2.4_ch_cca': 'NA',
                                '5_lo_channel': 'NA', '5_lo_ch_cca': 'NA',
                                '5_hi_channel': 'NA', '5_hi_ch_cca': 'NA'}
                    log = 'failed'
                ap_info = {**ap_info, **radio_fw}


            except:
                ap_info = {'uptime': 'NA', 'memory_usage': 'NA', 'cpu_usage': 'NA',
                           'fw': 'NA',
                           '2.4_channel': 'NA', '2.4_ch_cca': 'NA',
                           '5_lo_channel': 'NA', '5_lo_ch_cca': 'NA',
                           '5_hi_channel': 'NA', '5_hi_ch_cca': 'NA'}
                sess_op_topology = ''
                # log = '###Can telnet to AP; cannot get topology file from 4920 telnet, #{}\n\n'
                # log = self._telnet_rg._error_log + log
                log = 'failed'


        else:
            ap_info = {'uptime': 'NA', 'memory_usage': 'NA', 'cpu_usage': 'NA',
                       'fw': 'NA',
                       '2.4_channel': 'NA', '2.4_ch_cca': 'NA',
                       '5_lo_channel': 'NA', '5_lo_ch_cca': 'NA',
                       '5_hi_channel': 'NA', '5_hi_ch_cca': 'NA'}
            sess_op_topology = ''
            # log = '###Cannot telnet to AP; cannot get topology file from 4920 telnet, #{}\n\n'
            # log = self._telnet_rg._error_log + log
            log = 'failed'

        # if not log:
        #     if re.search(r'.*addr=', sess_op_topology):
        #         # log_failure = log_failure + self._telnet_rg._error_log
        #         log_failure = 'success'
        #         connection = {'conn_err': log_failure}
        #         ap_info = {**ap_info, **connection}
        #         # break
        #     else:
        #         # log_failure = log_failure + self._telnet_rg._error_log + \
        #         #               '### Empty topology file from AP, #{}\n\n'
        #         log_failure = 'failed'
        #         connection = {'conn_err': log_failure}
        #         ap_info = {**ap_info, **connection}
        # else:
        #     # log_failure = log_failure + log
        #     log_failure = 'failed'
        #     connection = {'conn_err': log_failure}
        #     ap_info = {**ap_info, **connection}
        connection = {'conn_err': log}
        ap_info = {**ap_info, **connection}

        # time.sleep(5)

        timestamp = int(time.mktime(datetime.datetime.now().timetuple()))

        if log_failure:
            print(log_failure)

        return status, ap_info, sess_op_topology, timestamp


if __name__ == "__main__":
    ap4971 = AP4971Cmd('192.168.1.64')

    _, friendlyInfo, _ = ap4971.get_ap_friendly_info_txt()
    print('friendly-info: \n{}\n\n'.format(friendlyInfo))

    _, ap_info_4971, topology, _ = ap4971.get_ap_topology_txt()
    print('ap_info: \n{}\n\n'.format(ap_info_4971))
    print('topology: \n{}\n'.format(topology))
