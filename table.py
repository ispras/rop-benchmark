#!/usr/bin/env python3

import argparse
import ast
from tabulate import tabulate


parser = argparse.ArgumentParser(description="Print results table")
parser.add_argument("results", type=str, help="Benchmark results file")
parser.add_argument("--latex", action="store_true", help="Print LaTeX table")
args = parser.parse_args()

highlight_row = ">{\columncolor[gray]{0.9}}"

t = None
with open(args.results, "r") as f:
    t = ast.literal_eval(f.readlines()[-1])

t = t["execve"]
tools = list(t.keys())
binary_sets = t[tools[0]].keys()
count = {}
for b in binary_sets:
    count[b] = t[tools[0]][b][-1]

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
        print(r" & \multicolumn{{3}}{{c{}}}{{{}}}".format("" if i == len(binary_sets) - 1 else " |", count[b]), end='')
    print(r""" \\
\midrule""")
else:
    s = "| Test suite   |"
    for b in binary_sets:
        s += " " + b + " " * (18 - len(b)) + "|"
    print(s)
    s = "| Total count  |"
    for b in binary_sets:
        c = " {} ".format(count[b])
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
    print(s)
