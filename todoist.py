class Todo:
    def __init__(self):
        self.time = None
        self.date = None
        self.content = None  # содержание

    def is_ready(self) -> bool:
        parameters = [self.time, self.date, self.content]
        return all(x is not None for x in parameters)


def log_todoist():
    pass
    return todoist_id


def add_todo(current_todo):
    pass
