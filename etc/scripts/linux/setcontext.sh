#!/bin/bash

set -e

cd "$(dirname $0)"

DISK="$1"
SCRIPT="distrib/$2.sh"
CONFIGPATH="$3"
ROOT="$4"

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

guestfish --remote -- mount $ROOT /

guestfish --remote -- upload "$CONFIGPATH" /tmp/configuration
guestfish --remote -- upload "$SCRIPT" /tmp/vmcontext
guestfish --remote -- chmod 0700 /tmp/vmcontext

guestfish --remote -- command /tmp/vmcontext > /dev/null
