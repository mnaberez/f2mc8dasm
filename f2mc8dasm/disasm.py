from f2mc8dasm.tables import (
    AddressModes,
    Opcodes,
    InstructionLengths,
    )


class Instruction(object):
    disasm_as_bytes = False  # instruction requires bytes-only disassembly
                             # output to reassamble identically on asf2mc8
    disasm_template = '' # "cmp @ix+IXD, #IMB"
    addr_mode = None     # addressing mode
    flow_type = None     # type of instruction for flow tracing
    opcode = None        # opcode byte
    operands = ()        # operand bytes
    address = None       # address (0-0xFF for direct, 0-0xFFFF for others)
    immediate = None     # immediate value (byte or word)
    ixd_offset = None    # IXD offset 0-0xFF
    bit = None           # bit 0-7
    callv = None         # callv 0-7
    register = None      # register r0-r7

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise KeyError(k)

    @property
    def all_bytes(self):
        return [self.opcode] + list(self.operands)

    def __str__(self):
        d = {}
        d['OPC'] = '0x%02x' % self.opcode
        if self.immediate is not None:
            d['IMB'] = '0x%02x' % self.immediate
        if self.immediate is not None:
            d['IMW'] = '0x%04x' % self.immediate
        if self.address is not None:
            d['DIR'] = '0x%02x' % self.address
        if self.address is not None:
            d['EXT'] = '0x%04x' % self.address
        if self.ixd_offset is not None:
            d['IXD'] = '0x%02x' % self.ixd_offset
        if self.address is not None:
            d['REL'] = '0x%04x' % self.address
        if self.callv is not None:
            d['VEC'] = '%d' % self.callv
        if self.bit is not None:
            d['BIT'] = '%d' % self.bit
        if self.register is not None:
            d['REG'] = '%d' % self.register
        disasm = self.disasm_template
        for k, v in d.items():
            disasm = disasm.replace(k, v)
        return disasm


def resolve_rel(pc, displacement):
    if displacement & 0x80:
        displacement = -((displacement ^ 0xff) + 1)
    return pc + displacement


def disassemble_inst(rom, pc):
    opcode = rom[pc]
    pc += 1
    disasm_template, addr_mode, flow_type = Opcodes[opcode]

    instlen = InstructionLengths[addr_mode]
    operands = bytearray()
    for i in range(instlen - 1):
        operands.append(rom[pc])
        pc +=1

    inst = Instruction()
    inst.opcode = opcode
    inst.operands = operands
    inst.disasm_template = disasm_template
    inst.addr_mode = addr_mode
    inst.flow_type = flow_type

    if addr_mode == AddressModes.Illegal:
        pass
    elif addr_mode == AddressModes.Inherent:
        pass
    elif addr_mode == AddressModes.ImmediateWord:
        inst.immediate = (operands[0] << 8) + operands[1]
    elif addr_mode == AddressModes.ImmediateByte:
        inst.immediate = operands[0]
    elif addr_mode == AddressModes.Extended:
        high_byte, low_byte = operands
        word = (high_byte << 8) + low_byte
        inst.address = word
        inst.disasm_as_bytes = (high_byte == 0)
    elif addr_mode == AddressModes.Direct:
        inst.address = operands[0]
    elif addr_mode == AddressModes.DirectWithImmediateByte:
        inst.address = operands[0]
        inst.immediate = operands[1]
    elif addr_mode == AddressModes.Register:
        inst.register = opcode & 0b111
    elif addr_mode == AddressModes.RegisterWithImmediateByte:
        inst.register = opcode & 0b111
        inst.immediate = operands[0]
    elif addr_mode == AddressModes.Pointer:
        pass
    elif addr_mode == AddressModes.PointerWithImmediateByte:
        inst.immediate = operands[0]
    elif addr_mode == AddressModes.Index:
        inst.ixd_offset = operands[0]
    elif addr_mode == AddressModes.IndexWithImmediateByte:
        inst.ixd_offset = operands[0]
        inst.immediate = operands[1]
    elif addr_mode == AddressModes.Vector:
        inst.callv = opcode & 0b111
    elif addr_mode == AddressModes.BitDirect:
        inst.bit = opcode & 0b111
        inst.address = operands[0]
    elif addr_mode == AddressModes.Relative:
        inst.address = resolve_rel(pc, operands[0])
        inst.disasm_as_bytes = True
    elif addr_mode == AddressModes.BitDirectWithRelative:
        inst.bit = opcode & 0b111
        inst.address = resolve_rel(pc, operands[0])
        inst.disasm_as_bytes = True
    else:
        raise NotImplementedError()

    return pc, inst
