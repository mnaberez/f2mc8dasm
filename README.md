# f2mc8dasm

## Overview

f2mc8dasm is a disassembler for Fujitsu F2MC-8 binaries that generates output
compatible with the [asf2mc8](https://shop-pdp.net/ashtml/asf2mc.htm)
assembler.  It can be used to disassemble firmware for many 8-bit Fujitsu
microcontrollers in the F2MC-8L (MB89xxx) and F2MC-8FX (MB95xxx) families.  The
16- and 32-bit F2MC microcontrollers use different instruction sets and
are not supported.

f2mc8dasm was developed for, and successfully used to, disassemble the
firmware of the Volkswagen Premium IV car radios made by Clarion.  These
radios use the Fujitsu MB89625R and MB89677AR microcontrollers, both of which
are the F2MC-8L architecture and have code in mask ROM.

## Features

 - Identical Reassembly.  The assembly language output of f2mc8dasm will
   assemble to a bit-for-bit exact copy of the original binary using
   asf2mc8.  This has been tested using several real firmware binaries and
   by fuzzing.

 - Code / Data Separation.  Starting from the vectors at the top of memory,
   f2mc8dasm uses recursive traversal disassembly to separate code from data.
   This automates much of the disassembly process but indirect jumps (`jmp @a`)
   will still need to be resolved manually.

 - Symbol Generation.  f2mc8dasm tries not to write hardcoded addresses in the
   output when possible.  It will automatically add symbols for hardware
   registers and vectors, other memory locations used, and will add labels for
   branches and subroutines.

## Installation

f2mc8dasm is written in Python and requires Python 3.4 or later.  Packages
are [published](https://pypi.python.org/pypi/f2mc8dasm) on the Python
Package Index (PyPI).  You can download the package from there or use `pip`
to automatically install or upgrade f2mc8dasm:

```
$ pip install -U f2mc8dasm
```

## Usage

f2mc8dasm accepts a plain binary file as input.  The file is assumed to be a
ROM image that should be aligned to the top of memory.  For example, if a
32K file is given, f2mc8dasm will assume the image should be located at
0x8000-0xFFFF.  After loading the image, the disassembler reads the vectors
at 0xFFC0-FFFF and starts tracing instructions from there.

```
$ f2mc8dasm -d mb89670 -o output.asm input.bin
```

Options:

 - `-d` (`--device`) accepts a Fujitsu part number and adds symbols specific
   to the device.  This is especially useful for peripheral registers.  If no
   device is specified, only symbols common to all F2MC-8 devices are used.

 - `-o` (`--outfile`) specifies a file where the asf2mc8-compatible assembly
   output will be written.  If not specified, the assembly will be printed
   to `stdout`.

 - `-h` (`--help`) shows help and describes other options not mentioned here.

## Author

[Mike Naberezny](https://github.com/mnaberez)
