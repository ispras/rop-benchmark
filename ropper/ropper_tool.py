from sys import exit
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired


class Ropper:

    def __init__(self, binary, input, job, ropchain):
        self.binary = binary
        self.input = input
        self.job = job
        self.logger = job.logger
        self.ropchain = ropchain

    def run(self, timeout):
        cmd = ["ropper", "--nocolor", "--file", self.binary, "--chain", "execve"]
        self.logger.debug("Run ropper: {}".format(" ".join(cmd)))
        process = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)

        try:
            stdout = process.communicate(timeout=timeout)[0]
            self.logger.debug("ropper output:")
            self.logger.debug(stdout.decode(errors='ignore'))
        except TimeoutExpired:
            process.kill()
            self.logger.critical("FAIL TIMEOUT")
            exit(1)

        if process.returncode != 0:
            self.logger.error("Compilation ERROR with {} (ropper)".format(process.returncode))
            exit(1)

        lines = stdout.splitlines()
        n = len(lines)
        ropchain_generator = []
        for i, line in enumerate(lines):
            if line == b"from struct import pack":
                n = i
            if i >= n:
                ropchain_generator.append(line)
                if line == b"print rop":
                    break

        script_path = "{}.ropper.script".format(self.binary)
        with open(script_path, 'wb') as script:
            script.write(b"\n".join(ropchain_generator))

        script_cmd = ["/usr/bin/python2", script_path]
        with open(self.ropchain, "wb") as ropchain_output:
            script_p = Popen(script_cmd, stdout=ropchain_output, stderr=PIPE)
            try:
                stderr = script_p.communicate(timeout=timeout)[1]
                self.logger.debug("ropper script output:")
                self.logger.debug(stderr.decode(errors='ignore'))
            except TimeoutExpired:
                script_p.kill()
                self.logger.critical("FAIL TIMEOUT")
                exit(1)

            if script_p.returncode != 0:
                self.logger.error("Compilation ERROR with {} (ropper script)".format(script_p.returncode))
                exit(1)

