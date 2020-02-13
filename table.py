#!/usr/bin/env python3

import sys
import ast
from tabulate import tabulate


if len(sys.argv) < 2:
    print("Usage: {} RESULTS".format(sys.argv[0]))
    sys.exit(1)

t = None
with open(sys.argv[1], "r") as f:
    t = ast.literal_eval(f.readlines()[-1])

t = t["execve"]
tools = list(t.keys())
binary_sets = t[tools[0]].keys()

headers = ["Tool"]
for i in range(len(binary_sets)):
    headers += ["OK", "F", "TL"]

table = [headers]
for tool in tools:
    row = [tool]
    for b in binary_sets:
        ok, f, tl, _ = t[tool][b]
        row += [ok, f, tl]
    table.append(row)

s = "|              |"
for b in binary_sets:
    s += " " + b + " " * (18 - len(b)) + "|"
print(s)

print(tabulate(table, headers="firstrow", tablefmt="pipe"))
