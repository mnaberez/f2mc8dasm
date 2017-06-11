import unittest
from f2mc8dasm.disasm import disassemble_inst
from f2mc8dasm.tables import AddressModes, Flags, FlowTypes


class InstructionTests(unittest.TestCase):

    # __str__

    def test_str_illegal(self):
        inst = disassemble_inst([0x44], pc=0)
        self.assertEqual(str(inst), ".byte 0x44")

    def test_str_inherent(self):
        inst = disassemble_inst([0x00], pc=0)
        self.assertEqual(str(inst), "nop")

    def test_str_immediate_byte(self):
        inst = disassemble_inst([0x04, 0xaa], pc=0)
        self.assertEqual(str(inst), "mov a, #0xaa")

    def test_str_immediate_word(self):
        inst = disassemble_inst([0xe4, 0xaa, 0xbb], pc=0)
        self.assertEqual(str(inst), "movw a, #0xaabb")

    def test_str_extended(self):
        inst = disassemble_inst([0x31, 0xaa, 0xbb], pc=0)
        self.assertEqual(str(inst), "call 0xaabb")

    def test_str_direct(self):
        inst = disassemble_inst([0x05, 0xaa], pc=0)
        self.assertEqual(str(inst), "mov a, 0xaa")

    def test_str_direct_with_immediate_byte(self):
        inst = disassemble_inst([0x85, 0xaa, 0xbb], pc=0)
        self.assertEqual(str(inst), "mov 0xaa, #0xbb")

    def test_str_register(self):
        inst = disassemble_inst([0xc8], pc=0)
        self.assertEqual(str(inst), "inc r0")

    def test_str_register_with_immediate_byte(self):
        inst = disassemble_inst([0x88, 0xaa], pc=0)
        self.assertEqual(str(inst), "mov r0, #0xaa")

    def test_str_pointer(self):
        inst = disassemble_inst([0x07], pc=0)
        self.assertEqual(str(inst), "mov a, @ep")

    def test_str_pointer_with_immediate_byte(self):
        inst = disassemble_inst([0x87, 0xaa], pc=0)
        self.assertEqual(str(inst), "mov @ep, #0xaa")

    def test_str_index(self):
        inst = disassemble_inst([0xd6, 0xaa], pc=0)
        self.assertEqual(str(inst), "movw @ix+0xaa, a")

    def test_str_index_with_immediate_byte(self):
        inst = disassemble_inst([0x86, 0xaa, 0xbb], pc=0)
        self.assertEqual(str(inst), "mov @ix+0xaa, #0xbb")

    def test_str_bit_direct(self):
        inst = disassemble_inst([0xa0, 0xaa], pc=0)
        self.assertEqual(str(inst), "clrb 0xaa:0")

    def test_str_bitdirect_with_relative(self):
        inst = disassemble_inst([0xb7, 0xaa, 0x08], pc=0)
        self.assertEqual(str(inst), "bbc 0xaa:7, 0x000b")

    def test_relative(self):
        inst = disassemble_inst([0xfd, 0x05], pc=0)
        self.assertEqual(str(inst), "beq 0x0007")

    def test_vector(self):
        inst = disassemble_inst([0xe8], pc=0)
        self.assertEqual(str(inst), "callv #0")


class disassemble_instTests(unittest.TestCase):
    def test_illegal(self):
        inst = disassemble_inst([0x44], pc=0)
        self.assertEqual(inst.disasm_template, ".byte OPC")
        self.assertEqual(inst.addr_mode, AddressModes.Illegal)
        self.assertEqual(inst.flow_type, FlowTypes.Continue)
        self.assertEqual(inst.affected_flags, ())
        self.assertEqual(inst.opcode, 0x44)
        self.assertEqual(inst.operands, bytearray())
        self.assertEqual(inst.address, None)
        self.assertEqual(inst.bittest_address, None)
        self.assertEqual(inst.immediate, None)
        self.assertEqual(inst.ixd_offset, None)
        self.assertEqual(inst.bit, None)
        self.assertEqual(inst.callv, None)
        self.assertEqual(inst.register, None)

    def test_inherent(self):
        inst = disassemble_inst([0x02], pc=0)
        self.assertEqual(inst.disasm_template, "rolc a")
        self.assertEqual(inst.addr_mode, AddressModes.Inherent)
        self.assertEqual(inst.flow_type, FlowTypes.Continue)
        self.assertEqual(inst.affected_flags, (Flags.N, Flags.Z, Flags.C))
        self.assertEqual(inst.opcode, 0x02)
        self.assertEqual(inst.operands, bytearray())
        self.assertEqual(inst.address, None)
        self.assertEqual(inst.bittest_address, None)
        self.assertEqual(inst.immediate, None)
        self.assertEqual(inst.ixd_offset, None)
        self.assertEqual(inst.bit, None)
        self.assertEqual(inst.callv, None)
        self.assertEqual(inst.register, None)

    def test_immediate_byte(self):
        inst = disassemble_inst([0x04, 0xaa], pc=0)
        self.assertEqual(inst.disasm_template, "mov a, #IMB")
        self.assertEqual(inst.addr_mode, AddressModes.ImmediateByte)
        self.assertEqual(inst.flow_type, FlowTypes.Continue)
        self.assertEqual(inst.affected_flags, (Flags.N, Flags.Z))
        self.assertEqual(inst.opcode, 0x04)
        self.assertEqual(inst.operands, bytearray([0xaa]))
        self.assertEqual(inst.address, None)
        self.assertEqual(inst.bittest_address, None)
        self.assertEqual(inst.immediate, 0xaa)
        self.assertEqual(inst.ixd_offset, None)
        self.assertEqual(inst.bit, None)
        self.assertEqual(inst.callv, None)
        self.assertEqual(inst.register, None)

    def test_immediate_word(self):
        inst = disassemble_inst([0xe4, 0xaa, 0xbb], pc=0)
        self.assertEqual(inst.disasm_template, "movw a, #IMW")
        self.assertEqual(inst.addr_mode, AddressModes.ImmediateWord)
        self.assertEqual(inst.flow_type, FlowTypes.Continue)
        self.assertEqual(inst.affected_flags, (Flags.N, Flags.Z))
        self.assertEqual(inst.opcode, 0xe4)
        self.assertEqual(inst.operands, bytearray([0xaa, 0xbb]))
        self.assertEqual(inst.address, None)
        self.assertEqual(inst.bittest_address, None)
        self.assertEqual(inst.immediate, 0xaabb)
        self.assertEqual(inst.ixd_offset, None)
        self.assertEqual(inst.bit, None)
        self.assertEqual(inst.callv, None)
        self.assertEqual(inst.register, None)

    def test_extended(self):
        inst = disassemble_inst([0x60, 0xaa, 0xbb], pc=0)
        self.assertEqual(inst.disasm_template, "mov a, EXT")
        self.assertEqual(inst.addr_mode, AddressModes.Extended)
        self.assertEqual(inst.flow_type, FlowTypes.Continue)
        self.assertEqual(inst.affected_flags, (Flags.N, Flags.Z))
        self.assertEqual(inst.opcode, 0x60)
        self.assertEqual(inst.operands, bytearray([0xaa, 0xbb]))
        self.assertEqual(inst.address, 0xaabb)
        self.assertEqual(inst.bittest_address, None)
        self.assertEqual(inst.immediate, None)
        self.assertEqual(inst.ixd_offset, None)
        self.assertEqual(inst.bit, None)
        self.assertEqual(inst.callv, None)
        self.assertEqual(inst.register, None)

    def test_direct(self):
        inst = disassemble_inst([0x65, 0xaa], pc=0)
        self.assertEqual(inst.disasm_template, "and a, DIR")
        self.assertEqual(inst.addr_mode, AddressModes.Direct)
        self.assertEqual(inst.flow_type, FlowTypes.Continue)
        self.assertEqual(inst.affected_flags, (Flags.N, Flags.Z, Flags.V))
        self.assertEqual(inst.opcode, 0x65)
        self.assertEqual(inst.operands, bytearray([0xaa]))
        self.assertEqual(inst.address, 0xaa)
        self.assertEqual(inst.bittest_address, None)
        self.assertEqual(inst.immediate, None)
        self.assertEqual(inst.ixd_offset, None)
        self.assertEqual(inst.bit, None)
        self.assertEqual(inst.callv, None)
        self.assertEqual(inst.register, None)

    def test_direct_with_immediate_byte(self):
        inst = disassemble_inst([0x95, 0xaa, 0xbb], pc=0)
        self.assertEqual(inst.disasm_template, "cmp DIR, #IMB")
        self.assertEqual(inst.addr_mode, AddressModes.DirectWithImmediateByte)
        self.assertEqual(inst.flow_type, FlowTypes.Continue)
        self.assertEqual(inst.affected_flags,
            (Flags.N, Flags.Z, Flags.V, Flags.C))
        self.assertEqual(inst.opcode, 0x95)
        self.assertEqual(inst.operands, bytearray([0xaa, 0xbb]))
        self.assertEqual(inst.address, 0xaa)
        self.assertEqual(inst.bittest_address, None)
        self.assertEqual(inst.immediate, 0xbb)
        self.assertEqual(inst.ixd_offset, None)
        self.assertEqual(inst.bit, None)
        self.assertEqual(inst.callv, None)
        self.assertEqual(inst.register, None)

    def test_register(self):
        inst = disassemble_inst([0xc9], pc=0)
        self.assertEqual(inst.disasm_template, "inc rREG")
        self.assertEqual(inst.addr_mode, AddressModes.Register)
        self.assertEqual(inst.flow_type, FlowTypes.Continue)
        self.assertEqual(inst.affected_flags, (Flags.N, Flags.Z, Flags.V))
        self.assertEqual(inst.opcode, 0xc9)
        self.assertEqual(inst.operands, bytearray())
        self.assertEqual(inst.address, None)
        self.assertEqual(inst.bittest_address, None)
        self.assertEqual(inst.immediate, None)
        self.assertEqual(inst.ixd_offset, None)
        self.assertEqual(inst.bit, None)
        self.assertEqual(inst.callv, None)
        self.assertEqual(inst.register, 1)

    def test_register_with_immediate_byte(self):
        inst = disassemble_inst([0x99, 0xaa], pc=0)
        self.assertEqual(inst.disasm_template, "cmp rREG, #IMB")
        self.assertEqual(inst.addr_mode,
            AddressModes.RegisterWithImmediateByte)
        self.assertEqual(inst.flow_type, FlowTypes.Continue)
        self.assertEqual(inst.affected_flags,
            (Flags.N, Flags.Z, Flags.V, Flags.C))
        self.assertEqual(inst.opcode, 0x99)
        self.assertEqual(inst.operands, bytearray([0xaa]))
        self.assertEqual(inst.address, None)
        self.assertEqual(inst.bittest_address, None)
        self.assertEqual(inst.immediate, 0xaa)
        self.assertEqual(inst.ixd_offset, None)
        self.assertEqual(inst.bit, None)
        self.assertEqual(inst.callv, None)
        self.assertEqual(inst.register, 1)

    def test_pointer(self):
        inst = disassemble_inst([0x07], pc=0)
        self.assertEqual(inst.disasm_template, "mov a, @ep")
        self.assertEqual(inst.addr_mode, AddressModes.Pointer)
        self.assertEqual(inst.flow_type, FlowTypes.Continue)
        self.assertEqual(inst.affected_flags, (Flags.N, Flags.Z))
        self.assertEqual(inst.opcode, 0x07)
        self.assertEqual(inst.operands, bytearray([]))
        self.assertEqual(inst.address, None)
        self.assertEqual(inst.bittest_address, None)
        self.assertEqual(inst.immediate, None)
        self.assertEqual(inst.ixd_offset, None)
        self.assertEqual(inst.bit, None)
        self.assertEqual(inst.callv, None)
        self.assertEqual(inst.register, None)

    def test_pointer_with_immediate_byte(self):
        inst = disassemble_inst([0x97, 0xaa], pc=0)
        self.assertEqual(inst.disasm_template, "cmp @ep, #IMB")
        self.assertEqual(inst.addr_mode, AddressModes.PointerWithImmediateByte)
        self.assertEqual(inst.flow_type, FlowTypes.Continue)
        self.assertEqual(inst.affected_flags,
            (Flags.N, Flags.Z, Flags.V, Flags.C))
        self.assertEqual(inst.opcode, 0x97)
        self.assertEqual(inst.operands, bytearray([0xaa]))
        self.assertEqual(inst.address, None)
        self.assertEqual(inst.bittest_address, None)
        self.assertEqual(inst.immediate, 0xaa)
        self.assertEqual(inst.ixd_offset, None)
        self.assertEqual(inst.bit, None)
        self.assertEqual(inst.callv, None)
        self.assertEqual(inst.register, None)

    def test_index(self):
        inst = disassemble_inst([0x06, 0xaa], pc=0)
        self.assertEqual(inst.disasm_template, "mov a, @ix+IXD")
        self.assertEqual(inst.addr_mode, AddressModes.Index)
        self.assertEqual(inst.flow_type, FlowTypes.Continue)
        self.assertEqual(inst.affected_flags, (Flags.N, Flags.Z))
        self.assertEqual(inst.opcode, 0x06)
        self.assertEqual(inst.operands, bytearray([0xaa]))
        self.assertEqual(inst.address, None)
        self.assertEqual(inst.bittest_address, None)
        self.assertEqual(inst.immediate, None)
        self.assertEqual(inst.ixd_offset, 0xaa)
        self.assertEqual(inst.bit, None)
        self.assertEqual(inst.callv, None)
        self.assertEqual(inst.register, None)

    def test_index_with_immediate_byte(self):
        inst = disassemble_inst([0x96, 0xaa, 0xbb], pc=0)
        self.assertEqual(inst.disasm_template, "cmp @ix+IXD, #IMB")
        self.assertEqual(inst.addr_mode, AddressModes.IndexWithImmediateByte)
        self.assertEqual(inst.flow_type, FlowTypes.Continue)
        self.assertEqual(inst.affected_flags,
            (Flags.N, Flags.Z, Flags.V, Flags.C))
        self.assertEqual(inst.opcode, 0x96)
        self.assertEqual(inst.operands, bytearray([0xaa, 0xbb]))
        self.assertEqual(inst.address, None)
        self.assertEqual(inst.bittest_address, None)
        self.assertEqual(inst.immediate, 0xbb)
        self.assertEqual(inst.ixd_offset, 0xaa)
        self.assertEqual(inst.bit, None)
        self.assertEqual(inst.callv, None)
        self.assertEqual(inst.register, None)

    def test_vector(self):
        memory = bytearray(0x10000)
        memory[0x0000] = 0xe9
        memory[0xffc2] = 0xaa
        memory[0xffc3] = 0xbb
        inst = disassemble_inst(memory, pc=0)
        self.assertEqual(inst.disasm_template, "callv #VEC")
        self.assertEqual(inst.addr_mode, AddressModes.Vector)
        self.assertEqual(inst.flow_type, FlowTypes.SubroutineCall)
        self.assertEqual(inst.affected_flags, ())
        self.assertEqual(inst.opcode, 0xe9)
        self.assertEqual(inst.operands, bytearray())
        self.assertEqual(inst.address, 0xaabb)
        self.assertEqual(inst.bittest_address, None)
        self.assertEqual(inst.immediate, None)
        self.assertEqual(inst.ixd_offset, None)
        self.assertEqual(inst.bit, None)
        self.assertEqual(inst.callv, 1)
        self.assertEqual(inst.register, None)

    def test_bit_direct(self):
        inst = disassemble_inst([0xa1, 0xaa], pc=0)
        self.assertEqual(inst.disasm_template, "clrb DIR:BIT")
        self.assertEqual(inst.addr_mode, AddressModes.BitDirect)
        self.assertEqual(inst.flow_type, FlowTypes.Continue)
        self.assertEqual(inst.affected_flags, ())
        self.assertEqual(inst.opcode, 0xa1)
        self.assertEqual(inst.operands, bytearray([0xaa]))
        self.assertEqual(inst.address, 0xaa)
        self.assertEqual(inst.bittest_address, None)
        self.assertEqual(inst.immediate, None)
        self.assertEqual(inst.ixd_offset, None)
        self.assertEqual(inst.bit, 1)
        self.assertEqual(inst.callv, None)
        self.assertEqual(inst.register, None)

    def test_relative_backward(self):
        memory = bytearray(0x10000)
        memory[0x8055] = 0xfc
        memory[0x8056] = 0xf4
        inst = disassemble_inst(memory, pc=0x8055)
        self.assertEqual(inst.disasm_template, "bne REL")
        self.assertEqual(inst.addr_mode, AddressModes.Relative)
        self.assertEqual(inst.flow_type, FlowTypes.ConditionalJump)
        self.assertEqual(inst.affected_flags, ())
        self.assertEqual(inst.opcode, 0xfc)
        self.assertEqual(inst.operands, bytearray([0xf4]))
        self.assertEqual(inst.address, 0x804b)
        self.assertEqual(inst.bittest_address, None)
        self.assertEqual(inst.immediate, None)
        self.assertEqual(inst.ixd_offset, None)
        self.assertEqual(inst.bit, None)
        self.assertEqual(inst.callv, None)
        self.assertEqual(inst.register, None)

    def test_relative_foward(self):
        memory = bytearray(0x10000)
        memory[0x8172] = 0xfc
        memory[0x8173] = 0x05
        inst = disassemble_inst(memory, pc=0x8172)
        self.assertEqual(inst.disasm_template, "bne REL")
        self.assertEqual(inst.addr_mode, AddressModes.Relative)
        self.assertEqual(inst.flow_type, FlowTypes.ConditionalJump)
        self.assertEqual(inst.affected_flags, ())
        self.assertEqual(inst.opcode, 0xfc)
        self.assertEqual(inst.operands, bytearray([0x05]))
        self.assertEqual(inst.address, 0x8179)
        self.assertEqual(inst.bittest_address, None)
        self.assertEqual(inst.immediate, None)
        self.assertEqual(inst.ixd_offset, None)
        self.assertEqual(inst.bit, None)
        self.assertEqual(inst.callv, None)
        self.assertEqual(inst.register, None)

    def test_bit_direct_with_relative_forward(self):
        memory = bytearray(0x10000)
        memory[0x84c6] = 0xb1
        memory[0x84c7] = 0xaa
        memory[0x84c8] = 0x01
        inst = disassemble_inst(memory, pc=0x84c6)
        self.assertEqual(inst.disasm_template, "bbc DIR:BIT, REL")
        self.assertEqual(inst.addr_mode, AddressModes.BitDirectWithRelative)
        self.assertEqual(inst.flow_type, FlowTypes.ConditionalJump)
        self.assertEqual(inst.affected_flags, (Flags.Z,))
        self.assertEqual(inst.opcode, 0xb1)
        self.assertEqual(inst.operands, bytearray([0xaa, 0x01]))
        self.assertEqual(inst.address, 0x84ca)
        self.assertEqual(inst.bittest_address, 0xaa)
        self.assertEqual(inst.immediate, None)
        self.assertEqual(inst.ixd_offset, None)
        self.assertEqual(inst.bit, 1)
        self.assertEqual(inst.callv, None)
        self.assertEqual(inst.register, None)

    def test_bit_direct_with_relative_backward(self):
        memory = bytearray(0x10000)
        memory[0x8471] = 0xb1
        memory[0x8472] = 0xaa
        memory[0x8473] = 0xfc
        inst = disassemble_inst(memory, pc=0x8471)
        self.assertEqual(inst.disasm_template, "bbc DIR:BIT, REL")
        self.assertEqual(inst.addr_mode, AddressModes.BitDirectWithRelative)
        self.assertEqual(inst.flow_type, FlowTypes.ConditionalJump)
        self.assertEqual(inst.affected_flags, (Flags.Z,))
        self.assertEqual(inst.opcode, 0xb1)
        self.assertEqual(inst.operands, bytearray([0xaa, 0xfc]))
        self.assertEqual(inst.address, 0x8470)
        self.assertEqual(inst.bittest_address, 0xaa)
        self.assertEqual(inst.immediate, None)
        self.assertEqual(inst.ixd_offset, None)
        self.assertEqual(inst.bit, 1)
        self.assertEqual(inst.callv, None)
        self.assertEqual(inst.register, None)
