class TOKEN:
    """Constants token for airphin."""

    QUESTION: str = "?"
    COMMA: str = ","
    POINT: str = "."
    SPACE: str = " "
    ZERO: str = "0"
    IMPORT: str = "import"
    STRING: str = "str"
    CODE: str = "code"
    NEW_LINE: str = "\n"


class KEYWORD:
    """Constants keywords for airphin."""

    MIGRATE_MARK: str = "-airphin"
    WORKFLOW_SUBMIT: str = "submit"
    AIRFLOW_DAG_SCHEDULE: str = "schedule_interval"
    AIRFLOW_DAG: str = "airflow.DAG"
    DEFAULT_SCHEDULE: str = "0 0 0 * * ? *"


class REGEXP:
    """Constants regular expression for airphin."""

    PATH_YAML: str = "*.yaml"
    PATH_PYTHON: str = "*.py"
    PATH_ALL: str = "**/*"


class CONFIG:
    """Constants config file for airphin."""

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


class NUMBER:
    """Constants number for airphin."""

    SCHEDULE_TOTAL_NUM: int = 9
    SCHEDULE_SPACE_NUM: int = 4
