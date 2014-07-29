#!/bin/bash

# File        : hooks/debian-wheezy/functions.sh
# Author      : Matthieu


function _mount_partitions()
{
    vgscan
    vgchange -ay
    VGNAME=$(pvs ${DISK}p5 --noheadings | awk '{ print $2 }')
    mount /dev/$VGNAME/root $MNT_DIR || fail "cannot mount /"
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

function _resize()
{
    echo ",+," | sfdisk -q -f -L -N2 $DISK
    echo ",+," | sfdisk -q -f -L -N5 $DISK

    vgscan
    vgchange -ay
    VGNAME=$(pvs ${DISK}p5 --noheadings | awk '{ print $2 }')

    pvresize ${DISK}p5
    lvextend /dev/$VGNAME/root ${DISK}p5
    e2fsck -y -f /dev/$VGNAME/root
    resize2fs /dev/$VGNAME/root

    vgchange -an $VGNAME
    qemu-nbd -d $DISK
}