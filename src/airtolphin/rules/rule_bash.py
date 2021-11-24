from _ast import Call


class Bash:
    def __init__(self, node: Call) -> None:
        self.node = node

    def run(self) -> None:
        if isinstance(self.node, Call):
            if self.node.func.id == "BashOperator":
                self.node.func.id = "Shell"
            for keyword in self.node.keywords:
                if keyword.arg == "task_id":
                    keyword.arg = "name"
                if keyword.arg == "bash_command":
                    keyword.arg = "command"
