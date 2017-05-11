import struct
from f2mc8dasm.memory import LocationTypes, LocationAnnotations
from f2mc8dasm.tables import AddressModes

class Printer(object):
    def __init__(self,
            memory,
            start_address,
            symbols
            ):
        self.memory = memory
        self.start_address = start_address
        self.symbols = symbols

    def print_listing(self):
        self.print_header()
        self.print_symbols()
        last_line_code = True
        pc = self.start_address
        while pc < 0x10000: # xxx
            if self.memory.get_type(pc) == LocationTypes.InstructionStart:
                inst = self.memory.get_instruction(pc)
                if not last_line_code:
                    print('')
                self.print_code_line(pc, inst)
                pc += len(inst.all_bytes)
                last_line_code = True
            else:
                if last_line_code:
                    print('')
                if self.memory.get_annotation(pc) == LocationAnnotations.Vector:
                    self.print_vector_line(pc)
                    pc += 2
                else:
                    self.print_data_line(pc)
                    pc += 1
                last_line_code = False

    def print_header(self):
        print('    .F2MC8L')
        print('    .area CODE1 (ABS)')
        print('    .org 0xe000\n')

    def print_symbols(self):
        used_symbols = set()
        for address in range(0, 0x10000):
            if self.memory.get_type(address) == LocationTypes.InstructionStart:
                inst = self.memory.get_instruction(address)

                if (inst.address in self.symbols):
                    used_symbols.add(inst.address)
                if (inst.bittest_address in self.symbols):
                    used_symbols.add(inst.bittest_address)

        for address in sorted(used_symbols):
            symbol = self.symbols[address]
            print("    %s = 0x%02x" % (symbol, address))

    def print_data_line(self, pc):
        line = ('    .byte 0x%02X' % self.memory[pc]).ljust(28)
        line += ';%04x  %02x          DATA %r ' % (pc, self.memory[pc], chr(self.memory[pc]))
        print(line)

    def print_vector_line(self, pc):
        target = struct.unpack('>H', self.memory[pc:pc+2])[0]
        target = self.format_ext_address(target)
        line = ('    .word %s' % target).ljust(28)
        line += ';%04x  %02x %02x       VECTOR' % (pc, self.memory[pc], self.memory[pc+1])
        print(line)

    def print_code_line(self, pc, inst):
        if self.memory.get_annotation(pc) in (LocationAnnotations.JumpTarget, LocationAnnotations.CallTarget):
            print("\n%s:" % self.format_ext_address(pc))

        disasm = self.format_instruction(inst)
        hexdump = (' '.join([ '%02x' % h for h in inst.all_bytes ])).ljust(8)

        if (inst.addr_mode == AddressModes.Extended) and ((inst.address & 0xFF00) == 0):
            # render instruction as .byte sequence to prevent asf2mc8 from optimizing
            # an extended address into a direct one, which breaks identical reassembly
            line = ('    .byte ' + ', '.join([ '0x%02x' % h for h in inst.all_bytes ])).ljust(28)
            line += (';%04x  %s' % (pc, hexdump)).ljust(19)
            line += disasm
        else:
            line = '    ' + disasm.ljust(24) + ';%04x  %s' % (pc, hexdump)
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
        if self.memory.get_annotation(address) == LocationAnnotations.JumpTarget:
            return 'lab_%04x' % address
        if self.memory.get_annotation(address) == LocationAnnotations.CallTarget:
            return 'sub_%04x' % address
        return '0x%04x' % address

    def format_dir_address(self, address):
        if address in self.symbols:
            return self.symbols[address]
        return '0x%02x' % address
