Migration Files Inplace
=======================

Airphin will create new file with addition ``-ariphin`` as stem suffix with users run migrate command
:code:`airphin covert /PATH/TO/FILE`, which mean the new file named ``/PATH/TO/FILE-airphin`` will be create and
all migrated contents in ``/PATH/TO/FILE-airphin``.

If you want to replace the exists file by the migrated content directly instead of create the new file to keep
them, you can use the option argument :code:`--inplace` or :code:`-i` for :code:`airphin covert` subcommand. Option
:code:`--inplace` and :code:`-i` work for multiple files and directories, for more detail please see :doc:`../cli`

.. note::

    Please make sure you already backup all of your source files, or make sure them under version control system
    when you run migrate command with option argument :code:`--inplace`, otherwise your source content will lost.
