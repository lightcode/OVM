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