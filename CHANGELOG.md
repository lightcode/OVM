# Changelog


## Version 0.4 (08/08/2015)

- Network: remove dependency to libvirt network
- Network: rename `openvswitch` to `bridge`. It support all kind of Linux bridge
- Add an IPv4 management system
- Add Python 2 support
- Modify the setup script to accept non-root installation


## Version 0.3 (07/12/2015)

- New metadata API: store arbitrary key/value data
- Add metadata support in templates
- Storage: LVM driver
- New command: `vm autostart`
- Add a default storage driver
- New command: `vm unset`
- Modify the command `vm set`
- Improve `vm top`: add CPU host graph, info about disks and network
- Create an abstract storage driver


## Version 0.2 (06/30/2015)

- Replace JSON configuration file by YAML configuration file
- Add bulk operations : remove, start and stop
- Add the command `vm top`
- Add commands to save/restore VMs
- Refactor contextualization scripts with guestfish


## Version 0.1

- First version of the project
