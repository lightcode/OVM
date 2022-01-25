#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from math import log


TABLE_PADDING = " " * 3


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[32m"
    WARNING = "\033[93m"
    FAIL = "\033[31m"
    ENDC = "\033[0m"

    def disable(self):
        self.HEADER = ""
        self.OKBLUE = ""
        self.OKGREEN = ""
        self.WARNING = ""
        self.FAIL = ""
        self.ENDC = ""


class ColoredString:
    def __init__(self, text, color):
        self.text = str(text)
        self.color = color

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return self.color + self.text + bcolors.ENDC


def bold_underline(text):
    return "\033[1;4m{0}\033[0m".format(text)


def underline(text):
    return "\033[4m{0}\033[24m".format(text)


def bold(text):
    return "\033[1m{0}\033[21m".format(text)


def print_title(text, length=60):
    title = text + ((length - len(text)) * " ")
    print(bold_underline(title.upper()))
    print()


def print_table(headers, rows, align=None):
    if not align:
        align = ["l"] * len(headers)

    col_width = [len(t) for t in headers]
    for i, line in enumerate(rows):
        rows[i] = list(line)

        for j, c in enumerate(line):
            if not isinstance(c, str) and not isinstance(c, ColoredString):
                c = str(c)
                rows[i][j] = c

            col_width[j] = max(len(c), col_width[j])

    template_headers = (
        TABLE_PADDING.join(["{%d:%d}" % (i, w) for i, w in enumerate(col_width)])
        + TABLE_PADDING
    )

    print(underline(template_headers.format(*headers)))

    for line in rows:
        row = ""
        for cell, size, a in zip(line, col_width, align):
            cell_pad = " " * (size - len(cell))
            if a == "r":
                row += cell_pad + str(cell) + TABLE_PADDING
            else:
                row += str(cell) + cell_pad + TABLE_PADDING
        print(row)


def si_unit(x, binary=False):
    x = abs(float(x))
    if x <= 0:
        return "0 "

    k = 1024 if binary else 1000

    units = ["n", "\u00B5", "m", "", "k", "M", "G", "T", "P", "E"]
    if x < 1:
        m = int(log(x, k))
        return "%.0f %s" % (x * pow(k, abs(m) + 1), units[2 + m])

    m = int(log(x, k))
    prefix = "i" if binary else ""
    return "%.0f %s%s" % (x / pow(k, m), units[3 + m], prefix)


def default(value, replacement=""):
    return replacement if value is None else value
