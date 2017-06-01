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
    def jump_table(start_address, length):
        address = start_address
        for i in range(length):
            vectors.append(address)
            address += 2

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
