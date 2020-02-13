from sys import exit
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired


class Ropium:

    def __init__(self, binary, input, job, ropchain, rwaddr):
        self.rwaddr = hex(rwaddr)
        self.binary = binary
        self.script = "{}.ropium.script".format(self.binary)
        self.input = input
        self.job = job
        self.logger = job.logger
        self.ropchain = ropchain

    def run(self, timeout):
        from os.path import abspath, dirname, join

        runner = abspath(join(dirname(__file__), "ropium_runner.py"))
        cmd = ["/usr/bin/python3", runner, self.binary, self.ropchain,
               self.script, self.rwaddr]
        self.logger.debug("Run ropium: {}".format(" ".join(cmd)))
        self.logger.debug("ropium rwaddr: {}".format(self.rwaddr))
        process = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)

        try:
            stdout = process.communicate(timeout=timeout)[0]
            self.logger.debug("ropium output:")
            self.logger.debug(stdout.decode(errors='ignore'))
        except TimeoutExpired:
            process.kill()
            self.logger.critical("FAIL TIMEOUT")
            exit(3)

        if process.returncode != 0:
            self.logger.error("Compilation ERROR with {} (ropium)".format(process.returncode))
            exit(1)

