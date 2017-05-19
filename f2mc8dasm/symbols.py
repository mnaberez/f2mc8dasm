MB89620R_SYMBOLS = {
    0x00: 'pdr0',   # port 0 data register
    0x01: 'ddr0',   # port 0 data direction register
    0x02: 'pdr1',   # port 1 data register
    0x03: 'ddr1',   # port 1 data direction register
    0x04: 'pdr2',   # port 2 data register
    0x05: 'bctr',   # external bus pin control register
    # 0x06-0x07 vacant
    0x08: 'stbc',   # standby control register
    0x09: 'wdtc',   # watchdog timer control register
    0x0a: 'tbtc',   # timebase timer control register
    # 0x0b vacant
    0x0c: 'pdr3',   # port 3 data register
    0x0d: 'ddr3',   # port 3 data direction register
    0x0e: 'pdr4',   # port 4 data register
    0x0f: 'bzcr',   # buzzer register
    0x10: 'pdr5',   # port 5 data register
    0x11: 'pdr6',   # port 6 data register
    0x12: 'cntr',   # pwm control register
    0x13: 'comr',   # pwm compare register
    0x14: 'pcr1',   # pwc pulse width control register 1
    0x15: 'pcr2',   # pwc pulse width control register 2
    0x16: 'rlbr',   # pwc reload buffer register
    # 0x17 vacant
    0x18: 'tmcr',   # 16-bit timer control register
    0x19: 'tchr',   # 16-bit timer count register (high)
    0x1a: 'tclr',   # 16-bit timer count register (low)
    # 0x1b vacant
    0x1c: 'smr1',   # serial i/o 1 mode register
    0x1d: 'sdr1',   # serial i/o 1 data register
    0x1e: 'smr2',   # serial i/o 2 mode register
    0x1f: 'sdr2',   # serial i/o 2 data register
    0x20: 'adc1',   # a/d converter control register 1
    0x21: 'adc2',   # a/d converter control register 2
    0x22: 'adcd',   # a/d converter data register
    # 0x23 vacant
    0x24: 'eic1',   # external interrupt 1 control register 1
    0x25: 'eic2',   # external interrupt 1 control register 2
    # 0x26-0x7b
    0x7c: 'ilr1',   # interrupt level setting register 1
    0x7d: 'ilr2',   # interrupt level setting register 2
    0x7e: 'ilr3',   # interrupt level setting register 3
    # 0x7f vacant
}

MB89670_SYMBOLS = {
    0x00: 'pdr0',   # port 0 data register
    0x01: 'ddr0',   # port 0 data direction register
    0x02: 'pdr1',   # port 1 data register
    0x03: 'ddr1',   # port 1 data direction register
    0x04: 'pdr2',   # port 2 data register
    0x05: 'bctr',   # external bus pin control register
    # 0x06-0x07 vacant
    0x07: 'sycc',   # system clock control register
    0x08: 'stbc',   # standby control register
    0x09: 'wdtc',   # watchdog timer control register
    0x0a: 'tbtc',   # timebase timer control register
    # 0x0b vacant
    0x0c: 'pdr3',   # port 3 data register
    0x0d: 'ddr3',   # port 3 data direction register
    0x0e: 'pdr4',   # port 4 data register
    0x0f: 'ddr4',   # port 4 data direction register
    0x10: 'pdr5',   # port 5 data register
    0x11: 'pdr6',   # port 6 data register
    0x12: 'ppcr',   # port 6 pull-up control register
    0x13: 'pdr7',   # port 7 data register
    0x14: 'pdr8',   # port 8 data / port 7 change register
    0x15: 'buzr',   # buzzer control register
    0x16: 'cntr',   # pwm control register #3
    0x17: 'comp',   # pwm compare register #3
    0x18: 'tmcr',   # 16-bit timer control register
    0x19: 'tchr',   # 16-bit timer count register high
    0x1a: 'tclr',   # 16-bit timer count register low
    # 0x1b vacant
    0x1c: 'smr',    # serial mode register
    0x1d: 'sdr',    # serial data register
    0x20: 'adc1',   # adc control register 1
    0x21: 'adc2',   # adc control register 2
    0x22: 'adch',   # adc data register high
    0x23: 'adcl',   # adc data register low
    0x24: 't2cr',   # timer 2 control register
    0x25: 't1cr',   # timer 1 control register
    0x26: 't2dr',   # timer 2 data register
    0x27: 't1dr',   # timer 1 data register
    0x28: 'cntr1',  # pwm-timer control register 1
    0x29: 'cntr2',  # pwm-timer control register 2
    0x2a: 'cntr3',  # pwm-timer control register 3
    0x2b: 'comr2',  # pwm-timer compare register 2
    0x2c: 'comr1',  # pwm-timer compare register 1
    # 0x2d-0x2f vacant
    0x30: 'udcr1',  # read: updown counter register 1, write: reload compare register 1
    0x31: 'udcr2',  # read: updown counter register 1, write: reload compare register 2
    0x32: 'ccra1',  # counter control register a1
    0x33: 'ccra2',  # counter control register a2
    0x34: 'ccrb1',  # counter control register b1
    0x35: 'ccrb2',  # counter contorl register b2
    0x36: 'csr1',   # counter status register 1
    0x37: 'csr2',   # counter status register 2
    0x38: 'eic1',   # external-interrupt 1 control register 1
    0x39: 'eic2',   # external-interrupt 1 control register 2
    0x3a: 'csr1',   # counter status register 1
    0x3b: 'csr2',   # counter status register 2
    0x3c: 'eic1',   # external-interrupt 1 control register 1
    0x3d: 'eic2',   # external-interrupt 1 control register 2
    0x3e: 'eie2',   # external-interrupt 2 control register
    0x3f: 'eif2',   # external-interrupt 2 flag register
    0x40: 'usmr',   # uart mode register
    0x41: 'uscr',   # uart control register
    0x42: 'ustr',   # uart status register
    0x43: 'rxdr',   # read: uart receive data register, write: uart transmit data register
    0x45: 'rrdr',   # baud-rate generate reload data register
    # 0x46-0x47 vacant
    0x48: 'cntr4',  # pwm-control register 4
    0x49: 'comp4',  # pwm-compare register 4
    0x4a: 'cntr5',  # pwm-control register 5
    0x4b: 'comp5',  # pwm-compare register 5
    0x4c: 'cntr6',  # pwm-control register 6
    0x4d: 'comp6',  # pwm-compare register 6
    # 0x4e-0x7b vacant
    0x7c: 'ilr1',   # interrupt-level setting register 1
    0x7d: 'ilr2',   # interrupt-level setting register 2
    0x7e: 'ilr3',   # interrupt-level setting register 3
    # 0x7f vacant
}
