import sys

from f2mc8dasm.trace import Tracer
from f2mc8dasm.listing import Printer
from f2mc8dasm.disasm import disassemble_inst


def main():
    start_address = 0xe000

    with open(sys.argv[1], 'rb') as f:
        rom = bytearray(start_address) + bytearray(f.read())

    entry_points = [
        # reset
        0xe012,
        # callv, irq vectors
        0xE0CB, 0xE0DD, 0xE0EF, 0xE163, 0xE175, 0xE187, 0xE012, 0xE199,
        # jmp @
        # TODO these are tables of vectors, not code
        #0xE63F, 0xE726, 0xE791, 0xE961, 0xEA21, 0xEA9F, 0xEBA8, 0xEC42, 0xEC80
        ]
    traceable_range = range(start_address, len(rom))

    tracer = Tracer(rom, entry_points, traceable_range)

    instructions_by_address, jump_addresses, subroutine_addresses = tracer.trace(disassemble_inst)

    printer = Printer(instructions_by_address, jump_addresses, subroutine_addresses, rom, start_address)
    printer.print_listing()


if __name__ == '__main__':
    main()
