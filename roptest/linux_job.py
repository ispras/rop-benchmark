#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Linux job.
"""
from .base_job import BaseJob
from elftools.elf.elffile import ELFFile
from sys import exit


class LinuxJob(BaseJob):

    def __init__(self):
        super().__init__()
        self.vuln_trigger_data[32] = 'a' * 25
        self.vuln_trigger_data[64] = 'a' * 29

    @staticmethod
    def determine_arch(binary):
        with open(binary, "rb") as bin_data:
            elf = ELFFile(bin_data)
            return elf.elfclass

    @staticmethod
    def find_rw_section(binary, section_name=".got.plt"):
        with open(binary, "rb") as bin_data:
            elf = ELFFile(bin_data)
            sec = elf.get_section_by_name(section_name)
            if not sec:
                sec = elf.get_section_by_name(".data")
            addr = sec['sh_addr']
            return addr

    def get_func_addr(self, binary, function_name):
        with open(binary, "rb") as bin_data:
            elf = ELFFile(bin_data)
            sec = elf.get_section_by_name(".symtab")
            if sec is None:
                sec = elf.get_section_by_name(".dynsym")
            symbols_list = sec.get_symbol_by_name(function_name)
            if symbols_list is None:
                self.error("{} not found".format(function_name))
                exit(1)
            symbol = symbols_list[0]
            addr = symbol.entry['st_value']
            self.debug("{} addr: {}".format(function_name, hex(addr)))
            return addr
