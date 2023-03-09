from typing import Any


class Variable:
    """Mock airflow.models.Variable class, make migrator do less thing."""

    @classmethod
    def get(cls, key: str) -> str:
        """Modck airflow.models.Variable.get method, only return income parameter."""
        return key

    @classmethod
    def set(cls, key: str, value: Any) -> str:
        """Mock airflow.models.Variable.set method, do nothing."""

    @classmethod
    def update(cls, key: str, value: Any) -> str:
        """Mock airflow.models.Variable.update method, do nothing."""

    @classmethod
    def delete(cls, key: str) -> str:
        """Mock airflow.models.Variable.delete method, do nothing."""
