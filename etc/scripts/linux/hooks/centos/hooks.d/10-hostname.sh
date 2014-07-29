#!/bin/bash

#
#  Set the hostname
#
cat <<EOF > $MNT_DIR/etc/sysconfig/network
NETWORKING=yes
HOSTNAME=$HOSTNAME
EOF

cat <<EOF > $MNT_DIR/etc/hosts
127.0.0.1       localhost
127.0.1.1       $HOSTNAME
 
# The following lines are desirable for IPv6 capable hosts
::1     localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
EOF

#
#  Print for debugging
#
_debug_file $MNT_DIR/etc/hostname
_debug_file $MNT_DIR/etc/hosts
