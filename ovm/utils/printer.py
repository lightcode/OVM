#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
########################################################################
# Copyright 2015 Matthieu Gaignière                  http://lightcode.fr
########################################################################
# This file is part of OVM.
#
# OVM is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# OVM is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with OVM. If not, see <http://www.gnu.org/licenses/>.
########################################################################


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


class ColoredString(object):
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
