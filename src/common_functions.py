
from . import configuration
from . import rg_cmd
import datetime
import re
import math
import multiprocessing.dummy
import multiprocessing
import subprocess


# Parse topology.txt file, to get connected live APs (4920/4921).
def get_live_ap_mac(rg_topology_data):

    mesh_ap_pattern = re.compile(
        r'ownaddr=(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w),type=mesh.*,dev=(.*),'
        r'mac=(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w),band=(\d+),qual=(\d+),nss=\d+,rxpr=\d+,txpr=\d+,'
        r'mrxpr=\d+,mtxpr=\d+,rssi=-\d+,'
    )

    matches = mesh_ap_pattern.finditer(rg_topology_data)

    live_ap_macs = []

    for match in matches:
        if int(match.group(5)) != 0:
            live_ap_macs.append(match.group(3))

    return live_ap_macs


# Compare the client list before and after channel change:
# client_connected, client_connected_ap, and client_band.
def compare_client_list(client_list_1, client_list_2):

    client_list_difference = {}

    # Iterate client_list_1.
    for client_mac in client_list_1:

        # Find out if client is connected to mesh.
        if client_mac not in client_list_2:

            # {client_mac:
            # [client_ip,
            #  client_friendly_name,
            #  {'connected': True/False},
            #  {'new_added': True/False},
            #  {'same_ap': True/False, 'ap_1': ap_mac, 'ap_2': ap_mac},
            #  {'same_band': True/False, 'band_1': band, 'band_2': band},
            #  {'same_5gch': True/False, '5gch_1': lo/hi/--, '5gch_2': lo/hi/--
            #  {'rssi_1': rssi_value, 'rssi_2': rssi_value},
            #  {'traffic': True/False, 'tx_1': tx_bytes, 'tx_2': tx_bytes},
            #  {'time_1': timestamp, 'time_2': timestamp}]
            # }
            client_list_difference.update(
                {client_mac: [client_list_1[client_mac][0],
                              client_list_1[client_mac][1],
                              {'connected': False},
                              {'new_added': False},
                              {'same_ap': False, 'ap_1': client_list_1[client_mac][2], 'ap_2': None},
                              {'same_band': False, 'band_1': client_list_1[client_mac][4], 'band_2': None},
                              {'same_ch5g': True, 'ch5g_1': client_list_1[client_mac][3], 'ch5g_2': None},
                              {'rssi_1': client_list_1[client_mac][5], 'rssi_2': None},
                              {'traffic': False, 'tx_1': client_list_1[client_mac][6], 'tx_2': None},
                              {'time_1': client_list_1[client_mac][7], 'time_2': None}]})
        else:
            # In general, 'same_ch5g' is always True.
            # The only time it becomes False, is when both before and current connection are on 5GHz radio,
            # and it's on different 5GHz radio: hi/lo
            ch5g = {'same_ch5g': True, 'ch5g_1': client_list_1[client_mac][3],
                    'ch5g_2': client_list_2[client_mac][3]}

            # Compare if client connects to the same AP.
            if client_list_1[client_mac][2] == client_list_2[client_mac][2]:
                ap = {'same_ap': True, 'ap_1': client_list_1[client_mac][2], 'ap_2': client_list_2[client_mac][2]}
            else:
                ap = {'same_ap': False, 'ap_1': client_list_1[client_mac][2], 'ap_2': client_list_2[client_mac][2]}

            # Compare if client is on the same radio band.
            if client_list_1[client_mac][4] == client_list_2[client_mac][4]:
                band = {'same_band': True, 'band_1': client_list_1[client_mac][4],
                        'band_2': client_list_2[client_mac][4]}
            # For BGW320, 5GHz channel could be 5 or 52, which depends on 5 low or 5 high.
            elif re.search(r'5', client_list_1[client_mac][4]) and re.search(r'5', client_list_2[client_mac][4]):
                band = {'same_band': True, 'band_1': client_list_1[client_mac][4],
                        'band_2': client_list_2[client_mac][4]}
                ch5g = {'same_ch5g': False, 'ch5g_1': client_list_1[client_mac][3],
                        'ch5g_2': client_list_2[client_mac][3]}
            else:
                band = {'same_band': False, 'band_1': client_list_1[client_mac][4],
                        'band_2': client_list_2[client_mac][4]}

            client_list_difference.update(
                {client_mac: [client_list_1[client_mac][0],
                              client_list_1[client_mac][1],
                              {'connected': True},
                              {'new_added': False},
                              ap, band, ch5g,
                              {'rssi_1': client_list_1[client_mac][5], 'rssi_2': client_list_2[client_mac][5]},
                              {'traffic': True, 'tx_1': client_list_1[client_mac][6],
                               'tx_2': client_list_2[client_mac][6]},
                              {'time_1': client_list_1[client_mac][7], 'time_2': client_list_2[client_mac][7]}]})

    # Iterate client_list_2.
    for client_mac in client_list_2:

        # Find out if there is newly added clients on client_list_2.
        if client_mac not in client_list_1:
            client_list_difference.update(
                {client_mac: [client_list_2[client_mac][0],
                              client_list_2[client_mac][1],
                              {'connected': True},
                              {'new_added': True},
                              {'same_ap': False, 'ap_1': None, 'ap_2': client_list_2[client_mac][2]},
                              {'same_band': False, 'band_1': None, 'band_2': client_list_2[client_mac][4]},
                              {'same_ch5g': True, 'ch5g_1': None, 'ch5g_2': client_list_2[client_mac][3]},
                              {'rssi_1': None, 'rssi_2': client_list_2[client_mac][5]},
                              {'traffic': False, 'tx_1': None, 'tx_2': client_list_2[client_mac][6]},
                              {'time_1': None, 'time_2': client_list_2[client_mac][7]}]})

    return client_list_difference


# Test if streaming clients are the same list.
def clients_keep_streaming(streaming_clients_1, streaming_clients_2):

    # The number of clients should be the same.
    if len(streaming_clients_1) != len(streaming_clients_2):
        return 1
    # Client MAC addresses should be the same.
    else:
        for key in streaming_clients_1:
            if streaming_clients_2.get(key) is None:
                return 1
        return 0


def print_client_list_difference_header():

    # client_state_0, friendly_name_1, client_MAC_2, client_IP_3, previous_AP_MAC_4, current_AP_MAC_5,
    # previous_band_6, current_band_7, previous_RSSI_8, current_RSSI_9, tx_bytes_sec_10, stream_vid_11,
    # stream_mc_12, bytes_diff_13, time_diff_14
    item_name = str_fmt_compare('mesh_clients_state', 'client_name', 'client_mac', 'client_ip',
                                'pre_AP_mac', 'cur_AP_mac', 'pre_5g', 'cur_5g', 'pre_band',
                                'cur_band', 'pre_RSSI', 'cur_RSSI', 'bytes_sec', 'stream_vid',
                                'stream_mc', 'bytes_diff', 'time_diff')
    symbol = '-'
    separator = str_fmt_compare(symbol*20, symbol*26, symbol*18, symbol*15, symbol*18, symbol*18,
                                symbol*6, symbol*6, symbol*8, symbol*8, symbol*8, symbol*8,
                                symbol*9, symbol*10, symbol*9, symbol*15, symbol*10)
    diff_header = item_name + separator

    return diff_header


# Print out the difference of clients after channel change. It's to print to log file,
# which is more readable to users.
def print_client_list_difference(clients_list_difference, stream_dict_1=None, stream_dict_2=None):
    client_list_no_change = ''
    client_list_disconnected = ''
    client_list_change_ap = ''
    client_list_change_band = ''
    client_list_change_lohi5g = ''
    client_list_new_added = ''
    streaming_clients_dic = {}

    for client_mac in clients_list_difference:

        stream_vid = 'no'
        stream_mc = '--'
        bytes_diff = 0
        time_diff = 0
        bytes_sec = 0

        # # Regarding streaming, find out if this method is to calculate throughput, or
        # # print out streaming difference, after mesh change (mc).
        # # streaming_dic (streaming_dictionary) is the client list which are streaming.
        # if (stream_dic_1 is not None) and (stream_dic_2 is not None):
        #     if client_mac in stream_dic_1:
        #         stream_vid = 'YES'
        #     else:
        #         stream_vid = 'no'
        #
        #     if client_mac in stream_dic_2:
        #         stream_mc = 'YES'
        #     else:
        #         stream_mc = 'no'

        # streaming_dic (streaming_dictionary) is the client list which are streaming.
        # stream_dic_1 is the list of streaming clients before channel change;
        # stream_dic_2 is the list of streaming clients after channel change.
        # If client streams before channel change, set stream_vid "YES".
        # If client streams before and after channel change, set stream_mc "YES".
        if (stream_dict_1 is not None) and (stream_dict_2 is not None):

            if (client_mac in stream_dict_1) and (client_mac in stream_dict_2):
                stream_vid = 'YES'
                stream_mc = 'YES'
            elif client_mac in stream_dict_1:
                stream_vid = 'YES'
                stream_mc = 'no'
            else:
                stream_vid = 'no'
                stream_mc = 'no'

        # Calculate client streaming
        else:
            if clients_list_difference[client_mac][8]['traffic']:
                bytes_diff = int(clients_list_difference[client_mac][8]['tx_2']) - \
                             int(clients_list_difference[client_mac][8]['tx_1'])

                time_diff = int(clients_list_difference[client_mac][9]['time_2']) - \
                            int(clients_list_difference[client_mac][9]['time_1'])
                bytes_sec = math.ceil(bytes_diff / time_diff)

            if bytes_sec > configuration.streaming_threshold:
                stream_vid = 'YES'

        # client_state_0, friendly_name_1, client_MAC_2, client_IP_3, previous_AP_MAC_4, current_AP_MAC_5,
        # previous_band_6, current_band_7, previous_RSSI_8, current_RSSI_9, tx_bytes_sec_10, stream_vid_11,
        # stream_mc_12, bytes_diff_13, time_diff_14
        if clients_list_difference[client_mac][3]['new_added'] is True:
            client_list_new_added = client_list_new_added + \
                                    str_fmt_compare(
                                        'Newly Added to mesh',
                                        clients_list_difference[client_mac][1],
                                        client_mac,
                                        clients_list_difference[client_mac][0],
                                        '---',
                                        clients_list_difference[client_mac][4]['ap_2'],
                                        '---',
                                        clients_list_difference[client_mac][6]['ch5g_2'],
                                        '---',
                                        clients_list_difference[client_mac][5]['band_2'],
                                        '---',
                                        clients_list_difference[client_mac][7]['rssi_2'],
                                        '---',
                                        stream_vid,
                                        stream_mc,
                                        '---',
                                        '---',
                                    )
        # client_state_0, friendly_name_1, client_MAC_2, client_IP_3, previous_AP_MAC_4, current_AP_MAC_5,
        # previous_band_6, current_band_7, previous_RSSI_8, current_RSSI_9, tx_bytes_sec_10, stream_vid_11,
        # stream_mc_12, bytes_diff_13, time_diff_14
        elif clients_list_difference[client_mac][2]['connected'] is False:
            client_list_disconnected = client_list_disconnected + \
                                       str_fmt_compare(
                                           'Disconnected to mesh',
                                           clients_list_difference[client_mac][1],
                                           client_mac,
                                           clients_list_difference[client_mac][0],
                                           clients_list_difference[client_mac][4]['ap_1'],
                                           '---',
                                           clients_list_difference[client_mac][6]['ch5g_1'],
                                           '---',
                                           clients_list_difference[client_mac][5]['band_1'],
                                           '---',
                                           clients_list_difference[client_mac][7]['rssi_1'],
                                           '---',
                                           '---',
                                           stream_vid,
                                           stream_mc,
                                           '---',
                                           '---')
        # client_state_0, friendly_name_1, client_MAC_2, client_IP_3, previous_AP_MAC_4, current_AP_MAC_5,
        # previous_band_6, current_band_7, previous_RSSI_8, current_RSSI_9, tx_bytes_sec_10, stream_vid_11,
        # stream_mc_12, bytes_diff_13, time_diff_14
        elif clients_list_difference[client_mac][4]['same_ap'] is False:
            client_list_change_ap = client_list_change_ap + \
                                    str_fmt_compare(
                                        'To different AP',
                                        clients_list_difference[client_mac][1],
                                        client_mac,
                                        clients_list_difference[client_mac][0],
                                        clients_list_difference[client_mac][4]['ap_1'],
                                        clients_list_difference[client_mac][4]['ap_2'],
                                        clients_list_difference[client_mac][6]['ch5g_1'],
                                        clients_list_difference[client_mac][6]['ch5g_2'],
                                        clients_list_difference[client_mac][5]['band_1'],
                                        clients_list_difference[client_mac][5]['band_2'],
                                        clients_list_difference[client_mac][7]['rssi_1'],
                                        clients_list_difference[client_mac][7]['rssi_2'],
                                        bytes_sec,
                                        stream_vid,
                                        stream_mc,
                                        bytes_diff,
                                        time_diff)
        # client_state_0, friendly_name_1, client_MAC_2, client_IP_3, previous_AP_MAC_4, current_AP_MAC_5,
        # previous_band_6, current_band_7, previous_RSSI_8, current_RSSI_9, tx_bytes_sec_10, stream_vid_11,
        # stream_mc_12, bytes_diff_13, time_diff_14
        elif clients_list_difference[client_mac][5]['same_band'] is False:
            client_list_change_band = client_list_change_band + \
                                      str_fmt_compare(
                                          'Different band',
                                          clients_list_difference[client_mac][1],
                                          client_mac,
                                          clients_list_difference[client_mac][0],
                                          clients_list_difference[client_mac][4]['ap_1'],
                                          clients_list_difference[client_mac][4]['ap_2'],
                                          clients_list_difference[client_mac][6]['ch5g_1'],
                                          clients_list_difference[client_mac][6]['ch5g_2'],
                                          clients_list_difference[client_mac][5]['band_1'],
                                          clients_list_difference[client_mac][5]['band_2'],
                                          clients_list_difference[client_mac][7]['rssi_1'],
                                          clients_list_difference[client_mac][7]['rssi_2'],
                                          bytes_sec,
                                          stream_vid,
                                          stream_mc,
                                          bytes_diff,
                                          time_diff)
        elif clients_list_difference[client_mac][6]['same_ch5g'] is False:
            client_list_change_lohi5g = client_list_change_lohi5g + \
                                      str_fmt_compare(
                                          'Different 5GHz Lo_Hi',
                                          clients_list_difference[client_mac][1],
                                          client_mac,
                                          clients_list_difference[client_mac][0],
                                          clients_list_difference[client_mac][4]['ap_1'],
                                          clients_list_difference[client_mac][4]['ap_2'],
                                          clients_list_difference[client_mac][6]['ch5g_1'],
                                          clients_list_difference[client_mac][6]['ch5g_2'],
                                          clients_list_difference[client_mac][5]['band_1'],
                                          clients_list_difference[client_mac][5]['band_2'],
                                          clients_list_difference[client_mac][7]['rssi_1'],
                                          clients_list_difference[client_mac][7]['rssi_2'],
                                          bytes_sec,
                                          stream_vid,
                                          stream_mc,
                                          bytes_diff,
                                          time_diff)
        else:
            # client_state_0, friendly_name_1, client_MAC_2, client_IP_3, previous_AP_MAC_4, current_AP_MAC_5,
            # previous_band_6, current_band_7, previous_RSSI_8, current_RSSI_9, tx_bytes_sec_10, stream_vid_11,
            # stream_mc_12, bytes_diff_13, time_diff_14
            client_list_no_change = client_list_no_change + \
                                    str_fmt_compare(
                                        'No change',
                                        clients_list_difference[client_mac][1],
                                        client_mac,
                                        clients_list_difference[client_mac][0],
                                        clients_list_difference[client_mac][4]['ap_1'],
                                        clients_list_difference[client_mac][4]['ap_2'],
                                        clients_list_difference[client_mac][6]['ch5g_1'],
                                        clients_list_difference[client_mac][6]['ch5g_2'],
                                        clients_list_difference[client_mac][5]['band_1'],
                                        clients_list_difference[client_mac][5]['band_2'],
                                        clients_list_difference[client_mac][7]['rssi_1'],
                                        clients_list_difference[client_mac][7]['rssi_2'],
                                        bytes_sec,
                                        stream_vid,
                                        stream_mc,
                                        bytes_diff,
                                        time_diff)

        if bytes_sec >= configuration.streaming_threshold:
            streaming_clients_dic.update({client_mac: bytes_sec})
            # client_list_streaming = client_list_streaming + \
            #                         'Streaming client: \t{0}, \t{1}, \t{2}, \t' \
            #                         'Throughput bytes/sec: {3}\n'.format(
            #                             client_mac, clients_list_difference[client_mac][0],
            #                             clients_list_difference[client_mac][1], bytes_sec)

    return client_list_no_change, client_list_disconnected, client_list_change_ap, \
           client_list_change_band, client_list_change_lohi5g, client_list_new_added, \
           streaming_clients_dic


# This ping function is to monitor if client host is connected to mesh network.
# It's good to use for Windows OS, not for Linux or Mac OS.
# Note: cannot handle the case when ip address is None.
def ping(host):

    if host is None:
        return [None, 1, None]

    else:
        # Ping for 5 times.
        result = subprocess.run(['ping', '-n', '5', host], stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')

        # # For testing purpose, output to console.
        # print('{} output: {}'.format(str(host), str(output)))
        #
        # # For testing purpose, output to console.
        # if result.returncode == 0:
        #     print('{} responded'.format(host))
        # else:
        #     print('{} did not respond'.format(host))

        match = re.search(r'Approximate round trip times in milli-seconds:\r\n.+Average = (\d+)ms', output)

        # match.group(1) is average round trip time in milli-seconds for ping.
        if match:
            return [host, 0, match.group(1)]
        else:
            return [host, 1, None]


# Ping the range of client hosts.
def ping_range(hosts):

    # Based on CPU, the number of thread to be generated for ping.
    num_threads = multiprocessing.cpu_count()
    # print('num_threads = ' + str(num_threads))

    # Thread pool.
    p = multiprocessing.dummy.Pool(num_threads)

    # Get return value of ping in list.
    results = p.map(ping, [host for host in hosts])
    # print(results)

    return results


# To find out 5GHz channel type: DFS (0), non-DFS (1), or invalid 5GHz channel (2)
# input channel is integer.
def channel_type_5g(channel):

    dfs_channels_5g = [52, 56, 60, 64, 100, 104, 108, 112, 116, 132, 136, 140, 144]
    nondfs_channels_5g = [36, 40, 44, 48, 149, 153, 157, 161, 165]

    if channel in dfs_channels_5g:
        return 0
    elif channel in nondfs_channels_5g:
        return 1
    else:
        return 2


# To filter out invalid channels in list, and return valid channel list.
def valid_channels(channel_list):
    valid_5g_channels = [36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 116,
                         132, 136, 140, 144, 149, 153, 157, 161, 165]
    valid_channel_list = []

    for channel in channel_list:
        try:
            channel_int = int(channel)
            if (channel_int in valid_5g_channels) or (1 <= channel_int <= 11):
                valid_channel_list.append(channel_int)
        except ValueError:
            if channel.lower() in ['dfs', 'radar']:
                valid_channel_list.append(channel.lower())

    return valid_channel_list


def str_fmt_aps_short(ap_name, ap_mac, ap_ip):
    fmt_string = '{0: <15}|{1:<18}|{2:<15}'.format(ap_name, ap_mac, ap_ip)
    return fmt_string


def format_ap_str_short(rg_ap_info, indent_count):
    ap_str = ' ' * indent_count + str_fmt_aps_short('ap_name', 'ap_5g_mac', 'ap_ip') + '\n' + \
             ' ' * indent_count + str_fmt_aps_short('-' * 15, '-' * 18, '-' * 15) + '\n'

    for key1, value1 in rg_ap_info.items():
        if value1[1]:
            ap_name = value1[1]
        else:
            ap_name = 'none'
        ap_str = ap_str + ' ' * indent_count + str_fmt_aps_short(ap_name, key1, value1[0]) + '\n'

    return ap_str


def str_fmt_triband_aps_details(ap_name, ap_mac, ap_ip, uptime, mem_usage, cpu_usage,
                                ap_fw, ch_24, cca_24, ch_hi_50, cca_hi_50, ch_lo_50, cca_lo_50, conn_err):
    fmt_string = '{0: <15}|{1:<18}|{2:<15}|{3:<16}|{4:<12}|{5:<10}|{6:<15}|{7:<5}|{8:<6}|{9:<9}|{10:<9}|{11:<9}|{12:<9}|{13:<8}'.format(
        ap_name, ap_mac, ap_ip, uptime, mem_usage, cpu_usage, ap_fw, ch_24, cca_24, ch_hi_50, cca_hi_50, ch_lo_50, cca_lo_50, conn_err)
    return fmt_string


def format_triband_ap_str_details(rg_ap_info, indent_count):
    ap_str = ' ' * indent_count + str_fmt_triband_aps_details('ap_name', 'ap_5g_mac', 'ap_ip', 'uptime',
                                                              'memory usage', 'cpu usage', 'AP fw', '24_ch',
                                                              '24_cca', '50_hi_ch', '50_hi_cca', '50_lo_ch',
                                                              '50_lo_cca', 'conn err') + '\n' + \
             ' ' * indent_count + str_fmt_triband_aps_details('-' * 15, '-' * 18, '-' * 15, '-' * 16, '-' * 12, '-' * 10,
                                                      '-' * 15, '-' * 5, '-' * 6, '-' * 9, '-' * 9, '-' * 9, '-' * 9, '-' * 8) + '\n'

    for key1, value1 in rg_ap_info.items():
        if value1['ap_name']:
            ap_name = value1['ap_name']
        else:
            ap_name = 'none'
        ap_str = ap_str + ' ' * indent_count + \
                 str_fmt_triband_aps_details(ap_name, value1['ap_mac'], value1['ap_ip'], value1['uptime'],
                                     value1['memory_usage'], value1['cpu_usage'], value1['fw'],
                                     value1['2.4_channel'], value1['2.4_ch_cca'], value1['5_hi_channel'],
                                     value1['5_hi_ch_cca'], value1['5_lo_channel'],
                                     value1['5_lo_ch_cca'], value1['conn_err']) + '\n'

    return ap_str


def str_fmt_clients(friendly_name, client_mac, client_ip, ap_mac, hilo5g, band, rssi, ping_succ,
                    ping_rtt, tx_bytes, time_stamp):
    fmt_string = '{0: <26}|{1: <18}|{2: <15}|{3: <18}|{4: <6}|{5: <4}|{6: <5}|{7: <9}|{8: <7}|{9: <15}|' \
                 '{10: <10}\n'.format(friendly_name, client_mac, client_ip, ap_mac, hilo5g, band, rssi, ping_succ,
                                     ping_rtt, tx_bytes, time_stamp)
    return fmt_string


def str_fmt_compare(client_state_0, friendly_name_1, client_mac_2, client_ip_3, previous_ap_mac_4,
                    current_ap_mac_5, previous_5g_6, current_5g_7, previous_band_8, current_band_9,
                    previous_rssi_10, current_rssi_11, tx_bytes_sec_12, stream_vid_13, stream_mc_14,
                    bytes_diff_15, time_diff_16):
    fmt_string = '{0: <20}|{1: <26}|{2: <18}|{3: <15}|{4: <18}|{5: <18}|{6: <6}|{7: <6}|' \
                 '{8: <8}|{9: <8}|{10: <8}|{11: <8}|{12: <9}|{13: <10}|{14: <9}|{15: <15}|' \
                 '{16: <10}\n'.format(client_state_0, friendly_name_1, client_mac_2, client_ip_3,
                                      previous_ap_mac_4, current_ap_mac_5, previous_5g_6, current_5g_7,
                                      previous_band_8, current_band_9, previous_rssi_10, current_rssi_11,
                                      tx_bytes_sec_12, stream_vid_13, stream_mc_14, bytes_diff_15,
                                      time_diff_16)

    return fmt_string


# Function to calculate memory and cpu usage for BGW210 and BGW320
def cal_mem_cpu_usage(sess_op_cpu_mem, ap_model):
    patt_memory = r'.*m: (\d*)K used, (\d*)K free.*'

    if ap_model == 'BGW210-700':
        patt_cpu = r'CPU:.*nice\s+(\d*)% idle.*'
    elif ap_model == 'BGW320-505':
        patt_cpu = r'.*CPU:.*nic (.*)% idle.*'
    elif ap_model == '4920' or ap_model == '4921':
        patt_cpu = r'.*CPU:.*nic (.*)% idle.*'
    else:
        patt_cpu = r'.*CPU:.*nic (.*)% idle.*'

    patterns_chip = [patt_memory, patt_cpu]

    search_results = [re.search(patt, sess_op_cpu_mem) for patt in patterns_chip]
    memory = search_results[0].groups() if search_results[0] else ('', '')
    cpu_idle = search_results[1].group(1) if search_results[1] else ''

    memory_usage = str(int(int(memory[0]) / (int(memory[0]) + int(memory[1])) * 100)) + '%' \
        if memory[0] != '' and memory[1] != '' else 'NA'
    cpu_usage = str(int((1 - float(cpu_idle) / 100) * 100)) + '%' if cpu_idle != '' else 'NA'

    return memory_usage, cpu_usage


# Test compare_sta_list function, as well as print_client_list_difference function
if __name__ == "__main__":
    rg_instance = rg_cmd.RGCmd()

    station_list_1 = {
        'cc:9e:a2:84:55:ad': ['192.168.1.96', 'amazon_fire_tv', 'a8:11:fc:9b:99:d3', '5', '-535', '8029396', 1560272382],
        '1c:f2:9a:67:5a:1f': ['192.168.1.139', 'google_home_hub', 'a8:11:fc:9b:99:d3', '5', '-607', '668394156', 1560272382],
        '40:98:ad:5f:96:78': ['192.168.1.108', 'iPhone 8', 'a8:11:fc:9b:99:d3', '5', '-651', '505201668', 1560272382],
        '40:98:ad:37:e5:e1': ['192.168.1.168', 'iPhone X', 'a8:11:fc:9b:99:d3', '5', '-634', '587087', 1560272382],
        'a4:f1:e8:a7:7e:7f': ['192.168.1.85', 'ipad_pro', 'a8:11:fc:9b:99:d3', '5', '-501', '3341346', 1560272382],
        '34:ab:37:87:a0:3f': ['192.168.1.251', 'iPad-Air2', 'a8:11:fc:9b:99:d3', '5', '-476', '406836295', 1560272382],
        'b8:d7:af:20:8a:02': ['192.168.1.169', 'galaxy_s8', 'a8:11:fc:9b:99:d3', '5', '-616', '2082045', 1560272382],
        'a4:b8:05:d7:4c:2f': ['192.168.1.72', 'FranksiPhone123', 'a8:11:fc:9b:99:d3', '5', '-587', '947088', 1560272382],
        'f8:6f:c1:01:a1:cb': ['192.168.1.70', 'HaofanspleWatch', 'a8:11:fc:9b:99:d3', '2', '-600', '23958138', 1560272382],
        '54:27:1e:fa:dd:18': ['192.168.1.90', 'Windows PC HP-8', '88:41:fc:e6:f6:5d', '5', '-343', '2629405', 1560272385],
        'd4:7a:e2:40:e4:36': ['192.168.1.189', 'osprey_box_1', '88:41:fc:e6:f6:5d', '5', '-280', '2304089820', 1560272385],
        '44:00:49:56:0a:76': ['192.168.1.91', 'amazon_smart_plug', '88:41:fc:e6:f6:5d', '2', '-725', '3909756', 1560272385],
        'b8:27:eb:a9:89:6d': ['192.168.1.97', 'RP-6', '88:41:fc:e6:f6:5d', '2', '-327', '4795953', 1560272385],
        'b8:27:eb:43:a4:99': ['192.168.1.69', 'RP-1', '88:41:fc:86:53:fb', '2', '-674', '115203', 1560272387],
        '24:4c:e3:60:38:b8': ['192.168.1.95', 'amazon_echo_plus', '88:41:fc:86:53:fb', '2', '-654', '6945113', 1560272387],
        '94:9f:3e:d6:e2:63': ['192.168.1.138', 'sonos_beam', '88:41:fc:86:53:fb', '2', '-554', '47887035', 1560272387],
        '44:00:49:92:d6:20': ['192.168.1.161', 'amazon_echo_dot_3', '88:41:fc:86:53:fb', '2', '-688', '6829078', 1560272387],
        '24:4c:e3:f8:49:80': ['192.168.1.133', 'amazon_echo_dot_1', '88:41:fc:86:53:fb', '2', '-620', '8603670', 1560272387],
        '30:fd:38:8f:c5:ab': ['192.168.1.140', 'google_home_mini', 'f4:17:b8:26:2c:ab', '5', '-330', '4601338', 1560272390],
        '44:07:0b:9f:18:b5': ['192.168.1.141', 'google_chromecast', 'f4:17:b8:26:2c:ab', '2', '-248', '19785158', 1560272390],
        'd0:73:d5:3c:b8:95': ['192.168.1.92', 'lifx_light', 'f4:17:b8:26:2c:ab', '2', '-384', '3608094', 1560272390],
        '0c:80:63:18:07:ec': ['192.168.1.93', 'tp_link_kasa_smart_light', 'f4:17:b8:26:2c:ab', '2', '-348', '4278077', 1560272390],
        'b8:27:eb:90:2e:3f': ['192.168.1.151', 'RP-2', 'f4:17:b8:26:2c:ab', '2', '-238', '4382904', 1560272390]
    }

    # Missing 2 clients, compared with list_1:
    # 'd4:7a:e2:40:e4:36' 'osprey_box_1', '54:27:1e:fa:dd:18' 'Windows PC HP-8'
    # Add new client, compared with list_1:
    # '0c:80:63:18:07:ec' 'tp_link_kasa_smart_light' connected to different AP
    # '30:fd:38:8f:c5:ab' 'google_home_mini' changed band from 5 to 2
    station_list_2 = {
        'cc:9e:a2:84:55:ad': ['192.168.1.96', 'amazon_fire_tv', 'a8:11:fc:9b:99:d3', '5', '-560', '8230127', 1560272812],
        '1c:f2:9a:67:5a:1f': ['192.168.1.139', 'google_home_hub', 'a8:11:fc:9b:99:d3', '5', '-573', '724624444', 1560272812],
        '40:98:ad:5f:96:78': ['192.168.1.108', 'iPhone 8', 'a8:11:fc:9b:99:d3', '5', '-619', '23446', 1560272812],
        '40:98:ad:37:e5:e1': ['192.168.1.168', 'iPhone X', 'a8:11:fc:9b:99:d3', '5', '-629', '1604', 1560272812],
        '34:ab:37:87:a0:3f': ['192.168.1.251', 'iPad-Air2', 'a8:11:fc:9b:99:d3', '5', '-464', '407091718', 1560272812],
        'b8:d7:af:20:8a:02': ['192.168.1.169', 'galaxy_s8', 'a8:11:fc:9b:99:d3', '5', '-603', '2288713', 1560272812],
        'a4:b8:05:d7:4c:2f': ['192.168.1.72', 'FranksiPhone123', 'a8:11:fc:9b:99:d3', '5', '-590', '1149067', 1560272812],
        '24:4c:e3:f9:0c:71': ['192.168.1.135', 'amazon_echo_dot_2', 'a8:11:fc:9b:99:d3', '2', '-510', '26843972', 1560272812],
        'f8:6f:c1:01:a1:cb': ['192.168.1.70', 'HaofanspleWatch', 'a8:11:fc:9b:99:d3', '2', '-600', '26724766', 1560272812],
        '54:27:1e:fa:dd:18': ['192.168.1.90', 'Windows PC HP-8', '88:41:fc:e6:f6:5d', '5', '-343', '3147473', 1560272815],
        'd4:7a:e2:40:e4:36': ['192.168.1.189', 'osprey_box_1', '88:41:fc:e6:f6:5d', '5', '-287', '2607563975', 1560272815],
        '44:00:49:56:0a:76': ['192.168.1.91', 'amazon_smart_plug', '88:41:fc:e6:f6:5d', '2', '-725', '4429498', 1560272815],
        'b8:27:eb:a9:89:6d': ['192.168.1.97', 'RP-6', '88:41:fc:e6:f6:5d', '2', '-337', '5314287', 1560272815],
        'b8:27:eb:43:a4:99': ['192.168.1.69', 'RP-1', '88:41:fc:86:53:fb', '2', '-644', '615139', 1560272817],
        '24:4c:e3:60:38:b8': ['192.168.1.95', 'amazon_echo_plus', '88:41:fc:86:53:fb', '2', '-660', '7853440', 1560272817],
        '94:9f:3e:d6:e2:63': ['192.168.1.138', 'sonos_beam', '88:41:fc:86:53:fb', '2', '-554', '53964588', 1560272817],
        '44:00:49:92:d6:20': ['192.168.1.161', 'amazon_echo_dot_3', '88:41:fc:86:53:fb', '2', '-620', '7677186', 1560272817],
        '24:4c:e3:f8:49:80': ['192.168.1.133', 'amazon_echo_dot_1', '88:41:fc:86:53:fb', '2', '-660', '9647679', 1560272817],
        '30:fd:38:8f:c5:ab': ['192.168.1.140', 'google_home_mini', 'f4:17:b8:26:2c:ab', '5', '-336', '5168974', 1560272819],
        '44:07:0b:9f:18:b5': ['192.168.1.141', 'google_chromecast', 'f4:17:b8:26:2c:ab', '2', '-248', '22324632', 1560272819],
        'd0:73:d5:3c:b8:95': ['192.168.1.92', 'lifx_light', 'f4:17:b8:26:2c:ab', '2', '-384', '4129809', 1560272819],
        '0c:80:63:18:07:ec': ['192.168.1.93', 'tp_link_kasa_smart_light', 'f4:17:b8:26:2c:ab', '2', '-348', '4798650', 1560272819],
        'b8:27:eb:90:2e:3f': ['192.168.1.151', 'RP-2', 'f4:17:b8:26:2c:ab', '2', '-238', '4902483', 1560272819]
    }

    compare_list = compare_client_list(station_list_1, station_list_2)
    # print(compare_list)
    # print('\n\n')

    clients_no_change_log, clients_disconnected_log, clients_ap_change_log, \
    clients_band_change_log, client_list_lohi5g_change, clients_new_added_log, \
    clients_streaming_log = print_client_list_difference(compare_list)

    time_stamp = datetime.datetime.now().strftime('%Y-%m-%d %A  %H:%M:%S.%f')
    log = clients_no_change_log + clients_disconnected_log + clients_ap_change_log + \
          clients_band_change_log + client_list_lohi5g_change + clients_new_added_log

    header = print_client_list_difference_header()

    before_msg = time_stamp + '\n' + header
    rg_instance.write_log_file('', log, before_msg, '')