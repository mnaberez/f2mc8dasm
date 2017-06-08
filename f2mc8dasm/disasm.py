from f2mc8dasm.tables import (
    AddressModes,
    Opcodes,
    InstructionLengths,
    )


class Instruction(object):
    disasm_template = '' # "cmp @ix+IXD, #IMB"
    addr_mode = None     # addressing mode
    flow_type = None     # type of instruction for flow tracing
    opcode = None        # opcode byte
    operands = ()        # operand bytes
    address = None       # address (0-0xFF for direct, 0-0xFFFF for ext)
    bittest_address = None # direct address for bit test instructions
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

    def __len__(self):
        return 1 + len(self.operands)

    @property
    def all_bytes(self):
        return [self.opcode] + list(self.operands)

    @property
    def stores_immediate_word_in_pointer(self):
        if self.addr_mode == AddressModes.ImmediateWord:
            for reg in ("ep", "ix", "sp"):
                if reg in self.disasm_template:
                    return True
        return False

    @property
    def stores_immediate_word_in_a(self):
        if self.addr_mode == AddressModes.ImmediateWord:
            if "a" in self.disasm_template:
                return True
        return False


def resolve_rel(pc, displacement):
    if displacement & 0x80:
        displacement = -((displacement ^ 0xFF) + 1)
    return (pc + displacement) & 0xFFFF


def disassemble_inst(rom, pc):
    opcode = Opcodes[rom[pc]]
    pc = (pc + 1) & 0xFFFF

    instlen = InstructionLengths[opcode.addr_mode]
    operands = bytearray()
    for i in range(instlen - 1):
        operands.append(rom[pc])
        pc = (pc + 1) & 0xFFFF

    inst = Instruction(
        disasm_template=opcode.disasm_template,
        addr_mode=opcode.addr_mode,
        flow_type=opcode.flow_type,
        opcode=opcode.number,
        operands=operands,
        )

    if inst.addr_mode == AddressModes.Illegal:
        pass
    elif inst.addr_mode == AddressModes.Inherent:
        pass
    elif inst.addr_mode == AddressModes.ImmediateWord:
        inst.immediate = (operands[0] << 8) + operands[1]
    elif inst.addr_mode == AddressModes.ImmediateByte:
        inst.immediate = operands[0]
    elif inst.addr_mode == AddressModes.Extended:
        high_byte, low_byte = operands
        word = (high_byte << 8) + low_byte
        inst.address = word
    elif inst.addr_mode == AddressModes.Direct:
        inst.address = operands[0]
    elif inst.addr_mode == AddressModes.DirectWithImmediateByte:
        inst.address = operands[0]
        inst.immediate = operands[1]
    elif inst.addr_mode == AddressModes.Register:
        inst.register = opcode.number & 0b111
    elif inst.addr_mode == AddressModes.RegisterWithImmediateByte:
        inst.register = opcode.number & 0b111
        inst.immediate = operands[0]
    elif inst.addr_mode == AddressModes.Pointer:
        pass
    elif inst.addr_mode == AddressModes.PointerWithImmediateByte:
        inst.immediate = operands[0]
    elif inst.addr_mode == AddressModes.Index:
        inst.ixd_offset = operands[0]
    elif inst.addr_mode == AddressModes.IndexWithImmediateByte:
        inst.ixd_offset = operands[0]
        inst.immediate = operands[1]
    elif inst.addr_mode == AddressModes.Vector:
        inst.callv = opcode.number & 0b111
    elif inst.addr_mode == AddressModes.BitDirect:
        inst.bit = opcode.number & 0b111
        inst.address = operands[0]
    elif inst.addr_mode == AddressModes.Relative:
        inst.address = resolve_rel(pc, operands[0])
    elif inst.addr_mode == AddressModes.BitDirectWithRelative:
        inst.bit = opcode.number & 0b111
        inst.bittest_address = operands[0]
        inst.address = resolve_rel(pc, operands[1])
    else:
        raise NotImplementedError()

    return inst
