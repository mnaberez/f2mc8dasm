from f2mc8dasm.tables import FlowTypes

class Tracer(object):
    def __init__(self, memory, entry_points, vectors, traceable_range):
        self.memory = memory
        self.traceable_range = traceable_range
        self.queue = TraceQueue()
        for address in entry_points:
            self.enqueue_address(address)
        for address in vectors:
            self.enqueue_vector(address)

    def trace(self, disassemble_func):
        mem_len = len(self.memory)

        while len(self.queue):
            pc = self.queue.pop()

            inst = disassemble_func(self.memory, pc)
            inst_len = len(inst)

            if (pc + inst_len) >= mem_len:
                continue  # ignore instruction that would wrap around memory

            if not self.memory.is_unknown(pc, inst_len):
                continue  # ignore instruction that would overlap another

            self.memory.set_instruction(pc, inst)
            new_pc = (pc + inst_len) & 0xFFFF

            if inst.flow_type == FlowTypes.Continue:
                self.enqueue_address(new_pc)
            elif inst.flow_type == FlowTypes.UnconditionalJump:
                self.memory.annotate_jump_target(inst.address)
                self.enqueue_address(inst.address)
            elif inst.flow_type == FlowTypes.ConditionalJump:
                self.memory.annotate_jump_target(inst.address)
                self.enqueue_address(inst.address)
                self.enqueue_address(new_pc)
            elif inst.flow_type == FlowTypes.SubroutineCall:
                self.memory.annotate_call_target(inst.address)
                self.enqueue_address(inst.address)
                self.enqueue_address(new_pc)
            elif inst.flow_type == FlowTypes.IndirectSubroutineCall:
                self.enqueue_address(new_pc)
            elif inst.flow_type == FlowTypes.IndirectUnconditionalJump:
                pass
            elif inst.flow_type == FlowTypes.SubroutineReturn:
                pass
            else:
                msg = "Unhandled flow type %r at 0x%04x" % (
                    self.memory.types[pc], inst.flow_type)
                raise NotImplementedError(msg) # always a bug

        self.mark_unknown_memory_as_data()

    def enqueue_address(self, address):
        if address in self.traceable_range:
            if self.memory.is_unknown(address):
                self.queue.push(address)

    def enqueue_vector(self, address):
        self.memory.set_vector(address)
        target = self.memory.read_word(address)
        if (target != 0xFFFF) and (target in self.traceable_range):
            self.memory.annotate_jump_target(target)
            self.enqueue_address(target)

    def mark_unknown_memory_as_data(self):
        for address in self.traceable_range:
            if self.memory.is_unknown(address):
                self.memory.set_data(address)


class TraceQueue(object):
    '''A queue for holding addresses that need to be traced.  Addresses may be
    pushed in any order but are always popped in sorted order.  An address that
    was already pushed will be ignored, even if it was popped.'''

    def __init__(self):
        self.untraced_addresses = SortedSet()
        self.traced_addresses = set()

    def __len__(self):
        return len(self.untraced_addresses)

    def push(self, address):
        if address not in self.traced_addresses:
            if address not in self.untraced_addresses:
                self.untraced_addresses.add(address)

    def pop(self):
        if self.untraced_addresses:
            address = self.untraced_addresses.pop()
            self.traced_addresses.add(address)
            return address
        raise KeyError("pop from empty trace queue")


class SortedSet(object):
    '''A set-like object where pop() returns items in sorted order'''

    def __init__(self, items=None):
        self.set_of_items = set()  # for presence
        self.list_of_items = []    # for ordered retrieval
        if items is not None:
            for item in items:
                self.add(item)

    def __len__(self):
        return len(self.set_of_items)

    def __contains__(self, item):
        return item in self.set_of_items

    def __iter__(self):
        return iter(self.list_of_items)

    def __eq__(self, other):
        return other == self.set_of_items

    def add(self, item):
        if item not in self.set_of_items:
            self.set_of_items.add(item)
            self.list_of_items.append(item)
            self.list_of_items.sort()

    def remove(self, item):
        if item not in self.set_of_items:
            raise KeyError(item)
        self.set_of_items.remove(item)
        self.list_of_items.remove(item)

    def pop(self):
        if self.set_of_items:
            item = self.list_of_items.pop(0)
            self.set_of_items.remove(item)
            return item
        else:
            raise KeyError("pop from empty SortedSet")
