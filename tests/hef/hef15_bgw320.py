import hef

def run():
    hef_code = 15
    test = hef.HEF()

    test._ap_addr = test.dut.bgw320['ap_addr']
    test._location = 'he15'
    test._build = test.dut.bgw320['build']
    test._iterations = 1

    test.run()

run()