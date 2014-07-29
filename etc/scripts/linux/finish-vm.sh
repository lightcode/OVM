#!/bin/bash

# File        : finish-vm.sh
# Author      : Matthieu
# Description : Script to finish install on a qcow image.


SCRIPTPATH="$(dirname $0)"
cd $SCRIPTPATH

source functions.sh


clean_all() {
    [ "$MNT_DIR" != "" ] && _umount_partitions
    sleep 1s
    [ "$DISK" != "" ] && qemu-nbd -d $DISK
    sleep 1s
    [ "$MNT_DIR" != "" ] && rm -r $MNT_DIR
}

cancel() {
    fail "CTRL-C detected"
}

if [ $# -ne 2 ]
then
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
rm $MNT_DIR
mkdir $MNT_DIR
DISK=

echo "Looking for nbd device..."
_nbd_connect $FILE

sleep 1s

echo "Mounting partitions..."
_mount_partitions


echo "Running hooks..."
source hooks.sh


echo "SUCCESS!"
clean_all
exit 0
