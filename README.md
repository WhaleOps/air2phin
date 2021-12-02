# airtolphin

Airflow to DolphinScheduler migration tool.

## Installation

For now, it just for test and without publish to pypi but will be adding in the future.
You could still install locally by yourself.

```shell
pip install -e .
```

## Quick Start

We have an example told you how it works in `./example/transfer_tutorial.py`, it migrates
Airflow's tutorial in path `./example/airflow/tutorial.py` to DolphinScheduler's Python
API. You could run it by

```shell
python ./example/transfer_tutorial.py
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
