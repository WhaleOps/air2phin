class Token:
    """Constants token for air2phin."""

    QUESTION: str = "?"
    COMMA: str = ","
    POINT: str = "."
    SPACE: str = " "
    ZERO: str = "0"
    IMPORT: str = "import"
    STRING: str = "str"
    CODE: str = "code"
    NEW_LINE: str = "\n"


class Keyword:
    """Constants keywords for air2phin."""

    MIGRATE_MARK: str = "-air2phin"
    WORKFLOW_SUBMIT: str = "submit"
    AIRFLOW_DAG_SCHEDULE: str = "schedule_interval"
    AIRFLOW_DAG: str = "airflow.DAG"
    AIRFLOW_DAG_SIMPLE: str = "DAG"
    DEFAULT_SCHEDULE: str = "0 0 0 * * ? *"


class Regexp:
    """Constants regular expression for air2phin."""

    PATH_YAML: str = "*.yaml"
    PATH_PYTHON: str = "*.py"
    PATH_ALL: str = "**/*"


class ConfigKey:
    """Constants config file for air2phin."""

    NAME: str = "name"

    EXAMPLE: str = "examples"

    MIGRATION: str = "migration"
    MODULE: str = "module"
    PARAMETER: str = "parameter"

    ACTION: str = "action"
    SOURCE: str = "src"
    DESTINATION: str = "dest"

    KW_REPLACE: str = "replace"
    KW_ADD: str = "add"
    KW_REMOVE: str = "remove"

    ARGUMENT: str = "arg"
    DEFAULT: str = "default"
    TYPE: str = "type"
    VALUE: str = "value"


class Number:
    """Constants number for air2phin."""

    SCHEDULE_TOTAL_NUM: int = 9
    SCHEDULE_SPACE_NUM: int = 4
