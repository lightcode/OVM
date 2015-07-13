#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
from math import log


TABLE_PADDING = ' ' * 3


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[32m'
    WARNING = '\033[93m'
    FAIL = '\033[31m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''


class ColoredString:
    def __init__(self, text, color):
        self.text = str(text)
        self.color = color

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return self.color + self.text + bcolors.ENDC


def bold_underline(text):
    return '\033[1;4m{0}\033[0m'.format(text)


def underline(text):
    return '\033[4m{0}\033[24m'.format(text)


def bold(text):
    return '\033[1m{0}\033[21m'.format(text)


def print_title(text, length=60):
    title = text + ((length - len(text)) * ' ')
    print(bold_underline(title.upper()))
    print()


def print_table(headers, rows, align=None):
    if not align:
        align = ['l'] * len(headers)
    row_width = [len(t) for t in headers]
    for line in rows:
        line = list(line)
        for i, l in enumerate(line):
            if not isinstance(l, str) and not isinstance(l, ColoredString):
                line[i] = str(l)
        for i, column in enumerate(line):
            row_width[i] = max(len(column), row_width[i])

    template = TABLE_PADDING.join(
        ['{%d:%s%d}' % (i, '>' if a == 'r' else '<', w) for i, w, a in
            zip(list(range(len(row_width))), row_width, align)])
    template_headers = TABLE_PADDING.join(
        ['{%d:%d}' % (i, w) for i, w in enumerate(row_width)]) + TABLE_PADDING

    print(underline(template_headers.format(*headers)))
    for line in rows:
        print(template.format(*line))


def si_unit(x, binary=False):
    x = abs(float(x))
    if x <= 0:
        return '0 '

    k = 1024 if binary else 1000

    units = ['n', '\u00B5', 'm', '', 'k', 'M', 'G', 'T', 'P', 'E']
    if x < 1:
        m = int(log(x, k))
        return '%.0f %s' % (x * pow(k, abs(m) + 1), units[2 + m])

    m = int(log(x, k))
    prefix = 'i' if binary else ''
    return '%.0f %s%s' % (x / pow(k, m), units[3 + m], prefix)


def default(value, replacement=''):
    return replacement if value is None else value
