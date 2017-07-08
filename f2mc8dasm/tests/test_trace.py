import unittest
from operator import attrgetter
from f2mc8dasm.trace import Tracer, TraceQueue, SortedSet, ProcessorState
from f2mc8dasm.memory import Memory
from f2mc8dasm.disasm import disassemble_inst

class TraceQueueTests(unittest.TestCase):
    # __init__

    def test_ctor(self):
        queue = TraceQueue()
        self.assertEqual(queue.traced_processor_states, set())
        self.assertEqual(queue.untraced_processor_states, SortedSet())

    # __len__

    def test_len_returns_untraced_length(self):
        queue = TraceQueue()
        queue.push(ProcessorState(pc=0x0001))
        queue.push(ProcessorState(pc=0x0002))
        self.assertEqual(len(queue), 2)

    # push

    def test_push_adds_state_to_untraced(self):
        queue = TraceQueue()
        queue.push(ProcessorState(pc=0x0005))
        self.assertEqual(queue.untraced_processor_states,
            set([ProcessorState(pc=0x0005)]))
        queue.push(ProcessorState(0x0006))
        self.assertEqual(set(queue.untraced_processor_states),
            set([ProcessorState(pc=0x0005), ProcessorState(pc=0x0006)]))

    def test_push_doesnt_add_state_if_already_in_traced(self):
        queue = TraceQueue()
        queue.push(ProcessorState(pc=0x0005))
        self.assertEqual(len(queue), 1)
        queue.pop()
        queue.push(ProcessorState(pc=0x0005))
        self.assertEqual(len(queue), 0)

    def test_push_doesnt_add_state_if_already_in_untraced(self):
        queue = TraceQueue()
        queue.push(ProcessorState(pc=0x0005))
        self.assertEqual(len(queue), 1)
        queue.push(ProcessorState(pc=0x0005))
        self.assertEqual(len(queue), 1)

    # pop

    def test_pop_raises_if_no_more_states(self):
        queue = TraceQueue()
        try:
            queue.pop()
            self.fail()
        except KeyError as exc:
            self.assertEqual(exc.args[0], 'pop from empty trace queue')

    def test_pop_removes_state_from_untraced_and_adds_to_traced(self):
        queue = TraceQueue()
        queue.push(ProcessorState(pc=0x0005))
        self.assertEqual(queue.untraced_processor_states,
            set([ProcessorState(pc=0x0005)]))
        state = queue.pop()
        self.assertEqual(state.pc, 0x0005)
        self.assertEqual(queue.untraced_processor_states, set())
        self.assertEqual(queue.traced_processor_states,
            set([ProcessorState(pc=0x0005)]))

    def test_pop_returns_states_in_pc_sorted_order(self):
        queue = TraceQueue()
        queue.push(ProcessorState(pc=0x0003))
        queue.push(ProcessorState(pc=0x0001))
        queue.push(ProcessorState(pc=0x0002))
        self.assertEqual(queue.pop().pc, 0x0001)
        self.assertEqual(queue.pop().pc, 0x0002)
        self.assertEqual(queue.pop().pc, 0x0003)


class SortedSetTests(unittest.TestCase):
    # __init__

    def test_ctor(self):
        s = SortedSet([1, 2])
        self.assertTrue(1 in s)
        self.assertTrue(2 in s)

    # __len__

    def test_len_initially_0(self):
        s = SortedSet()
        self.assertEqual(len(s), 0)

    def test_len(self):
        s = SortedSet([1, 2])
        s.add(3)
        self.assertEqual(len(s), 3)

    # __contains__

    def test_contains(self):
        s = SortedSet([1])
        s.add(2)
        self.assertTrue(1 in s)
        self.assertTrue(2 in s)
        self.assertFalse(3 in s)

    # __iter__

    def test_iter(self):
        s = SortedSet([2,1,3])
        s.add(5)
        s.add(4)
        self.assertEqual(list(s), [1,2,3,4,5])

    # __eq__

    def test_eq_set(self):
        s = SortedSet([1, 2])
        self.assertTrue(s == set([1, 2]))
        self.assertFalse(s == set([1, 2, 3]))

    def test_eq_SortedSet(self):
        s = SortedSet([1, 2])
        self.assertTrue(s == SortedSet([1, 2]))
        self.assertFalse(s == SortedSet([1, 2, 3]))

    # add

    def test_add_new_item(self):
        s = SortedSet()
        s.add(1)
        self.assertEqual(s, set([1]))

    def test_add_existing_item(self):
        s = SortedSet()
        s.add(1)
        s.add(1)
        s.add(1)
        self.assertEqual(s, set([1]))
        self.assertEqual(list(s), [1])

    # remove

    def test_remove(self):
        s = SortedSet([1, 2, 3])
        s.remove(2)
        self.assertEqual(s, set([1, 3]))
        self.assertEqual(list(s), [1, 3])

    def test_remove_nonexistent_item(self):
        s = SortedSet()
        self.assertRaises(KeyError, s.remove, 1)

    # pop

    def test_pop_no_sort_key(self):
        s = SortedSet([3,1,4])
        s.add(2)
        self.assertEqual(s.pop(), 1)
        self.assertEqual(s.pop(), 2)
        self.assertEqual(s.pop(), 3)
        self.assertEqual(s.pop(), 4)

    def test_pop_sort_key(self):
        items = [ProcessorState(pc=3), ProcessorState(pc=1),
            ProcessorState(pc=4)]
        s = SortedSet(items, key=attrgetter('pc'))
        s.add(ProcessorState(pc=2))
        self.assertEqual(s.pop().pc, 1)
        self.assertEqual(s.pop().pc, 2)
        self.assertEqual(s.pop().pc, 3)
        self.assertEqual(s.pop().pc, 4)

    def test_pop_empty(self):
        s = SortedSet()
        self.assertRaises(KeyError, s.pop)


class TracerTests(unittest.TestCase):

    # branch always taken

    def test_branch_always_taken_bnz_bz(self):
        rom = bytearray(0x10000)
        rom[0x8ac1] = 0xfc   # bnz 0x8ac5     ;8ac1  fc 02
        rom[0x8ac2] = 0x02
        rom[0x8ac3] = 0xfd   # bz 0x8b15      ;8ac3  fd 50  branch always
        rom[0x8ac4] = 0x50
        memory = Memory(rom)
        tracer = Tracer(
            memory=memory,
            entry_points=[0x8ac1],
            vectors=[],
            traceable_range=range(0x8ac1, 0x8ac4+1)
            )
        tracer.trace(disassemble_inst)
        self.assertTrue(memory.is_branch_always_taken(0x8ac3))

    def test_branch_always_taken_bz_bnz(self):
        rom = bytearray(0x10000)
        rom[0x8ac1] = 0xfd   # bz 0x8ac5     ;8ac1  fd 02
        rom[0x8ac2] = 0x02
        rom[0x8ac3] = 0xfc   # bnz 0x8b15    ;8ac3  fc 50  branch always
        rom[0x8ac4] = 0x50
        memory = Memory(rom)
        tracer = Tracer(
            memory=memory,
            entry_points=[0x8ac1],
            vectors=[],
            traceable_range=range(0x8ac1, 0x8ac4+1)
            )
        tracer.trace(disassemble_inst)
        self.assertTrue(memory.is_branch_always_taken(0x8ac3))

    def test_branch_always_taken_mov_bz(self):
        rom = bytearray(0x10000)
        rom[0xf90c] = 0x04   # mov a, #0x00  ;f90c  04 00
        rom[0xf90d] = 0x00
        rom[0xf90e] = 0xfd   # bz 0xf8f4     ;f90e  fc e4  branch always
        rom[0xf90f] = 0xe4
        memory = Memory(rom)
        tracer = Tracer(
            memory=memory,
            entry_points=[0xf90c],
            vectors=[],
            traceable_range=range(0xf90c, 0xf90f+1)
            )
        tracer.trace(disassemble_inst)
        self.assertTrue(memory.is_branch_always_taken(0xf90e))

    def test_branch_always_taken_mov_bnz(self):
        rom = bytearray(0x10000)
        rom[0xf90c] = 0x04   # mov a, #0x1c  ;f90c  04 1c
        rom[0xf90d] = 0x1c
        rom[0xf90e] = 0xfc   # bnz 0xf8f4    ;f90e  fc e4  branch always
        rom[0xf90f] = 0xe4
        memory = Memory(rom)
        tracer = Tracer(
            memory=memory,
            entry_points=[0xf90c],
            vectors=[],
            traceable_range=range(0xf90c, 0xf90f+1)
            )
        tracer.trace(disassemble_inst)
        self.assertTrue(memory.is_branch_always_taken(0xf90e))

    def test_branch_always_taken_movw_bz(self):
        rom = bytearray(0x10000)
        rom[0xf90b] = 0xe4   # movw a, #0x0000  ;f90b  e4 00 00
        rom[0xf90c] = 0x00
        rom[0xf90d] = 0x00
        rom[0xf90e] = 0xfd   # bz 0xf8f4        ;f90e  fd e4  branch always
        rom[0xf90f] = 0xe4
        memory = Memory(rom)
        tracer = Tracer(
            memory=memory,
            entry_points=[0xf90b],
            vectors=[],
            traceable_range=range(0xf90b, 0xf90e+1)
            )
        tracer.trace(disassemble_inst)
        self.assertTrue(memory.is_branch_always_taken(0xf90e))

    def test_branch_always_taken_movw_bnz(self):
        rom = bytearray(0x10000)
        rom[0xf90b] = 0xe4   # movw a, #0x0001  ;f90b  e4 00 01
        rom[0xf90c] = 0x00
        rom[0xf90d] = 0x01
        rom[0xf90e] = 0xfc   # bnz 0xf8f4       ;f90e  fc e4  branch always
        rom[0xf90f] = 0xe4
        memory = Memory(rom)
        tracer = Tracer(
            memory=memory,
            entry_points=[0xf90b],
            vectors=[],
            traceable_range=range(0xf90b, 0xf90f+1)
            )
        tracer.trace(disassemble_inst)
        self.assertTrue(memory.is_branch_always_taken(0xf90e))

    def test_branch_always_taken_clrc_bnc(self):
        rom = bytearray(0x10000)
        rom[0xf9e6] = 0x81   # clrc         ;f9e6  81
        rom[0xf9e7] = 0xf8   # bnc 0xf9eb   ;f9e7  f8 02  branch always
        memory = Memory(rom)
        tracer = Tracer(
            memory=memory,
            entry_points=[0xf9e6],
            vectors=[],
            traceable_range=range(0xf9e3, 0xf9e7+1)
            )
        tracer.trace(disassemble_inst)
        self.assertTrue(memory.is_branch_always_taken(0xf9e7))

    def test_branch_always_taken_setc_bc(self):
        rom = bytearray(0x10000)
        rom[0xf9e6] = 0x91   # setc         ;f9e6  91
        rom[0xf9e7] = 0xf9   # bc 0xf9eb    ;f9e3  f9 02  branch always
        memory = Memory(rom)
        tracer = Tracer(
            memory=memory,
            entry_points=[0xf9e6],
            vectors=[],
            traceable_range=range(0xf9e3, 0xf9e7+1)
            )
        tracer.trace(disassemble_inst)
        self.assertTrue(memory.is_branch_always_taken(0xf9e7))

    def test_branch_always_taken_bc_bnc(self):
        rom = bytearray(0x10000)
        rom[0xf9e3] = 0xf9   # bc 0xf9e9    ;f9e3  f9 04
        rom[0xf9e4] = 0x04
        rom[0xf9e5] = 0xa8   # setb pdr0:0  ;f9e5  a8 00
        rom[0xf9e6] = 0x00
        rom[0xf9e7] = 0xf8   # bnc 0xf9eb   ;f9e7  f8 02  branch always
        rom[0xf9e8] = 0x02
        memory = Memory(rom)
        tracer = Tracer(
            memory=memory,
            entry_points=[0xf9e3],
            vectors=[],
            traceable_range=range(0xf9e3, 0xf9e8+1)
            )
        tracer.trace(disassemble_inst)
        self.assertTrue(memory.is_branch_always_taken(0xf9e7))

    def test_branch_always_taken_bnc_bc(self):
        rom = bytearray(0x10000)
        rom[0xf9e3] = 0xf8   # bnc 0xf9e9  ;f9e3  f8 04
        rom[0xf9e4] = 0x04
        rom[0xf9e5] = 0xa8   # setb pdr0:0 ;f9e5  a8 00
        rom[0xf9e6] = 0x00
        rom[0xf9e7] = 0xf9   # bc 0xf9eb   ;f9e7  f9 02  branch always
        rom[0xf9e8] = 0x02
        memory = Memory(rom)
        tracer = Tracer(
            memory=memory,
            entry_points=[0xf9e3],
            vectors=[],
            traceable_range=range(0xf9e3, 0xf9e8+1)
            )
        tracer.trace(disassemble_inst)
        self.assertTrue(memory.is_branch_always_taken(0xf9e7))

    def test_branch_always_taken_mov_bp(self):
        rom = bytearray(0x10000)
        rom[0xf9e5] = 0x04   # mov a, #0x42  ;f9e5  04 42
        rom[0xf9e6] = 0x42
        rom[0xf9e7] = 0xfa   # bp 0xf9eb     ;f9e7  fa 02  branch always
        rom[0xf9e8] = 0x02
        memory = Memory(rom)
        tracer = Tracer(
            memory=memory,
            entry_points=[0xf9e5],
            vectors=[],
            traceable_range=range(0xf9e5, 0xf9e8+1)
            )
        tracer.trace(disassemble_inst)
        self.assertTrue(memory.is_branch_always_taken(0xf9e7))

    def test_branch_always_taken_mov_bn(self):
        rom = bytearray(0x10000)
        rom[0xf9e5] = 0x04   # mov a, #0x82  ;f9e5  04 82
        rom[0xf9e6] = 0x82
        rom[0xf9e7] = 0xfb   # bn 0xf9eb     ;f9e7  fb 02  branch always
        rom[0xf9e8] = 0x02
        memory = Memory(rom)
        tracer = Tracer(
            memory=memory,
            entry_points=[0xf9e5],
            vectors=[],
            traceable_range=range(0xf9e5, 0xf9e8+1)
            )
        tracer.trace(disassemble_inst)
        self.assertTrue(memory.is_branch_always_taken(0xf9e7))

    def test_branch_always_taken_bp_bn(self):
        rom = bytearray(0x10000)
        rom[0xf9e3] = 0xfa   # bp 0xf9e9    ;f9e3  fa 04
        rom[0xf9e4] = 0x04
        rom[0xf9e5] = 0xa8   # setb pdr0:0  ;f9e5  a8 00
        rom[0xf9e6] = 0x00
        rom[0xf9e7] = 0xfb   # bn 0xf9eb    ;f9e7  fb 02  branch always
        rom[0xf9e8] = 0x02
        memory = Memory(rom)
        tracer = Tracer(
            memory=memory,
            entry_points=[0xf9e3],
            vectors=[],
            traceable_range=range(0xf9e3, 0xf9e8+1)
            )
        tracer.trace(disassemble_inst)
        self.assertTrue(memory.is_branch_always_taken(0xf9e7))

    def test_branch_always_taken_bn_np(self):
        rom = bytearray(0x10000)
        rom[0xf9e3] = 0xfb   # bn 0xf9e9    ;f9e3  fb 04
        rom[0xf9e4] = 0x04
        rom[0xf9e5] = 0xa8   # setb pdr0:0  ;f9e5  a8 00
        rom[0xf9e6] = 0x00
        rom[0xf9e7] = 0xfa   # bn 0xf9eb    ;f9e7  fa 02  branch always
        rom[0xf9e8] = 0x02
        memory = Memory(rom)
        tracer = Tracer(
            memory=memory,
            entry_points=[0xf9e3],
            vectors=[],
            traceable_range=range(0xf9e3, 0xf9e8+1)
            )
        tracer.trace(disassemble_inst)
        self.assertTrue(memory.is_branch_always_taken(0xf9e7))
