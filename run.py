#!/usr/bin/python3
from os.path import join, splitext, basename, isdir, dirname
from os import listdir, environ, getcwd
from argparse import ArgumentParser
from sys import exit
from multiprocessing import Pool, cpu_count


def list_all_reallife_test_suites():
    """Return all directories placed under binaries/reallife/vuln"""
    d = REALLIFE_VULN_DIR
    return [f for f in listdir(d) if isdir(join(d, f))]


def list_tests(directory):
    """Return list of all tests inside `directory`."""
    tests = []
    for filename in listdir(directory):
        _, extension = splitext(filename)
        if extension in [".bin", ".vuln64", ".vuln32"]:
            tests.append(join(directory, filename))
    return sorted(tests)


def run_test(args):
    """Try to generate ROP chain for `testname` by `tool` for `exploit_type`
    payload.

    Run script for `exploit_type` should be placed inside `tool` directory with
    name `job_<exploit_type>`. It actually runs tool to generate payload for
    `testname`.
    """
    from subprocess import Popen, PIPE, STDOUT

    testname, tool, exploit_type = args
    cmd = ["/usr/bin/python3", "{}/job_{}.py".format(tool, exploit_type), testname]
    if CHECK_ONLY:
        cmd.append("-c")
    process = Popen(cmd, stdout=PIPE, stderr=STDOUT)
    stdout, stderr = process.communicate()

    return (1, stdout) if not process.returncode else (0, stdout)


parser = ArgumentParser(description=("Rop-benchmark entry point. "
                                    "By default it runs all tests."))
parser.add_argument("-s", "--synthetic", action='store_true',
                    default=False, help="Run only synthetic test-suite")
parser.add_argument("-t", "--tool", type=str, help="Run only tool")
parser.add_argument("-r", "--real-life", type=str,
                    help="Run only specified real life binary test-suite.")
parser.add_argument("-n", "--cores", type=int,
                    help="The number of parallel instances to run.")
parser.add_argument("-a", "--arch", type=str, default="x86",
                    help="The target architecture of framework.")
parser.add_argument("-c", "--check-only", action='store_true', default=False,
                    help="Only check chains generated previously")
parser.add_argument("-b", "--binary", type=str,
                    help="Run particular binary e.g. openbsd-62/ac.bin")
args = parser.parse_args()

environ["PYTHONPATH"] = getcwd()
SYNTHETIC_VULN_DIR = join("binaries", args.arch, "synthetic", "vuln")
REALLIFE_VULN_DIR = join("binaries", args.arch, "reallife", "vuln")
CHECK_ONLY = args.check_only

exploit_types = ["execve"]
reallife_test_suites = list_all_reallife_test_suites()

if not args.tool:
    tools = ["ropgadget", "angrop", "ropgenerator", "ropper"]
else:
    tools = [args.tool]

test_suites = {}
if args.binary:
    test_suite = dirname(args.binary)
    test_suites[test_suite] = join(REALLIFE_VULN_DIR, test_suite)
else:
    test_suites["synthetic"] = SYNTHETIC_VULN_DIR
    if not args.synthetic:
        if args.real_life:
            if args.real_life not in reallife_test_suites:
                print("Incorrect real life test set. Choose one of:")
                print(" ".join(reallife_test_suites))
                exit(1)
            test_suites[args.real_life] = join(REALLIFE_VULN_DIR, args.real_life)
        else:
            for t in reallife_test_suites:
                test_suites[t] = join(REALLIFE_VULN_DIR, t)

results = {}
for exp_type in exploit_types:
    results[exp_type] = {}
    for tool in tools:
        results[exp_type][tool] = {}

n_core = args.cores if args.cores is not None else cpu_count()
print("---- Run rop-benchmark in {} parallel jobs ----".format(n_core))
proc_pool = Pool(n_core)
for tool in tools:
    for exploit_type in exploit_types:
        for test_suite_name, test_suite_dir in test_suites.items():
            if args.binary:
                tests = [join(test_suite_dir, basename(args.binary))]
            else:
                print("=== Tool '{}' === Exp. type '{}' === Test suite '{}'"
                      .format(tool, exploit_type, test_suite_name))
                tests = list_tests(test_suite_dir)
            passed = 0
            current_id = 1
            run_test_args = [(test, tool, exploit_type) for test in tests]
            for r in proc_pool.imap(run_test, run_test_args):
                is_passed, bstdout = r
                if bstdout:
                    stdout = bstdout.decode()
                    print(f"{current_id: >{4}}:{stdout}", end="")
                passed += is_passed
                current_id += 1
            results[exploit_type][tool][test_suite_name] = (passed, len(tests))
            if not args.binary:
                print("--- Result --- {} {} {} : {} / {} (passed/all)"
                      .format(tool, exploit_type, test_suite_name,
                              passed, len(tests)))

print("--== Overall results summary ==--")
print(results)
