#!/bin/bash

# File        : hooks/debian-wheezy/functions.sh
# Author      : Matthieu
# Description : 


function _mount_partitions()
{
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


function _umount_partitions()
{
    [ "$MNT_DIR" != "" ] && chroot $MNT_DIR umount /proc/ /sys/ /dev/pts/ /dev/ /boot/
    sleep 1s
    [ "$MNT_DIR" != "" ] && umount $MNT_DIR
    sleep 1s
    vgchange -an $VGNAME
}
