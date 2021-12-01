import libcst as cst


class From:
    """Covert import from statement."""

    def __init__(self, node: cst.ImportFrom):
        self.node = node

    def run(self) -> cst.ImportFrom:
        module = self.node.module
        if isinstance(module, cst.Attribute):
            # covert `airflow.operators.bash`
            if module.attr.value == "bash" and module.value.attr.value == "operators":
                self.node = self.node.with_changes(
                    module=cst.Attribute(
                        cst.Attribute(
                            cst.Name("pydolphinscheduler"),
                            cst.Name("tasks"),
                        ),
                        cst.Name("shell"),
                    )
                )
        if isinstance(module, cst.Name):
            # covert `airflow`
            if module.value == "airflow":
                self.node = self.node.with_changes(
                    module=cst.Attribute(
                        cst.Attribute(
                            cst.Name("pydolphinscheduler"),
                            cst.Name("core"),
                        ),
                        cst.Name("process_definition"),
                    )
                )
        for import_alias in self.node.names:
            # covert `DAG`
            if import_alias.name.value == "DAG":
                self.node = self.node.with_changes(
                    names=(cst.ImportAlias(cst.Name("ProcessDefinition")),)
                )
            # covert `BashOperator`
            if import_alias.name.value == "BashOperator":
                self.node = self.node.with_changes(
                    names=(cst.ImportAlias(cst.Name("Shell")),)
                )
        return self.node
