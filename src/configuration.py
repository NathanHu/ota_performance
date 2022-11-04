# Customize test run settings
#test_exe = '"C:/Users/LCL-Spectrum-03/Desktop/Python Scripts/OTA Test/IxChariotPythonInterface/Debug/IxChariotPythonInterface.exe"'
#test_exe = '"C:/Users/LCL-Spectrum-03/Desktop/ota_automation/packages/IxChariotPythonInterface/Debug/IxChariotPythonInterface.exe"'
test_exe = '"C:/Users/LCL-Spectrum-03/Desktop/ota_automation/packages/IxChariotPythonInterface/Debug/single_client.exe"'
test_results = 'C:/Users/LCL-Spectrum-03/Desktop/OTA Results/Test Runs/'
test_iterations = 1
test_duration = 60
test_streams = [10]     # List of stream quantities to test. Ex. [1, 2, 3]

# Customize topology data to extract during testing
test_data = ['throughput',
             'rssi',
             'phy',
             'nss',
             'memory_usage',
             'cpu_usage',
             'channel',
             'cca',
             'latency'
             ]

# Customize OTA devices and test endpoints
#rg_4971 = '192.168.1.'
test_console = '192.168.1.50'
test_clients = {
    'S12'       : '192.168.1.30',
    'Note'      : '192.168.1.31',
    'iPhoneSE'  : '192.168.1.32',
    'IpadPro'   : '192.168.1.33',
    'Tab'       : '192.168.1.34',
    'S10'       : '192.168.1.35',
    'iPhone10'  : '192.168.1.36',
    'iPhone12'  : '192.168.1.37',
    'iPhone6S'  : '192.168.1.38',
    'MBP'       : '192.168.1.40'
}
ota_clients = {
    'a8:11:fc:9b:99:d3': 'BGW210',
    #'20:78:52:f5:b6:c7': 'BGW320',
    '20:78:52:f5:ac:77': 'BGW320',
    #'38:3b:c8:59:0c:a4': '5268ac',
    #'b8:ca:3a:ca:48:93': 'RDK',
    '60:03:08:9a:d4:70': 'MBP',
    'd4:11:a3:6d:72:bd': 'Tab',
    '1a:c7:c3:a2:35:e0': 'iPhone',
    'b8:e8:56:a5:3d:24': 'iPad',
    'da:55:a6:92:48:3f':'S12',
    '02:96:42:7b:db:14': 'Note',
    'b6:82:f2:f8:d8:ab':'iPhoneSE',
    'e2:23:8a:8b:2d:d1':'IpadPro',
    '82:5c:dc:55:da:13':'Tab',
    '10:98:c3:a0:c7:e9':'S10',
    '56:06:2e:c3:1a:55':'iPhone10',
    'a0:fb:c5:a8:49:ba':'iPhone12',
    '52:d7:cc:34:c9:d8':'iPhone6S',
    '3c:15:c2:c5:60:80':'MBP',
    'b8:ca:3a:ca:49:2b': 'test_console'
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



