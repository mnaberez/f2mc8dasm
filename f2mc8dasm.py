import sys

class AddressModes(object):
    Illegal                   = 0       # 44        .byte 0x44 ;illegal
    Inherent                  = 1       # 00        nop
    ImmediateByte             = 2       # 04 aa     mov a, #0xaa
    ImmediateWord             = 3       # e4 aa bb  movw a, #0xaabb
    Extended                  = 4       # 31 aa bb  call 0xaabb
    Direct                    = 5       # 05 aa     mov a, 0xaa
    DirectWithImmediateByte   = 6       # 85 aa bb  mov 0xaa, #0xbb
    Register                  = 7       # c8        inc r0
    RegisterWithImmediateByte = 8       # 88 aa     mov r0, #0xaa
    Pointer                   = 9       # 07        mov a, @ep
    PointerWithImmediateByte  = 10      # 87 aa     mov @ep, #0xaa
    Index                     = 11      # d6 aa     movw @ix+0xaa, a
    IndexWithImmediateByte    = 12      # 86 aa bb  mov @ix+0xaa, #0xbb
    BitDirect                 = 13      # a0 aa     clrb 0xaa:0
    BitDirectWithRelative     = 14      # b0 aa 05  bbc 0xaa:0, 0xe005
    Relative                  = 15      # fd 05     beq $e005
    Vector                    = 16      # e8        callv #0

InstructionLengths = {
    AddressModes.Illegal:       1,
    AddressModes.Inherent:      1,
    AddressModes.ImmediateByte: 2,
    AddressModes.ImmediateWord: 3,
    AddressModes.Extended:      3,
    AddressModes.Direct:        2,
    AddressModes.DirectWithImmediateByte: 3,
    AddressModes.Register:      1,
    AddressModes.RegisterWithImmediateByte: 2,
    AddressModes.Pointer:       1,
    AddressModes.PointerWithImmediateByte: 2,
    AddressModes.Index:         2,
    AddressModes.IndexWithImmediateByte: 3,
    AddressModes.BitDirect:     2,
    AddressModes.BitDirectWithRelative: 3,
    AddressModes.Relative:      2,
    AddressModes.Vector:        1,
    }


class FlowTypes(object):
    Continue = 0                # nop, mulu a, rol a, ...
    IndirectBranch = 1          # jmp @a, xchw a, pc
    UnconditionalBranch = 2     # jmp
    ConditionalBranch = 3       # beq, bcc, ...
    SubroutineCall = 4          # call
    IndirectSubroutineCall = 5  # callv
    SubroutineReturn = 6        # ret


Opcodes = {
    # 0x00
    0x00: ("nop",                 AddressModes.Inherent,      FlowTypes.Continue),
    0x01: ("mulu a",              AddressModes.Inherent,      FlowTypes.Continue),
    0x02: ("rolc a",              AddressModes.Inherent,      FlowTypes.Continue),
    0x03: ("rorc a",              AddressModes.Inherent,      FlowTypes.Continue),
    0x04: ("mov a, #IMB",         AddressModes.ImmediateByte, FlowTypes.Continue),
    0x05: ("mov a, DIR",          AddressModes.Direct,        FlowTypes.Continue),
    0x06: ("mov a, @ix+IXD",      AddressModes.Index,         FlowTypes.Continue),
    0x07: ("mov a, @ep",          AddressModes.Pointer,       FlowTypes.Continue),
    0x08: ("mov a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x09: ("mov a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x0a: ("mov a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x0b: ("mov a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x0c: ("mov a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x0d: ("mov a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x0e: ("mov a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x0f: ("mov a, rREG",         AddressModes.Register,      FlowTypes.Continue),

    # 0x10
    0x10: ("swap",                AddressModes.Inherent,      FlowTypes.Continue),
    0x11: ("divu a",              AddressModes.Inherent,      FlowTypes.Continue),
    0x12: ("cmp a",               AddressModes.Inherent,      FlowTypes.Continue),
    0x13: ("cmpw a",              AddressModes.Inherent,      FlowTypes.Continue),
    0x14: ("cmp a, #IMB",         AddressModes.ImmediateByte, FlowTypes.Continue),
    0x15: ("cmp a, DIR",          AddressModes.Direct,        FlowTypes.Continue),
    0x16: ("cmp a, @ix+IXD",      AddressModes.Index,         FlowTypes.Continue),
    0x17: ("cmp a, @ep",          AddressModes.Pointer,       FlowTypes.Continue),
    0x18: ("cmp a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x19: ("cmp a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x1a: ("cmp a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x1b: ("cmp a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x1c: ("cmp a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x1d: ("cmp a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x1e: ("cmp a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x1f: ("cmp a, rREG",         AddressModes.Register,      FlowTypes.Continue),

    # 0x20
    0x20: ("ret",                 AddressModes.Inherent,      FlowTypes.SubroutineReturn),
    0x21: ("jmp EXT",             AddressModes.Extended,      FlowTypes.UnconditionalBranch),
    0x22: ("addc a",              AddressModes.Inherent,      FlowTypes.Continue),
    0x23: ("addcw a",             AddressModes.Inherent,      FlowTypes.Continue),
    0x24: ("addc a, #IMB",        AddressModes.ImmediateByte, FlowTypes.Continue),
    0x25: ("addc a, DIR",         AddressModes.Direct,        FlowTypes.Continue),
    0x26: ("addc a, @ix+IXD",     AddressModes.Index,         FlowTypes.Continue),
    0x27: ("addc a, @ep",         AddressModes.Pointer,       FlowTypes.Continue),
    0x28: ("addc a, rREG",        AddressModes.Register,      FlowTypes.Continue),
    0x29: ("addc a, rREG",        AddressModes.Register,      FlowTypes.Continue),
    0x2a: ("addc a, rREG",        AddressModes.Register,      FlowTypes.Continue),
    0x2b: ("addc a, rREG",        AddressModes.Register,      FlowTypes.Continue),
    0x2c: ("addc a, rREG",        AddressModes.Register,      FlowTypes.Continue),
    0x2d: ("addc a, rREG",        AddressModes.Register,      FlowTypes.Continue),
    0x2e: ("addc a, rREG",        AddressModes.Register,      FlowTypes.Continue),
    0x2f: ("addc a, rREG",        AddressModes.Register,      FlowTypes.Continue),

    # 0x30
    0x30: ("reti",                AddressModes.Inherent,      FlowTypes.SubroutineReturn),
    0x31: ("call EXT",            AddressModes.Extended,      FlowTypes.SubroutineCall),
    0x32: ("subc a",              AddressModes.Inherent,      FlowTypes.Continue),
    0x33: ("subcw a",             AddressModes.Inherent,      FlowTypes.Continue),
    0x34: ("subc a, #IMB",        AddressModes.ImmediateByte, FlowTypes.Continue),
    0x35: ("subc a, DIR",         AddressModes.Direct,        FlowTypes.Continue),
    0x36: ("subc a, @ix+IXD",     AddressModes.Index,         FlowTypes.Continue),
    0x37: ("subc a, @ep",         AddressModes.Pointer,       FlowTypes.Continue),
    0x38: ("subc a, rREG",        AddressModes.Register,      FlowTypes.Continue),
    0x39: ("subc a, rREG",        AddressModes.Register,      FlowTypes.Continue),
    0x3a: ("subc a, rREG",        AddressModes.Register,      FlowTypes.Continue),
    0x3b: ("subc a, rREG",        AddressModes.Register,      FlowTypes.Continue),
    0x3c: ("subc a, rREG",        AddressModes.Register,      FlowTypes.Continue),
    0x3d: ("subc a, rREG",        AddressModes.Register,      FlowTypes.Continue),
    0x3e: ("subc a, rREG",        AddressModes.Register,      FlowTypes.Continue),
    0x3f: ("subc a, rREG",        AddressModes.Register,      FlowTypes.Continue),

    # 0x40
    0x40: ("pushw a",             AddressModes.Inherent,      FlowTypes.Continue),
    0x41: ("pushw ix",            AddressModes.Inherent,      FlowTypes.Continue),
    0x42: ("xch a, t",            AddressModes.Inherent,      FlowTypes.Continue),
    0x43: ("xchw a, t",           AddressModes.Inherent,      FlowTypes.Continue),
    0x44: (".byte OPC",           AddressModes.Illegal,       FlowTypes.Continue),
    0x45: ("mov DIR, a",          AddressModes.Direct,        FlowTypes.Continue),
    0x46: ("mov @ix+IXD, a",      AddressModes.Index,         FlowTypes.Continue),
    0x47: ("mov @ep, a",          AddressModes.Pointer,       FlowTypes.Continue),
    0x48: ("mov r0, a",           AddressModes.Register,      FlowTypes.Continue),
    0x49: ("mov r1, a",           AddressModes.Register,      FlowTypes.Continue),
    0x4a: ("mov r2, a",           AddressModes.Register,      FlowTypes.Continue),
    0x4b: ("mov r3, a",           AddressModes.Register,      FlowTypes.Continue),
    0x4c: ("mov r4, a",           AddressModes.Register,      FlowTypes.Continue),
    0x4d: ("mov r5, a",           AddressModes.Register,      FlowTypes.Continue),
    0x4e: ("mov r6, a",           AddressModes.Register,      FlowTypes.Continue),
    0x4f: ("mov r7, a",           AddressModes.Register,      FlowTypes.Continue),

    # 0x50
    0x50: ("popw a",              AddressModes.Inherent,      FlowTypes.Continue),
    0x51: ("popw ix",             AddressModes.Inherent,      FlowTypes.Continue),
    0x52: ("xor a",               AddressModes.Inherent,      FlowTypes.Continue),
    0x53: ("xorw a",              AddressModes.Inherent,      FlowTypes.Continue),
    0x54: ("xor a, #IMB",         AddressModes.ImmediateByte, FlowTypes.Continue),
    0x55: ("xor a, DIR",          AddressModes.Direct,        FlowTypes.Continue),
    0x56: ("xor a, @ix+IXD",      AddressModes.Index,         FlowTypes.Continue),
    0x57: ("xor a, @ep",          AddressModes.Pointer,       FlowTypes.Continue),
    0x58: ("xor a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x59: ("xor a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x5a: ("xor a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x5b: ("xor a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x5c: ("xor a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x5d: ("xor a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x5e: ("xor a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x5f: ("xor a, rREG",         AddressModes.Register,      FlowTypes.Continue),

    # 0x60
    0x60: ("mov a, EXT",          AddressModes.Extended,      FlowTypes.Continue),
    0x61: ("mov EXT, a",          AddressModes.Extended,      FlowTypes.Continue),
    0x62: ("and a",               AddressModes.Inherent,      FlowTypes.Continue),
    0x63: ("andw a",              AddressModes.Inherent,      FlowTypes.Continue),
    0x64: ("and a, #IMB",         AddressModes.ImmediateByte, FlowTypes.Continue),
    0x65: ("and a, DIR",          AddressModes.Direct,        FlowTypes.Continue),
    0x66: ("and a, @ix+IXD",      AddressModes.Index,         FlowTypes.Continue),
    0x67: ("and a, @ep",          AddressModes.Pointer,       FlowTypes.Continue),
    0x68: ("and a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x69: ("and a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x6a: ("and a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x6b: ("and a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x6c: ("and a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x6d: ("and a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x6e: ("and a, rREG",         AddressModes.Register,      FlowTypes.Continue),
    0x6f: ("and a, rREG",         AddressModes.Register,      FlowTypes.Continue),

    # 0x70
    0x70: ("movw a, ps",          AddressModes.Inherent,      FlowTypes.Continue),
    0x71: ("movw ps, a",          AddressModes.Inherent,      FlowTypes.Continue),
    0x72: ("or a",                AddressModes.Inherent,      FlowTypes.Continue),
    0x73: ("orw a",               AddressModes.Inherent,      FlowTypes.Continue),
    0x74: ("or a, #IMB",          AddressModes.ImmediateByte, FlowTypes.Continue),
    0x75: ("or a, DIR",           AddressModes.Direct,        FlowTypes.Continue),
    0x76: ("or a, @ix+IXD",       AddressModes.Index,         FlowTypes.Continue),
    0x77: ("or a, @ep",           AddressModes.Pointer,       FlowTypes.Continue),
    0x78: ("or a, rREG",          AddressModes.Register,      FlowTypes.Continue),
    0x79: ("or a, rREG",          AddressModes.Register,      FlowTypes.Continue),
    0x7a: ("or a, rREG",          AddressModes.Register,      FlowTypes.Continue),
    0x7b: ("or a, rREG",          AddressModes.Register,      FlowTypes.Continue),
    0x7c: ("or a, rREG",          AddressModes.Register,      FlowTypes.Continue),
    0x7d: ("or a, rREG",          AddressModes.Register,      FlowTypes.Continue),
    0x7e: ("or a, rREG",          AddressModes.Register,      FlowTypes.Continue),
    0x7f: ("or a, rREG",          AddressModes.Register,      FlowTypes.Continue),

    # 0x80
    0x80: ("clri",                AddressModes.Inherent,                    FlowTypes.Continue),
    0x81: ("clrc",                AddressModes.Inherent,                    FlowTypes.Continue),
    0x82: ("mov @a, t",           AddressModes.Inherent,                    FlowTypes.Continue),
    0x83: ("movw @a, t",          AddressModes.Inherent,                    FlowTypes.Continue),
    0x84: ("daa",                 AddressModes.Inherent,                    FlowTypes.Continue),
    0x85: ("mov DIR, #IMB",       AddressModes.DirectWithImmediateByte,     FlowTypes.Continue),
    0x86: ("mov @ix+IXD, #IMB",   AddressModes.IndexWithImmediateByte,      FlowTypes.Continue),
    0x87: ("mov @ep, #IMB",       AddressModes.PointerWithImmediateByte,    FlowTypes.Continue),
    0x88: ("mov rREG, #IMB",      AddressModes.RegisterWithImmediateByte,   FlowTypes.Continue),
    0x89: ("mov rREG, #IMB",      AddressModes.RegisterWithImmediateByte,   FlowTypes.Continue),
    0x8a: ("mov rREG, #IMB",      AddressModes.RegisterWithImmediateByte,   FlowTypes.Continue),
    0x8b: ("mov rREG, #IMB",      AddressModes.RegisterWithImmediateByte,   FlowTypes.Continue),
    0x8c: ("mov rREG, #IMB",      AddressModes.RegisterWithImmediateByte,   FlowTypes.Continue),
    0x8d: ("mov rREG, #IMB",      AddressModes.RegisterWithImmediateByte,   FlowTypes.Continue),
    0x8e: ("mov rREG, #IMB",      AddressModes.RegisterWithImmediateByte,   FlowTypes.Continue),
    0x8f: ("mov rREG, #IMB",      AddressModes.RegisterWithImmediateByte,   FlowTypes.Continue),

    # 0x90
    0x90: ("seti",                AddressModes.Inherent,                    FlowTypes.Continue),
    0x91: ("setc",                AddressModes.Inherent,                    FlowTypes.Continue),
    0x92: ("mov a, @a",           AddressModes.Inherent,                    FlowTypes.Continue),
    0x93: ("movw a, @a",          AddressModes.Inherent,                    FlowTypes.Continue),
    0x94: ("das",                 AddressModes.Inherent,                    FlowTypes.Continue),
    0x95: ("cmp DIR, #IMB",       AddressModes.DirectWithImmediateByte,     FlowTypes.Continue),
    0x96: ("cmp @ix+IXD, #IMB",   AddressModes.IndexWithImmediateByte,      FlowTypes.Continue),
    0x97: ("cmp @ep, #IMB",       AddressModes.PointerWithImmediateByte,    FlowTypes.Continue),
    0x98: ("cmp rREG, #IMB",      AddressModes.RegisterWithImmediateByte,   FlowTypes.Continue),
    0x99: ("cmp rREG, #IMB",      AddressModes.RegisterWithImmediateByte,   FlowTypes.Continue),
    0x9a: ("cmp rREG, #IMB",      AddressModes.RegisterWithImmediateByte,   FlowTypes.Continue),
    0x9b: ("cmp rREG, #IMB",      AddressModes.RegisterWithImmediateByte,   FlowTypes.Continue),
    0x9c: ("cmp rREG, #IMB",      AddressModes.RegisterWithImmediateByte,   FlowTypes.Continue),
    0x9d: ("cmp rREG, #IMB",      AddressModes.RegisterWithImmediateByte,   FlowTypes.Continue),
    0x9e: ("cmp rREG, #IMB",      AddressModes.RegisterWithImmediateByte,   FlowTypes.Continue),
    0x9f: ("cmp rREG, #IMB",      AddressModes.RegisterWithImmediateByte,   FlowTypes.Continue),

    # 0xa0
    0xa0: ("clrb DIR:BIT",        AddressModes.BitDirect,      FlowTypes.Continue),
    0xa1: ("clrb DIR:BIT",        AddressModes.BitDirect,      FlowTypes.Continue),
    0xa2: ("clrb DIR:BIT",        AddressModes.BitDirect,      FlowTypes.Continue),
    0xa3: ("clrb DIR:BIT",        AddressModes.BitDirect,      FlowTypes.Continue),
    0xa4: ("clrb DIR:BIT",        AddressModes.BitDirect,      FlowTypes.Continue),
    0xa5: ("clrb DIR:BIT",        AddressModes.BitDirect,      FlowTypes.Continue),
    0xa6: ("clrb DIR:BIT",        AddressModes.BitDirect,      FlowTypes.Continue),
    0xa7: ("clrb DIR:BIT",        AddressModes.BitDirect,      FlowTypes.Continue),
    0xa8: ("setb DIR:BIT",        AddressModes.BitDirect,      FlowTypes.Continue),
    0xa9: ("setb DIR:BIT",        AddressModes.BitDirect,      FlowTypes.Continue),
    0xaa: ("setb DIR:BIT",        AddressModes.BitDirect,      FlowTypes.Continue),
    0xab: ("setb DIR:BIT",        AddressModes.BitDirect,      FlowTypes.Continue),
    0xac: ("setb DIR:BIT",        AddressModes.BitDirect,      FlowTypes.Continue),
    0xad: ("setb DIR:BIT",        AddressModes.BitDirect,      FlowTypes.Continue),
    0xae: ("setb DIR:BIT",        AddressModes.BitDirect,      FlowTypes.Continue),
    0xaf: ("setb DIR:BIT",        AddressModes.BitDirect,      FlowTypes.Continue),

    # 0xb0
    0xb0: ("bbc DIR:BIT,REL",     AddressModes.BitDirectWithRelative,   FlowTypes.ConditionalBranch),
    0xb1: ("bbc DIR:BIT,REL",     AddressModes.BitDirectWithRelative,   FlowTypes.ConditionalBranch),
    0xb2: ("bbc DIR:BIT,REL",     AddressModes.BitDirectWithRelative,   FlowTypes.ConditionalBranch),
    0xb3: ("bbc DIR:BIT,REL",     AddressModes.BitDirectWithRelative,   FlowTypes.ConditionalBranch),
    0xb4: ("bbc DIR:BIT,REL",     AddressModes.BitDirectWithRelative,   FlowTypes.ConditionalBranch),
    0xb5: ("bbc DIR:BIT,REL",     AddressModes.BitDirectWithRelative,   FlowTypes.ConditionalBranch),
    0xb6: ("bbc DIR:BIT,REL",     AddressModes.BitDirectWithRelative,   FlowTypes.ConditionalBranch),
    0xb7: ("bbc DIR:BIT,REL",     AddressModes.BitDirectWithRelative,   FlowTypes.ConditionalBranch),
    0xb8: ("bbs DIR:BIT,REL",     AddressModes.BitDirectWithRelative,   FlowTypes.ConditionalBranch),
    0xb9: ("bbs DIR:BIT,REL",     AddressModes.BitDirectWithRelative,   FlowTypes.ConditionalBranch),
    0xba: ("bbs DIR:BIT,REL",     AddressModes.BitDirectWithRelative,   FlowTypes.ConditionalBranch),
    0xbb: ("bbs DIR:BIT,REL",     AddressModes.BitDirectWithRelative,   FlowTypes.ConditionalBranch),
    0xbc: ("bbs DIR:BIT,REL",     AddressModes.BitDirectWithRelative,   FlowTypes.ConditionalBranch),
    0xbd: ("bbs DIR:BIT,REL",     AddressModes.BitDirectWithRelative,   FlowTypes.ConditionalBranch),
    0xbe: ("bbs DIR:BIT,REL",     AddressModes.BitDirectWithRelative,   FlowTypes.ConditionalBranch),
    0xbf: ("bbs DIR:BIT,REL",     AddressModes.BitDirectWithRelative,   FlowTypes.ConditionalBranch),

    # 0xc0
    0xc0: ("incw a",              AddressModes.Inherent,    FlowTypes.Continue),
    0xc1: ("incw sp",             AddressModes.Inherent,    FlowTypes.Continue),
    0xc2: ("incw ix",             AddressModes.Inherent,    FlowTypes.Continue),
    0xc3: ("incw ep",             AddressModes.Inherent,    FlowTypes.Continue),
    0xc4: ("movw a, EXT",         AddressModes.Extended,    FlowTypes.Continue),
    0xc5: ("movw a, DIR",         AddressModes.Direct,      FlowTypes.Continue),
    0xc6: ("movw a, @ix+IXD",     AddressModes.Index,       FlowTypes.Continue),
    0xc7: ("movw a, @ep",         AddressModes.Inherent,    FlowTypes.Continue),
    0xc8: ("inc rREG",            AddressModes.Register,    FlowTypes.Continue),
    0xc9: ("inc rREG",            AddressModes.Register,    FlowTypes.Continue),
    0xca: ("inc rREG",            AddressModes.Register,    FlowTypes.Continue),
    0xcb: ("inc rREG",            AddressModes.Register,    FlowTypes.Continue),
    0xcc: ("inc rREG",            AddressModes.Register,    FlowTypes.Continue),
    0xcd: ("inc rREG",            AddressModes.Register,    FlowTypes.Continue),
    0xce: ("inc rREG",            AddressModes.Register,    FlowTypes.Continue),
    0xcf: ("inc rREG",            AddressModes.Register,    FlowTypes.Continue),

    # 0xd0
    0xd0: ("decw a",              AddressModes.Inherent,    FlowTypes.Continue),
    0xd1: ("decw sp",             AddressModes.Inherent,    FlowTypes.Continue),
    0xd2: ("decw ix",             AddressModes.Inherent,    FlowTypes.Continue),
    0xd3: ("decw ep",             AddressModes.Inherent,    FlowTypes.Continue),
    0xd4: ("movw EXT, a",         AddressModes.Extended,    FlowTypes.Continue),
    0xd5: ("movw DIR, a",         AddressModes.Direct,      FlowTypes.Continue),
    0xd6: ("movw @ix+IXD, a",     AddressModes.Index,       FlowTypes.Continue),
    0xd7: ("movw @ep, a",         AddressModes.Pointer,     FlowTypes.Continue),
    0xd8: ("dec rREG",            AddressModes.Register,    FlowTypes.Continue),
    0xd9: ("dec rREG",            AddressModes.Register,    FlowTypes.Continue),
    0xda: ("dec rREG",            AddressModes.Register,    FlowTypes.Continue),
    0xdb: ("dec rREG",            AddressModes.Register,    FlowTypes.Continue),
    0xdc: ("dec rREG",            AddressModes.Register,    FlowTypes.Continue),
    0xdd: ("dec rREG",            AddressModes.Register,    FlowTypes.Continue),
    0xde: ("dec rREG",            AddressModes.Register,    FlowTypes.Continue),
    0xdf: ("dec rREG",            AddressModes.Register,    FlowTypes.Continue),

    # 0xe0
    0xe0: ("jmp @a",              AddressModes.Inherent,        FlowTypes.IndirectBranch),
    0xe1: ("movw sp, a",          AddressModes.Inherent,        FlowTypes.Continue),
    0xe2: ("movw ix, a",          AddressModes.Inherent,        FlowTypes.Continue),
    0xe3: ("movw ep, a",          AddressModes.Inherent,        FlowTypes.Continue),
    0xe4: ("movw a, #IMW",        AddressModes.ImmediateWord,   FlowTypes.Continue),
    0xe5: ("movw sp, #IMW",       AddressModes.ImmediateWord,   FlowTypes.Continue),
    0xe6: ("movw ix, #IMW",       AddressModes.ImmediateWord,   FlowTypes.Continue),
    0xe7: ("movw ep, #IMW",       AddressModes.ImmediateWord,   FlowTypes.Continue),
    0xe8: ("callv #VEC",          AddressModes.Vector,          FlowTypes.IndirectSubroutineCall),
    0xe9: ("callv #VEC",          AddressModes.Vector,          FlowTypes.IndirectSubroutineCall),
    0xea: ("callv #VEC",          AddressModes.Vector,          FlowTypes.IndirectSubroutineCall),
    0xeb: ("callv #VEC",          AddressModes.Vector,          FlowTypes.IndirectSubroutineCall),
    0xec: ("callv #VEC",          AddressModes.Vector,          FlowTypes.IndirectSubroutineCall),
    0xed: ("callv #VEC",          AddressModes.Vector,          FlowTypes.IndirectSubroutineCall),
    0xee: ("callv #VEC",          AddressModes.Vector,          FlowTypes.IndirectSubroutineCall),
    0xef: ("callv #VEC",          AddressModes.Vector,          FlowTypes.IndirectSubroutineCall),

    # 0xf0
    0xf0: ("movw a, pc",          AddressModes.Inherent,    FlowTypes.Continue),
    0xf1: ("movw a, sp",          AddressModes.Inherent,    FlowTypes.Continue),
    0xf2: ("movw a, ix",          AddressModes.Inherent,    FlowTypes.Continue),
    0xf3: ("movw a, ep",          AddressModes.Inherent,    FlowTypes.Continue),
    0xf4: ("xchw a, pc",          AddressModes.Inherent,    FlowTypes.IndirectBranch),
    0xf5: ("xchw a, sp",          AddressModes.Inherent,    FlowTypes.Continue),
    0xf6: ("xchw a, ix",          AddressModes.Inherent,    FlowTypes.Continue),
    0xf7: ("xchw a, ep",          AddressModes.Inherent,    FlowTypes.Continue),
    0xf8: ("bhs REL",             AddressModes.Relative,    FlowTypes.ConditionalBranch),
    0xf9: ("blo REL",             AddressModes.Relative,    FlowTypes.ConditionalBranch),
    0xfa: ("bp REL",              AddressModes.Relative,    FlowTypes.ConditionalBranch),
    0xfb: ("bn REL",              AddressModes.Relative,    FlowTypes.ConditionalBranch),
    0xfc: ("bne REL",             AddressModes.Relative,    FlowTypes.ConditionalBranch),
    0xfd: ("beq REL",             AddressModes.Relative,    FlowTypes.ConditionalBranch),
    0xfe: ("bge REL",             AddressModes.Relative,    FlowTypes.ConditionalBranch),
    0xff: ("blt REL",             AddressModes.Relative,    FlowTypes.ConditionalBranch),
    }


class Instruction(object):
    disasm_as_bytes = False  # instruction requires bytes-only disassembly
                             # output to reassamble identically on asf2mc8
    disasm_template = '' # "cmp @ix+IXD, #IMB"
    addr_mode = None     # addressing mode
    flow_type = None     # type of instruction for flow tracing
    opcode = None        # opcode byte
    operands = ()        # operand bytes
    address = None       # address (0-0xFF for direct, 0-0xFFFF for others)
    immediate = None     # immediate value (byte or word)
    ixd_offset = None    # IXD offset 0-0xFF
    bit = None           # bit 0-7
    callv = None         # callv 0-7
    register = None      # register r0-r7

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise KeyError(k)

    @property
    def all_bytes(self):
        return [self.opcode] + list(self.operands)

    def __str__(self):
        d = {}
        d['OPC'] = '0x%02x' % self.opcode
        if self.immediate is not None:
            d['IMB'] = '0x%02x' % self.immediate
        if self.immediate is not None:
            d['IMW'] = '0x%04x' % self.immediate
        if self.address is not None:
            d['DIR'] = '0x%02x' % self.address
        if self.address is not None:
            d['EXT'] = '0x%04x' % self.address
        if self.ixd_offset is not None:
            d['IXD'] = '0x%02x' % self.ixd_offset
        if self.address is not None:
            d['REL'] = '0x%04x' % self.address
        if self.callv is not None:
            d['VEC'] = '%d' % self.callv
        if self.bit is not None:
            d['BIT'] = '%d' % self.bit
        if self.register is not None:
            d['REG'] = '%d' % self.register
        disasm = self.disasm_template
        for k, v in d.items():
            disasm = disasm.replace(k, v)
        return disasm


def resolve_rel(pc, displacement):
    if displacement & 0x80:
        displacement = -((displacement ^ 0xff) + 1)
    return pc + displacement


def disassemble_inst(rom, pc):
    opcode = rom[pc]
    pc += 1
    disasm_template, addr_mode, flow_type = Opcodes[opcode]

    instlen = InstructionLengths[addr_mode]
    operands = bytearray()
    for i in range(instlen - 1):
        operands.append(rom[pc])
        pc +=1

    inst = Instruction()
    inst.opcode = opcode
    inst.operands = operands
    inst.disasm_template = disasm_template
    inst.addr_mode = addr_mode
    inst.flow_type = flow_type

    if addr_mode == AddressModes.Illegal:
        pass
    elif addr_mode == AddressModes.Inherent:
        pass
    elif addr_mode == AddressModes.ImmediateWord:
        inst.immediate = (operands[0] << 8) + operands[1]
    elif addr_mode == AddressModes.ImmediateByte:
        inst.immediate = operands[0]
    elif addr_mode == AddressModes.Extended:
        high_byte, low_byte = operands
        word = (high_byte << 8) + low_byte
        inst.address = word
        inst.disasm_as_bytes = (high_byte == 0)
    elif addr_mode == AddressModes.Direct:
        inst.address = operands[0]
    elif addr_mode == AddressModes.DirectWithImmediateByte:
        inst.address = operands[0]
        inst.immediate = operands[1]
    elif addr_mode == AddressModes.Register:
        inst.register = opcode & 0b111
    elif addr_mode == AddressModes.RegisterWithImmediateByte:
        inst.register = opcode & 0b111
        inst.immediate = operands[0]
    elif addr_mode == AddressModes.Pointer:
        pass
    elif addr_mode == AddressModes.PointerWithImmediateByte:
        inst.immediate = operands[0]
    elif addr_mode == AddressModes.Index:
        inst.ixd_offset = operands[0]
    elif addr_mode == AddressModes.IndexWithImmediateByte:
        inst.ixd_offset = operands[0]
        inst.immediate = operands[1]
    elif addr_mode == AddressModes.Vector:
        inst.callv = opcode & 0b111
    elif addr_mode == AddressModes.BitDirect:
        inst.bit = opcode & 0b111
        inst.address = operands[0]
    elif addr_mode == AddressModes.Relative:
        inst.address = resolve_rel(pc, operands[0])
        inst.disasm_as_bytes = True
    elif addr_mode == AddressModes.BitDirectWithRelative:
        inst.bit = opcode & 0b111
        inst.address = resolve_rel(pc, operands[0])
        inst.disasm_as_bytes = True
    else:
        raise NotImplementedError()

    return pc, inst


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


def main():
    with open(sys.argv[1], 'rb') as f:
        rom = bytearray(0xe000) + bytearray(f.read())

    queue = TraceQueue([
        # reset
        0xE012,
        # callv, irq vectors
        0xE0CB, 0xE0DD, 0xE0EF, 0xE163, 0xE175, 0xE187, 0xE012, 0xE199,
        # jmp @
        0xE63F, 0xE726, 0xE791, 0xE961, 0xEA21, 0xEA9F, 0xEBA8, 0xEC42, 0xEC80
        ],
        range(0xe000, 0x10000)
        )
    instructions_by_address = {}
    subroutine_addresses = set()

    while queue.has_addresses():
        pc = queue.pop_address()

        new_pc, inst = disassemble_inst(rom, pc)
        instructions_by_address[pc] = inst

        if inst.flow_type == FlowTypes.Continue:
            queue.push_address(new_pc)
        elif inst.flow_type == FlowTypes.UnconditionalBranch:
            queue.push_address(inst.address)
        elif inst.flow_type == FlowTypes.ConditionalBranch:
            queue.push_address(inst.address)
            queue.push_address(new_pc)
        elif inst.flow_type == FlowTypes.SubroutineCall:
            subroutine_addresses.add(inst.address)
            queue.push_address(inst.address)
            queue.push_address(new_pc)
        elif inst.flow_type == FlowTypes.IndirectBranch:
            pass
        elif inst.flow_type == FlowTypes.IndirectSubroutineCall:
            queue.push_address(new_pc)
        elif inst.flow_type == FlowTypes.SubroutineReturn:
            pass

    print('    .F2MC8L')
    print('    .area CODE1 (ABS)')
    print('    .org 0xe000\n')

    last_line_code = True
    pc = 0xe000
    while pc < 0x10000:
        inst = instructions_by_address.get(pc)
        if inst is None:
            if last_line_code:
                print('')
            last_line_code = False

            _, inst = disassemble_inst(rom, pc) # disassemble data as code

            print('    ' +
                    ('.byte 0x%02X' % rom[pc]).ljust(24) +
                    (';DATA  0x%04x  %02x %r ' % (pc, rom[pc], chr(rom[pc]))).ljust(26) +
                    ('(%s)' % (inst)))
            pc += 1
        else:
            if not last_line_code:
                print('')
            last_line_code = True

            if pc in subroutine_addresses:
                print("\nsub_%04x:" % pc)

            disasm = str(inst)
            hexdump = (' '.join([ '%02x' % h for h in inst.all_bytes ])).ljust(8)

            line = '    ' + disasm.ljust(24) + ';0x%04x  %s' % (pc, hexdump)
            print(line)
            pc += len(inst.all_bytes)


if __name__ == '__main__':
    main()
