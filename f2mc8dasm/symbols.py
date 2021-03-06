from f2mc8dasm.tables import AddressModes

class SymbolTable(object):
    def __init__(self, initial_symbols=None):
        if initial_symbols is None:
            initial_symbols = {}
        self.symbols = initial_symbols.copy()

    def generate(self, memory, start_address):
        self.generate_code_symbols(memory, start_address)
        self.generate_data_symbols(memory, start_address)

    def generate_code_symbols(self, memory, start_address):
        for address in range(start_address, len(memory)):
            if address in self.symbols:
                pass # do not overwrite existing symbols
            elif memory.is_call_target(address):
                if memory.is_instruction_start(address):
                    self.symbols[address] = ('sub_%04x' % address, '')
            elif memory.is_jump_target(address):
                if memory.is_instruction_start(address):
                    self.symbols[address] = ('lab_%04x' % address, '')

    def generate_data_symbols(self, memory, start_address):
        # symbols are always generated for direct or extended address r/w
        for address, inst in memory.iter_instructions():
            if inst.addr_mode not in (AddressModes.Extended,
                                      AddressModes.Direct,
                                      AddressModes.DirectWithImmediateByte,
                                      AddressModes.BitDirect):
                continue
            if inst.address in self.symbols:
                continue
            if memory.is_single_byte_or_start_of_multibyte(inst.address):
                self.symbols[inst.address] = ('mem_%04x' % inst.address, '')

        # bbc 0xaa:0, 0xe005
        # symbols are always generated for the tested address (0xaa)
        for address, inst in memory.iter_instructions():
            if inst.addr_mode != AddressModes.BitDirectWithRelative:
                continue
            if inst.bittest_address in self.symbols:
                continue
            if memory.is_single_byte_or_start_of_multibyte(inst.bittest_address):
                self.symbols[inst.bittest_address] = ('mem_%04x' % inst.bittest_address, '')

        # mov ep, #0x0123
        # mov ix, #0x0123
        # mov sp, #0x0123
        # symbols are always generated for immediate words loaded into pointers
        for address, inst in memory.iter_instructions():
            if not inst.stores_immediate_word_in_pointer:
                continue
            if inst.immediate in self.symbols:
                continue
            if memory.is_single_byte_or_start_of_multibyte(inst.immediate):
                self.symbols[inst.immediate] = ('mem_%04x' % inst.immediate, '')

        # mov a, #0xee9f
        # symbols are only generated for immediate word loads into A if the
        # address is in the rom range or else many false positives will result
        for address, inst in memory.iter_instructions():
            if not inst.stores_immediate_word_in_a:
                continue
            if inst.immediate in self.symbols:
                continue
            if inst.immediate < start_address:
                continue
            if memory.is_single_byte_or_start_of_multibyte(inst.immediate):
                self.symbols[inst.immediate] = ('mem_%04x' % inst.immediate, '')


F2MC8L_COMMON_SYMBOLS = {
    0xffc0: ('callv_0_vect', 'callv #0'),
    0xffc2: ('callv_1_vect', 'callv #1'),
    0xffc4: ('callv_2_vect', 'callv #2'),
    0xffc6: ('callv_3_vect', 'callv #3'),
    0xffc8: ('callv_4_vect', 'callv #4'),
    0xffca: ('callv_5_vect', 'callv #5'),
    0xffcc: ('callv_6_vect', 'callv #6'),
    0xffce: ('callv_7_vect', 'callv #7'),
    0xffd0: ('irq15_vect', 'irq15 (unused)'),
    0xffd2: ('irq14_vect', 'irq14 (unused)'),
    0xffd4: ('irq13_vect', 'irq13 (unused)'),
    0xffd6: ('irq12_vect', 'irq12 (unused)'),
    0xffd8: ('irq11_vect', 'irq11 (unused)'),
    0xffda: ('irq10_vect', 'irq10 (unused)'),
    0xffdc: ('irqf_vect',  'irqf (unused)'),
    0xffde: ('irqe_vect',  'irqe (unused)'),
    0xffe0: ('irqd_vect',  'irqd (unused)'),
    0xffe2: ('irqc_vect',  'irqc (unused)'),
    0xffe4: ('irqb_vect',  'irqb (unused)'),
    0xffe6: ('irqa_vect',  'irqa (unused)'),
    0xffe8: ('irq9_vect',  'irq9 (unused)'),
    0xffea: ('irq8_vect',  'irq8 (unused)'),
    0xffec: ('irq7_vect',  'irq7 (unused)'),
    0xffee: ('irq6_vect',  'irq6 (unused)'),
    0xfff0: ('irq5_vect',  'irq5 (unused)'),
    0xfff2: ('irq4_vect',  'irq4 (unused)'),
    0xfff4: ('irq3_vect',  'irq3 (unused)'),
    0xfff6: ('irq2_vect',  'irq2 (unused)'),
    0xfff8: ('irq1_vect',  'irq1 (unused)'),
    0xfffa: ('irq0_vect',  'irq0 (unused)'),
    0xfffc: ('reserved',   'reserved byte'),
    0xfffd: ('mode',       'mode byte'),
    0xfffe: ('reset_vect', 'reset'),
}

MB89620R_SYMBOLS = F2MC8L_COMMON_SYMBOLS.copy()
MB89620R_SYMBOLS.update({
    0x00: ('pdr0', 'port 0 data register'),
    0x01: ('ddr0', 'port 0 data direction register'),
    0x02: ('pdr1', 'port 1 data register'),
    0x03: ('ddr1', 'port 1 data direction register'),
    0x04: ('pdr2', 'port 2 data register'),
    0x05: ('bctr', 'external bus pin control register'),
    # 0x06-0x07 vacant
    0x08: ('stbc', 'standby control register'),
    0x09: ('wdtc', 'watchdog timer control register'),
    0x0a: ('tbtc', 'timebase timer control register'),
    # 0x0b vacant
    0x0c: ('pdr3', 'port 3 data register'),
    0x0d: ('ddr3', 'port 3 data direction register'),
    0x0e: ('pdr4', 'port 4 data register'),
    0x0f: ('bzcr', 'buzzer register'),
    0x10: ('pdr5', 'port 5 data register'),
    0x11: ('pdr6', 'port 6 data register'),
    0x12: ('cntr', 'pwm control register'),
    0x13: ('comr', 'pwm compare register'),
    0x14: ('pcr1', 'pwc pulse width control register 1'),
    0x15: ('pcr2', 'pwc pulse width control register 2'),
    0x16: ('rlbr', 'pwc reload buffer register'),
    # 0x17 vacant
    0x18: ('tmcr', '16-bit timer control register'),
    0x19: ('tchr', '16-bit timer count register (high)'),
    0x1a: ('tclr', '16-bit timer count register (low)'),
    # 0x1b vacant
    0x1c: ('smr1', 'serial i/o 1 mode register'),
    0x1d: ('sdr1', 'serial i/o 1 data register'),
    0x1e: ('smr2', 'serial i/o 2 mode register'),
    0x1f: ('sdr2', 'serial i/o 2 data register'),
    0x20: ('adc1', 'a/d converter control register 1'),
    0x21: ('adc2', 'a/d converter control register 2'),
    0x22: ('adcd', 'a/d converter data register'),
    # 0x23 vacant
    0x24: ('eic1', 'external interrupt 1 control register 1'),
    0x25: ('eic2', 'external interrupt 1 control register 2'),
    # 0x26-0x7b
    0x7c: ('ilr1', 'interrupt level setting register 1'),
    0x7d: ('ilr2', 'interrupt level setting register 2'),
    0x7e: ('ilr3', 'interrupt level setting register 3'),
    # 0x7f vacant
    0xffe4: ('irqb_vect', 'irqb (unused)'),
    0xffe6: ('irqa_vect', 'irqa (timebase timer)'),
    0xffe8: ('irq9_vect', 'irq9 (a/d converter)'),
    0xffea: ('irq8_vect', 'irq8 (8-bit serial I/O #2)'),
    0xffec: ('irq7_vect', 'irq7 (8-bit serial I/O #1)'),
    0xffee: ('irq6_vect', 'irq6 (16-bit timer/counter)'),
    0xfff0: ('irq5_vect', 'irq5 (pulse width count timer)'),
    0xfff2: ('irq4_vect', 'irq4 (8-bit pwm timer)'),
    0xfff4: ('irq3_vect', 'irq3 (external interrupt #3)'),
    0xfff6: ('irq2_vect', 'irq2 (external interrupt #2)'),
    0xfff8: ('irq1_vect', 'irq1 (external interrupt #1)'),
    0xfffa: ('irq0_vect', 'irq0 (external interrupt #0)'),
})

MB89670_SYMBOLS = F2MC8L_COMMON_SYMBOLS.copy()
MB89670_SYMBOLS.update({
    0x00: ('pdr0', 'port 0 data register'),
    0x01: ('ddr0', 'port 0 data direction register'),
    0x02: ('pdr1', 'port 1 data register'),
    0x03: ('ddr1', 'port 1 data direction register'),
    0x04: ('pdr2', 'port 2 data register'),
    0x05: ('bctr', 'external bus pin control register'),
    # 0x06 vacant
    0x07: ('sycc', 'system clock control register'),
    0x08: ('stbc', 'standby control register'),
    0x09: ('wdtc', 'watchdog timer control register'),
    0x0a: ('tbtc', 'timebase timer control register'),
    # 0x0b vacant
    0x0c: ('pdr3', 'port 3 data register'),
    0x0d: ('ddr3', 'port 3 data direction register'),
    0x0e: ('pdr4', 'port 4 data register'),
    0x0f: ('ddr4', 'port 4 data direction register'),
    0x10: ('pdr5', 'port 5 data register'),
    0x11: ('pdr6', 'port 6 data register'),
    0x12: ('ppcr', 'port 6 pull-up control register'),
    0x13: ('pdr7', 'port 7 data register'),
    0x14: ('pdr8', 'port 8 data / port 7 change register'),
    0x15: ('buzr', 'buzzer control register'),
    0x16: ('cntr', 'pwm control register #3'),
    0x17: ('comp', 'pwm compare register #3'),
    0x18: ('tmcr', '16-bit timer control register'),
    0x19: ('tchr', '16-bit timer count register high'),
    0x1a: ('tclr', '16-bit timer count register low'),
    # 0x1b vacant
    0x1c: ('smr',  'serial mode register'),
    0x1d: ('sdr',  'serial data register'),
    # 0x1e-0x-1f vacant
    0x20: ('adc1', 'adc control register 1'),
    0x21: ('adc2', 'adc control register 2'),
    0x22: ('adch', 'adc data register high'),
    0x23: ('adcl', 'adc data register low'),
    0x24: ('t2cr', 'timer 2 control register'),
    0x25: ('t1cr', 'timer 1 control register'),
    0x26: ('t2dr', 'timer 2 data register'),
    0x27: ('t1dr', 'timer 1 data register'),
    0x28: ('cntr1','pwm-timer control register 1'),
    0x29: ('cntr2','pwm-timer control register 2'),
    0x2a: ('cntr3','pwm-timer control register 3'),
    0x2b: ('comr2','pwm-timer compare register 2'),
    0x2c: ('comr1','pwm-timer compare register 1'),
    # 0x2d-0x2f vacant
    0x30: ('udcr1','read: updown counter register 1, write: reload compare register 1'),
    0x31: ('udcr2','read: updown counter register 1, write: reload compare register 2'),
    0x32: ('ccra1','counter control register a1'),
    0x33: ('ccra2','counter control register a2'),
    0x34: ('ccrb1','counter control register b1'),
    0x35: ('ccrb2','counter contorl register b2'),
    0x36: ('csr1', 'counter status register 1'),
    0x37: ('csr2', 'counter status register 2'),
    0x38: ('eic1', 'external-interrupt control register 1'),
    0x39: ('eic2', 'external-interrupt control register 2'),
    0x3a: ('eie2', 'external-interrupt control register 2'),
    0x3b: ('eif2', 'external-interrupt flag register 2'),
    # 0x3c-0x3f vacant
    0x40: ('usmr', 'uart mode register'),
    0x41: ('uscr', 'uart control register'),
    0x42: ('ustr', 'uart status register'),
    0x43: ('rxdr', 'read: uart receive data register, write: uart transmit data register'),
    # 0x44 vacant
    0x45: ('rrdr', 'baud-rate generate reload data register'),
    # 0x46-0x47 vacant
    0x48: ('cntr4','pwm-control register 4'),
    0x49: ('comp4','pwm-compare register 4'),
    0x4a: ('cntr5','pwm-control register 5'),
    0x4b: ('comp5','pwm-compare register 5'),
    0x4c: ('cntr6','pwm-control register 6'),
    0x4d: ('comp6','pwm-compare register 6'),
    # 0x4e-0x7b vacant
    0x7c: ('ilr1', 'interrupt-level setting register 1'),
    0x7d: ('ilr2', 'interrupt-level setting register 2'),
    0x7e: ('ilr3', 'interrupt-level setting register 3'),
    # 0x7f vacant
    0xffe4: ('irqb_vect', 'irqb (timebase timer)'),
    0xffe6: ('irqa_vect', 'irqa (a/d converter)'),
    0xffe8: ('irq9_vect', 'irq9 (8/16-bit updown counter)'),
    0xffea: ('irq8_vect', 'irq8 (uart)'),
    0xffec: ('irq7_vect', 'irq7 (8-bit serial i/o)'),
    0xffee: ('irq6_vect', 'irq6 (8-bit pwm timer #3 (#4, #5, #6))'),
    0xfff0: ('irq5_vect', 'irq5 (2ch 8-bit pwm timer)'),
    0xfff2: ('irq4_vect', 'irq4 (unused)'),
    0xfff4: ('irq3_vect', 'irq3 (8/16 bit timer #1, #2)'),
    0xfff6: ('irq2_vect', 'irq2 (16-bit timer counter)'),
    0xfff8: ('irq1_vect', 'irq1 (external interrupt 2)'),
    0xfffa: ('irq0_vect', 'irq0 (external interrupt 1)'),
})
