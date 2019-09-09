import unittest

import numpy as np
import time
import som_functions

class TestADRV9009ZU11EG(unittest.TestCase):

    measurements = 10
    buf_len = 2 ** 14
    uri1 = "ip:192.168.1.60"
    uri2 = "ip:192.168.1.61"

    prints = True

    def test_mean_over_time(self):

        LO = 1000000000
        sync = True
        phase_diff_s1, phase_diff_s2, phase_diff_s12 = som_functions.run_hardware_tests(LO,sync,self.measurements,self.buf_len,self.uri1,self.uri2)
        var1_s1 = np.var(phase_diff_s1)
        m1_s1 = np.mean(phase_diff_s1)
        var1_s2 = np.var(phase_diff_s2)
        m1_s2 = np.mean(phase_diff_s2)
        var1_s12 = np.var(phase_diff_s12)
        m1_s12 = np.mean(phase_diff_s12)

        time.sleep(1)

        sync = False
        phase_diff2_s1, phase_diff2_s2, phase_diff2_s12 = som_functions.run_hardware_tests(LO,sync,self.measurements,self.buf_len,self.uri1,self.uri2)
        var2_s1 = np.var(phase_diff2_s1)
        m2_s1 = np.mean(phase_diff2_s1)
        var2_s2 = np.var(phase_diff2_s2)
        m2_s2 = np.mean(phase_diff2_s2)
        var2_s12 = np.var(phase_diff2_s12)
        m2_s12 = np.mean(phase_diff2_s12)


        if self.prints:
            print("SOM1")
            print("Run 1 Variance %f (Degress^2)" % (var1_s1))
            print("Run 2 Variance %f (Degress^2)" % (var2_s1))
            print("Run 1 Mean Offset %f (Degress)" % (m1_s1))
            print("Run 2 Mean Offset %f (Degress)" % (m2_s1))
            print("Mean Diff %f (Degress)" % (m2_s1-m1_s1))

            print("SOM2")
            print("Run 1 Variance %f (Degress^2)" % (var1_s2))
            print("Run 2 Variance %f (Degress^2)" % (var2_s2))
            print("Run 1 Mean Offset %f (Degress)" % (m1_s2))
            print("Run 2 Mean Offset %f (Degress)" % (m2_s2))
            print("Mean Diff %f (Degress)" % (m2_s2-m1_s2))

            print("SOM12")
            print("Run 1 Variance %f (Degress^2)" % (var1_s12))
            print("Run 2 Variance %f (Degress^2)" % (var2_s12))
            print("Run 1 Mean Offset %f (Degress)" % (m1_s12))
            print("Run 2 Mean Offset %f (Degress)" % (m2_s12))
            print("Mean Diff %f (Degress)" % (m2_s12-m1_s12))

        #self.assertAlmostEqual(m1, m2, places=1)
        self.assertLess(np.abs(m2_s1-m1_s1),0.2)

        #self.assertLess(var1, 0.1)
        #self.assertLess(var2, 0.1)

    def test_lo_change(self):

        LO = 1000000000
        sync = True
        # phase_diff1 = som_functions.run_hardware_tests(LO,sync,self.measurements,self.uri1,self.uri2)
        #
        # var1 = np.var(phase_diff1)
        # m1 = np.mean(phase_diff1)
        phase_diff_s1, phase_diff_s2, phase_diff_s12 = som_functions.run_hardware_tests(LO,sync,self.measurements,self.buf_len,self.uri1,self.uri2)
        var1_s1 = np.var(phase_diff_s1)
        m1_s1 = np.mean(phase_diff_s1)
        var1_s2 = np.var(phase_diff_s2)
        m1_s2 = np.mean(phase_diff_s2)
        var1_s12 = np.var(phase_diff_s12)
        m1_s12 = np.mean(phase_diff_s12)

        LO = 2000000000
        sync = False
        som_functions.run_hardware_tests(LO,sync,self.measurements,self.buf_len,self.uri1,self.uri2)

        LO = 1000000000
        # phase_diff2 = som_functions.run_hardware_tests(LO,sync,self.measurements,self.uri1,self.uri2)
        # phase_diff2 = som_functions.run_hardware_tests(LO,sync,self.measurements,self.uri1,self.uri2)
        # var2 = np.var(phase_diff2)
        # m2 = np.mean(phase_diff2)
        phase_diff2_s1, phase_diff2_s2, phase_diff2_s12 = som_functions.run_hardware_tests(LO,sync,self.measurements,self.buf_len,self.uri1,self.uri2)
        var2_s1 = np.var(phase_diff2_s1)
        m2_s1 = np.mean(phase_diff2_s1)
        var2_s2 = np.var(phase_diff2_s2)
        m2_s2 = np.mean(phase_diff2_s2)
        var2_s12 = np.var(phase_diff2_s12)
        m2_s12 = np.mean(phase_diff2_s12)

        if self.prints:
            print("SOM1")
            print("Run 1 Variance %f (Degress^2)" % (var1_s1))
            print("Run 2 Variance %f (Degress^2)" % (var2_s1))
            print("Run 1 Mean Offset %f (Degress)" % (m1_s1))
            print("Run 2 Mean Offset %f (Degress)" % (m2_s1))
            print("Mean Diff %f (Degress)" % (m2_s1 - m1_s1))

            print("SOM2")
            print("Run 1 Variance %f (Degress^2)" % (var1_s2))
            print("Run 2 Variance %f (Degress^2)" % (var2_s2))
            print("Run 1 Mean Offset %f (Degress)" % (m1_s2))
            print("Run 2 Mean Offset %f (Degress)" % (m2_s2))
            print("Mean Diff %f (Degress)" % (m2_s2 - m1_s2))

            print("SOM12")
            print("Run 1 Variance %f (Degress^2)" % (var1_s12))
            print("Run 2 Variance %f (Degress^2)" % (var2_s12))
            print("Run 1 Mean Offset %f (Degress)" % (m1_s12))
            print("Run 2 Mean Offset %f (Degress)" % (m2_s12))
            print("Mean Diff %f (Degress)" % (m2_s12 - m1_s12))
        #self.assertAlmostEqual(m1, m2, places=1)
        self.assertLess(np.abs(m2_s1-m1_s1), 0.2)

        #self.assertLess(var1, 0.1)
        #self.assertLess(var2, 0.1)

if __name__ == '__main__':
    unittest.main()
