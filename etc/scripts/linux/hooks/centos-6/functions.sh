#!/bin/bash
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
########################################################################
# Copyright 2014 Matthieu Gaignière                  http://lightcode.fr
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


function _mount_partitions() {
    local vgname
    local -r disk="$DISK"
    local -r boot_part="${disk}p1"
    local -r lvm_part="${disk}p2"

    vgscan
    vgchange -ay
    vgname=$(pvs ${lvm_part} --noheadings | awk '{ print $2 }')

    mount "/dev/${vgname}/lv_root" $MNT_DIR || fail "cannot mount /"
    mount --bind /dev/ $MNT_DIR/dev || fail "cannot bind /dev"
    mount --bind /dev/pts/ $MNT_DIR/dev/pts || fail "cannot bind /dev/pts"
    chroot $MNT_DIR mount -t ext4 "${boot_part}p1" /boot || fail "cannot mount /boot"
    chroot $MNT_DIR mount -t proc none /proc || fail "cannot mount /proc"
    chroot $MNT_DIR mount -t sysfs none /sys || fail "cannot mount /sys"
}

function _umount_partitions() {
    [ "$MNT_DIR" != "" ] && umount $MNT_DIR/proc $MNT_DIR/sys $MNT_DIR/dev/pts $MNT_DIR/dev $MNT_DIR/boot
    sleep 1s
    [ "$MNT_DIR" != "" ] && umount $MNT_DIR
    sleep 1s
    vgchange -an $VGNAME
}

function _resize() {
    local vgname
    local -r disk="$1"
    local -r lvm_part="${disk}p2"
    local -r lv_root="lv_root"

    echo ",+," | sfdisk -q -f -L -N2 "$disk"

    vgscan
    vgchange -ay
    vgname=$(pvs "$lvm_part" --noheadings | awk '{ print $2 }')

    pvresize "$lvm_part"
    lvextend "/dev/$vgname/${lv_root}" "$lvm_part"
    e2fsck -y -f "/dev/$vgname/${lv_root}"
    resize2fs "/dev/$vgname/${lv_root}"

    vgchange -an "${vgname}"
    qemu-nbd -d "${disk}"
}