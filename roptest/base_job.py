#!/usr/bin/python3
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from os.path import dirname, realpath, exists
from sys import exit
from subprocess import Popen, PIPE, STDOUT


class BaseJob:

    def __init__(self):
        self.script_file = None
        self.vuln_trigger_data = {}
        self.rop_tool = None
        self.script_dir = None
        self.cwd = None
        self.timeout = None
        self.binary = None
        self.ropchain = None
        self.arch = None
        self.vuln = None
        self.input = None
        self.logger = None
        self.vuln_run_output = None
        self.debug = None
        self.info = None
        self.error = None
        self.failure = None
        self.parser = self.create_parser()

    @staticmethod
    def determine_arch(binary):
        """Return arch depending from binary architecture, used as key into `vuln_trigger_data`."""
        # Note: it should be implemented in LinuxJob and WindowsJob
        return NotImplemented

    @staticmethod
    def find_rw_section(binary, section_name=".data"):
        """Return address of rw memory region."""
        # Note: it should be implemented in LinuxJob and WindowsJob
        return NotImplemented

    def get_func_addr(self, binary, function_name):
        """Return `function_name` function address inside `binary`."""
        # Note: it should be implemented in LinuxJob and WindowsJob
        return NotImplemented

    def run(self):
        """Job processing."""
        # Initialization
        parsed_args = self.parser.parse_args()
        self.initialize_parameters(parsed_args)
        self.create_loggers()
        self.print_parameters()

        if not self.check_only:
            # Job specific action
            self.job_specific()

            # Actual run of tool.
            self.run_rop_tool()

        if not exists(self.ropchain):
            self.failure("ERROR (not generated)")
            exit(1)

        # Prepare input date for target test binary.
        self.write_input()

        # Perform 10 functionality tests.
        stable = True
        for _ in range(10):
            # Run test binary.
            self.run_vuln_binary()

            # Check if exploit correctly works.
            if self.check_functionality():
                stable = False
            else:
                if not stable:
                    self.debug("Unstable functionality tests")
                exit(2)

        exit(0)

    @staticmethod
    def create_parser():
        parser = ArgumentParser(description="Rop-benchmark entry point for one test of one tool")
        parser.add_argument("-s", "--script-dir", type=str,
                            help="Path to script hosted directory")
        parser.add_argument("-t", "--timeout", type=int, default=300,
                            help="The number of seconds for timeout test")
        parser.add_argument("binary", type=str,
                            help="Binary for testing")
        parser.add_argument("-c", "--check-only",
                            action='store_true', default=False,
                            help="Only check chain generated previously")
        return parser

    @staticmethod
    def get_script_dir(file):
        return dirname(realpath(file))

    def create_loggers(self):
        """Initialize logging. For every test created separate output file of job run."""
        from logging import getLogger, FileHandler, StreamHandler, Formatter
        from logging import DEBUG, INFO
        logger = getLogger("rop-benchmark:{}:{}".format(self.rop_tool, self.binary))
        logger.setLevel(DEBUG)
        fh = FileHandler('{}.{}.output'.format(self.binary, self.rop_tool), mode='w')
        fh.setLevel(DEBUG)
        ch = StreamHandler()
        ch.setLevel(INFO)
        formatter = Formatter('%(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)
        self.logger = logger
        self.debug = self.logger.debug
        self.info = self.logger.info
        self.error = self.logger.error
        self.failure = self.logger.critical

    def initialize_parameters(self, args):
        from os.path import isabs, relpath
        from os import getcwd
        self.check_only = args.check_only
        self.cwd = getcwd()
        if args.script_dir:
            self.script_dir = args.script_dir
        else:
            self.script_dir = self.get_script_dir(self.script_file)
        self.timeout = args.timeout
        self.binary = relpath(args.binary, self.cwd) \
            if isabs(args.binary) else args.binary
        self.arch = self.determine_arch(self.binary)
        self.input = "{}.{}.input".format(self.binary, self.rop_tool)
        self.ropchain = "{}.{}.ropchain".format(self.binary, self.rop_tool)

    def print_parameters(self):
        self.debug("Run with parameters:")
        self.debug("rop_tool: '{}'".format(self.rop_tool))
        self.debug("binary: '{}'".format(self.binary))
        self.debug("arch: '{}'".format(self.arch))
        self.debug("script_dir: '{}'".format(self.script_dir))
        self.debug("timeout: '{}'".format(self.timeout))
        self.debug("check only {}".format(self.check_only))

    def job_specific(self):
        """Do job specific action."""
        # Note: it may be redefined in some jobs.
        pass

    def run_rop_tool(self, extra_opts=None):
        """Run tool for test binary."""
        # Note: it should be implemented in job runner tool/job_{exploit_type}.py.
        return NotImplemented

    def write_input(self, extra_buf=None):
        """Create input file for test binary."""
        with open(self.input, 'wb') as input_data:
            input_data.write(self.vuln_trigger_data[self.arch].encode('ascii'))
            with open(self.ropchain, 'rb') as ropchain_data:
                input_data.write(ropchain_data.read())
                if extra_buf is not None:
                    input_data.write(extra_buf)

    def run_vuln_binary(self):
        """Run test binary."""
        run_cmd = ["./{}".format(self.binary), self.input]
        self.debug("Run binary: {}".format(" ".join(run_cmd)))
        run = Popen(run_cmd, stdout=PIPE, stderr=STDOUT)
        self.vuln_run_output = run.communicate()[0]

    def get_vuln_output(self):
        output = self.vuln_run_output.decode(errors='ignore')
        self.debug(output)
        return output.splitlines()

    def check_functionality(self):
        """Check if exploit works."""
        output_lines = self.get_vuln_output()
        stripped_lines = [line.strip() for line in output_lines]
        if "SUCCESS" in stripped_lines:
            if "PARAMETERS ARE CORRECT" in stripped_lines:
                self.info("OK")
                return True
            else:
                self.failure("FAIL PARAMS")
                return False
        else:
            self.failure("FAIL HIJACK")
            return False
