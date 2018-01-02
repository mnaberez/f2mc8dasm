from f2mc8dasm.tables import (
    AddressModes,
    Opcodes,
    InstructionLengths,
    )


class Instruction(object):
    __slots__ = ('disasm_template', 'addr_mode', 'flow_type',
                 'affected_flags', 'opcode', 'operands', 'address',
                 'bittest_address', 'immediate', 'ixd_offset', 'bit',
                 'callv', 'register',)

    def __init__(self, **kwargs):
        self.disasm_template = '' # "cmp @ix+IXD, #IMB"
        self.addr_mode = None     # addressing mode
        self.flow_type = None     # type of instruction for flow tracing
        self.affected_flags = ()  # tuple of flags affected
        self.opcode = None        # opcode byte
        self.operands = ()        # operand bytes
        self.address = None       # address (dir=0-0xFF, ext=0-0xFFFF)
        self.bittest_address = None # direct address for bit test instructions
        self.immediate = None     # immediate value (byte or word)
        self.ixd_offset = None    # IXD offset 0-0xFF
        self.bit = None           # bit 0-7
        self.callv = None         # callv 0-7
        self.register = None      # register r0-r7

        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise KeyError(k)

    def __len__(self):
        return 1 + len(self.operands)

    def __str__(self):
        disasm = self.disasm_template
        for attr, tpl, fmt in self._disasm_formats:
            v = getattr(self, attr)
            if v is not None:
                disasm = disasm.replace(tpl, fmt % v)
        return disasm

    _disasm_formats = (
        ('opcode',          'OPC', '0x%02x'),
        ('bittest_address', 'DIR', '0x%02x'),
        ('address',         'DIR', '0x%02x'),
        ('address',         'EXT', '0x%04x'),
        ('address',         'REL', '0x%04x'),
        ('immediate',       'IMB', '0x%02x'),
        ('immediate',       'IMW', '0x%04x'),
        ('ixd_offset',      'IXD', '0x%02x'),
        ('bit',             'BIT', '%d'),
        ('callv',           'VEC', '%d'),
        ('register',        'REG', '%d'),
        )

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

    @property
    def extended_address_page_0(self):
        '''Indicates the instruction uses extended addressing for page 0
        that could be optimized to direct addressing'''
        return ((self.addr_mode == AddressModes.Extended) and
                ((self.address & 0xFF00) == 0) and
                (self.opcode not in (0x21, 0x31)))


def disassemble_inst(memory, pc):
    opcode = Opcodes[memory[pc]]
    pc = (pc + 1) & 0xFFFF

    instlen = InstructionLengths[opcode.addr_mode]
    operands = bytearray()
    for i in range(instlen - 1):
        operands.append(memory[pc])
        pc = (pc + 1) & 0xFFFF

    inst = Instruction(
        disasm_template=opcode.disasm_template,
        addr_mode=opcode.addr_mode,
        flow_type=opcode.flow_type,
        affected_flags=opcode.affected_flags,
        opcode=opcode.number,
        operands=operands,
        )

    if inst.addr_mode == AddressModes.Illegal:
        pass
    elif inst.addr_mode == AddressModes.Inherent:
        pass
    elif inst.addr_mode == AddressModes.ImmediateByte:
        inst.immediate = operands[0]
    elif inst.addr_mode == AddressModes.ImmediateWord:
        inst.immediate = (operands[0] << 8) + operands[1]
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
        inst.address = _resolve_callv(inst.callv, memory)
    elif inst.addr_mode == AddressModes.BitDirect:
        inst.bit = opcode.number & 0b111
        inst.address = operands[0]
    elif inst.addr_mode == AddressModes.Relative:
        inst.address = _resolve_rel(pc, operands[0])
    elif inst.addr_mode == AddressModes.BitDirectWithRelative:
        inst.bit = opcode.number & 0b111
        inst.bittest_address = operands[0]
        inst.address = _resolve_rel(pc, operands[1])
    else:
        msg = "Unhandled addressing mode %r at 0x%04x" % (
            inst.addr_mode, pc)
        raise NotImplementedError(msg) # always a bug

    return inst


def _resolve_rel(pc, displacement):
    if displacement & 0x80:
        displacement = -((displacement ^ 0xFF) + 1)
    return (pc + displacement) & 0xFFFF


def _resolve_callv(callv, memory):
    vector = 0xffc0 + (callv * 2)
    try:
        high = memory[vector] << 8
        low = memory[(vector + 1) & 0xFFFF]
        return high + low
    except IndexError:
        return None
