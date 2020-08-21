import sys
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired


class Angrop:

    def __init__(self, binary, input, job, ropchain, bad_chars):
        self.binary = binary
        self.input = input
        self.job = job
        self.logger = job.logger
        self.ropchain = ropchain
        self.bad_chars = bad_chars

    def run(self, timeout):
        from os.path import abspath, dirname, join
        runner = abspath(join(dirname(__file__), "angrop_runner.py"))
        cmd = ["/usr/bin/python3", runner, self.binary, self.ropchain]
        if self.bad_chars:
            cmd += [self.bad_chars]
        self.logger.debug("RUN angrop runner {}".format(" ".join(cmd)))
        process = Popen(cmd, stderr=STDOUT, stdout=PIPE)

        try:
            stdout = process.communicate(timeout=timeout)[0]
            self.logger.debug("angrop runner output:")
            self.logger.debug(stdout.decode(errors='ignore'))
        except TimeoutExpired:
            process.kill()
            self.logger.critical("FAIL TIMEOUT")
            exit(3)

        if process.returncode != 0:
            self.logger.error("Compilation ERROR with {} (angrop)".format(process.returncode))
            exit(1)
