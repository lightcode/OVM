#!/bin/bash

# File        : finish-vm.sh
# Author      : Matthieu


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

    for i in /dev/nbd*
    do
        if qemu-nbd -c $i $diskfile
        then
            DISK=$i
            break
        fi
    done

    [ "$DISK" == "" ] && fail "no nbd device available"
}
