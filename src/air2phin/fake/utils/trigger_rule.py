from enum import Enum


class TriggerRule(str, Enum):
    """Mock trigger rule"""

    ALL_SUCCESS = "all_success"
    ALL_FAILED = "all_failed"
    ALL_DONE = "all_done"
    ONE_SUCCESS = "one_success"
    ONE_FAILED = "one_failed"
    ONE_DONE = "one_done"
    NONE_FAILED = "none_failed"
    NONE_FAILED_OR_SKIPPED = "none_failed_or_skipped"
    NONE_SKIPPED = "none_skipped"
    DUMMY = "dummy"
    ALWAYS = "always"
    NONE_FAILED_MIN_ONE_SUCCESS = "none_failed_min_one_success"
    ALL_SKIPPED = "all_skipped"

    @classmethod
    def is_valid(cls, trigger_rule: str) -> bool:
        """Validates a trigger rule."""
        return trigger_rule in cls.all_triggers()

    @classmethod
    def all_triggers(cls) -> set[str]:
        """Returns all trigger rules."""
        return set(cls.__members__.values())

    def __str__(self) -> str:
        return self.value
