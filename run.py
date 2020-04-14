#!/usr/bin/python3
from os.path import join, splitext, basename, isdir, dirname, exists, abspath
from os import listdir, environ, getcwd
from argparse import ArgumentParser
from sys import exit
from multiprocessing import Pool, cpu_count
import signal


global timeout


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


def kill_childs():
    """Kill all child processes."""
    from os import getpid
    from psutil import Process, NoSuchProcess
    for child in Process(getpid()).children(recursive=True):
        try:
            child.terminate()
        except NoSuchProcess:
            pass
    for child in Process(getpid()).children(recursive=True):
        try:
            child.kill()
        except NoSuchProcess:
            pass


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
    if timeout is not None:
        cmd += ["-t", str(timeout)]
    if CHECK_ONLY:
        cmd.append("-c")
    if GENERATE_ONLY:
        cmd.append("-g")

    def handle(signum, frame):
        kill_childs()
        exit(1)

    signal.signal(signal.SIGTERM, handle)
    process = Popen(cmd, stdout=PIPE, stderr=STDOUT)
    stdout, stderr = process.communicate()

    return (process.returncode, stdout)


def do_clean():
    from subprocess import Popen, PIPE, STDOUT
    print("Clean-up working tree")
    cmd = ["git", "clean", "./", "-f", "-d", "-x"]
    process = Popen(cmd, stdout=PIPE, stderr=STDOUT,
                    cwd=join(BENCHMARK_DIR, "binaries"))
    stdout, stderr = process.communicate()
    if process.returncode:
        print(stdout)
        print(stderr)

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
parser.add_argument("-g", "--generate-only", action="store_true",
                    default=False, help=("Only generate chains. Do not try "
                                         "to run and check them."))
parser.add_argument("-b", "--binary", type=str,
                    help="Run particular binary e.g. openbsd-62/ac.bin")
parser.add_argument("--timeout", type=int,
                    help="The timeout in seconds for each binary")
parser.add_argument("--clean", action="store_true", default=False,
                    help=("Clean rop-benchmark working tree "
                          "from any artifacts of previous runs"))
args = parser.parse_args()

timeout = args.timeout

BENCHMARK_DIR = abspath(dirname(__file__))
SYNTHETIC_VULN_DIR = join(BENCHMARK_DIR, "binaries", args.arch, "synthetic", "vuln")
REALLIFE_VULN_DIR = join(BENCHMARK_DIR, "binaries", args.arch, "reallife", "vuln")
CHECK_ONLY = args.check_only
GENERATE_ONLY = args.generate_only

environ["PYTHONPATH"] = BENCHMARK_DIR

if args.clean:
    do_clean()
    exit(0)

exploit_types = ["execve"]
reallife_test_suites = list_all_reallife_test_suites()

if not args.tool:
    tools = ["ropgadget", "angrop", "ropium", "ropper", "exrop"]
else:
    tools = [args.tool]

test_suites = {}
if args.binary:
    test_suite = dirname(args.binary)
    test_suites[test_suite] = join(REALLIFE_VULN_DIR, test_suite)
else:
    if exists(SYNTHETIC_VULN_DIR):
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
test_suite_ok = {}
for exp_type in exploit_types:
    test_suite_ok[exp_type] = {}
    for test_suite in test_suites:
        test_suite_ok[exp_type][test_suite] = set()

def print_results():
    for exp_type in exploit_types:
        oks = test_suite_ok[exp_type]
        cnt = results[exp_type][tools[0]]
        results[exp_type]["total"] = {t: (len(oks[t]), cnt[t][3]) for t in test_suites}
    print("--== Overall results summary (OK, F, TL, CNT) ==--")
    print(results)

n_core = args.cores if args.cores is not None else cpu_count()
print("---- Run rop-benchmark in {} parallel jobs ----".format(n_core))
proc_pool = Pool(n_core)

passed = 0
failed = 0
tl = 0
tool = None
exploit_type = None
test_suite_name = None
job_cnt = None

def print_test_suite_result():
    results[exploit_type][tool][test_suite_name] = (passed, failed, tl, job_cnt)
    if not args.binary:
        print("--- Result --- {} {} {} : {} / {} (passed/all)"
              .format(tool, exploit_type, test_suite_name, passed, job_cnt))

def handle(signum, frame):
    proc_pool.terminate()
    print_test_suite_result()
    print_results()
    exit(1)

signal.signal(signal.SIGTERM, handle)
try:
    run_test_args = []
    suites = []
    for tool in tools:
        for exploit_type in exploit_types:
            for test_suite_name, test_suite_dir in test_suites.items():
                if args.binary:
                    tests = [join(test_suite_dir, basename(args.binary))]
                else:
                    tests = list_tests(test_suite_dir)
                run_test_args += [(test, tool, exploit_type) for test in tests]
                suites.append((tool, exploit_type, test_suite_name, len(tests)))
    i = 0
    current_id = 1
    tool, exploit_type, test_suite_name, job_cnt = suites[0]
    for retcode, bstdout in proc_pool.imap(run_test, run_test_args):
        if current_id == 1 and not args.binary:
            print("=== Tool '{}' === Exp. type '{}' === Test suite '{}'"
                  .format(tool, exploit_type, test_suite_name))
        if bstdout:
            stdout = bstdout.decode()
            print(f"{current_id: >{4}}:{stdout}", end="")
        if not retcode:
            passed += 1
            test_suite_ok[exploit_type][test_suite_name].add(current_id)
        elif retcode == 2:
            failed += 1
        elif retcode == 3:
            tl += 1
        if current_id == job_cnt:
            print_test_suite_result()
            i += 1
            if i == len(suites):
                break
            passed = 0
            failed = 0
            tl = 0
            current_id = 1
            tool, exploit_type, test_suite_name, job_cnt = suites[i]
        else:
            current_id += 1
except KeyboardInterrupt:
    proc_pool.terminate()
    print("\n\nStopped by user")
    print_test_suite_result()

print_results()
