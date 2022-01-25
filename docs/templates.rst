
Configure OS templates
======================

You can create your own templates based on those given in the
``/etc/ovm/templates/examples``. In this case, you must modify
parameters in the YAML file. For example, you have to edit the path to
the disk in the file:

.. code-block:: yaml

    main_disk:
      path: /mnt/pool-templates/debian-wheezy.qcow2


Templates are stored into the ``/etc/ovm/templates`` directory.
Templates names have to end with ``.yml`` extension.
