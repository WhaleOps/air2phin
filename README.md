# airtolphin

[![PyPi Version](https://img.shields.io/pypi/v/airtolphin.svg?style=flat-square&logo=PyPi)](https://pypi.org/project/airtolphin/)
[![PyPi Python Versions](https://img.shields.io/pypi/pyversions/airtolphin.svg?style=flat-square&logo=python)](https://pypi.org/project/airtolphin/)
[![PyPi License](https://img.shields.io/:license-Apache%202-blue.svg?style=flat-square)](https://raw.githubusercontent.com/WhaleOps/airtolphin/main/LICENSE)
[![PyPi Status](https://img.shields.io/pypi/status/airtolphin.svg?style=flat-square)](https://pypi.org/project/airtolphin/)
[![Downloads](https://pepy.tech/badge/airtolphin/month)](https://pepy.tech/project/airtolphin)
[![Coverage Status](https://img.shields.io/codecov/c/github/WhaleOps/airtolphin/main.svg?style=flat-square)](https://codecov.io/github/WhaleOps/airtolphin?branch=main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat-square&labelColor=ef8336)](https://pycqa.github.io/isort)
[![CI](https://github.com/WhaleOps/airtolphin/actions/workflows/ci.yaml/badge.svg)](https://github.com/WhaleOps/airtolphin/actions/workflows/ci.yaml)

Airflow to DolphinScheduler migration tool.

## Installation

For now, it just for test and without publish to pypi but will be adding in the future.
You could still install locally by yourself.

```shell
python pip install --upgrade airtolphin
```

## Quick Start

Get example airflow DAG file via terminal:

```shell
wget https://raw.githubusercontent.com/WhaleOps/airtolphin/main/examples/airflow/tutorial.py
```

Convert it to Apache DolphinScheduler Python API define:

```shell
airtolphin tutorial.py
```

## Support Statement

For now, we support following conversion from Airflow's DAG files

### DAG

| Before Conversion | After Conversion |
| ----- | ----- |
| `from airflow import DAG` | `from pydolphinscheduler.core.process_definition import ProcessDefinition` |
| `with DAG(...) as dag: pass` | `with ProcessDefinition(...) as dag: pass` |

### Operators

#### Dummy Operator

| Before Conversion | After Conversion |
| ----- | ----- |
| `from airflow.operators.dummy_operator import DummyOperator` | `from pydolphinscheduler.tasks.shell import Shell` |
| `from airflow.operators.dummy import DummyOperator` | `from pydolphinscheduler.tasks.shell import Shell` |
| `dummy = DummyOperator(...)` | `dummy = Shell(..., command="echo 'airflow dummy operator'")` |

#### Shell Operator

| Before Conversion | After Conversion |
| ----- | ----- |
| `from airflow.operators.bash import BashOperator` | `from pydolphinscheduler.tasks.shell import Shell` |
| `bash = BashOperator(...)` | `bash = Shell(...)` |

#### Spark Sql Operator

| Before Conversion | After Conversion |
| ----- | ----- |
| `from airflow.operators.spark_sql_operator import SparkSqlOperator` | `from pydolphinscheduler.tasks.sql import Sql` |
| `spark = SparkSqlOperator(...)` | `spark = Sql(...)` |

#### Python Operator

| Before Conversion                                              | After Conversion                                     |
|----------------------------------------------------------------|------------------------------------------------------|
| `from airflow.operators.python_operator import PythonOperator` | `from pydolphinscheduler.tasks.python import Python` |
| `python = PythonOperator(...)`                                 | `python = Python(...)`                               |
