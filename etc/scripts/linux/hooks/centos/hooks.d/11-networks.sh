#!/bin/bash

#cat <<EOF > $MNT_DIR/etc/network/interfaces

INTERFACE=${INTERFACE:-eth0}

NET_FILE="$MNT_DIR/etc/sysconfig/network-scripts/ifcfg-$INTERFACE"
echo -n > $NET_FILE

cat <<EOF >> $NET_FILE 
DEVICE="$INTERFACE"
NM_CONTROLLED="yes"
ONBOOT="yes"
TYPE="Ethernet"
EOF


# IPv4
IP=${IP:-dhcp}

if [ $IP == "dhcp" ]; then
    cat <<EOF >> $NET_FILE
BOOTPROTO="dhcp"
EOF
elif [ -n $IP ] && [ -n $NETMASK ] && [ -n $GATEWAY ]; then
    cat <<EOF >> $NET_FILE
BOOTPROTO="static"
IPADDR="$IP"
NETMASK="$NETMASK"
GATEWAY="$GATEWAY"
EOF
fi


# IPv6
IPV6=${IPV6:-disabled}
if [ $IPV6 == "auto" ]; then
    cat <<EOF >> $NET_FILE
IPV6INIT="yes"
IPV6_AUTOCONF="yes"
EOF
fi


#
#  Print for debugging
#
_debug_file $NET_FILE
