import struct

from f2mc8dasm.memory import LocationAnnotations
from f2mc8dasm.tables import FlowTypes

class Tracer(object):
    def __init__(self, memory, entry_points, traceable_range):
        self.memory = memory
        self.traceable_range = traceable_range
        self.queue = TraceQueue()
        for address in entry_points:
            self.add_to_queue(address)

    def trace(self, disassemble_func):
        while self.queue.has_addresses():
            pc = self.queue.pop_address()

            new_pc, inst = disassemble_func(self.memory, pc)
            self.memory.set_instruction(pc, inst)

            if inst.flow_type == FlowTypes.Continue:
                self.add_to_queue(new_pc)
            elif inst.flow_type == FlowTypes.UnconditionalJump:
                self.memory.set_annotation(inst.address, LocationAnnotations.JumpTarget)
                self.add_to_queue(inst.address)
            elif inst.flow_type == FlowTypes.ConditionalJump:
                self.memory.set_annotation(inst.address, LocationAnnotations.JumpTarget)
                self.add_to_queue(inst.address)
                self.add_to_queue(new_pc)
            elif inst.flow_type == FlowTypes.SubroutineCall:
                self.memory.set_annotation(inst.address, LocationAnnotations.CallTarget)
                self.add_to_queue(inst.address)
                self.add_to_queue(new_pc)
            elif inst.flow_type == FlowTypes.IndirectUnconditionalJump:
                for vector, target in self.try_to_trace_case_idiom(pc).items():
                    self.memory.set_annotation(vector, LocationAnnotations.Vector)
                    self.memory.set_annotation(target, LocationAnnotations.JumpTarget)
                    self.add_to_queue(target)
            elif inst.flow_type == FlowTypes.IndirectSubroutineCall:
                self.add_to_queue(new_pc)
            elif inst.flow_type == FlowTypes.SubroutineReturn:
                pass
            else:
                raise NotImplementedError()

    def try_to_trace_case_idiom(self, address):
        # extract code that may be a case statement idiom
        case_address = address - 12
        table_address = address + 1
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
        targets_by_vector = {}
        if expected == code:
            table_size = code[1]
            for offset in range(0, table_size * 2, 2):
                vector = table_address + offset
                target = struct.unpack('>H', self.memory[vector:vector+2])[0]
                targets_by_vector[vector] = target
        return targets_by_vector

    def add_to_queue(self, address):
        if address in self.traceable_range:
            self.queue.push_address(address)


class TraceQueue(object):
    def __init__(self):
        self.untraced_addresses = set()
        self.traced_addresses = set()

    def has_addresses(self):
        return len(self.untraced_addresses) != 0

    def push_address(self, address):
        if address not in self.traced_addresses:
            self.untraced_addresses.add(address)

    def pop_address(self):
        if self.untraced_addresses:
            address = self.untraced_addresses.pop()
            self.traced_addresses.add(address)
            return address
        return None
