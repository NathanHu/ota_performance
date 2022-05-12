from context import run_ota
import
def run():
    test = run_ota.RunOTA('192.168.1.246')
    test._test_info['location'] = 'he3'
    test._test_info['build'] = 'BGW320-PI17-MR2'
    test._test_iterations = 1

    print(test._test_info['build'])
    print(test._test_info['location'])

    out = test.run_test()
    test.calc_avg()

    print('RUN DATA: ',test._results)
    print('AVERAGE DATA: ', test._results_avg)

    test._log_instance.log_test(test._test_info, test._results_avg, test._client_data)


if __name__ == '__main__':
    run()