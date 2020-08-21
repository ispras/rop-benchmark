#!/usr/bin/python3
# -*- coding: utf-8 -*-
from roptest import get_class_name
from ropper_tool import Ropper


job_class = get_class_name()


class RopchainJob(job_class):

    def __init__(self):
        super().__init__()
        self.script_file = __file__
        self.rop_tool = "ropper"

    def run_rop_tool(self):
        rw_address = self.find_rw_section(self.binary)
        rop_tool = Ropper(self.binary, self.input, self, self.ropchain, self.bad_chars)
        rop_tool.run(self.timeout)


RopchainJob().run()
