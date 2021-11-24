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
