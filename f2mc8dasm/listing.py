
class Printer(object):
    def __init__(self, instructions_by_address, jump_addresses, subroutine_addresses, rom):
        self.instructions_by_address = instructions_by_address
        self.jump_addresses = jump_addresses
        self.subroutine_addresses = subroutine_addresses
        self.rom = rom

    def print_listing(self):
        self.print_header()
        last_line_code = True
        pc = 0xe000
        while pc < 0x10000:
            inst = self.instructions_by_address.get(pc)
            if inst is None:
                if last_line_code:
                    print('')
                self.print_data_line(pc)
                pc += 1
                last_line_code = False
            else:
                if not last_line_code:
                    print('')
                self.print_code_line(pc, inst)
                pc += len(inst.all_bytes)
                last_line_code = True

    def print_header(self):
        print('    .F2MC8L')
        print('    .area CODE1 (ABS)')
        print('    .org 0xe000\n')

    def print_data_line(self, pc):
        line = ('    .byte 0x%02X' % self.rom[pc]).ljust(28)
        line += ';%04x  %02x          DATA %r ' % (pc, self.rom[pc], chr(self.rom[pc]))
        print(line)

    def print_code_line(self, pc, inst):
        if (pc in self.jump_addresses) or (pc in self.subroutine_addresses):
            print("\n%s:" % self.format_address(pc))

        disasm = self.format_instruction(inst)
        hexdump = (' '.join([ '%02x' % h for h in inst.all_bytes ])).ljust(8)

        if inst.disasm_as_bytes:
            line = ('    .byte ' + ', '.join([ '0x%02x' % h for h in inst.all_bytes ])).ljust(28)
            line += (';%04x  %s' % (pc, hexdump)).ljust(19)
            line += disasm
        else:
            line = '    ' + disasm.ljust(24) + ';%04x  %s' % (pc, hexdump)
        print(line)

    def format_instruction(self, inst):
        d = {}
        d['OPC'] = '0x%02x' % inst.opcode

        if inst.immediate is not None:
            d['IMB'] = '0x%02x' % inst.immediate
        if inst.immediate is not None:
            d['IMW'] = '0x%04x' % inst.immediate
        if inst.address is not None:
            d['EXT'] = self.format_address(inst.address)
        if inst.ixd_offset is not None:
            d['IXD'] = '0x%02x' % inst.ixd_offset
        if inst.address is not None:
            d['REL'] = self.format_address(inst.address)
        if inst.callv is not None:
            d['VEC'] = '%d' % inst.callv
        if inst.bit is not None:
            d['BIT'] = '%d' % inst.bit
        if inst.register is not None:
            d['REG'] = '%d' % inst.register
        if inst.bittest_address is not None:
            d['DIR'] = '0x%02x' % inst.bittest_address
        elif inst.address is not None:
            d['DIR'] = '0x%02x' % inst.address

        disasm = inst.disasm_template
        for k, v in d.items():
            disasm = disasm.replace(k, v)
        return disasm

    def format_address(self, address):
        if address in self.jump_addresses:
            return 'lab_%04x' % address
        elif address in self.subroutine_addresses:
            return 'sub_%04x' % address
        else:
            return '0x%04x' % address
