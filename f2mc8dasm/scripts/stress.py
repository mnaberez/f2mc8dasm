'''
Perform a stress test on f2mc8dasm.  Continuously generates random data,
disassembles it, and reassembles it with asf2mc8.  Halts only if the
reassembled file is not identical to the original binary data.

Usage: python stress.py
'''

import os
import random
import subprocess

def run(command):
    print(command)
    subprocess.check_call(command, shell=True)

def main():
    dirname = os.path.abspath(os.path.dirname(__file__))
    os.chdir(dirname)
    try:
        while True:
            size = random.randint(0x100, 0x10000-0x100)
            data = os.urandom(size)
            with open('original.bin', 'wb') as f:
                f.write(data)
            print("\nWrote %d random bytes to original.bin" % size)

            run('rm -f disasm.*')
            run('f2mc8dasm original.bin > disasm.asm')
            run('asf2mc8 -l disasm.asm')
            run('python lst2bin.py disasm.lst disasm.bin')

            with open('disasm.bin', 'rb') as f:
                assert data == f.read()
                print("OK")
    except:
        print("\nFiles were left in: %s\n" % dirname)

if __name__ == '__main__':
    main()
