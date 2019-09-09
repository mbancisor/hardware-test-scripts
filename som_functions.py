#!/usr/bin/env python
#
# Copyright (C) 2019 Analog Devices, Inc.
# Author: Travis Collins <travis.collins@analog.com>
#
# Licensed under the GPL-2.

import sys
try:
    import iio
except:
    # By default the iio python bindings are not in path
    sys.path.append('/usr/lib/python2.7/site-packages/')
    import iio

import numpy as np
try:
    import matplotlib.pyplot as plt
    do_plots = True
except:
    print("To view plots install matplotlib")
    do_plots = False

def measure_phase(chan0,chan1):
    errorV = np.angle(chan0 * np.conj(chan1))*180/np.pi
    error = np.mean(errorV)
    return error
def setup_hardware():
    return 1

def run_hardware_tests(TRXLO,sync,runs,buf_len, uri1,uri2):

    # User configurable
    DDS_Freq = 4000000

    # Setup contexts
    try:
        ctx1 = iio.Context(uri1)
    except:
        raise Exception("No device1 found")
    try:
        ctx2 = iio.Context(uri2)
    except:
        raise Exception("No device1 found")

    ctrl_chip1A = ctx1.find_device("adrv9009-phy")
    ctrl_chip1B = ctx1.find_device("adrv9009-phy-b")
    ctrl_chip2A = ctx2.find_device("adrv9009-phy")
    ctrl_chip2B = ctx2.find_device("adrv9009-phy-b")


    txdac1 = ctx1.find_device("axi-adrv9009-tx-hpc")
    rxadc1 = ctx1.find_device("axi-adrv9009-rx-hpc")
    txdac2 = ctx2.find_device("axi-adrv9009-tx-hpc")
    rxadc2 = ctx2.find_device("axi-adrv9009-rx-hpc")

    hmc7044_1 = ctx1.find_device("hmc7044")
    hmc7044_1_car = ctx1.find_device("hmc7044-car")
    hmc7044_2 = ctx2.find_device("hmc7044")
    hmc7044_2_car = ctx2.find_device("hmc7044-car")
    hmc7044_1_ext = ctx1.find_device("hmc7044-ext")

    # request sync pulse
    hmc7044_1_ext.attrs["sysref_request"].value = str(1)
    # Check Sync status
    # print(hmc7044_1._debug_attrs["status"].value)

    # Configure transceiver settings
    LO1 = ctrl_chip1A.find_channel("TRX_LO", True)
    LO1.attrs["frequency"].value = str(int(TRXLO))
    LO1 = ctrl_chip1B.find_channel("TRX_LO", True)
    LO1.attrs["frequency"].value = str(int(TRXLO))

    LO2 = ctrl_chip2A.find_channel("TRX_LO", True)
    LO2.attrs["frequency"].value = str(int(TRXLO))
    LO2 = ctrl_chip2B.find_channel("TRX_LO", True)
    LO2.attrs["frequency"].value = str(int(TRXLO))
    #
    rx1 = ctrl_chip1A.find_channel("voltage0")
    rx1.attrs['gain_control_mode'].value = 'slow_attack'
    rx1 = ctrl_chip1B.find_channel("voltage0")
    rx1.attrs['gain_control_mode'].value = 'slow_attack'

    rx2 = ctrl_chip2A.find_channel("voltage0")
    rx2.attrs['gain_control_mode'].value = 'slow_attack'
    rx2 = ctrl_chip2B.find_channel("voltage0")
    rx2.attrs['gain_control_mode'].value = 'slow_attack'


    if sync:
        # Calibrate
        ctrl_chip1A.attrs['calibrate_rx_phase_correction_en'] = True
        ctrl_chip1A.attrs['calibrate'] = True
        ctrl_chip1B.attrs['calibrate_rx_phase_correction_en'] = True
        ctrl_chip1B.attrs['calibrate'] = True

        ctrl_chip2A.attrs['calibrate_rx_phase_correction_en'] = True
        ctrl_chip2A.attrs['calibrate'] = True
        ctrl_chip2B.attrs['calibrate_rx_phase_correction_en'] = True
        ctrl_chip2B.attrs['calibrate'] = True

        # MCS
        #hmc7044_1.reg_write(0x5a,0)
        for k in range(12):
            ctrl_chip1A.attrs['multichip_sync'] = str(k)
            ctrl_chip1B.attrs['multichip_sync'] = str(k)

        #hmc7044_2.reg_write(0x5a,0)
        for k in range(12):
            ctrl_chip2A.attrs['multichip_sync'] = str(k)
            ctrl_chip2B.attrs['multichip_sync'] = str(k)


    # Enable all IQ channels
    v0 = rxadc1.find_channel("voltage0_i")
    v1 = rxadc1.find_channel("voltage0_q")
    v2 = rxadc1.find_channel("voltage1_i")
    v3 = rxadc1.find_channel("voltage1_q")
    v0.enabled = True
    v1.enabled = True
    v2.enabled = True
    v3.enabled = True

    v4 = rxadc2.find_channel("voltage0_i")
    v5 = rxadc2.find_channel("voltage0_q")
    v6 = rxadc2.find_channel("voltage1_i")
    v7 = rxadc2.find_channel("voltage1_q")
    v4.enabled = True
    v5.enabled = True
    v6.enabled = True
    v7.enabled = True

    # Create buffer for RX data
    rxbuf1 = iio.Buffer(rxadc1, buf_len, False)
    rxbuf2 = iio.Buffer(rxadc2, buf_len, False)
    #
    # Enable single tone DDS
    dds0_tx1_1 = txdac1.find_channel('altvoltage0',True)
    dds2_tx1_1 = txdac1.find_channel('altvoltage2',True)
    dds0_tx1_2 = txdac1.find_channel('altvoltage8',True)
    dds2_tx1_2 = txdac1.find_channel('altvoltage10',True)

    dds0_tx2_1 = txdac2.find_channel('altvoltage0',True)
    dds2_tx2_1 = txdac2.find_channel('altvoltage2',True)
    dds0_tx2_2 = txdac2.find_channel('altvoltage8',True)
    dds2_tx2_2 = txdac2.find_channel('altvoltage10',True)

    # Turn all others off
    dds1_1 = txdac1.find_channel('altvoltage1',True)
    dds1_1.attrs['raw'].value = str(0)
    dds1_1.attrs['scale'].value = str(0)
    for r in range(3,16):
        dds1_1 = txdac1.find_channel('altvoltage'+str(r),True)
        dds1_1.attrs['scale'].value = str(0)
        dds1_1.attrs['raw'].value = str(0)

    dds2_1 = txdac2.find_channel('altvoltage1', True)
    dds2_1.attrs['raw'].value = str(0)
    dds2_1.attrs['scale'].value = str(0)
    for r in range(3, 16):
        dds2_1 = txdac2.find_channel('altvoltage' + str(r), True)
        dds2_1.attrs['scale'].value = str(0)
        dds2_1.attrs['raw'].value = str(0)

    # Set frequency of enabled DDSs
    dds0_tx1_1.attrs['raw'].value = str(1)
    dds0_tx1_1.attrs['frequency'].value = str(DDS_Freq)
    dds0_tx1_1.attrs['scale'].value = str(0.5)
    dds0_tx1_1.attrs['phase'].value = str(90000)
    dds2_tx1_1.attrs['raw'].value = str(1)
    dds2_tx1_1.attrs['frequency'].value = str(DDS_Freq)
    dds2_tx1_1.attrs['scale'].value = str(0.5)
    dds2_tx1_1.attrs['phase'].value = str(0)

    dds0_tx2_1.attrs['raw'].value = str(1)
    dds0_tx2_1.attrs['frequency'].value = str(DDS_Freq)
    dds0_tx2_1.attrs['scale'].value = str(0.5)
    dds0_tx2_1.attrs['phase'].value = str(90000)
    dds2_tx2_1.attrs['raw'].value = str(1)
    dds2_tx2_1.attrs['frequency'].value = str(DDS_Freq)
    dds2_tx2_1.attrs['scale'].value = str(0.5)
    dds2_tx2_1.attrs['phase'].value = str(0)

    dds0_tx1_2.attrs['raw'].value = str(1)
    dds0_tx1_2.attrs['frequency'].value = str(DDS_Freq)
    dds0_tx1_2.attrs['scale'].value = str(0.5)
    dds0_tx1_2.attrs['phase'].value = str(90000)
    dds2_tx1_2.attrs['raw'].value = str(1)
    dds2_tx1_2.attrs['frequency'].value = str(DDS_Freq)
    dds2_tx1_2.attrs['scale'].value = str(0.5)
    dds2_tx1_2.attrs['phase'].value = str(0)

    dds0_tx2_2.attrs['raw'].value = str(1)
    dds0_tx2_2.attrs['frequency'].value = str(DDS_Freq)
    dds0_tx2_2.attrs['scale'].value = str(0.5)
    dds0_tx2_2.attrs['phase'].value = str(90000)
    dds2_tx2_2.attrs['raw'].value = str(1)
    dds2_tx2_2.attrs['frequency'].value = str(DDS_Freq)
    dds2_tx2_2.attrs['scale'].value = str(0.5)
    dds2_tx2_2.attrs['phase'].value = str(0)

    # Stop continuous sysref 1
    hmc7044_1_ext.reg_write(0x5, 0x2)
    hmc7044_1_car.reg_write(0x5, 0x42)
    hmc7044_1_car.reg_write(0x49, 0x0)
    hmc7044_1_car.reg_write(0x5a, 0x1)
    hmc7044_1.reg_write(0x49, 0x0)
    hmc7044_1.reg_write(0x5a, 0x1)
    hmc7044_1.reg_write(0x5, 0x43)
    hmc7044_1.reg_write(0x5, 0x83)

    # Stop continuous sysref 2
    # hmc7044_2_ext.reg_write(0x5, 0x2)
    hmc7044_2_car.reg_write(0x5, 0x42)
    hmc7044_2_car.reg_write(0x49, 0x0)
    hmc7044_2_car.reg_write(0x5a, 0x1)
    hmc7044_2.reg_write(0x49, 0x0)
    hmc7044_2.reg_write(0x5a, 0x1)
    hmc7044_2.reg_write(0x5, 0x43)
    hmc7044_2.reg_write(0x5, 0x83)

    # Collect data
    # reals0 = np.array([])
    # imags0 = np.array([])
    # reals1 = np.array([])
    # imags1 = np.array([])
    phase_error1 = np.array([])
    phase_error2 = np.array([])
    phase_error12 = np.array([])

    i = 0
    while rxadc1.reg_read(0x80000068) == 0:
        rxadc1.reg_write(0x80000044, 0x8)
        if (i == 50):
            print("no HDL 1 sync")
            break
        i += 1
    print("HDL 1 sync reg", rxadc1.reg_read(0x80000068))
    print("tried ",i)

    i = 0
    while rxadc2.reg_read(0x80000068) == 0:
        rxadc2.reg_write(0x80000044, 0x8)
        if (i == 50):
            print("no HDL 2 sync")
            break
        i += 1
    print("HDL 2 sync reg", rxadc2.reg_read(0x80000068))
    print("tried ",i)



    for i in range(runs):


      rxbuf1.refill()
      rxbuf2.refill()

      hmc7044_1_ext.attrs["sysref_request"].value = str(1)

      data1 = rxbuf1.read()
      data2 = rxbuf2.read()

      x1 = np.frombuffer(data1,dtype=np.int16)
      x2 = np.frombuffer(data2, dtype=np.int16)
      # reals0 = np.append(reals0,x[::4])
      # imags0 = np.append(imags0,x[1::4])
      # reals1 = np.append(reals1,x[2::4])
      # imags1 = np.append(imags1,x[3::4])
      chan1 = x1[2::4] + 1j*x1[3::4]
      chan0 = x1[0::4] + 1j*x1[1::4]
      chan3 = x2[2::4] + 1j*x2[3::4]
      chan2 = x2[0::4] + 1j*x2[1::4]
      phase_error1 = np.append(phase_error1, measure_phase(chan0, chan1))
      phase_error2 = np.append(phase_error2, measure_phase(chan2, chan3))
      phase_error12 = np.append(phase_error12, measure_phase(chan0, chan2))
    # # Plot
    # if do_plots:
    #     plt.plot(phase_error)
    #     # plt.plot(reals0)
    #     # # plt.plot(imags0)
    #     # plt.plot(reals1)
    #     # # plt.plot(imags1)
    #     plt.xlabel("Samples")
    #     plt.ylabel("Amplitude [dbFS]")
    #     plt.show()
    return phase_error1, phase_error2, phase_error12
