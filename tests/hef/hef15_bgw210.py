from context import run_ota

test = run_ota.RunOTA('192.168.1.246')
test._test_info['location'] = 'Faraday-5-he3'
test._test_info['build'] = 'BGW210-PI14-MR2'
test._test_iterations = 1

print(test._test_info['build'])
print(test._test_info['location'])

out = test.run_test()
test.calc_avg()

print('RUN DATA: ',test._results)
print('AVERAGE DATA: ', test._results_avg)

test._log_instance.log_test(test._test_info, test._results_avg, test._client_data)