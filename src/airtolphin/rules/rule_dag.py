from _ast import Call, Name


class Dag:
    def __init__(self, node: Call) -> None:
        self.node = node

    def run(self) -> None:
        if isinstance(self.node, Call):
            if isinstance(self.node.func, Name):
                if self.node.func.id == "DAG":
                    self.node.func.id = "ProcessDefinition"
            for keyword in self.node.keywords:
                if keyword.arg == "schedule_interval":
                    keyword.arg = "schedule"
                if keyword.arg == "start_date":
                    keyword.arg = "start_time"
