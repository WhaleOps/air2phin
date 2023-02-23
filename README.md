# Air2phin

[![PyPi Version](https://img.shields.io/pypi/v/air2phin.svg?style=flat-square&logo=PyPi)](https://pypi.org/project/air2phin/)
[![PyPi Python Versions](https://img.shields.io/pypi/pyversions/air2phin.svg?style=flat-square&logo=python)](https://pypi.org/project/air2phin/)
[![PyPi License](https://img.shields.io/:license-Apache%202-blue.svg?style=flat-square)](https://raw.githubusercontent.com/WhaleOps/air2phin/main/LICENSE)
[![PyPi Status](https://img.shields.io/pypi/status/air2phin.svg?style=flat-square)](https://pypi.org/project/air2phin/)
[![Downloads](https://pepy.tech/badge/air2phin/month)](https://pepy.tech/project/air2phin)
[![Coverage Status](https://img.shields.io/codecov/c/github/WhaleOps/air2phin/main.svg?style=flat-square)](https://codecov.io/github/WhaleOps/air2phin?branch=main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat-square&labelColor=ef8336)](https://pycqa.github.io/isort)
[![CI](https://github.com/WhaleOps/air2phin/actions/workflows/ci.yaml/badge.svg)](https://github.com/WhaleOps/air2phin/actions/workflows/ci.yaml)
[![Documentation Status](https://readthedocs.org/projects/air2phin/badge/?version=latest)](https://air2phin.readthedocs.io/en/latest/?badge=latest)

air2phin is a tool for migrating Airflow DAGs to DolphinScheduler Python API.

## Installation

For now, it just for test and without publish to pypi but will be adding in the future.
You could still install locally by yourself.

```shell
python -m pip install --upgrade air2phin
```

## Quick Start

Here will give a quick example to show how to migrate base on standard input.

```shell
# Quick test the migrate rule for standard input
# Can also add option `--diff` to see the diff detail of this migrate
air2phin test "from airflow.operators.bash import BashOperator

test = BashOperator(
    task_id='test',
    bash_command='echo 1',
)
"
```

And you will see the migrated result in the standard output. air2phin can only migrate standard input, it can
also migrate file, directory and even can use in your python code. For more detail, please see [our usage](https://air2phin.readthedocs.io/en/latest/start.html#usage).

## Documentation

The documentation host on read the doc and is available at [https://air2phin.readthedocs.io](https://air2phin.readthedocs.io).

## Support Statement

For now, we support following statement from Airflow's DAG files

### DAG

| Before Migration             | After Migration                                                            |
|------------------------------|----------------------------------------------------------------------------|
| `from airflow import DAG`    | `from pydolphinscheduler.core.process_definition import ProcessDefinition` |
| `with DAG(...) as dag: pass` | `with ProcessDefinition(...) as dag: pass`                                 |

### Operators

#### Dummy Operator

| Before Migration                                             | After Migration                                               |
|--------------------------------------------------------------|---------------------------------------------------------------|
| `from airflow.operators.dummy_operator import DummyOperator` | `from pydolphinscheduler.tasks.shell import Shell`            |
| `from airflow.operators.dummy import DummyOperator`          | `from pydolphinscheduler.tasks.shell import Shell`            |
| `dummy = DummyOperator(...)`                                 | `dummy = Shell(..., command="echo 'airflow dummy operator'")` |

#### Shell Operator

| Before Migration                                  | After Migration                                    |
|---------------------------------------------------|----------------------------------------------------|
| `from airflow.operators.bash import BashOperator` | `from pydolphinscheduler.tasks.shell import Shell` |
| `bash = BashOperator(...)`                        | `bash = Shell(...)`                                |

#### Spark Sql Operator

| Before Migration                                                    | After Migration                                |
|---------------------------------------------------------------------|------------------------------------------------|
| `from airflow.operators.spark_sql_operator import SparkSqlOperator` | `from pydolphinscheduler.tasks.sql import Sql` |
| `spark = SparkSqlOperator(...)`                                     | `spark = Sql(...)`                             |

#### Python Operator

| Before Migration                                               | After Migration                                      |
|----------------------------------------------------------------|------------------------------------------------------|
| `from airflow.operators.python_operator import PythonOperator` | `from pydolphinscheduler.tasks.python import Python` |
| `python = PythonOperator(...)`                                 | `python = Python(...)`                               |
