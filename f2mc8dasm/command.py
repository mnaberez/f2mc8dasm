import sys

from f2mc8dasm.disasm import disassemble_inst
from f2mc8dasm.trace import Tracer
from f2mc8dasm.memory import Memory
from f2mc8dasm.listing import Printer
from f2mc8dasm.symbols import MB89620R_SYMBOLS

def main():
    with open(sys.argv[1], 'rb') as f:
        rom = bytearray(f.read())

    start_address = 0x10000 - len(rom)
    memory = Memory(rom)

    entry_points = [
        # reset
        0xe012,
        # irq vectors
        0xE0CB, 0xE0DD, 0xE0EF, 0xE163, 0xE175, 0xE187, 0xE199,
        ]
    traceable_range = range(start_address, start_address + len(rom) + 1)
    tracer = Tracer(memory, entry_points, traceable_range)
    tracer.trace(disassemble_inst)

    printer = Printer(memory,
                      start_address,
                      MB89620R_SYMBOLS
                      )
    printer.print_listing()


if __name__ == '__main__':
    main()
