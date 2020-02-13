#!/usr/bin/python3
# -*- coding: utf-8 -*-
from roptest import get_class_name
from ropium_tool import Ropium


job_class = get_class_name()


class RopchainJob(job_class):

    def __init__(self):
        super().__init__()
        self.script_file = __file__
        self.rop_tool = "ropium"

    def run_rop_tool(self):
        rw_address = self.find_rw_section(self.binary)
        rop_tool = Ropium(self.binary, self.input, self, self.ropchain, rw_address)
        rop_tool.run(self.timeout)


RopchainJob().run()
