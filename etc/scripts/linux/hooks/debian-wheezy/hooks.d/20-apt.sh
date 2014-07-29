#!/bin/bash

#
#  Add french repository
#
cat <<EOF > $MNT_DIR/etc/apt/sources.list
deb http://ftp.fr.debian.org/debian/ wheezy main
deb-src http://ftp.fr.debian.org/debian/ wheezy main

deb http://security.debian.org/ wheezy/updates main
deb-src http://security.debian.org/ wheezy/updates main

# wheezy-updates, previously known as 'volatile'
deb http://ftp.fr.debian.org/debian/ wheezy-updates main
deb-src http://ftp.fr.debian.org/debian/ wheezy-updates main

deb http://ftp.fr.debian.org/debian wheezy-backports main
EOF

#
#  Update
#
LANG=C DEBIAN_FRONTEND=noninteractive chroot $MNT_DIR apt-get update


#
#  Print for debugging
#
_debug_file $MNT_DIR/etc/apt/sources.list
