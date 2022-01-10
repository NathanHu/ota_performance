
import time
import datetime
import re
import telnet_rg
# import telnetlib


# Help to find out RG type.
def rg_type(host, user, pwd):
    try:
        rg_inst = RGCmd(host, user, pwd)
        rg_type = rg_inst._model
    except:
        rg_type = ''
    return rg_type


class RGCmd:

    qtn_cmd_get_5g_channel = 'call_qcsapi get_channel wifi0'
    qtn_cmd_set_5g_channel = 'call_qcsapi set_channel wifi0'
    qtn_cmd_simulate_radar = 'iwpriv wifi0 doth_radar 0'

    debug_cmd_get_2p4g_channel = 'tr69 get InternetGatewayDevice.LANDevice.1.WLANConfiguration.1.Channel'
    debug_cmd_set_2p4g_channel = 'tr69 set InternetGatewayDevice.LANDevice.1.WLANConfiguration.1.Channel='
    debug_cmd_get_5glo_channel = 'tr69 get InternetGatewayDevice.LANDevice.1.WLANConfiguration.5.Channel'
    debug_cmd_set_5glo_channel = 'tr69 set InternetGatewayDevice.LANDevice.1.WLANConfiguration.5.Channel='
    debug_cmd_get_5ghi_channel = 'tr69 get InternetGatewayDevice.LANDevice.1.WLANConfiguration.9.Channel'
    debug_cmd_set_5ghi_channel = 'tr69 set InternetGatewayDevice.LANDevice.1.WLANConfiguration.9.Channel='
    linux_cmd_simulate_radar = 'wl radar 1'

    cmd_enter_airties_www = 'cd /airties/www'
    cmd_cat_topology_txt = 'cat topology.txt'
    cmd_cat_friendly_info_txt = 'cat friendly-info.txt'
    cmd_get_uptime = 'uptime'
    cmd_top_cpu = 'top -n 1 -d 3'
    cmd_show_summary = 'show summary'

    def __init__(self, host, user, pwd):
        self._telnet_rg = telnet_rg.TelnetRG(host, user, pwd, 'rg')
        self._rg_logfile = 'RG_Log.txt'
        self._model = self.get_rg_model()
        self._rg_5g_mac = None
        self._rg_ap_info = {'change': False,
                            'initial_list': None,
                            'previous_list': None,
                            'current_list': None}
        self._channel_cca_info = {'change': False,
                                  'previous': None,
                                  'current': None}
        self._qtn_stat = {}

    def get_rg_inst(self):
        pass

    def get_rg_logfile(self):
        return self._rg_logfile

    def set_rg_logfile(self, file):
        self._rg_logfile = file

    def get_rg_model(self):
        cmd = 'show summary'
        pattern = r'Hardware:.*Model ([A-Z0-9-]+).*'
        self._telnet_rg.enter_magic()
        time.sleep(.1)
        self._telnet_rg.get_telnet_obj().write(cmd.encode('ascii') + b'\r')
        time.sleep(1)
        sess_op = self._telnet_rg.get_telnet_obj().read_very_eager()
        self._telnet_rg.close_connection()
        match = re.search(pattern, sess_op.decode('utf-8'))
        # print('Match: {}\n'.format(match))
        return match.group(1)

    def get_current_channel_cca_info(self):
        if self._channel_cca_info['current'] is None:
            return '{}'
        else:
            return self._channel_cca_info['current']

    def get_channel_cca_info_change(self):
        return self._channel_cca_info['change']

    def get_qtn_stat_info(self):
        return self._qtn_stat

    def _send_cmd(self, cmd):
        self._telnet_rg.get_telnet_obj().write(cmd.encode('ascii') + b'\r')
        time.sleep(3)

        sess_op = self._telnet_rg.get_telnet_obj().read_very_eager()

        self._telnet_rg.close_connection()

        return sess_op

    def send_rg_cmd(self, cmd):
        self._telnet_rg.enter_magic()
        return self._send_cmd(cmd)

    def send_qtn_cmd(self, cmd):
        self._telnet_rg.telnet_qtn()
        return self._send_cmd(cmd)

    def send_linux_cmd(self, cmd):
        self._telnet_rg.enter_linux()
        return self._send_cmd(cmd)

    # Get RG topology.txt file stream
    # Also retrieve Wi-Fi channel info from topology file,
    # and store Wi-Fi channel info to RG private variable.
    def get_rg_topology_txt(self):
        status = 0
        try:
            if self._model == 'BGW210-700':
                self._telnet_rg.telnet_qtn()
            else:
                self._telnet_rg.enter_linux()

            # Parse QTN status, including chipset uptime, memory usage, and CPU usage
            patt_uptime = r'.*up (.*), load.*'
            patt_memory = r'.*m: (\d*)K used, (\d*)K free.*'
            patt_cpu = r'CPU:.*nice\s+(\d*)% idle.*'

            # Read from socket, and get QTN uptime
            self._telnet_rg.get_telnet_obj().write(RGCmd.cmd_get_uptime.encode('ascii') + b'\r')
            self._telnet_rg._telnet_obj.expect([b'[0-2][0-9]:[0-5][0-9]:[0-5][0-9]'], 5)
            time.sleep(.1)
            sess_op_uptime = self._telnet_rg.get_telnet_obj().read_very_eager().decode('utf-8')
            # print(sess_op_uptime + '=================\n\n')

            uptime_results = re.search(patt_uptime, sess_op_uptime)
            uptime = uptime_results.group(1) if uptime_results else 'NA'

            # Read from socket, and get QTN Memory, CPU usage.
            self._telnet_rg.get_telnet_obj().write(RGCmd.cmd_top_cpu.encode('ascii') + b'\r')
            # Sometimes it takes longer time to run "top" command.
            self._telnet_rg._telnet_obj.expect([b'Me'], 5)
            time.sleep(.1)
            sess_op_qtn = self._telnet_rg.get_telnet_obj().read_very_eager().decode('utf-8')
            # print(sess_op_qtn + '=================\n\n')

            patterns_chip = [patt_memory, patt_cpu]
            search_results = [re.search(patt, sess_op_qtn) for patt in patterns_chip]

            memory = search_results[0].groups() if search_results[0] else ('', '')
            cpu_idle = search_results[1].group(1) if search_results[1] else ''

            memory_usage = str(int(int(memory[0]) / (int(memory[0]) + int(memory[1])) * 100)) + '%' \
                if memory[0] != '' and memory[1] != '' else 'NA'
            cpu_usage = str(int((1 - int(cpu_idle) / 100) * 100)) + '%' if cpu_idle != '' else 'NA'

            qtn_stat = {'uptime': uptime, 'memory_usage': memory_usage, 'cpu_usage': cpu_usage}
            self._qtn_stat = qtn_stat
            print(qtn_stat)

            self._telnet_rg.get_telnet_obj().write(RGCmd.cmd_enter_airties_www.encode('ascii') + b'\r')
            time.sleep(.2)
            self._telnet_rg.get_telnet_obj().write(RGCmd.cmd_cat_topology_txt.encode('ascii') + b'\r')
            _, ret_str, _ = self._telnet_rg._telnet_obj.expect([b'own'], 5)
            time.sleep(.2)

            sess_op_topology = self._telnet_rg.get_telnet_obj().read_very_eager()
            # print(sess_op_topology.decode('utf-8') + '=================\n\n')

            # Parse channel info and cca info from topology results
            pattern = r'master=\d+,(.*),fwversion='
            match = re.search(pattern, sess_op_topology.decode('utf-8'))
            if match:
                text = match.group(1)
                if self._model == 'BGW210-700':
                    patt2 = r'channel=(\d+),channel2g=(\d+),cca=(.*),cca2g=(.*)'
                    match2 = re.search(patt2,text)
                    if match2:
                        pre_ch = self._channel_cca_info['current']
                        cur_ch = {'2.4_channel': match2.group(2), '2.4_ch_cca': match2.group(4),
                                  '5GHz_channel': match2.group(1), '5GHz_channel_cca': match2.group(3)}

                        if pre_ch is not None:
                            if int(pre_ch['2.4_channel']) == int(cur_ch['2.4_channel']) and \
                                    int(pre_ch['5GHz_channel']) == int(cur_ch['5GHz_channel']):
                                self._channel_cca_info['change'] = False
                            else:
                                self._channel_cca_info['change'] = True

                        self._channel_cca_info['previous'] = pre_ch
                        self._channel_cca_info['current'] = cur_ch
                    else:
                        self._channel_cca_info['change'] = True
                        self._channel_cca_info['previous'] = self._channel_cca_info['current']
                        self._channel_cca_info['current'] = None
                else:
                    patt2 = r'channel2g=(\d+),channel=(\d+),channel52g=(\d+),cca2g=(.*),cca=(.*),cca52g=(.*)'
                    match2 = re.search(patt2, text)
                    if match2:
                        channel5gHzlo = match2.group(3)
                        channel5gHzhi = match2.group(2)
                        channel2p4gHz = match2.group(1)
                        cca5gHzlo = match2.group(6)
                        cca5gHzhi = match2.group(5)
                        cca2p4gHz = match2.group(4)
                        channel_cca_info = '2.4GHz channel: {}, cca: {}, 5Ghz Lo channel: {}, cca: {}, 5GHz Hi channel: {}, cca: {}'.format(channel2p4gHz, cca2p4gHz, channel5gHzlo, cca5gHzlo, channel5gHzhi, cca5gHzhi)
                        self._channel_cca_info = channel_cca_info
                    else:
                        self._channel_cca_info = 'Channel cca info unavailable'
            else:
                self._channel_cca_info = 'Channel cca info unavailable'

            # Get time stamp for calculating streaming throughput
            timestamp = int(time.mktime(datetime.datetime.now().timetuple()))

            self._telnet_rg.close_connection()
            sess_op_topology = sess_op_topology.decode('utf-8')
        except:
            status = 1
            sess_op_topology = ""
            timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
        return status, sess_op_topology, timestamp

    # Get both friendly_info and topology file for processing friendly name info.
    # Topology info is to find out live APs (4920/4921).
    def get_rg_friendly_topology_info(self):

        # Telnet to QTN chip.
        self._telnet_rg.telnet_qtn()

        # Enter directory /airties/www in QTN chip.
        self._telnet_rg.get_telnet_obj().write(RGCmd.cmd_enter_airties_www.encode('ascii') + b'\r')
        time.sleep(.2)

        # Get friendly_info text.
        self._telnet_rg.get_telnet_obj().write(RGCmd.cmd_cat_friendly_info_txt.encode('ascii') + b'\r')
        time.sleep(.4)

        # Get topology text.
        self._telnet_rg.get_telnet_obj().write(RGCmd.cmd_cat_topology_txt.encode('ascii') + b'\r')
        time.sleep(.5)

        sess_op = self._telnet_rg.get_telnet_obj().read_very_eager()
        sess_op = sess_op.decode('utf-8')

        self._telnet_rg.close_connection()

        return sess_op


    # Get RG friendly-info.txt file stream
    def get_rg_friendly_info(self):
        status = 0
        try:
            if self._model == 'BGW210-700':
                self._telnet_rg.telnet_qtn()
            else:
                self._telnet_rg.enter_linux()

            self._telnet_rg.get_telnet_obj().write(RGCmd.cmd_enter_airties_www.encode('ascii') + b'\r')
            time.sleep(.1)
            self._telnet_rg.get_telnet_obj().write(RGCmd.cmd_cat_friendly_info_txt.encode('ascii') + b'\r')
            time.sleep(.2)

            sess_op = self._telnet_rg.get_telnet_obj().read_very_eager()

            # Get time stamp for calculating streaming throughput
            timestamp = int(time.mktime(datetime.datetime.now().timetuple()))

            self._telnet_rg.close_connection()
            sess_op = sess_op.decode('utf-8')
        except:
            status = 1
            sess_op = ""
            timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
        return status, sess_op, timestamp

    # Get 2.4GHz channel.
    def get_24g_channel(self):
        status = 0

        if self._model == 'BGW210-700':
            self._telnet_rg.enter_debug()
            self._telnet_rg.get_telnet_obj().write(RGCmd.debug_cmd_get_2p4g_channel.encode('ascii') + b'\r')
            time.sleep(.2)
            sess_op = self._telnet_rg.get_telnet_obj().read_very_eager()

            match = re.search(r'InternetGatewayDevice.LANDevice.1.WLANConfiguration.1.Channel (\d+)',
                              sess_op.decode('utf-8'))

            if match:
                channel = match.group(1)
            else:
                channel = '-1'

        else:
            channel = '-1'

        return status, channel

    # Get QTN 5g channel
    def get_qtn_5g_channel(self):
        status = 0
        try:
            if self._model == 'BGW210-700':
                self._telnet_rg.telnet_qtn()
                self._telnet_rg.get_telnet_obj().write(RGCmd.qtn_cmd_get_5g_channel.encode('ascii') + b'\r')
                time.sleep(.5)
                sess_op = self._telnet_rg.get_telnet_obj().read_very_eager()

                self._telnet_rg.close_connection()

                match = re.search(r'call_qcsapi get_channel wifi0\r\n(\d+)', sess_op.decode('utf-8'))

                if match:
                    channel = match.group(1)
                    channel = int(channel)
                else:
                    channel = 0
            else:
                self._telnet_rg.enter_debug()
                self._telnet_rg.get_telnet_obj().write(RGCmd.debug_cmd_get_5glo_channel.encode('ascii') + b'\r')

                sess_op = self._telnet_rg.get_telnet_obj().read_very_eager()

                self._telnet_rg.close_connection()

                match = re.search(r'InternetGatewayDevice.LANDevice.1.WLANConfiguration.5.Channel (\d+)',
                                  sess_op.decode('utf-8'))

                if match:
                    channel = match.group(1)
                    channel = int(channel)
                else:
                    channel = 0
        except:
            status = 1
            channel = 0
        return status, channel

    # Channel change for 2.4GHz or 5GHz channel.
    # After performing channel change, return new 2.4GHz or 5GHz channel.
    def manual_channel_change(self, channel):
        status = 0
        try:
            if self._model == 'BGW210-700':
                if channel > 20:
                    self._telnet_rg.telnet_qtn()

                    cmd = RGCmd.qtn_cmd_set_5g_channel + ' ' + str(channel)

                    # Set 5g channel
                    self._telnet_rg.get_telnet_obj().write(cmd.encode('ascii') + b'\r')

                    # Original is 2 seconds, which works well. To be safe, set it to 3 seconds.
                    time.sleep(3)

                    # Get new 5GHz channel, after setting channel.
                    self._telnet_rg.get_telnet_obj().write(RGCmd.qtn_cmd_get_5g_channel.encode('ascii') + b'\r')
                    time.sleep(1)
                    sess_op = self._telnet_rg.get_telnet_obj().read_very_eager()

                    # Close telnet session
                    self._telnet_rg.close_connection()

                    match = re.search(r'call_qcsapi get_channel wifi0\r\n(\d+)', sess_op.decode('utf-8'))

                else:
                    self._telnet_rg.enter_debug()

                    cmd = RGCmd.debug_cmd_set_2p4g_channel + str(channel)

                    # Set 2.4GHz channel
                    self._telnet_rg.get_telnet_obj().write(cmd.encode('ascii') + b'\r')

                    # If wait time is 8 seconds, it still returns the channel before channel change.
                    # Setting wait time for 9 seconds, it returns new channel. TR69 command is slow.
                    # To be safe, set delay to 12 seconds.
                    time.sleep(12)

                    # Get current 2.4GHz channel, after setting channel.
                    self._telnet_rg.get_telnet_obj().write(RGCmd.debug_cmd_get_2p4g_channel.encode('ascii') + b'\r')
                    time.sleep(1)
                    sess_op = self._telnet_rg.get_telnet_obj().read_very_eager()

                    # Close telnet session
                    self._telnet_rg.close_connection()

                    match = re.search(r'InternetGatewayDevice.LANDevice.1.WLANConfiguration.1.Channel (\d+)', sess_op.decode('utf-8'))

                if match:
                    channel = int(match.group(1))
                else:
                    channel = 0
            else:
                self._telnet_rg.enter_debug()

                if channel < 100 and channel > 20:

                    cmd = RGCmd.debug_cmd_set_5glo_channel + str(channel)

                    # Set 5g channel
                    self._telnet_rg.get_telnet_obj().write(cmd.encode('ascii') + b'\r')
                    time.sleep(5)

                    # Get current 5g channel, after setting channel.
                    self._telnet_rg.get_telnet_obj().write(RGCmd.debug_cmd_get_5glo_channel.encode('ascii') + b'\r')
                    time.sleep(1)
                    sess_op = self._telnet_rg.get_telnet_obj().read_very_eager()

                    # Close telnet session
                    self._telnet_rg.close_connection()

                    match = re.search(r'InternetGatewayDevice.LANDevice.1.WLANConfiguration.5.Channel (\d+)', sess_op.decode('utf-8'))

                elif channel >= 100:

                    cmd = RGCmd.debug_cmd_set_5ghi_channel + str(channel)

                    # Set 5g channel
                    self._telnet_rg.get_telnet_obj().write(cmd.encode('ascii') + b'\r')
                    time.sleep(5)

                    # Get current 5g channel, after setting channel.
                    self._telnet_rg.get_telnet_obj().write(RGCmd.debug_cmd_get_5ghi_channel.encode('ascii') + b'\r')
                    time.sleep(1)
                    sess_op = self._telnet_rg.get_telnet_obj().read_very_eager()

                    # Close telnet session
                    self._telnet_rg.close_connection()

                    match = re.search(r'InternetGatewayDevice.LANDevice.1.WLANConfiguration.9.Channel (\d+)', sess_op.decode('utf-8'))

                elif channel < 20:

                    cmd = RGCmd.debug_cmd_set_2p4g_channel + str(channel)

                    # Set 5g channel
                    self._telnet_rg.get_telnet_obj().write(cmd.encode('ascii') + b'\r')
                    time.sleep(5)

                    # Get current 5g channel, after setting channel.
                    self._telnet_rg.get_telnet_obj().write(RGCmd.debug_cmd_get_2p4g_channel.encode('ascii') + b'\r')
                    time.sleep(1)
                    sess_op = self._telnet_rg.get_telnet_obj().read_very_eager()

                    # Close telnet session
                    self._telnet_rg.close_connection()

                    match = re.search(r'InternetGatewayDevice.LANDevice.1.WLANConfiguration.1.Channel (\d+)', sess_op.decode('utf-8'))

                if match:
                    channel = match.group(1)
                    channel = int(channel)
                else:
                    channel = 0
        except:
            status = 1
            channel = 0
        return status, channel

    # Simulate radar to perform DFS channel change
    def dfs_channel_change(self):
        status = 0
        try:
            if self._model == 'BGW210-700':
                self._telnet_rg.telnet_qtn()

                cmd = RGCmd.qtn_cmd_simulate_radar

                # Simulate radar
                self._telnet_rg.get_telnet_obj().write(cmd.encode('ascii') + b'\r')
                time.sleep(2)

                # Get current 5g channel, after setting channel.
                self._telnet_rg.get_telnet_obj().write(RGCmd.qtn_cmd_get_5g_channel.encode('ascii') + b'\r')
                time.sleep(1)
                sess_op = self._telnet_rg.get_telnet_obj().read_very_eager()

                # Close telnet session
                self._telnet_rg.close_connection()

                match = re.search(r'call_qcsapi get_channel wifi0\r\n(\d+)', sess_op.decode('utf-8'))

                if match:
                    channel = match.group(1)
                    channel = int(channel)
                else:
                    channel = 0
            else:
                self._telnet_rg.enter_linux()

                cmd = RGCmd.linux_cmd_simulate_radar

                # Simulate radar
                self._telnet_rg.get_telnet_obj().write(cmd.encode('ascii') + b'\r')
                time.sleep(2)

                # Close telnet session
                self._telnet_rg.close_connection()

                # Enter debug session
                self._telnet_rg.enter_debug()

                # Get current 5g channel, after setting channel.
                self._telnet_rg.get_telnet_obj().write(RGCmd.debug_cmd_get_5glo_channel.encode('ascii') + b'\r')
                time.sleep(1)
                sess_op = self._telnet_rg.get_telnet_obj().read_very_eager()

                # Close telnet session
                self._telnet_rg.close_connection()

                match = re.search(r'InternetGatewayDevice.LANDevice.1.WLANConfiguration.5.Channel (\d+)', sess_op.decode('utf-8'))

                if match:
                    channel = match.group(1)
                    channel = int(channel)
                else:
                    channel = 0
        except:
            status = 1
            channel = 0
        return status, channel

    # Write log file
    def write_log_file(self, time_stamp, log, before_msg, after_msg):

        with open(self._rg_logfile, 'a') as logfile:
            logfile.write('\n\n{0}\n=============== {1} ===============\n'.format(before_msg, time_stamp))
            logfile.write(log)
            logfile.write('{0}\n\n'.format(after_msg))

        return 0







# if __name__ == "__main__":
#     test = RGCmd()
#     return_value = test.send_rg_cmd('show wireless client')
#
#     print(return_value)

# if __name__ == "__main__":
#
#     test = RGCmd()
#     print(test._model)
#     # print(test.get_24g_channel())
#     print('2.4 Channel: {}\n'.format(test.manual_channel_change(36)[1]))


if __name__ == "__main__":

    # test = RGCmd('192.168.1.254', 'admin', 'austin123')
    # print('RG model: {}'.format(test.get_rg_model()))
    # _, topology_info, _ = test.get_rg_topology_txt()
    # print(topology_info)
    print(rg_type('192.168.1.254', 'admin', 'austin123'))


# inst = telnet_rg.TelnetRG()
# print(dir(inst))
#
# print(help(inst))

# if __name__ == "__main__":
#     test = RGCmd()
#     return_value = test.get_qtn_5g_channel()
#     print(return_value)


# # Test get_connected_stations function.
# if __name__ == "__main__":
#     test = RGCmd()
#     topology_stream = test.get_rg_topology_txt()
#     connected_stations = get_connected_stations(topology_stream.decode('utf-8'))
#     print(connected_stations)


