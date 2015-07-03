#!/bin/bash
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
########################################################################
# Copyright 2015 Matthieu Gaignière                  http://lightcode.fr
########################################################################
# This file is part of OVM.
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

set -ex

source /tmp/configuration


##################################################
# HOSTNAME
##################################################

echo $HOSTNAME > /etc/hostname

cat <<EOF > /etc/hosts
127.0.0.1       localhost
127.0.1.1       $HOSTNAME

# The following lines are desirable for IPv6 capable hosts
::1     localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
EOF


##################################################
# NETWORKS
##################################################

INTERFACE=${INTERFACE:-eth0}

NET_FILE="/etc/sysconfig/network-scripts/ifcfg-$INTERFACE"
echo -n > $NET_FILE

cat <<EOF >> $NET_FILE
DEVICE="$INTERFACE"
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


##################################################
# NAMESERVERS
##################################################

if [ -n "$NAMESERVERS" ]; then
    echo -n > /etc/resolv.conf
    for addr in $NAMESERVERS; do
        echo "nameserver $addr" >> /etc/resolv.conf
    done
fi


##################################################
# CLEAN UP
##################################################

/usr/bin/find /var/log -type f -delete
rm -f /root/.bash_history 2> /dev/null