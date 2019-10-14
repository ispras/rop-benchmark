#!/usr/bin/python3
# -*- coding: utf-8 -*-
from roptest import get_class_name
from ropgenerator import Ropgenerator


job_class = get_class_name()


class RopchainJob(job_class):

    def __init__(self):
        super().__init__()
        self.script_file = __file__
        self.rop_tool = "ropgenerator"

    def run_rop_tool(self):
        rw_address = self.find_rw_section(self.binary)
        commands = ("load -r '--depth 15' {}\n"
                    "exploit\n"
                    'syscall -c LINUX execve("/bin/sh\\x00", 0, 0) -f python '
                    "-rw {},{}\n").format(self.binary, hex(rw_address), hex(rw_address + 1000))
        rop_tool = Ropgenerator(self.binary, self.input, self, self.ropchain, commands)
        rop_tool.run(self.timeout)


RopchainJob().run()
