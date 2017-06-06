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
    def __init__(self):
        self.untraced_addresses = set()
        self.traced_addresses = set()

    def __len__(self):
        return len(self.untraced_addresses)

    def push(self, address):
        if address not in self.traced_addresses:
            self.untraced_addresses.add(address)

    def pop(self):
        if self.untraced_addresses:
            address = self.untraced_addresses.pop()
            self.traced_addresses.add(address)
            return address
        raise KeyError("pop from empty trace queue")
