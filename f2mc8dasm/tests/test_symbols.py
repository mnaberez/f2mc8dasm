import re
import unittest
import f2mc8dasm.symbols

_DICT_NAMES = [s for s in dir(f2mc8dasm.symbols) if s.endswith('_SYMBOLS')]

class SymbolTests(unittest.TestCase):
    def test_addresses_are_in_range(self):
        for dict_name in _DICT_NAMES:
            d = getattr(f2mc8dasm.symbols, dict_name)
            for address in d.keys():
                msg = "Address %r out of range in %r" % (address, dict_name)
                self.assertTrue((address >= 0) and (address <= 0xFFFF), msg)

    def test_each_address_has_symbol_name_and_comment(self):
        for dict_name in _DICT_NAMES:
            d = getattr(f2mc8dasm.symbols, dict_name)
            for address, name_comment in d.items():
                msg = "Address %r bad value in %r" % (address, dict_name)
                self.assertEqual(len(name_comment), 2, msg)

    def test_symbol_names_never_repeat(self):
        for dict_name in _DICT_NAMES:
            d = getattr(f2mc8dasm.symbols, dict_name)
            names_seen = set()
            for address, (name, comment) in d.items():
                msg = "Symbol name %r repeats in %r" % (name, dict_name)
                self.assertTrue((name not in names_seen), msg)
                names_seen.add(name)

    def test_symbol_names_are_legal_for_asf2mc8(self):
        pat = re.compile(r'\A[a-z\.\$_]{1}[\da-z\.\$_]{0,78}\Z', re.IGNORECASE)
        for dict_name in _DICT_NAMES:
            d = getattr(f2mc8dasm.symbols, dict_name)
            for address, (name, comment) in d.items():
                msg = "Symbol name %r not valid in %r" % (name, dict_name)
                self.assertTrue(pat.match(name), msg)

