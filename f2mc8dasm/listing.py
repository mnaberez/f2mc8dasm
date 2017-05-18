import struct
from f2mc8dasm.tables import AddressModes

class Printer(object):
    def __init__(self, memory, start_address, symbols):
        self.memory = memory
        self.start_address = start_address
        self.symbols = symbols

    def print_listing(self):
        self.print_header()
        self.print_symbols()
        last_line_code = True
        address = self.start_address
        while address < len(self.memory):
            if self.memory.is_instruction_start(address):
                inst = self.memory.get_instruction(address)
                if not last_line_code:
                    print('')
                self.print_code_line(address, inst)
                address += len(inst.all_bytes)
                last_line_code = True
            else:
                if last_line_code:
                    print('')
                if self.memory.is_vector_start(address):
                    self.print_vector_line(address)
                    address += 2
                else:
                    self.print_data_line(address)
                    address += 1
                last_line_code = False

    def print_header(self):
        print('    .F2MC8L')
        print('    .area CODE1 (ABS)')
        print('    .org 0x%04x\n' % self.start_address)

    def print_symbols(self):
        used_symbols = set()
        for inst in self.memory.iter_instructions():
            if inst.address in self.symbols:
                used_symbols.add(inst.address)
            if inst.bittest_address in self.symbols:
                used_symbols.add(inst.bittest_address)

        for address in sorted(used_symbols):
            symbol = self.symbols[address]
            print("    %s = 0x%02x" % (symbol, address))

    def print_data_line(self, address):
        line = ('    .byte 0x%02X' % self.memory[address]).ljust(28)
        line += ';%04x  %02x          DATA %r ' % (address, self.memory[address], chr(self.memory[address]))
        print(line)

    def print_vector_line(self, address):
        target = struct.unpack('>H', self.memory[address:address+2])[0]
        target = self.format_ext_address(target)
        line = ('    .word %s' % target).ljust(28)
        line += ';%04x  %02x %02x       VECTOR' % (address, self.memory[address], self.memory[address+1])
        print(line)

    def print_code_line(self, address, inst):
        if self.memory.is_jump_target(address) or self.memory.is_call_target(address):
            print("\n%s:" % self.format_ext_address(address))

        disasm = self.format_instruction(inst)
        hexdump = (' '.join([ '%02x' % h for h in inst.all_bytes ])).ljust(8)

        # render instruction as a .byte sequence if asf2mc8 would optimize an
        # extended address into a direct one, breaking identical reassembly
        as_bytes = ((inst.addr_mode == AddressModes.Extended) and
                    ((inst.address & 0xFF00) == 0) and
                    (inst.opcode not in (0x21, 0x31)))

        if as_bytes:
            line = ('    .byte ' + ', '.join([ '0x%02x' % h for h in inst.all_bytes ])).ljust(28)
            line += (';%04x  %s' % (address, hexdump)).ljust(19)
            line += disasm
        else:
            line = '    ' + disasm.ljust(24) + ';%04x  %s' % (address, hexdump)
        print(line)

    def format_instruction(self, inst):
        d = {'OPC': '0x%02x' % inst.opcode}

        if inst.immediate is not None:
            d['IMB'] = '0x%02x' % inst.immediate
            d['IMW'] = '0x%04x' % inst.immediate
        if inst.address is not None:
            d['EXT'] = self.format_ext_address(inst.address)
            d['REL'] = self.format_ext_address(inst.address)
            d['DIR'] = self.format_dir_address(inst.address)
        if inst.bittest_address is not None:
            d['DIR'] = self.format_ext_address(inst.bittest_address)
        if inst.ixd_offset is not None:
            d['IXD'] = '0x%02x' % inst.ixd_offset
        if inst.callv is not None:
            d['VEC'] = '%d' % inst.callv
        if inst.bit is not None:
            d['BIT'] = '%d' % inst.bit
        if inst.register is not None:
            d['REG'] = '%d' % inst.register

        disasm = inst.disasm_template
        for k, v in d.items():
            disasm = disasm.replace(k, v)
        return disasm

    def format_ext_address(self, address):
        if address in self.symbols:
            return self.symbols[address]
        if address >= self.start_address: # XXX should be put in symbols instead
            if self.memory.is_jump_target(address):
                return 'lab_%04x' % address
            if self.memory.is_call_target(address):
                return 'sub_%04x' % address
        return '0x%04x' % address

    def format_dir_address(self, address):
        if address in self.symbols:
            return self.symbols[address]
        return '0x%02x' % address
