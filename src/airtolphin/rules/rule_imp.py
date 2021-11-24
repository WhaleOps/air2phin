from _ast import ImportFrom


class Package:
    def __init__(self, node: ImportFrom):
        self.node = node

    def run(self):
        # DAG
        if self.node.module == "airflow":
            self.node.module = 'pydolphinscheduler.core.process_definition'
            for name in self.node.names:
                if name.name == "DAG":
                    name.name = "ProcessDefinition"
                    name.asname = None
        # Operator
        if self.node.module == "airflow.operators.bash":
            self.node.module = 'pydolphinscheduler.tasks.shell'
            for name in self.node.names:
                if name.name == "BashOperator":
                    name.name = "Shell"
                    name.asname = None
