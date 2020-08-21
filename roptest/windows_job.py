#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Windows job.
"""
from .base_job import BaseJob


class WindowsJob(BaseJob):

    def __init__(self):
        super().__init__()
        # TODO! when supporting windows define `self.vuln_trigger_data` to trigger vulnerability.
        self.vuln_trigger_data_size[32] = 5
        self.vuln_trigger_data_size[64] = 40

    @staticmethod
    def determine_arch(binary):
        # TODO!
        return NotImplemented

    @staticmethod
    def find_rw_section(binary, section_name=".data"):
        # TODO!
        return NotImplemented

    def get_func_addr(self, binary, function_name):
        # TODO!
        return NotImplemented
