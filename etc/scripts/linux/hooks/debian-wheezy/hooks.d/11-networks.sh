#!/bin/bash

#cat <<EOF > $MNT_DIR/etc/network/interfaces

INTERFACE=${INTERFACE:-eth0}

NET_FILE="$MNT_DIR/etc/network/interfaces"
echo -n > $NET_FILE

#
#  Set interface loopback
#
cat <<EOF >> $NET_FILE 
auto lo
iface lo inet loopback

auto $INTERFACE
EOF


#
#  Set main interface's IP
#

# IPv4
IP=${IP:-dhcp}

if [ $IP == "dhcp" ]; then
    cat <<EOF >> $NET_FILE
iface $INTERFACE inet dhcp
EOF
elif [ -n $IP ] && [ -n $NETMASK ] && [ -n $GATEWAY ]; then
    cat <<EOF >> $NET_FILE
iface $INTERFACE inet static
  address $IP
  netmask $NETMASK
  gateway $GATEWAY
EOF
fi


# IPv6
IPV6=${IPV6:-disabled}
if [ $IPV6 == "auto" ]; then
    cat <<EOF >> $NET_FILE

iface $INTERFACE inet6 auto
EOF
fi


#
#  Print for debugging
#
cat $NET_FILE
