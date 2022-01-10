
streaming_threshold = 50000  # streaming threshold for detecting possible client streaming

# Customize IOT devices friendly name.
iot_devices = {
    'a8:11:fc:9b:99:d3': 'BGW210',
    'b8:ca:3a:ca:48:93': 'RDK',
    '60:03:08:9a:d4:70': 'MBP',
    '10:98:c3:a0:c7:e9': 'S10',
    'd4:11:a3:6d:72:bd': 'Tab',
    'b8:e8:56:a5:3d:24': 'iPad',
    '4c:66:41:93:2d:49': 'galaxy_s7',
    'a4:f1:e8:a7:7e:7f': 'ipad_pro',
    'f4:0f:24:21:67:25': 'macbook_pro_2016',
    'b8:d7:af:20:8a:02': 'galaxy_s8',
    '1e:2f:9a:67:5a:1f': 'google_home_hub BGW210',
    '1c:f2:9a:51:05:5d': 'google_home_hub BGW320',
    '30:fd:38:8f:c5:ab': 'google_home_mini',
    '44:07:0b:9f:18:b5': 'google_chromecast_old',
    '7c:d9:5c:21:f2:ae': 'google_chromecast_new',
    '0c:80:63:18:07:ec': 'tp_link_kasa_smart_light',
    'd0:73:d5:3c:b8:95': 'lifx_light',
    'd0:73:d5:54:88:ec': 'lifx_light',
    'b0:f8:93:69:69:ef': 'Seng_LED_Smart_Light_A',
    'b0:f8:93:66:d5:65': 'Seng_LED_Smart_Light_B',
    'f0:81:73:93:b7:f8': 'amazon_echo_spot',
    '4c:17:44:5c:92:1e': 'Amazon echo show',
    '24:4c:e3:60:38:b8': 'amazon_echo_plus_BGW210',
    '1c:12:b0:18:be:df': 'amazon_echo_plus_BGW320',
    '24:4c:e3:f8:49:80': 'amazon_echo_dot_2nd_gen_1',
    '24:4c:e3:f9:0c:71': 'amazon_echo_dot_2nd_gen_2',
    '44:00:49:92:d6:20': 'amazon_echo_dot_2nd_gen_3',
    '74:d6:37:75:5a:42': 'amazon_echo_dot_3rd_gen_A',
    '4c:17:44:65:83:d3': 'amazon_echo_dot_3rd_gen_B',
    '68:db:f5:88:8a:cb': 'amazon_echo_dot_3rd_gen_C',
    '44:00:49:56:0a:76': 'amazon_smart_plug',
    'cc:9e:a2:84:55:ad': 'amazon_fire_tv 4K',
    '08:84:9d:82:8c:81': 'amazon_fire_tv HD 1080',
    '34:7e:5c:14:da:16': 'sonos_speaker_1',
    '34:7e:5c:14:d7:da': 'sonos_speaker_2',
    '94:9f:3e:d6:e2:63': 'sonos_beam',
    'd4:7a:e2:40:e4:36': 'osprey_box_1',
    'd4:7a:e2:40:a7:31': 'osprey_box_2',
    '28:ff:3c:ad:99:9c': 'Apple_TV',
    '64:16:66:ca:3b:ca': 'Nest Smoke Alam 1',
    '64:16:66:ca:4e:5a': 'Nest Smoke Alam 2',
    '3c:e1:a1:ad:20:af': 'RingElite Web Camera',
    '3c:15:c2:c5:60:80': 'Hectors-MBP',
    'a4:b8:05:d7:4c:2f': 'FranksiPhone123',
    '54:27:1e:fa:dd:18': 'Windows PC HP-8',
    'b8:27:eb:a9:89:6d': 'RP-6',
    'b8:27:eb:43:a4:99': 'RP-1',
    'b8:27:eb:90:2e:3f': 'RP-2',
    '34:ab:37:87:a0:3f': 'iPad-Air2',
    '00:ee:bd:ad:27:58': 'HTC M8',
    '14:5a:05:68:d6:15': 'iPhone-2.4',
    'f8:6f:c1:01:a1:cb': 'HaofanspleWatch',
    '40:98:ad:5f:96:78': 'iPhone 8',
    '40:98:ad:37:e5:e1': 'iPhone X',
    '24:4c:e3:b7:a1:40': 'Kindle Fire Tab 7 8G',
    '1c:12:b0:fb:f0:9b': 'Kindle Fire Tab 7 16G',
    'd4:11:a3:5c:9a:89': 'Samsung Galaxy Tab S4-1',
    '6c:00:6b:99:5f:5d': 'Samsung Galaxy Tab S4-2',
    'd4:11:a3:6d:79:89': 'Samsung Galaxy Tab S4-3',
    'd4:11:a3:6d:72:bd': 'Samsung Galaxy Tab S4',
    '10:98:c3:a0:c7:e9': 'Samsung Galaxy S10e Test2',
    'e8:e8:b7:45:8a:4a': 'Samsung Galaxy S10e Test4',
    'e8:e8:b7:55:60:6a': 'Samsung Galaxy S10e Test5'
}

# To match 4920 to different RG type connection, regarding 5GHz radio hi/lo.
match_rg_4920 = {
    'BGW210-700': '4920-BGW210',
    'BGW320-505': '4920-BGW320',
}

match_rg_4971 = {
    'BGW210-700': '4971-BGW210',
    'BGW320-505': '4971-BGW320',
}

# To match 5GHz radio hi/lo based on different RG and 4920 type.
map_5g_low_high = {
    'BGW210-700': {'wifi1': '--', 'wl0': '--'},
    'BGW320-505': {'wl0': 'lo', 'wl1': 'hi', 'wl2': '--'},
    'BGW320-500': {'wl0': '--', 'wl1': 'hi', 'wl2': 'lo'},
    '4920-BGW210': {'wl0': '--', 'wl1': '--'},
    '4920-BGW320': {'wl0': '--', 'wl1': 'hi'},
    '4971-BGW320': {'wl0': '--', 'wl1': 'lo', 'wl2': 'hi'},
    '4971-BGW210': {'wl0': '--', 'wl1': 'lo', 'wl2': 'hi'}
}

# Customize APs friendly name
mesh_aps = {
    'a8:11:fc:9b:99:d3': 'BGW210',
    '88:41:fc:e6:f6:5d': 'AC2121814000033',
    'f4:17:b8:26:2c:ab': 'AC2591851000675',
    '88:41:fc:86:53:fb': 'AT2121618000942',
    '88:41:fc:86:4f:e3': 'AT2121618000680',
    'f4:17:b8:b5:30:d9': '4971-1',
    'f4:17:b8:b5:32:05': '4971-2',
    'f4:17:b8:b5:32:37': '4971-3'
}


ping_hosts = [
    '192.168.1.190',  # Osprey box 2
    '192.168.1.141',  # Google Chromecast
    '192.168.1.96',   # Amazon FireTV
    '192.168.1.140'   # Google Home Mini
]

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

# # BGW210 login variables
# bgw210_host_ip = '192.168.1.254'
# bgw210_user = 'admin'
# bgw210_pw = 'austin123'
#
#
# # QTN login variables
# qtn_user = 'root'
# qtn_host_ip = '203.0.113.2'
#
#
# # BGW210 CLI commands
# bgw210_cli_show_wireless_clients = 'show wireless client'
# bgw210_cli_show_cpu = 'show cpu'
# bgw210_tr69_associated_devices = 'tr69 get InternetGatewayDevice.LANDevice.1.WLANConfiguration.1.AssociatedDevice.'
#
#
# # QTN CLI commands
# qtn_cmd_get_channel = 'call_qcsapi get_channel wifi0'
#
#
# # Output files
# bgw210_cli_output_file = 'RG_CLI_Log.txt'
# qtn_output_file = 'QTN_CLI_Log.txt'

