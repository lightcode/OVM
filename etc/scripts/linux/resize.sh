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

cleanup_guestfish()
{
    guestfish --remote -- exit >/dev/null 2>&1 ||:
}
trap cleanup_guestfish EXIT ERR


# Returns informations about the partition
# 1st line : part number
# 2nd line : sector start
get_part_info()
{
    PART_ID=$1
    guestfish --remote -- part-list $DEVICE | sed -n "/^\[$PART_ID\]/,/\}/ { /start/ s/^.*: // p ; /num/ s/^.*: // p}"
}

convert_in_block() {
    SIZE_IN_BYTE=$1
    blocksize=$(guestfish --remote -- blockdev-getss $DEVICE)
    echo $(( $SIZE_IN_BYTE / $blocksize ))
}


###########################
# Resize partition
###########################

guestfish --remote -- run

DEVICE="$(guestfish --remote -- list-devices | grep -E '^(/dev/sda|/dev/vda)$' | head -n1)"

if [ -z "$DEVICE" ]; then
  echo "No device found" >&2
  exit 1
fi

nb_part=$(guestfish --remote -- part-list $DEVICE | grep -c '^\[')

lastid=$((nb_part - 1))

lastpart=( $(get_part_info $lastid) )

part_num="${lastpart[0]}"
part_start="${lastpart[1]}"

guestfish --remote -- part-del $DEVICE $part_num

part_start_block=$(convert_in_block $part_start)

prlogex=p
if [ "$part_num" -ge 5 ]; then
    prlogex=l
    eid=$(( $lastid - 1 ))
    epart=( $(get_part_info $eid) )
    epart_num="${epart[0]}"
    epart_start="${epart[1]}"
    epart_start_block=$(convert_in_block $epart_start)
    guestfish --remote -- part-del $DEVICE $epart_num
    guestfish --remote -- part-add $DEVICE e "$epart_start_block" -1 >/dev/null 2>&1 ||:
    guestfish --remote -- exit >/dev/null 2>&1 ||:

    GUESTFISH_PID=
    eval $("${guestfish[@]}")
    if [ -z "$GUESTFISH_PID" ]; then
        echo "error: guestfish didn't start up, see error messages above"
        exit 1
    fi
    guestfish --remote -- run
fi

guestfish --remote -- part-add $DEVICE "$prlogex" "$part_start_block" -1 >/dev/null 2>&1 ||:

guestfish --remote -- exit >/dev/null 2>&1 ||:


###########################
# Resize PV, LV and FS
###########################

GUESTFISH_PID=
eval $("${guestfish[@]}")
if [ -z "$GUESTFISH_PID" ]; then
    echo "error: guestfish didn't start up, see error messages above"
    exit 1
fi

guestfish --remote -- run
guestfish --remote -- pvresize ${DEVICE}$part_num
guestfish --remote -- lvresize-free $ROOT 100
guestfish --remote -- e2fsck $ROOT correct:true
guestfish --remote -- resize2fs $ROOT
