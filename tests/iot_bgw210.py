from context import run_ota

test = run_ota.RunOTA('192.168.1.252')
test._test_info['location'] = '161'
test._test_info['build'] = 'BGW210-PI19-3.19.3-MR3'
test._test_iterations = 1

print(test._test_info['build'])
print(test._test_info['location'])

out = test.run_test()
test.calc_avg()

test.console_output()

test._log_instance.log_test(test._test_info, test._results_avg, test._client_data)