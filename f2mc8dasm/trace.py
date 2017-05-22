import struct

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

            if not self.memory.is_data(pc, inst_len):
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
            elif inst.flow_type == FlowTypes.IndirectUnconditionalJump:
                for vector in self.parse_vectors_from_case_idiom(pc):
                    self.enqueue_vector(vector)
            elif inst.flow_type == FlowTypes.IndirectSubroutineCall:
                self.enqueue_address(new_pc)
            elif inst.flow_type == FlowTypes.SubroutineReturn:
                pass
            else:
                raise NotImplementedError()

    def enqueue_address(self, address):
        if address in self.traceable_range:
            if self.memory.is_data(address):
                self.queue.push(address)

    def enqueue_vector(self, address):
        self.memory.set_vector(address)
        target = self.memory.read_word(address)
        if (target != 0xFFFF) and (target in self.traceable_range):
            self.memory.annotate_jump_target(target)
            self.enqueue_address(target)

    def parse_vectors_from_case_idiom(self, address):
        # extract code that may be a case statement idiom
        case_address = (address - 12) & 0xFFFF
        table_address = (address + 1) & 0xFFFF
        code = list(self.memory[case_address:table_address])

        # template for case statement idiom
        expected = [0x14, None,         # cmp a, #{table_size}
                    0xf8, None,         # bhs {out_of_range}
                    0x81,               # clrc
                    0x02,               # rol c
                    0xe4, None, None,   # movw a, {vector_table}
                    0x81,               # clrc
                    0x23,               # addcw a
                    0x93,               # movw a, @a
                    0xe0                # jmp @a
                    ]                   # .word addr, .word addr, ...

        # fill in missing values in template
        expected[1], expected[3] = code[1], code[3]
        expected[7], expected[8] = bytearray(struct.pack('>H', table_address))

        # extract vectors from table if the code matched
        vectors = set()
        if expected == code:
            table_size = code[1]
            for offset in range(0, table_size * 2, 2):
                vector = (table_address + offset) & 0xFFFF
                vectors.add(vector)
        return vectors


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
