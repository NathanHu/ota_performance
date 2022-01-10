from context import run_ota
#import argparse

test = run_ota.RunOTA('192.168.1.251')

"""
parser = argparse.ArgumentParser()
parser.add_argument('-loc', action="store", dest="loc", help='client location')
parser.add_argument('-build', action="store", dest="build", help='firmware build')
args = parser.parse_args()
try:
    test._test_info['build'] = args.build
    test._test_info['location'] = args.loc
except:
    test._test_info['location'] = 'NONE'
    test._test_info['build'] = 'NONE'
"""

test._test_info['location'] = 'NONE'
test._test_info['build'] = 'NONE'

print(test._test_info['build'])
print(test._test_info['location'])

out = test.run_test()
test.calc_avg()

print('RUN DATA: ',test._results)
print('AVERAGE DATA: ', test._results_avg)

test._log_instance.log_test(test._test_info, test._results_avg, test._client_data)