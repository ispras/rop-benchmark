from sys import exit
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired


class ROPGadget:

    def __init__(self, binary, input, job, ropchain, bad_chars):
        self.binary = binary
        self.input = input
        self.job = job
        self.logger = job.logger
        self.ropchain = ropchain
        self.bad_chars = bad_chars

    def run(self, timeout):
        from os import environ

        pp = environ["PYTHONPATH"]
        del environ["PYTHONPATH"]
        cmd = ["ROPgadget", "--binary", self.binary, "--ropchain"]
        if self.bad_chars:
            import binascii
            bad_chars = "|".join("{:02x}".format(char) for char in binascii.unhexlify(self.bad_chars))
            cmd += ["--badbytes", bad_chars]
        self.logger.debug("RUN {}".format(" ".join(cmd)))
        process = Popen(cmd, env=environ, stderr=STDOUT, stdout=PIPE)

        try:
            stdout = process.communicate(timeout=timeout)[0]
            self.logger.debug("ROPgadget output:")
            self.logger.debug(stdout.decode(errors='ignore'))
        except TimeoutExpired:
            process.kill()
            self.logger.critical("FAIL TIMEOUT")
            exit(3)

        if process.returncode != 0:
            self.logger.error("Compilation ERROR with {} (ROPgadget)".format(process.returncode))
            exit(1)

        environ["PYTHONPATH"] = pp

        lines = stdout.splitlines()
        n = len(lines)
        ropchain_generator = []
        for i, line in enumerate(lines):
            if line == b"- Step 5 -- Build the ROP chain":
                n = i
            if i > n:
                ropchain_generator.append(line[1:])
        if not ropchain_generator:
            self.logger.error("ROPgadget could not generate a chain")
            exit(1)
        ropchain_generator.append(b"print p")

        script_path = "{}.ropgadget.script".format(self.binary)
        with open(script_path, 'wb') as script:
            script.write(b"\n".join(ropchain_generator))

        script_cmd = ["/usr/bin/python2", script_path]
        with open(self.ropchain, "wb") as ropchain_output:
            script_p = Popen(script_cmd, stdout=ropchain_output, stderr=PIPE)
            try:
                stderr = script_p.communicate(timeout=timeout)[1]
                self.logger.debug("ROPgadget script output:")
                self.logger.debug(stderr.decode(errors='ignore'))
            except TimeoutExpired:
                script_p.kill()
                self.logger.critical("FAIL TIMEOUT")
                exit(3)

            if script_p.returncode != 0:
                self.logger.error("Compilation ERROR with {} (ROPgadget script)".format(script_p.returncode))
                exit(1)
