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

    entry_points = []
    vectors = [
        # callv
        0xffc0, 0xffc2, 0xffc4, 0xffc6, 0xffc8, 0xffca, 0xffcc, 0xffce,
        # irq
        0xffd0, 0xffd2, 0xffd4, 0xffd6, 0xffd8, 0xffda, 0xffdc, 0xffde,
        0xffe0, 0xffe2, 0xffe4, 0xffe6, 0xffe8, 0xffea, 0xffec, 0xffee,
        0xfff0, 0xfff2, 0xfff4, 0xfff6, 0xfff8, 0xfffa,
        # reset
        0xfffe
    ]

    traceable_range = range(start_address, start_address + len(rom) + 1)
    tracer = Tracer(memory, entry_points, vectors, traceable_range)
    tracer.trace(disassemble_inst)

    printer = Printer(memory,
                      start_address,
                      MB89620R_SYMBOLS
                      )
    printer.print_listing()


if __name__ == '__main__':
    main()
