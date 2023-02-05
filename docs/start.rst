Getting Started
===============

Install
-------

Airphin releases are available on PyPI. The easiest way to install Airphin is via pip, and we highly recommend using
the latest version

.. code-block:: bash

    python -m pip install --upgrade airphin 

Usage
-----

The easiest way to use Airphin is via `cli`_, and you can also use API if you prefer to `programming`_

CLI
~~~

Standard input
^^^^^^^^^^^^^^

The CLI is the easiest way to use Airphin, we will take a quick look at the basic usage of the CLI.

.. code-block:: bash

    # Show all arguments or subcommands of airphin
    airphin --help

    # A simple migrate example base on stdin, and will show migrated result on stdout
    # Can add option argument `--diff` to see the diff detail of this migrate
    airphin test "from airflow.operators.bash import BashOperator
    
    test = BashOperator(
        task_id='test',
        bash_command='echo 1',
    )
    "

Single File
^^^^^^^^^^^

After run the above command, will get the migrated result show in stdout. And the most common usage is migrate
a existing Airflow DAG file, which can be done by :code:`airphin migrate` command. We have a out of box example:

.. code-block:: bash

    # Get example airflow DAG file via terminal
    wget https://raw.githubusercontent.com/WhaleOps/airphin/main/examples/airflow/tutorial.py

    # Run migrate command
    airphin migrate tutorial.py

And the migrated result will in the same directory with stem suffix :code:`-airphin` (by default, also support
:doc:`inplace migrate <howto/migrate-inplace>`), in this case, it will be `tutorial-airphin.py` in current directory.

Multiple Files or Directories
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

airphin can not only migrate one single file, but also works for multiple files and even the whole directory DAGs file,

.. code-block:: bash

    # Covert multiple files
    airphin migrate /PATH/TO/FILE1.py /PATH/TO/FILE2.py

    # Covert all *.py file in directory
    airphin migrate <DIRECTORY>
    
    # Covert all *.py file Airflow DAG directory
    airphin migrate ~/airflow/dags

Same as `single file`_, the migrated result in the same directory as source file, with stem suffix :code:`-airphin`
(by default, also support :doc:`inplace migrate <howto/migrate-inplace>`) to marked.

If you want to deep dive into the CLI, please check the :doc:`cli` section. 

Programming
~~~~~~~~~~~

Airphin also provide API to use in your own program, all you need to do is import :code:`airphin.runner` module and
call :code:`with_str` or :code:`with_file` base on your input type.

For String
^^^^^^^^^^

:code:`with_file` will handle and migrate the input string, and return the migrated string.

.. code-block:: python

    from airphin import runner

    code = """from airflow.operators.bash import BashOperator
    
    test = BashOperator(
        task_id='test',
        bash_command='echo 1',
    )
    """

    migrated = runner.with_str(code)
    print(migrated)

For File
^^^^^^^^

:code:`with_file` will handle and migrate the input file, and write the migrated result with addition :code:`-ariphin` as stem suffix
to the same directory of input file. 

.. code-block:: python

    from airphin import runner

    path = "~/airflow/dags/tutorial.py"

    migrated = runner.with_file(path)
    print(migrated)


What's Next
-----------

- :doc:`cli` if you want to deep dive into CLI usage
- :doc:`arch` if you want to know Airphin's architecture
