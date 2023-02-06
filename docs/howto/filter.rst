Filter Files with Pattern
=========================

Airphin will only migrate files pass its filter rule, default is :code:`*.py` (include all python files in given path).

Custom Include Pattern
----------------------

Migration include files behavior can be overwrite by option argument :code:`--include` or :code:`-I`, for example
if you want to migrate all python files with prefix ``airflow``, you can use command

.. code-block:: bash

    airphin migrate --include 'airflow*.py' /PATH/TO/DIRECTORY

Custom Exclude Pattern
----------------------

Migration all files exclude some files or directory can use option argument :code:`--exclude` or :code:`-E`, for example
if you want to exclude all python files in package ``utils``, you can use command

.. code-block:: bash

    airphin migrate --exclude 'utils/*.py' /PATH/TO/DIRECTORY

.. note::

    Both include and exclude option argument is respect `Path.rglob <https://docs.python.org/3/library/pathlib.html#pathlib.Path.rglob>`_
    rule, if you want to include add Python files match ``dag-*.py`` in directory ``~/airflow/dags`` expect ``utils`` directory, you can
    use :code:`airphin migrate --include 'dag-*.py' --exclude 'utils/*' ~/airflow/dags`

For more detail please see :doc:`../cli`.
