import sys

from f2mc8dasm.trace import TraceQueue, Tracer
from f2mc8dasm.listing import print_listing
from f2mc8dasm.disasm import disassemble_inst


def main():
    with open(sys.argv[1], 'rb') as f:
        rom = bytearray(0xe000) + bytearray(f.read())

    entry_points = [
        # reset
        0xE012,
        # callv, irq vectors
        0xE0CB, 0xE0DD, 0xE0EF, 0xE163, 0xE175, 0xE187, 0xE012, 0xE199,
        # jmp @
        # TODO these are tables of vectors, not code
        #0xE63F, 0xE726, 0xE791, 0xE961, 0xEA21, 0xEA9F, 0xEBA8, 0xEC42, 0xEC80
        ]
    traceable_range = range(0xe000, 0x10000)

    trace_queue = TraceQueue(entry_points, traceable_range)
    tracer = Tracer(rom, trace_queue)

    instructions_by_address, subroutine_addresses = tracer.trace(disassemble_inst)

    print_listing(instructions_by_address, subroutine_addresses, rom, disassemble_inst)


if __name__ == '__main__':
    main()