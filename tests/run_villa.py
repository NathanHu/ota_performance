from context import run_ota

villa_exe = '"C:/Users/LCL-Spectrum-03/Desktop/ota_automation/packages/IxChariotPythonInterface/Debug/multiple_client.exe"'

test_data = {}

test = run_ota.RunOTA('192.168.1.251')
test._exe = villa_exe    # SET TEST PATH TO VILLA TEST EXECUTABLE
test._test_info['location'] = 'L0'
test._test_info['build'] = 'TESTBUILD'
test._test_iterations = 1

print(test._test_info['build'])
print(test._test_info['location'])

for i in range(10):
    test.run_villa()
#out = test.run_test()
#test.calc_avg()

print('RUN DATA: ',test._results)
print('AVERAGE DATA: ', test._results_avg)
test._log_instance.log_test(test._test_info, test._results_avg, test._client_data)