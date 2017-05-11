
class Memory(object):
    def __init__(self, rom):
        self.contents = bytearray(0x10000 - len(rom)) + bytearray(rom)
        self.instructions = {}
        self.types = {}
        self.annotations = {}

        for address in range(len(self.contents)):
            self.instructions[address] = None
            self.types[address] = LocationTypes.Data
            self.annotations[address] = LocationAnnotations.Unknown

    def __getitem__(self, address):
        ifnone = lambda a, b: b if a is None else a
        if isinstance(address, slice):
            l = list(range(ifnone(address.start, 0), address.stop, ifnone(address.step, 1)))
            return bytearray([self.contents[x] for x in l])
        return self.contents[address]

    def __len__(self):
        return len(self.contents)

    def set_instruction(self, address, inst):
        self.instructions[address] = inst
        for i in range(len(inst)):
            if i == 0:
                loc_type = LocationTypes.InstructionStart
            else:
                loc_type = LocationTypes.InstructionContinuation
            self.types[address + i] = loc_type

    def get_instruction(self, address):
        return self.instructions[address]

    def iter_instructions(self, address=0):
        for a in range(address, len(self.contents)):
            if self.types[a] == LocationTypes.InstructionStart:
                yield self.instructions[a]

    def get_type(self, address):
        return self.types[address]

    def set_annotation(self, address, loc_anno):
        self.annotations[address] = loc_anno

    def get_annotation(self, address):
        return self.annotations[address]

class LocationTypes(object):
    Data = 0
    InstructionStart = 1
    InstructionContinuation = 2

class LocationAnnotations(object):
    Unknown = 0
    JumpTarget = 1
    CallTarget = 2
    Vector = 3
