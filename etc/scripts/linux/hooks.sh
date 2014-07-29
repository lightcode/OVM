#!/bin/bash

_debug_file()
{
    echo $1
    cat $1
    echo
    echo
}

for hook in hooks/${HOOKSET}/hooks.d/*.sh; do
    echo $hook
    echo "-----------"
    source $hook
    echo
done

echo "FIN"
