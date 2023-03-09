Fake Module
===========

Module Fake is an advanced usage of air2phin, which makes it possible for some airflow's DAG contain :code:`airflow.hooks`
or other airflow's concept can migrate and run in dolphinscheduler without modifying any hook code.

.. note::

    1. The network of dolphinscheduler worker can connect to dolphinscheduler metadata database is be required, when
       you want to execute the migrated DAG with :code:`air2phin.fake`.

    2. Air2phin fake module is an option dependency, which means you can install it via pip with :code:`air2phin[fake]`.

       .. code-block:: bash
        
           python -m pip install --upgrade air2phin[fake]

.. toctree::
   :maxdepth: 2

   hooks
   models
