import os
from operator import attrgetter
from f2mc8dasm.tables import FlowTypes, Flags

class Tracer(object):
    def __init__(self, memory, entry_points, vectors, traceable_range):
        self.memory = memory
        self.traceable_range = traceable_range
        self.queue = TraceQueue()

        for address in entry_points:
            if address not in traceable_range:
                msg = "Address 0x%04X outside of traceable range"
                raise ValueError(msg % address)
            self.enqueue_address(address)

        for address in vectors:
            if address not in traceable_range:
                msg = "Vector address 0x%04X outside of traceable range"
                raise ValueError(msg % address)
            self.enqueue_vector(address)

    def trace(self, disassemble_func):
        mem_len = len(self.memory)

        while len(self.queue):
            ps = self.queue.pop() # current processor state
            inst = disassemble_func(self.memory, ps.pc)

            if "LOG" in os.environ: # XXX hack
                self._log(inst, ps)

            inst_len = len(inst)
            if (ps.pc + inst_len) >= mem_len:
                continue  # ignore instruction that would wrap around memory

            if self.memory.is_instruction_start(ps.pc):
                # tracing previously seen instruction with new processor state
                pass
            elif not self.memory.is_unknown(ps.pc, inst_len):
                # ignore new instruction that would overlap a previous marking
                continue
            else:
                # mark new instruction
                self.memory.set_instruction(ps.pc, inst)

            new_ps = ps.copy()  # new state after this instruction
            new_ps.pc = (ps.pc + inst_len) & 0xFFFF

            # trace this instruction
            handler = self._instruction_handlers.get(inst.opcode)
            if handler is None:
                handler = self._generic_handlers[inst.flow_type]
            handler(self, inst, ps, new_ps)

        self.mark_unknown_memory_as_data()
        self.annotate_branches()

    def _log(self, inst, ps):
        print("TRACE " + str(ps).ljust(24) + str(inst))

    # Handlers for specific instructions

    def _trace_inst_0x04_mov(self, inst, ps, new_ps):
        # flowtype = continue
        a = inst.immediate
        new_ps.n = int((a & 0x80) == 0x80)
        new_ps.z = int(a == 0)
        # TODO A register
        self.enqueue_processor_state(new_ps)

    def _trace_inst_0xe4_movw(self, inst, ps, new_ps):
        # flowtype = continue
        a = inst.immediate
        new_ps.n = int((a & 0x8000) == 0x8000)
        new_ps.z = int(a == 0)
        # TODO A register
        self.enqueue_processor_state(new_ps)

    def _trace_inst_0x91_setc(self, inst, ps, new_ps):
        # flowtype = continue
        new_ps.c = 1
        self.enqueue_processor_state(new_ps)

    def _trace_inst_0x81_clrc(self, inst, ps, new_ps):
        # flowtype = continue
        new_ps.c = 0
        self.enqueue_processor_state(new_ps)

    def _trace_inst_0xf8_bnc(self, inst, ps, new_ps):
        # flowtype = conditional jump
        if ps.c is Unknown:
            # don't take the branch
            self.memory.annotate_branch_not_taken(ps.pc)
            new_ps.c = 1
            self.enqueue_processor_state(new_ps)

            # take the branch
            self.memory.annotate_branch_taken(ps.pc)
            new_ps = new_ps.copy()
            new_ps.c = 0
            new_ps.pc = inst.address
            self.enqueue_processor_state(new_ps)
            self.memory.annotate_jump_target(inst.address)

        elif ps.c == 0:
            # take the branch
            self.memory.annotate_branch_taken(ps.pc)
            new_ps.pc = inst.address
            self.enqueue_processor_state(new_ps)
            self.memory.annotate_jump_target(inst.address)

        elif ps.c == 1:
            # don't take the branch
            self.memory.annotate_branch_not_taken(ps.pc)
            self.enqueue_processor_state(new_ps)

    def _trace_inst_0xfa_bp(self, inst, ps, new_ps):
        # flowtype = conditional jump
        if ps.n is Unknown:
            # don't take the branch
            self.memory.annotate_branch_not_taken(ps.pc)
            new_ps.n = 1
            self.enqueue_processor_state(new_ps)

            # take the branch
            self.memory.annotate_branch_taken(ps.pc)
            new_ps = new_ps.copy()
            new_ps.n = 0
            new_ps.pc = inst.address
            self.enqueue_processor_state(new_ps)
            self.memory.annotate_jump_target(inst.address)

        elif ps.n == 1:
            # don't take the branch
            self.memory.annotate_branch_not_taken(ps.pc)
            self.enqueue_processor_state(new_ps)

        elif ps.n == 0:
            # take the branch
            self.memory.annotate_branch_taken(ps.pc)
            new_ps.pc = inst.address
            self.enqueue_processor_state(new_ps)
            self.memory.annotate_jump_target(inst.address)

    def _trace_inst_0xfb_bn(self, inst, ps, new_ps):
        # flowtype = conditional jump
        if ps.n is Unknown:
            # don't take the branch
            self.memory.annotate_branch_not_taken(ps.pc)
            new_ps.n = 0
            self.enqueue_processor_state(new_ps)

            # take the branch
            self.memory.annotate_branch_taken(ps.pc)
            new_ps = new_ps.copy()
            new_ps.n = 1
            new_ps.pc = inst.address
            self.enqueue_processor_state(new_ps)
            self.memory.annotate_jump_target(inst.address)

        elif ps.n == 0:
            # don't take the branch
            self.memory.annotate_branch_not_taken(ps.pc)
            self.enqueue_processor_state(new_ps)

        elif ps.n == 1:
            # take the branch
            self.memory.annotate_branch_taken(ps.pc)
            new_ps.pc = inst.address
            self.enqueue_processor_state(new_ps)
            self.memory.annotate_jump_target(inst.address)

    def _trace_inst_0xf9_bc(self, inst, ps, new_ps):
        # flowtype = conditional jump
        if ps.c is Unknown:
            # don't take the branch
            self.memory.annotate_branch_not_taken(ps.pc)
            new_ps.c = 0
            self.enqueue_processor_state(new_ps)

            # take the branch
            self.memory.annotate_branch_taken(ps.pc)
            new_ps = new_ps.copy()
            new_ps.c = 1
            new_ps.pc = inst.address
            self.enqueue_processor_state(new_ps)
            self.memory.annotate_jump_target(inst.address)

        elif ps.c == 0:
            # don't take the branch
            self.memory.annotate_branch_not_taken(ps.pc)
            self.enqueue_processor_state(new_ps)

        elif ps.c == 1:
            # take the branch
            self.memory.annotate_branch_taken(ps.pc)
            new_ps.pc = inst.address
            self.enqueue_processor_state(new_ps)
            self.memory.annotate_jump_target(inst.address)

    def _trace_inst_0xfd_beq(self, inst, ps, new_ps):
        # flowtype = conditional jump
        if ps.z is Unknown:
            # don't take the branch
            self.memory.annotate_branch_not_taken(ps.pc)
            new_ps.z = 0
            self.enqueue_processor_state(new_ps)

            # take the branch
            self.memory.annotate_branch_taken(ps.pc)
            new_ps = new_ps.copy()
            new_ps.z = 1
            new_ps.pc = inst.address
            self.enqueue_processor_state(new_ps)
            self.memory.annotate_jump_target(inst.address)

        elif ps.z == 0:
            # don't take the branch
            self.memory.annotate_branch_not_taken(ps.pc)
            self.enqueue_processor_state(new_ps)

        elif ps.z == 1:
            # take the branch
            self.memory.annotate_branch_taken(ps.pc)
            new_ps.pc = inst.address
            self.enqueue_processor_state(new_ps)
            self.memory.annotate_jump_target(inst.address)

    def _trace_inst_0xfc_bne(self, inst, ps, new_ps):
        # flowtype = conditional jump
        if ps.z is Unknown:
            # don't take the branch
            self.memory.annotate_branch_not_taken(ps.pc)
            new_ps.z = 1
            self.enqueue_processor_state(new_ps)

            # take the branch
            self.memory.annotate_branch_taken(ps.pc)
            new_ps2 = new_ps.copy()
            new_ps2.z = 0
            new_ps2.pc = inst.address
            self.enqueue_processor_state(new_ps2)
            self.memory.annotate_jump_target(inst.address)

        elif ps.z == 0:
            # take the branch
            self.memory.annotate_branch_taken(ps.pc)
            new_ps.pc = inst.address
            self.enqueue_processor_state(new_ps)
            self.memory.annotate_jump_target(inst.address)

        elif ps.z == 1:
            # don't take the branch
            self.memory.annotate_branch_not_taken(ps.pc)
            self.enqueue_processor_state(new_ps)

    _instruction_handlers = {
        0x04: _trace_inst_0x04_mov,
        0xe4: _trace_inst_0xe4_movw,
        0x91: _trace_inst_0x91_setc,
        0x81: _trace_inst_0x81_clrc,
        0xf8: _trace_inst_0xf8_bnc,
        0xf9: _trace_inst_0xf9_bc,
        0xfa: _trace_inst_0xfa_bp,
        0xfb: _trace_inst_0xfb_bn,
        0xfc: _trace_inst_0xfc_bne,
        0xfd: _trace_inst_0xfd_beq,
    }

    # Fallback handlers for when an instruction handler is not available

    def _trace_generic_continue(self, inst, ps, new_ps):
        self._update_flags(inst, new_ps)
        self.enqueue_processor_state(new_ps)

    def _trace_generic_conditional_jump(self, inst, ps, new_ps):
        self._update_flags(inst, new_ps)

        # don't take the branch
        self.enqueue_processor_state(new_ps)

        # take the branch
        new_ps = new_ps.copy()
        new_ps.pc = inst.address
        self.enqueue_processor_state(new_ps)
        self.memory.annotate_jump_target(inst.address)

        return False

    def _trace_generic_unconditional_jump(self, inst, ps, new_ps):
        self._update_flags(inst, new_ps)
        self.memory.annotate_jump_target(inst.address)
        new_ps.pc = inst.address
        self.enqueue_processor_state(new_ps)

    def _trace_generic_subroutine_call(self, inst, ps, new_ps):
        # enqueue the next instruction after call returns
        # XXX the processor flags are dropped here because we don't
        # know how the subroutine would have affected them.
        new_ps2 = ProcessorState(pc=new_ps.pc)
        self.enqueue_processor_state(new_ps2)

        # enqueue the subroutine called
        new_ps.pc = inst.address
        self.memory.annotate_call_target(inst.address)
        self.enqueue_processor_state(new_ps)

    def _trace_generic_indirect_unconditional_jump(self, inst, ps, new_ps):
        pass

    def _trace_generic_subroutine_return(self, inst, ps, new_ps):
        pass

    def _update_flags(self, inst, ps):
        if Flags.C in inst.affected_flags:
            ps.c = Unknown
        if Flags.N in inst.affected_flags:
            ps.n = Unknown
        if Flags.Z in inst.affected_flags:
            ps.z = Unknown

    _generic_handlers = {
        FlowTypes.Continue:          _trace_generic_continue,
        FlowTypes.UnconditionalJump: _trace_generic_unconditional_jump,
        FlowTypes.ConditionalJump:   _trace_generic_conditional_jump,
        FlowTypes.SubroutineCall:    _trace_generic_subroutine_call,
        FlowTypes.IndirectUnconditionalJump: _trace_generic_indirect_unconditional_jump,
        FlowTypes.SubroutineReturn:  _trace_generic_subroutine_return,
    }

    def enqueue_processor_state(self, ps):
        if ps.pc in self.traceable_range:
            if self.memory.is_unknown(ps.pc):
                self.queue.push(ps)
            elif self.memory.is_instruction_start(ps.pc):
                # we need to queue it again to so it's traced with the current
                # processor state
                self.queue.push(ps)

    def enqueue_address(self, address):
        if address in self.traceable_range:
            ps = ProcessorState(pc=address)
            self.enqueue_processor_state(ps)

    def enqueue_vector(self, address):
        if address in self.traceable_range:
            self.memory.set_vector(address)
            target = self.memory.read_word(address)
            # TODO 0xFFFF can be replaced with a check for is unknown or is
            # start of instruction, since 0xFFFF is the reset vector
            if (target != 0xFFFF) and (target in self.traceable_range):
                self.memory.annotate_jump_target(target)
                self.enqueue_address(target)

    def mark_unknown_memory_as_data(self):
        for address in self.traceable_range:
            if self.memory.is_unknown(address):
                self.memory.set_data(address)

    def annotate_branches(self):
        for address, inst in self.memory.iter_instructions():
            if self.memory.is_branch_taken(address):
                if not self.memory.is_branch_not_taken(address):
                    self.memory.annotate_branch_always_taken(address)

            if self.memory.is_branch_not_taken(address):
                if not self.memory.is_branch_taken(address):
                    self.memory.annotate_branch_never_taken(address)


class TraceQueue(object):
    '''A queue for holding processor states that need to be traced.  States may
    be pushed in any order but are always popped sorted by the program counter.
    A state that was pushed will be ignored if it is pushed again, even if it
    was popped off.'''

    def __init__(self):
        self.untraced_processor_states = SortedSet(key=attrgetter('pc'))
        self.traced_processor_states = set()

    def __len__(self):
        return len(self.untraced_processor_states)

    def push(self, processor_state):
        if processor_state not in self.traced_processor_states:
            if processor_state not in self.untraced_processor_states:
                self.untraced_processor_states.add(processor_state)

    def pop(self):
        if self.untraced_processor_states:
            processor_state = self.untraced_processor_states.pop()
            self.traced_processor_states.add(processor_state)
            return processor_state
        raise KeyError("pop from empty trace queue")


class SortedSet(object):
    '''A set-like object where pop() returns items in sorted order'''

    def __init__(self, items=None, key=None):
        self.items = []            # for ordered retrieval
        self.key = key             # key function for sorting
        if items is not None:
            for item in items:
                self.add(item)

    def __len__(self):
        return len(self.items)

    def __contains__(self, item):
        return item in self.items

    def __iter__(self):
        return iter(self.items)

    def __eq__(self, other):
        return sorted(other) == self.items

    def add(self, item):
        if item not in self.items:
            self.items.append(item)
            self.items.sort(key=self.key)

    def remove(self, item):
        try:
            self.items.remove(item)
        except ValueError:
            raise KeyError(item)

    def pop(self):
        try:
            return self.items.pop(0)
        except IndexError:
            raise KeyError("pop from empty SortedSet")


Unknown = object()


class ProcessorState(object):
    __slots__ = ('pc', 'c', 'n', 'z')

    def __init__(self, pc=Unknown, n=Unknown, z=Unknown, c=Unknown):
        self.pc = pc    # program counter
        self.c = c      # c flag
        self.n = n      # n flag
        self.z = z      # z flag

    def __repr__(self):
        return "<ProcessorState %s>" % str(self)

    def __str__(self):
        pc = "    " if self.pc is Unknown else "%04x" % self.pc
        c = " " if self.c is Unknown else "%d" % self.c
        n = " " if self.n is Unknown else "%d" % self.n
        z = " " if self.z is Unknown else "%d" % self.z
        return "pc=%s c=%s n=%s z=%s" % (pc, c, n, z)

    def __eq__(self, other):
        return ((self.pc, self.c, self.n, self.z) ==
                (other.pc, other.c, other.n, other.z))

    def __hash__(self):
        return hash((self.pc, self.c, self.n, self.z))

    def copy(self):
        return ProcessorState(pc=self.pc, c=self.c, n=self.n, z=self.z)
