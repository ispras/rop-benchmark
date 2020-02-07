import sys
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired


class Exrop:

    def __init__(self, binary, input, job, ropchain):
        self.binary = binary
        self.input = input
        self.job = job
        self.logger = job.logger
        self.ropchain = ropchain

    def run(self, timeout):
        from os import environ, pathsep, unlink, symlink
        from os.path import abspath, dirname, join

        pp = environ["PYTHONPATH"]
        del environ["PYTHONPATH"]
        environ["PYTHONPATH"] = "{}{}{}".format(pp, pathsep, "/exrop")

        runner = abspath(join(dirname(__file__), "exrop_runner.py"))
        cmd = ["/usr/bin/python3", runner, self.binary, self.ropchain]
        self.logger.debug("RUN exrop run {}".format(" ".join(cmd)))
        process = Popen(cmd, env=environ, stderr=STDOUT, stdout=PIPE)

        environ["PYTHONPATH"] = pp

        try:
            stdout = process.communicate(timeout=timeout)[0]
            self.logger.debug("exrop runner output:")
            self.logger.debug(stdout.decode(errors='ignore'))
        except TimeoutExpired:
            process.kill()
            self.logger.critical("FAIL TIMEOUT")
            exit(3)

        if process.returncode != 0:
            self.logger.error("Compilation ERROR with {} (exrop)".format(process.returncode))
            exit(1)
