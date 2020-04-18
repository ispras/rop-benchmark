#!/usr/bin/env python3

import argparse
import ast
from tabulate import tabulate


parser = argparse.ArgumentParser(description="Print results table")
parser.add_argument("results", type=str, help="Benchmark results file")
parser.add_argument("--latex", action="store_true", help="Print LaTeX table")
parser.add_argument("--tools", type=str, help="List of tools to print (comma-separated)")
parser.add_argument("--suites", type=str, help="List of test suites to print (comma-separated)")
args = parser.parse_args()

highlight_row = ">{\columncolor[gray]{0.9}}"

t = None
with open(args.results, "r") as f:
    t = ast.literal_eval(f.readlines()[-1])

t = t["execve"]
if args.suites:
    binary_sets = args.suites.split(",")
else:
    binary_sets = t["total"].keys()
if args.tools:
    tools = args.tools.split(",")
    # Recalculate Total OK
    import re
    r = re.compile("Tool '([^\s]+)'.*Test suite '([^\s]+)'")
    oks = {b: set() for b in binary_sets}
    b = None
    with open(args.results, "r") as f:
        for line in f:
            m = r.search(line)
            if m:
                tool = m.group(1)
                if tool not in tools:
                    b = None
                    continue
                b = m.group(2)
                if b not in binary_sets:
                    b = None
                continue
            if b and line.startswith(" ") and "OK" in line:
                oks[b].add(line.split(" - ", 1)[0].rsplit(":", 1)[-1])
    for b in binary_sets:
        t["total"][b] = (len(oks[b]), t["total"][b][1])
else:
    tools = [tool for tool in t.keys() if tool != "total"]

tool_width = max(len(tool) for tool in tools)
first_column_width = max(11, tool_width)

def first_column(name):
    return "| {}{} |".format(name, " " * (first_column_width - len(name)))

headers = ["Tool"]
for _ in binary_sets:
    headers += ["OK", "F", "TL"]

table = [headers]
for tool in tools:
    row = [tool]
    for b in binary_sets:
        ok, f, tl, _ = t[tool][b]
        row += [ok, f, tl]
    table.append(row)

if args.latex:
    print(r"""\documentclass[]{standalone}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{colortbl}
\begin{document}
\begin{tabular}{ l""", end='')
    for _ in binary_sets:
        print(f" | {highlight_row}r r r", end='')
    print(r""" }
\toprule
Test suite""", end='')
    for i, b in enumerate(binary_sets):
        print(r" & \multicolumn{{3}}{{c{}}}{{{}}}".format("" if i == len(binary_sets) - 1 else " |", b), end='')
    print(r""" \\
Number of files""", end='')
    for i, b in enumerate(binary_sets):
        count = t["total"][b][-1]
        print(r" & \multicolumn{{3}}{{c{}}}{{{}}}".format("" if i == len(binary_sets) - 1 else " |", count), end='')
    print(r""" \\
At least one OK""", end='')
    for i, b in enumerate(binary_sets):
        ok = t["total"][b][0]
        print(r" & \multicolumn{{3}}{{c{}}}{{{}}}".format("" if i == len(binary_sets) - 1 else " |", ok), end='')
    print(r""" \\
\midrule""")
else:
    s = first_column("Test suite")
    for b in binary_sets:
        s += " " + b + " " * (18 - len(b)) + "|"
    print(s)
    s = first_column("Total count")
    for b in binary_sets:
        count = t["total"][b][-1]
        c = " {} ".format(count)
        s += c + " " * (19 - len(c)) +  "|"
    print(s)
    s = first_column("Total OK")
    for b in binary_sets:
        ok = t["total"][b][0]
        c = " {} ".format(ok)
        s += c + " " * (19 - len(c)) +  "|"
    print(s)

s = str(tabulate(table, headers="firstrow", tablefmt=("latex" if args.latex else "pipe")))

if args.latex:
    s = s.split('\n', 2)[-1]
    s = s.rsplit('\n', 2)[0]
    s = s.replace("\\hline\n", "")
    print(s)
    print(r"""\bottomrule
\end{tabular}
\end{document}""")
else:
    if tool_width < first_column_width:
        import re
        p = " " * (first_column_width - tool_width)
        s = re.sub(r"(\| [a-zA-Z]+ *) \|", r"\1{} |".format(p), s)
        s = re.sub(":{}".format("-" * (tool_width + 1)), ":{}".format("-" * (first_column_width + 1)), s)
    print(s)
