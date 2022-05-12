from context import run_ota, dut_info

class HEF():
    def __init__(self):
        self.dut = dut_info
        self._ap_addr = ''
        self._location = ''
        self._build = ''
        self._iterations = 1

    def run(self):
        test = run_ota.RunOTA(self._ap_addr)
        test._test_info['location'] = self._location
        test._test_info['build'] = self._build
        test._test_iterations = self._iterations

        print(test._test_info['build'])
        print(test._test_info['location'])

        out = test.run_test()
        test.calc_avg()

        test.console_output()

        test._log_instance.log_test(test._test_info, test._results_avg, test._client_data)

if __name__ == '__main__':
    test = HEF()
    test.run()