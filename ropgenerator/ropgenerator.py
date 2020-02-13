from sys import exit
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired


class Ropgenerator:

    def __init__(self, binary, input, job, ropchain, commands):
        self.commands = commands
        self.binary = binary
        self.input = input
        self.job = job
        self.logger = job.logger
        self.ropchain = ropchain

    def run(self, timeout):
        from os import environ
        from os.path import abspath

        pp = environ["PYTHONPATH"]
        del environ["PYTHONPATH"]
        #cmd = ["/snap/bin/docker", "run", "--rm", "-i", "-v",
        #       "{}:/tmp/test:ro".format(abspath(self.binary)), "ropgenerator"]
        cmd = ["/usr/bin/python3", "/usr/local/bin/ROPGenerator"]
        self.logger.debug("Run ropgenerator: {}".format(" ".join(cmd)))
        self.logger.debug("ropgenerator input: {}".format(self.commands))
        process = Popen(cmd, env=environ, stdin=PIPE, stdout=PIPE, stderr=STDOUT)

        try:
            stdout = process.communicate(input=self.commands.encode(), timeout=timeout)[0]
            self.logger.debug("ropgenerator output:")
            self.logger.debug(stdout.decode(errors='ignore'))
        except TimeoutExpired:
            process.kill()
            self.logger.critical("FAIL TIMEOUT")
            exit(3)

        if process.returncode != 0:
            self.logger.error("Compilation ERROR with {} (ropgenerator)".format(process.returncode))
            exit(1)

        environ["PYTHONPATH"] = pp

        lines = stdout.splitlines()
        n = len(lines)
        ropchain_generator = []
        for i, line in enumerate(lines):
            if line == b"\tfrom struct import pack":
                n = i
            if i >= n:
                if line == b"":
                    break
                import re
                new_str = re.sub(b'\x1b\[93m', b'', re.sub(b'\x1b\[0m', b'', line[1:]))
                ropchain_generator.append(new_str)
        if not ropchain_generator:
            self.logger.error("ROPGenerator could not generate a chain")
            exit(1)
        ropchain_generator.append(b"print p")

        script_path = "{}.ropgenerator.script".format(self.binary)
        with open(script_path, 'wb') as script:
            script.write(b"\n".join(ropchain_generator))

        script_cmd = ["/usr/bin/python2", script_path]
        with open(self.ropchain, "wb") as ropchain_output:
            script_p = Popen(script_cmd, stdout=ropchain_output, stderr=PIPE)
            try:
                stderr = script_p.communicate(timeout=timeout)[1]
                self.logger.debug("ropgenerator script output:")
                self.logger.debug(stderr.decode(errors='ignore'))
            except TimeoutExpired:
                script_p.kill()
                self.logger.critical("FAIL TIMEOUT")
                exit(3)

            if script_p.returncode != 0:
                self.logger.error("Compilation ERROR with {} (ropgenerator script)".format(script_p.returncode))
                exit(1)
