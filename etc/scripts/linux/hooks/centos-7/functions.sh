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


function _mount_partitions() {
    vgscan
    vgchange -ay
    VGNAME=$(pvs ${DISK}p2 --noheadings | awk '{ print $2 }')
    mount /dev/$VGNAME/lv_root $MNT_DIR || fail "cannot mount /"
    mount --bind /dev/ $MNT_DIR/dev || fail "cannot bind /dev"
    mount --bind /dev/pts/ $MNT_DIR/dev/pts || fail "cannot bind /dev/pts"
    chroot $MNT_DIR mount -t ext4 ${DISK}p1 /boot || fail "cannot mount /boot"
    chroot $MNT_DIR mount -t proc none /proc || fail "cannot mount /proc"
    chroot $MNT_DIR mount -t sysfs none /sys || fail "cannot mount /sys"
}

function _umount_partitions() {
    echo "Umounting all partitions..."
    echo $MNT_DIR
    [ "$MNT_DIR" != "" ] && umount $MNT_DIR/proc $MNT_DIR/sys $MNT_DIR/dev/pts $MNT_DIR/dev $MNT_DIR/boot
    sleep 1s
    [ "$MNT_DIR" != "" ] && umount $MNT_DIR
    sleep 1s
    vgchange -an $VGNAME
}

function _resize() {
    local -r lvm_part="${DISK}p2"
    local -r lv_root="lv_root"

    echo ",+," | sfdisk -q -f -L -N2 $DISK
    echo ",+," | sfdisk -q -f -L -N5 $DISK

    vgscan
    vgchange -ay
    VGNAME=$(pvs "$lvm_part" --noheadings | awk '{ print $2 }')

    pvresize "$lvm_part"
    lvextend "/dev/$VGNAME/$lv_root" "$lvm_part"
    e2fsck -y -f "/dev/$VGNAME/$lv_root"
    resize2fs "/dev/$VGNAME/$lv_root"

    vgchange -an "$VGNAME"
    qemu-nbd -d "$DISK"
}