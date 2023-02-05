class TOKEN:
    """Constants token for airphin."""

    IMPORT: str = "import"
    COMMA: str = ","
    POINT: str = "."
    STRING: str = "str"
    CODE: str = "code"
    NEW_LINE: str = "\n"


class KEYWORD:
    """Constants keywords for airphin."""

    MIGRATE_MARK: str = "-airphin"


class REGEXP:
    """Constants regular expression for airphin."""

    PATH_YAML: str = "**/*.yaml"
    PATH_PYTHON: str = "**/*.py"


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
