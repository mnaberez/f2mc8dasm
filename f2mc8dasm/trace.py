from f2mc8dasm.tables import FlowTypes

class TraceQueue(object):
    def __init__(self, entry_points, traceable_range):
        self.untraced_addresses = set(entry_points)
        self.traced_addresses = set()
        self.traceable_range = traceable_range

    def has_addresses(self):
        return len(self.untraced_addresses) != 0

    def push_address(self, address):
        if address in self.traceable_range:
            if address not in self.traced_addresses:
                self.untraced_addresses.add(address)

    def pop_address(self):
        if self.untraced_addresses:
            address = self.untraced_addresses.pop()
            self.traced_addresses.add(address)
            return address
        return None

class Tracer(object):
    def __init__(self, rom, queue):
        self.rom = rom
        self.queue = queue

    def trace(self, disassemble_func):
        instructions_by_address = {}
        subroutine_addresses = set()

        while self.queue.has_addresses():
            pc = self.queue.pop_address()

            new_pc, inst = disassemble_func(self.rom, pc)
            instructions_by_address[pc] = inst

            if inst.flow_type == FlowTypes.Continue:
                self.queue.push_address(new_pc)
            elif inst.flow_type == FlowTypes.UnconditionalJump:
                self.queue.push_address(inst.address)
            elif inst.flow_type == FlowTypes.ConditionalJump:
                self.queue.push_address(inst.address)
                self.queue.push_address(new_pc)
            elif inst.flow_type == FlowTypes.SubroutineCall:
                subroutine_addresses.add(inst.address)
                self.queue.push_address(inst.address)
                self.queue.push_address(new_pc)
            elif inst.flow_type == FlowTypes.IndirectUnconditionalJump:
                pass
            elif inst.flow_type == FlowTypes.IndirectSubroutineCall:
                self.queue.push_address(new_pc)
            elif inst.flow_type == FlowTypes.SubroutineReturn:
                pass
            else:
                raise NotImplementedError()

        return instructions_by_address, subroutine_addresses
