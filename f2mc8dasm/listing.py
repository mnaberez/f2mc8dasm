
class Printer(object):
    def __init__(self, instructions_by_address, subroutine_addresses, rom, disassemble_func):
        self.instructions_by_address = instructions_by_address
        self.subroutine_addresses = subroutine_addresses
        self.rom = rom
        self.disassemble_func = disassemble_func

    def print_listing(self):
        self.print_header()
        last_line_code = True
        pc = 0xe000
        while pc < 0x10000:
            inst = self.instructions_by_address.get(pc)
            if inst is None:
                if last_line_code:
                    print('')
                pc = self.print_data_line(pc)
                last_line_code = False
            else:
                if not last_line_code:
                    print('')
                pc = self.print_code_line(pc, inst)
                last_line_code = True

    def print_header(self):
        print('    .F2MC8L')
        print('    .area CODE1 (ABS)')
        print('    .org 0xe000\n')

    def print_code_line(self, pc, inst):
        if pc in self.subroutine_addresses:
            print("\nsub_%04x:" % pc)

        disasm = str(inst)
        hexdump = (' '.join([ '%02x' % h for h in inst.all_bytes ])).ljust(8)

        if inst.disasm_as_bytes:
            print('')
            print(("    ;" + disasm).ljust(29) + ('0x%04x  %s' % (pc, hexdump) ))
            line = '.byte ' + ', '.join([ '0x%02x' % h for h in inst.all_bytes ])
            print("    " + line)
            print('')
        else:
            line = '    ' + disasm.ljust(24) + ';0x%04x  %s' % (pc, hexdump)
            print(line)
        pc += len(inst.all_bytes)
        return pc

    def print_data_line(self, pc):
        _, inst = self.disassemble_func(self.rom, pc) # disassemble data as code

        print('    ' +
                ('.byte 0x%02X' % self.rom[pc]).ljust(24) +
                (';DATA  0x%04x  %02x %r ' % (pc, self.rom[pc], chr(self.rom[pc]))).ljust(26) +
                ('(%s)' % (inst)))
        pc += 1  # XXX this is wrong for disassembly pc
        return pc
