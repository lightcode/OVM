#!/bin/bash
########################################################################
# Copyright 2014 Matthieu Gaignière                matthieu@lightcode.fr
########################################################################
# This file is part of OVM.                          http://lightcode.fr
#
# OVM is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# OVM is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with OVM. If not, see <http://www.gnu.org/licenses/>.
########################################################################


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