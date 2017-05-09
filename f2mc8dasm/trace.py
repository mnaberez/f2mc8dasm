import struct

from f2mc8dasm.tables import FlowTypes


class Tracer(object):
    def __init__(self, rom, entry_points, traceable_range):
        self.rom = rom
        self.traceable_range = traceable_range
        self.queue = TraceQueue()
        for address in entry_points:
            self.add_to_queue(address)

    def trace(self, disassemble_func):
        instructions_by_address = {}
        jump_addresses = set()
        subroutine_addresses = set()

        while self.queue.has_addresses():
            pc = self.queue.pop_address()

            new_pc, inst = disassemble_func(self.rom, pc)
            instructions_by_address[pc] = inst

            if inst.flow_type == FlowTypes.Continue:
                self.add_to_queue(new_pc)
            elif inst.flow_type == FlowTypes.UnconditionalJump:
                jump_addresses.add(inst.address)
                self.add_to_queue(inst.address)
            elif inst.flow_type == FlowTypes.ConditionalJump:
                jump_addresses.add(inst.address)
                self.add_to_queue(inst.address)
                self.add_to_queue(new_pc)
            elif inst.flow_type == FlowTypes.SubroutineCall:
                subroutine_addresses.add(inst.address)
                self.add_to_queue(inst.address)
                self.add_to_queue(new_pc)
            elif inst.flow_type == FlowTypes.IndirectUnconditionalJump:
                vectors = self.try_to_trace_case_idiom(pc)
                for vector in vectors:
                    jump_addresses.add(vector)
                    self.add_to_queue(vector)
            elif inst.flow_type == FlowTypes.IndirectSubroutineCall:
                self.add_to_queue(new_pc)
            elif inst.flow_type == FlowTypes.SubroutineReturn:
                pass
            else:
                raise NotImplementedError()
        return instructions_by_address, jump_addresses, subroutine_addresses

    def try_to_trace_case_idiom(self, address):
        # extract code that may be a case statement idiom
        case_address = address - 12
        table_address = address + 1
        code = list(self.rom[case_address:table_address])

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
            for i in range(0, table_size + 1, 2):
                high = self.rom[table_address + i + 0]
                low  = self.rom[table_address + i + 1]
                vector = (high << 8) + low
                vectors.add(vector)
        return vectors

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
