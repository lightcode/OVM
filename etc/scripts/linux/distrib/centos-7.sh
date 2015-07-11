#!/bin/bash

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
