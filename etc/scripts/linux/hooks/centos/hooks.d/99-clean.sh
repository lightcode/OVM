#!/bin/bash

rm -r $MNT_DIR/var/log/* 2> /dev/null
rm $MNT_DIR/root/.bash_history 2> /dev/null
rm $MNT_DIR/etc/udev/rules.d/70-persistent-net.rules 2> /dev/null