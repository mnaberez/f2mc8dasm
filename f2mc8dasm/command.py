import sys

from f2mc8dasm.trace import Tracer
from f2mc8dasm.listing import Printer
from f2mc8dasm.disasm import disassemble_inst
from f2mc8dasm.symbols import MB89620R_SYMBOLS

def main():
    start_address = 0xe000

    with open(sys.argv[1], 'rb') as f:
        rom = bytearray(start_address) + bytearray(f.read())

    entry_points = [
        # reset
        0xe012,
        # irq vectors
        0xE0CB, 0xE0DD, 0xE0EF, 0xE163, 0xE175, 0xE187, 0xE199,
        ]
    traceable_range = range(start_address, len(rom))

    tracer = Tracer(rom, entry_points, traceable_range)

    instructions_by_address, jump_addresses, subroutine_addresses, vector_addresses = tracer.trace(disassemble_inst)

    printer = Printer(instructions_by_address,
                      jump_addresses,
                      subroutine_addresses,
                      vector_addresses,
                      rom,
                      start_address,
                      MB89620R_SYMBOLS
                      )
    printer.print_listing()


if __name__ == '__main__':
    main()
