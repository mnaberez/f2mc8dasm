import sys

from f2mc8dasm.disasm import disassemble_inst
from f2mc8dasm.trace import Tracer
from f2mc8dasm.memory import Memory
from f2mc8dasm.listing import Printer
from f2mc8dasm.symbols import MB89620R_SYMBOLS, SymbolTable

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
    def jump_table(start_address, length):
        address = start_address
        for i in range(length):
            vectors.append(address)
            address += 2
    jump_table (0x81a8, 6)
    jump_table (0xf139, 4)
    jump_table (0xd7e1, 16)
    jump_table (0xde79, 9)
    jump_table (0xedd8, 4)
    jump_table (0xee39, 7)
    jump_table (0xee77, 6)
    jump_table (0xf254, 4)
    jump_table (0xd501, 16)
    jump_table (0xd528, 16)
    jump_table (0x8f44, 14)
    jump_table (0x958a, 51)
    jump_table (0x9a51, 33)
    jump_table (0x9ee0, 11)
    jump_table (0xa4a0, 11)
    jump_table (0xac03, 17)
    jump_table (0xae73, 8)
    jump_table (0xb318, 17)
    jump_table (0xb467, 7)
    jump_table (0xb5a4, 7)
    jump_table (0xbe62, 8)
    jump_table (0xbe62, 6)
    jump_table (0xc354, 11)
    jump_table (0xc4c9, 10)
    jump_table (0xc9ec, 6)
    jump_table (0xca39, 6)
    jump_table (0xcb16, 6)
    jump_table (0xe223, 7)
    jump_table (0xe3bd, 14)
    jump_table (0xee20, 3)
    jump_table (0xee5b, 6)
    jump_table (0xf4b7, 6)
    jump_table (0xfe00, 66)

    traceable_range = range(start_address, start_address + len(rom) + 1)
    tracer = Tracer(memory, entry_points, vectors, traceable_range)
    tracer.trace(disassemble_inst)

    symbol_table = SymbolTable(MB89620R_SYMBOLS)
    symbol_table.generate(memory, start_address) # xxx should pass traceable_range

    printer = Printer(memory,
                      start_address,
                      symbol_table.symbols, # xxx should pass symbol_table
                      )
    printer.print_listing()


if __name__ == '__main__':
    main()
