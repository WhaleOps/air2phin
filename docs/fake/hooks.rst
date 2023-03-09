fake.hooks
==========

Some users will use hook in Python operator or custom operator, for example, we have a custom Python task like:

.. code-block:: python

    from contextlib import closing
    from airflow.operators.python import PythonOperator
    from airflow.providers.postgres.hooks.postgres import PostgresHook

    def demo():
        connection = PostgresHook.get_connection("postgres_default")
        hook = PostgresHook(connection=connection)
        with closing(hook.get_conn()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("SELECT 1")
                print(cursor.fetchall())

    demo = PythonOperator(
        task_id="demo",
        python_callable=test,
    )

when you use air2phin to migrate it to dolphinscheduler python SDK, the result will be:

.. code-block:: python

    from contextlib import closing
    from pydolphinscheduler.tasks.python import Python
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    
    def demo():
        connection = PostgresHook.get_connection("postgres_default")
        hook = PostgresHook(connection=connection)
        with closing(hook.get_conn()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("SELECT 1")
                print(cursor.fetchall())
    
    demo = Python(
        name="demo",
        definition=test,
    )

As you can see, the task ``demo``'s class name and its attributes is migrated to dolphinscheduler's, but the function
``demo`` is not migrated, because it is a function and not an airflow task.

We can find it used :code:`airflow.PostgresHook` to connect to airflow's metadata database, and then execute SQL.
This code cannot be run in dolphinscheduler python SDK, because :code:`airflow.PostgresHook` is a concept of airflow
only. There are two ways if you want it successfully run by dolphinscheduler python SDK, one is to rewrite the function
to make it work with dolphinscheduler, another is to use :code:`air2phin.fake` without any modification.

Usage
-----

Basic Usage
~~~~~~~~~~~

When you run :code:`air2phin migrate` subcommand, it will automatically detect if there are any :code:`airflow.hooks`
in your DAG. If so, it will automatically migrate the hook module into module :code:`air2phin.fake`, which means
you can do nothing for hook migration.

.. note::

    Module :code:`air2phin.fake` only support two hooks migration, which are :code:`airflow.PostgresHook`
    and :code:`airflow.MySqlHook`. If you want to migrate other hooks, you can use :doc:`custom rules <../howto/custom-rules>`

With :code:`air2phin.fake` module, the original DAG can be migrated to:

.. code-block:: python

    from contextlib import closing
    from pydolphinscheduler.tasks.python import Python
    from air2phin.fake.hooks.postgres import PostgresHook
    
    def demo():
        connection = PostgresHook.get_connection("postgres_default")
        hook = PostgresHook(connection=connection)
        with closing(hook.get_conn()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("SELECT 1")
                print(cursor.fetchall())
    
    demo = Python(
        name="demo",
        definition=test,
    )

And you can see air2phin migrate the hook module from :code:`airflow.providers.postgres.hooks.postgres.PostgresHook` to
:code:`air2phin.fake.hooks.postgres.PostgresHook`. When you run the code in dolphinscheduler, :code:`air2phin.fake` will
query dolphinscheduler metadata database to get the connection information, you can use it just like you use
:code:`airflow.providers.postgres.hooks.postgres.PostgresHook`

Requirement
^^^^^^^^^^^

- The network of dolphinscheduler workers can connect to dolphinscheduler metadata database is be required. Because
  :code:`air2phin.fake` will query the connection information from dolphinscheduler metadata database.
- The data source named ``postgres_default`` (same as airflow's connection) must exist in dolphinscheduler metadata
  database for air2phin.fake to get the connection information.
- Methods can connect to the dolphinscheduler metabase, any one of the following is acceptable:

  - Package `pydolphinscheduler <https://pypi.org/project/apache-dolphinscheduler>`_ is installed in the
    dolphinscheduler worker's python environment, and make sure the
    `token is correct <https://dolphinscheduler.apache.org/python/main/concept.html#authentication-token>`_.

  - An environment variable named ``AIR2PHIN_FAKE_CONNECTION`` set with the connection information of the
    dolphinscheduler metadata database. It is use
    `sqlalchemy connection string format <https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls>`_ 
    for example: :code:`postgresql+psycopg2://scott:tiger@localhost:5432/mydatabase`. We recommend you use
    dolphinscheduler's `Environmental Management <https://dolphinscheduler.apache.org/en-us/docs/3.1.3/guide/security>`_
    to do that, all you should do is add a new environment with content like

    .. code-block:: bash
    
        export AIR2PHIN_FAKE_CONNECTION=postgresql+psycopg2://scott:tiger@localhost:5432/mydatabase

    and use it in your dolphinscheduler's Python task.

  .. note::

      The priority of package ``pydolphinscheduler`` is higher than the environment variables
      ``AIR2PHIN_FAKE_CONNECTION``. If you want less connections for your dolphinscheduler metadata database,
      please use package pydolphinscheduler which will reuse the connection pool of dolphinscheduler itself.
      But if you do not case much of the connections number(such as do not have many tasks using air2phin.fake),
      or do not want to install pydolphinscheduler dolphinscheduler worker, environment variable ``AIR2PHIN_FAKE_CONNECTION``
      is a better choice.

With Non-unique Datasource Name 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dolphinscheduler datasource uses joint unique index :code:`(type, name)` to ensure the datasource name is unique.
but the airflow connection id is unique. So when your dolphinscheduler metadata database has two datasource with the same name,
air2phin.fake will raise an error, in this case, you should add the type of datasource

.. code-block:: python

    # When you have two datasource named "postgres_default" in the dolphinscheduler metadata database
    from air2phin.fake.hooks.postgres import PostgresHook
    connection = PostgresHook.get_connection("postgres_default")
    
    # You should add the type of datasource, into the format "type.name"
    from air2phin.fake.hooks.postgres import PostgresHook
    connection = PostgresHook.get_connection("postgres.postgres_default")

or you can change your datasource name to make it unique.

.. code-block:: python

    # Change the datasource name to make it unique, for example, change from "postgres_default" to "postgres_default_uniq"
    from air2phin.fake.hooks.postgres import PostgresHook
    connection = PostgresHook.get_connection("postgres_default_uniq")

And dolphinscheduler only supports the following types of datasource, which mean your type must be one of them:

- mysql
- postgresql
- hive
- spark
- clickhouse
- oracle
- sqlserver
- db2
- presto
- h2
- redshift
- dameng
- starrocks
