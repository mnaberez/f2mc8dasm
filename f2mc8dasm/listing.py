

def print_listing(instructions_by_address, subroutine_addresses, rom, disassemble_func):
    print('    .F2MC8L')
    print('    .area CODE1 (ABS)')
    print('    .org 0xe000\n')

    last_line_code = True
    pc = 0xe000
    while pc < 0x10000:
        inst = instructions_by_address.get(pc)
        if inst is None:
            if last_line_code:
                print('')
            last_line_code = False

            _, inst = disassemble_func(rom, pc) # disassemble data as code

            print('    ' +
                    ('.byte 0x%02X' % rom[pc]).ljust(24) +
                    (';DATA  0x%04x  %02x %r ' % (pc, rom[pc], chr(rom[pc]))).ljust(26) +
                    ('(%s)' % (inst)))
            pc += 1  # XXX this is wrong for disassembly pc
        else:
            if not last_line_code:
                print('')
            last_line_code = True

            if pc in subroutine_addresses:
                print("\nsub_%04x:" % pc)

            disasm = str(inst)
            hexdump = (' '.join([ '%02x' % h for h in inst.all_bytes ])).ljust(8)

            line = '    ' + disasm.ljust(24) + ';0x%04x  %s' % (pc, hexdump)
            print(line)
            pc += len(inst.all_bytes)
