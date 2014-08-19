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


SCRIPTPATH="$(dirname $0)"
cd $SCRIPTPATH

source functions.sh


clean_all() {
    [ "$MNT_DIR" != "" ] && _umount_partitions
    sleep 1s
    [ "$DISK" != "" ] && qemu-nbd -d $DISK
    sleep 1s
    [ "$MNT_DIR" != "" ] && rm -rf $MNT_DIR
}

cancel() {
    fail "CTRL-C detected"
}

if [ $# -ne 2 ]; then
    echo "usage: $0 <image-file> <hookset>" 1>&2
    exit 1
fi

FILE=$1
HOOKSET=$2
shift 2

trap cancel INT


source hooks/${HOOKSET}/functions.sh


echo "Installing $RELEASE into $FILE..."

MNT_DIR=`tempfile`
rm -f $MNT_DIR
mkdir $MNT_DIR
DISK=

echo "Looking for nbd device..."
_nbd_connect $FILE

sleep 1s

echo "Mounting partitions..."
_mount_partitions


echo "Running hooks..."
source hooks.sh


echo "Unmount all and clean..."
clean_all
exit 0