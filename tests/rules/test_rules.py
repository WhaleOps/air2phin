from airphin.core.rules.loader import path_rule
from airphin.utils.file import read_yaml

MUST_HAVE_ATTR = ["name", "description", "migration"]


all_rules = [path for path in path_rule.glob("**/*") if path.is_file()]


def test_rules_suffix() -> None:
    for rule in all_rules:
        assert rule.suffix == ".yaml", f"Rule file {rule} must have suffix .yaml"


def test_rule_file_must_attr() -> None:
    for rule in all_rules:
        content = read_yaml(rule)
        for attr in MUST_HAVE_ATTR:
            assert attr in content, f"Rule file {rule} must have attribute {attr}"


def test_rules_module_pair() -> None:
    for rule in all_rules:
        content = read_yaml(rule)
        migration = content["migration"]
        if "module" in migration:
            module = migration["module"]
            assert (
                "src" in module
            ), f"Rule file {rule} migration.module pair key `src` not exists."
            assert (
                "dest" in module
            ), f"Rule file {rule} migration.module pair key `dest` not exists."


def test_rules_param_pair() -> None:
    for rule in all_rules:
        content = read_yaml(rule)
        migration = content["migration"]
        if "parameter" in migration:
            for params in migration["parameter"]:
                assert (
                    "src" in params.keys()
                ), f"Rule file {rule} migration.parameter pair key `src` not exists."
                assert (
                    "dest" in params.keys()
                ), f"Rule file {rule} migration.parameter pair key `dest` not exists."


def test_rules_module_src_list_or_str() -> None:
    for rule in all_rules:
        content = read_yaml(rule)
        migration = content["migration"]
        if "module" in migration:
            src = migration["module"]["src"]
            assert isinstance(
                src, (list, str)
            ), f"Rule file {rule} migration.module.src must be list or str."


def test_rules_module_src_duplicate() -> None:
    exists = set()
    for rule in all_rules:
        content = read_yaml(rule)
        migration = content["migration"]
        if "module" in migration:
            src = migration["module"]["src"]
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
