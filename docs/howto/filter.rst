Filter Files with Pattern
=========================

Airphin will only migrate files pass its filter rule, default is :code:`**/*.py` (all python files in given path).
This behavior can be overwrite by option argument :code:`--filter` or :code:`--f`, for example if you want to covert all python
files with prefix ``airflow``, you can use command

.. code-block:: bash

    airphin covert --filter '**/airflow*.py' /PATH/TO/DIRECTORY


For more detail please see :doc:`../cli`.
