#!/usr/bin/env python3

import re
from os.path import basename
from argparse import ArgumentParser


parser = ArgumentParser(
            description=("Script to find out the common set of binaries "
                         "that are OK at least for one instrument."))
parser.add_argument("results", help="Result log produced by rop-benchmark")
parser.add_argument("-d", "--diff", type=str,
                    help=("Show the difference between the specified tool "
                          "result and the common set of OK's"))
args = parser.parse_args()

all_output_file = args.results

with open(all_output_file, 'r') as f:
    lines = f.read().splitlines()

# set -> instrument -> result
ok_results = {}

tools = set()
tool_regexp = re.compile("=== Tool '(.*)' === Exp. type '(.*)' === Test suite '(.*)'.*")
bin_regexp = re.compile(".*:rop-benchmark:(.*):(.*) - (.*) - (.*)")
tool, test_suite = None, None
for line in lines:
    m = tool_regexp.match(line)
    if m:
        tool, test_suite = m.group(1), m.group(3)
        if test_suite not in ok_results:
            ok_results[test_suite] = {}
        if tool not in ok_results[test_suite]:
            tools.add(tool)
            ok_results[test_suite][tool] = set()
        continue

    m = bin_regexp.match(line)
    if m:
        tool_r, binary, log_level, status = m.group(1), m.group(2), m.group(3), m.group(4)
        assert tool_r == tool, "MISMATCH tool {} != {}".format(tool_r, tool)
        if log_level == "INFO" and status == "OK":
            ok_results[test_suite][tool].add(basename(binary))

common = {}
for test_suite, ts_dic in ok_results.items():
    common[test_suite] = set()
    for tool, results in ts_dic.items():
        for binary in results:
            common[test_suite].add(binary)
    print("Common for {} consists of {} binaries".format(test_suite, len(common[test_suite])))
    if not args.diff:
        print(common[test_suite])

if args.diff:
    diff_tool = args.diff
    print("Possible improvements for {}".format(diff_tool))
    for test_suite, ok_all in common.items():
        diff = ok_all - ok_results[test_suite][diff_tool]
        print("Test suite {}".format(test_suite))
        print(diff)
        diff_dict = {}
        for el in diff:
            diff_dict[el] = []
            for tool in tools:
                if el in ok_results[test_suite][tool]:
                    diff_dict[el].append(tool)
        print(diff_dict)

