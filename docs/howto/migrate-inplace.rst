Migration Files Inplace
=======================

Air2phin will create a new file with the addition ``-ariphin`` as a stem suffix with users run migrate command
:code:`air2phin migrate /PATH/TO/FILE`, which means the new file named ``/PATH/TO/FILE-air2phin`` will be created and
all migrated contents in ``/PATH/TO/FILE-air2phin``.

If you want to replace the existing file with the migrated content directly instead of creating a new file to keep
them, you can use the options argument :code:`--inplace` or :code:`-i` for :code:`air2phin migrate` subcommand. Option
:code:`--inplace` and :code:`-i` work for multiple files and directories, for more detail please see :doc:`../cli`

.. note::

    Please make sure you already backup all of your source files, or make sure they under version control system
    when you run migrate command with option argument :code:`--inplace`, otherwise your source content will be lost.
