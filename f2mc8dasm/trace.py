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
        subroutine_addresses = set()

        while self.queue.has_addresses():
            pc = self.queue.pop_address()

            new_pc, inst = disassemble_func(self.rom, pc)
            instructions_by_address[pc] = inst

            if inst.flow_type == FlowTypes.Continue:
                self.add_to_queue(new_pc)
            elif inst.flow_type == FlowTypes.UnconditionalJump:
                self.add_to_queue(inst.address)
            elif inst.flow_type == FlowTypes.ConditionalJump:
                self.add_to_queue(inst.address)
                self.add_to_queue(new_pc)
            elif inst.flow_type == FlowTypes.SubroutineCall:
                subroutine_addresses.add(inst.address)
                self.add_to_queue(inst.address)
                self.add_to_queue(new_pc)
            elif inst.flow_type == FlowTypes.IndirectUnconditionalJump:
                pass
            elif inst.flow_type == FlowTypes.IndirectSubroutineCall:
                self.add_to_queue(new_pc)
            elif inst.flow_type == FlowTypes.SubroutineReturn:
                pass
            else:
                raise NotImplementedError()

        return instructions_by_address, subroutine_addresses

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
