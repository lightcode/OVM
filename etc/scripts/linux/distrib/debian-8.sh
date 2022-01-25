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

NET_FILE="/etc/network/interfaces"
echo -n > $NET_FILE

# Set interface loopback
cat <<EOF >> $NET_FILE
auto lo
iface lo inet loopback

auto $INTERFACE
EOF

# IPv4 on eth0
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

# IPv6 on eth0
IPV6=${IPV6:-disabled}
if [ $IPV6 == "auto" ]; then
    cat <<EOF >> $NET_FILE

iface $INTERFACE inet6 auto
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
# REPOSITORY
##################################################

# Add french repository
cat <<EOF > /etc/apt/sources.list
deb http://ftp.fr.debian.org/debian/ jessie main
deb-src http://ftp.fr.debian.org/debian/ jessie main

deb http://security.debian.org/ jessie/updates main
deb-src http://security.debian.org/ jessie/updates main

deb http://ftp.fr.debian.org/debian/ jessie-updates main
deb-src http://ftp.fr.debian.org/debian/ jessie-updates main

deb http://ftp.fr.debian.org/debian jessie-backports main
EOF


##################################################
# CLEAN UP
##################################################

/usr/bin/find /var/log -type f -delete
rm -f /root/.bash_history 2> /dev/null
