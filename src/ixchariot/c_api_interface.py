import ctypes

# Load ChrApi.dll
dll = ctypes.WinDLL("C:\\Program Files (x86)\\Ixia\\IxChariot\\ChrApi.dll")
print(dll)
