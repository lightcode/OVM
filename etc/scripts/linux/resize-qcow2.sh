#!/bin/bash

# File        : resize-qcow2.sh
# Author      : Matthieu
# Description : script to resize partition


HOOKSET="$1"
FILE="$2"

SCRIPTPATH="$(dirname $0)"
echo $SCRIPTPATH
cd $SCRIPTPATH

source $SCRIPTPATH/functions.sh
source hooks/${HOOKSET}/functions.sh


echo $FILE

_nbd_connect $FILE

_resize
