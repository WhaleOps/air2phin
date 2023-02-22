.. airphin documentation master file, created by
   sphinx-quickstart on Sat Dec  3 23:11:01 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Airphin's Documentation
=======================

Airphin is a tool for migrating Airflow DAGs to DolphinScheduler Python API.

It is a rule-based AST transformer, using `LibCST <https://github.com/Instagram/LibCST>`_ to parse and transform Python code,
and Yaml file to define the transformation rules.


.. toctree::
   :maxdepth: 2

   start
   cli
   fake
   howto/index
   arch
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
