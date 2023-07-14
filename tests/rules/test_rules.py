from typing import Any, Dict

from air2phin.constants import ConfigKey
from air2phin.core.rules.config import Config
from air2phin.core.rules.loader import path_rule
from air2phin.utils.file import read_yaml

ROOT_MUST_HAVE_ATTR = ["name", "description", "migration", "examples"]
EXAMPLES_MUST_HAVE_ATTR = ["description", "src", "dest"]

all_rules = [path for path in path_rule.glob("**/*") if path.is_file()]


def test_suffix() -> None:
    for rule in all_rules:
        assert rule.suffix == ".yaml", f"Rule file {rule} must have suffix .yaml"


def test_file_must_have_attr() -> None:
    for rule in all_rules:
        content = read_yaml(rule)
        for attr in ROOT_MUST_HAVE_ATTR:
            assert attr in content, f"Rule file {rule} must have attribute {attr}"


def module_add_rm(action: Dict[str, Any]) -> bool:
    return ConfigKey.MODULE in action


def test_module_action_type() -> None:
    for rule in all_rules:
        content = read_yaml(rule)
        migration = content["migration"]

        # will raise error if more than one action in :func:``get_module_action``
        Config.get_module_action(migration, ConfigKey.KW_REPLACE)

        add = Config.get_module_action(migration, ConfigKey.KW_ADD)
        if add:
            assert isinstance(
                add[ConfigKey.MODULE], (str, list)
            ), f"Rule file {rule} `add` action value must with type str or list."

        remove = Config.get_module_action(migration, ConfigKey.KW_REMOVE)
        if remove:
            assert isinstance(
                remove[ConfigKey.MODULE], (str, list)
            ), f"Rule file {rule} `remove` action value must with type str or list."


def test_module_action_attr() -> None:
    for rule in all_rules:
        content = read_yaml(rule)
        actions = content["migration"]["module"]
        for action in actions:
            assert (
                ConfigKey.ACTION in action
            ), "Rule {rule} module each item must have attr action."
            if action[ConfigKey.ACTION] in {ConfigKey.KW_REMOVE, ConfigKey.KW_ADD}:
                assert module_add_rm(
                    action
                ), "Rule {rule} module action `remove` or `add` do not have must exits attr."
            elif action[ConfigKey.ACTION] == ConfigKey.KW_REPLACE:
                assert action_replace(
                    action
                ), "Rule {rule} parameter action `replace` do not have must exits attr."
            else:
                raise ValueError(
                    "Rule {rule} parameter action must with specific value."
                )


def test_module_action_replace() -> None:
    for rule in all_rules:
        content = read_yaml(rule)
        migration = content["migration"]
        if "module" in migration:
            replace = Config.get_module_action(migration, ConfigKey.KW_REPLACE)
            assert (
                "src" in replace
            ), f"Rule file {rule} migration.module pair key `src` not exists."
            assert (
                "dest" in replace
            ), f"Rule file {rule} migration.module pair key `dest` not exists."


def test_module_action_replace_src_list_or_str() -> None:
    for rule in all_rules:
        content = read_yaml(rule)
        migration = content["migration"]
        if "module" in migration:
            replace = Config.get_module_action(migration, ConfigKey.KW_REPLACE)
            src = replace["src"]
            assert isinstance(
                src, (list, str)
            ), f"Rule file {rule} migration.module.src must be list or str."


def test_module_action_replace_src_duplicate() -> None:
    exists = set()
    for rule in all_rules:
        content = read_yaml(rule)
        migration = content["migration"]
        if "module" in migration:
            replace = Config.get_module_action(migration, ConfigKey.KW_REPLACE)
            src = replace["src"]
            if isinstance(src, list):
                for s in src:
                    assert (
                        s not in exists
                    ), f"Rule file {rule} migration.module.src {s} duplicate."
                    exists.add(s)
            elif isinstance(src, str):
                assert (
                    src not in exists
                ), f"Rule file {rule} migration.module.src {src} duplicate."
                exists.add(src)


def test_example_must_attr() -> None:
    for rule in all_rules:
        content = read_yaml(rule)
        examples = content["examples"]
        for key in examples:
            example = examples[key]
            assert all(
                attr in example for attr in EXAMPLES_MUST_HAVE_ATTR
            ), f"Rule file {rule} examples missing must have attribute {EXAMPLES_MUST_HAVE_ATTR}"


def test_param_action_type() -> None:
    for rule in all_rules:
        content = read_yaml(rule)
        parameter = content["migration"].get("parameter", [])
        for params in parameter:
            assert (
                ConfigKey.ACTION in params
            ), "Rule {rule} all parameter must have attr action."
            if params[ConfigKey.ACTION] == ConfigKey.KW_ADD:
                assert param_action_add(
                    params
                ), "Rule {rule} parameter action `add` do not have must exits attr."
            elif params[ConfigKey.ACTION] == ConfigKey.KW_REMOVE:
                assert param_action_remove(
                    params
                ), "Rule {rule} parameter action `remove` do not have must exits attr."
            elif params[ConfigKey.ACTION] == ConfigKey.KW_REPLACE:
                assert action_replace(
                    params
                ), "Rule {rule} parameter action `replace` do not have must exits attr."
            else:
                raise ValueError(
                    "Rule {rule} parameter action must with specific value."
                )


def action_replace(param: Dict[str, Any]) -> bool:
    return ConfigKey.SOURCE in param and ConfigKey.DESTINATION in param


def param_action_add(param: Dict[str, Any]) -> bool:
    return (
        ConfigKey.ARGUMENT in param
        and ConfigKey.DEFAULT in param
        and ConfigKey.TYPE in param[ConfigKey.DEFAULT]
        and ConfigKey.VALUE in param[ConfigKey.DEFAULT]
    )


def param_action_remove(param: Dict[str, Any]) -> bool:
    return ConfigKey.ARGUMENT in param
