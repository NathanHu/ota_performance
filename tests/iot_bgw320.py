from context import run_ota

test = run_ota.RunOTA('192.168.1.254')
test._test_info['location'] = '132'
test._test_info['build'] = 'BGW320-500-PI19-2.19.5'
#test._test_info['build'] = 'BGW320-PI18-2.18.5'
test._test_iterations = 1

print(test._test_info['build'])
print(test._test_info['location'])

out = test.run_test()
test.calc_avg()

#print('RUN DATA: ',test._results)
#print('AVERAGE DATA: ', test._results_avg)
test.console_output()

test._log_instance.log_test(test._test_info, test._results_avg, test._client_data)