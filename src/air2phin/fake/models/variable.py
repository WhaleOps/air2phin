from typing import Any


class Variable:
    """Mock airflow.models.Variable class, make migrator do less thing."""

    @classmethod
    def get(
        cls,
        key: str,
        default_var: Any = None,
        *args,
        **kwargs,
    ) -> str:
        """Modck airflow.models.Variable.get method, only return income parameter."""
        return key if default_var is None else default_var

    @classmethod
    def set(
        cls,
        key: str,
        value: Any,
        *args,
        **kwargs,
    ) -> str:
        """Mock airflow.models.Variable.set method, do nothing."""

    @classmethod
    def update(
        cls,
        key: str,
        value: Any,
        *args,
        **kwargs,
    ) -> str:
        """Mock airflow.models.Variable.update method, do nothing."""

    @classmethod
    def delete(
        cls,
        key: str,
        *args,
        **kwargs,
    ) -> str:
        """Mock airflow.models.Variable.delete method, do nothing."""
