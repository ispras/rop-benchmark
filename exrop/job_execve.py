#!/usr/bin/python3
# -*- coding: utf-8 -*-
from roptest import get_class_name
from exrop_tool import Exrop


job_class = get_class_name()


class RopchainJob(job_class):

    def __init__(self):
        super().__init__()
        self.script_file = __file__
        self.rop_tool = "exrop"

    def run_rop_tool(self):
        rop_tool = Exrop(self.binary, self.input, self, self.ropchain)
        rop_tool.run(self.timeout)


RopchainJob().run()
