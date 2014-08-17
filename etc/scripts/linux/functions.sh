#!/bin/bash
########################################################################
# Copyright 2014 Matthieu Gaignière                matthieu@lightcode.fr
########################################################################
# This file is part of OVM.                          http://lightcode.fr
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


fail() {
    clean_all
    echo ""
    echo "FAILED: $1"
    exit 1
}

_nbd_connect() {
    local i diskfile
    diskfile="$1"

    modprobe nbd max_part=16 || fail "failed to load nbd module into kernel"

    for i in /dev/nbd*; do
        if qemu-nbd -c $i $diskfile
        then
            DISK=$i
            break
        fi
    done

    [ "$DISK" == "" ] && fail "no nbd device available"
}