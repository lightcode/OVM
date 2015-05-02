#!/bin/bash

set -e

cd "$(dirname $0)"

DISK="$1"
ROOT="$2"

guestfish[0]="guestfish"
guestfish[1]="--listen"
guestfish[2]="-a"
guestfish[3]="$DISK"

GUESTFISH_PID=
eval $("${guestfish[@]}")
if [ -z "$GUESTFISH_PID" ]; then
    echo "error: guestfish didn't start up, see error messages above"
    exit 1
fi

cleanup_guestfish ()
{
    guestfish --remote -- exit >/dev/null 2>&1 ||:
}
trap cleanup_guestfish EXIT ERR

guestfish --remote -- run

lastpart=( $(guestfish --remote -- part-list /dev/vda | sed -n '/^\[1\]/,/\}/ { /start/ s/^.*: // p ; /num/ s/^.*: // p}') )

part_num="${lastpart[0]}"
part_start="${lastpart[1]}"

guestfish --remote -- part-del /dev/vda $part_num

blocksize=$(guestfish --remote -- blockdev-getss /dev/vda)

part_start_block=$(( $part_start / $blocksize ))

guestfish --remote -- part-add /dev/vda p $part_start_block -1 || true

guestfish --remote -- exit || true


GUESTFISH_PID=
eval $("${guestfish[@]}")
if [ -z "$GUESTFISH_PID" ]; then
    echo "error: guestfish didn't start up, see error messages above"
    exit 1
fi

guestfish --remote <<EOF
run
pvresize /dev/vda$part_num
lvresize-free $ROOT 100
e2fsck $ROOT correct:true
resize2fs $ROOT
EOF