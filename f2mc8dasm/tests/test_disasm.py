import unittest
from f2mc8dasm.disasm import disassemble_inst


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
