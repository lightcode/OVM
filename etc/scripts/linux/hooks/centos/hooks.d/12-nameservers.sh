#!/bin/bash

if [ -n "$NAMESERVERS" ]; then
    echo -n > $MNT_DIR/etc/resolv.conf
    for addr in $NAMESERVERS; do
        echo "nameserver $addr" >> $MNT_DIR/etc/resolv.conf
    done

    _debug_file $MNT_DIR/etc/resolv.conf
else
    echo "Nothing to do."
fi
