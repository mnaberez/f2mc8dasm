import re
import unittest
from f2mc8dasm import symbols, memory, disasm


class SymbolTableTests(unittest.TestCase):
    def test_generate_makes_lab_symbol_for_jump_target(self):
        mem = memory.Memory(bytearray(0x10000))
        mem.annotate_jump_target(0xF000)
        mem.set_instruction(0xF000, disasm.Instruction())
        st = symbols.SymbolTable()
        st.generate(mem, 0)
        self.assertEqual(st.symbols, {0xf000: ('lab_f000', '')})

    def test_generate_makes_sub_symbol_for_call_target(self):
        mem = memory.Memory(bytearray(0x10000))
        mem.annotate_call_target(0xF000)
        mem.set_instruction(0xF000, disasm.Instruction())
        st = symbols.SymbolTable()
        st.generate(mem, 0)
        self.assertEqual(st.symbols, {0xf000: ('sub_f000', '')})

    def test_generate_makes_sub_symbol_for_jump_and_call_target(self):
        mem = memory.Memory(bytearray(0x10000))
        mem.annotate_jump_target(0xF000)
        mem.annotate_call_target(0xF000)
        mem.set_instruction(0xF000, disasm.Instruction())
        st = symbols.SymbolTable()
        st.generate(mem, 0)
        self.assertEqual(st.symbols, {0xf000: ('sub_f000', '')})

    def test_generate_doesnt_make_symbol_for_jump_to_mid_instruction(self):
        mem = memory.Memory(bytearray(0x10000))
        inst = disasm.Instruction(opcode=0x31, operands=(0xaa, 0xbb,))
        self.assertTrue(len(inst), 3)
        mem.set_instruction(0xF000, inst)
        self.assertTrue(mem.is_instruction_start(0xF000))
        self.assertTrue(mem.is_instruction_continuation(0xF001))
        mem.annotate_jump_target(0xF001)
        st = symbols.SymbolTable()
        st.generate(mem, 0)
        self.assertEqual(st.symbols, {})


class SymbolDictionariesTests(unittest.TestCase):
    def test_addresses_are_in_range(self):
        for dict_name in _DICT_NAMES:
            d = getattr(symbols, dict_name)
            for address in d.keys():
                msg = "Address %r out of range in %r" % (address, dict_name)
                self.assertTrue((address >= 0) and (address <= 0xFFFF), msg)

    def test_each_address_has_symbol_name_and_comment(self):
        for dict_name in _DICT_NAMES:
            d = getattr(symbols, dict_name)
            for address, name_comment in d.items():
                msg = "Address %r bad value in %r" % (address, dict_name)
                self.assertEqual(len(name_comment), 2, msg)

    def test_symbol_names_never_repeat(self):
        for dict_name in _DICT_NAMES:
            d = getattr(symbols, dict_name)
            names_seen = set()
            for address, (name, comment) in d.items():
                msg = "Symbol name %r repeats in %r" % (name, dict_name)
                self.assertTrue((name not in names_seen), msg)
                names_seen.add(name)

    def test_symbol_names_are_legal_for_asf2mc8(self):
        pat = re.compile(r'\A[a-z\.\$_]{1}[\da-z\.\$_]{0,78}\Z', re.IGNORECASE)
        for dict_name in _DICT_NAMES:
            d = getattr(symbols, dict_name)
            for address, (name, comment) in d.items():
                msg = "Symbol name %r not valid in %r" % (name, dict_name)
                self.assertTrue(pat.match(name), msg)


_DICT_NAMES = [s for s in dir(symbols) if s.endswith('_SYMBOLS')]
