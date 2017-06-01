import sys

from f2mc8dasm.disasm import disassemble_inst
from f2mc8dasm.trace import Tracer
from f2mc8dasm.memory import Memory
from f2mc8dasm.listing import Printer
from f2mc8dasm.symbols import MB89670_SYMBOLS

def main():
    with open(sys.argv[1], 'rb') as f:
        rom = bytearray(f.read())
    start_address = 0x10000 - len(rom)

    memory = Memory(rom)
    memory.set_reserved_byte(0xfffc)
    memory.set_mode_byte(0xfffd)

    entry_points = []
    vectors = [
        # callv
        0xffc0, 0xffc2, 0xffc4, 0xffc6, 0xffc8, 0xffca, 0xffcc, 0xffce,
        # irq
        0xffd0, 0xffd2, 0xffd4, 0xffd6, 0xffd8, 0xffda, 0xffdc, 0xffde,
        0xffe0, 0xffe2, 0xffe4, 0xffe6, 0xffe8, 0xffea, 0xffec, 0xffee,
        0xfff0, 0xfff2, 0xfff4, 0xfff6, 0xfff8, 0xfffa,
        # reset
        0xfffe,
    ]

    # XXX put this in a more sensible place
    vectors += [
        # pu-1666a main mcu indirect jmp table at 0xefbb
        0xefbd,0xefc2,0xefc7,0xefcc,0xefd1,0xefd6,
    ]
    def jump_table(start_address, length):
        address = start_address
        for i in range(length):
            vectors.append(address)
            address += 2
    # pu-1666a main mcu jump tables
    jump_table(0x81a8, 6)
    jump_table(0xf139, 4)
    jump_table(0xd7e1, 16)
    jump_table(0xde79, 9)
    jump_table(0xedd8, 4)
    jump_table(0xee39, 7)
    jump_table(0xee77, 6)
    jump_table(0xf254, 9)
    jump_table(0xd501, 16)
    jump_table(0xd528, 16)
    jump_table(0x8f44, 14)
    jump_table(0x958a, 51)
    jump_table(0x9a51, 33)
    jump_table(0x9ee0, 11)
    jump_table(0xa4a0, 11)
    jump_table(0xac03, 17)
    jump_table(0xae73, 8)
    jump_table(0xb318, 17)
    jump_table(0xb467, 7)
    jump_table(0xb5a4, 7)
    jump_table(0xbe62, 8)
    jump_table(0xbe62, 6)
    jump_table(0xc354, 11)
    jump_table(0xc4c9, 10)
    jump_table(0xc9ec, 6)
    jump_table(0xca39, 6)
    jump_table(0xcb16, 6)
    jump_table(0xe223, 7)
    jump_table(0xe3bd, 14)
    jump_table(0xee20, 3)
    jump_table(0xee5b, 6)
    jump_table(0xf4b7, 6)
    jump_table(0xfe00, 66)
    # pu-1666a main mcu branch-always
    memory.set_data(0x869e) # beq at 0x869c always branches
    memory.set_data(0x86ac) # beq at 0x86aa always branches
    # pu-1666a main mcu known code locations
    entry_points += [0xf0f5, 0xf0e0]

    traceable_range = range(start_address, start_address + len(rom) + 1)
    tracer = Tracer(memory, entry_points, vectors, traceable_range)
    tracer.trace(disassemble_inst)

    # XXX move symbol generation to a more sensible place
    symbols = MB89670_SYMBOLS.copy()
    for address in range(start_address, len(memory)):
        if memory.is_call_target(address):
            if memory.is_instruction_start(address):
                symbols[address] = ('sub_%04x' % address, '')
        elif memory.is_jump_target(address):
            if memory.is_instruction_start(address):
                symbols[address] = ('lab_%04x' % address, '')

    printer = Printer(memory,
                      start_address,
                      symbols,
                      )
    printer.print_listing()


if __name__ == '__main__':
    main()
