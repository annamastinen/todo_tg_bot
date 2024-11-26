class Task:
    def __init__(self):
        self.time = None
        self.date = None
        self.duration = None  # продолжительность
        self.content = None  # содержание

    def is_ready(self) -> bool:
        parameters = [self.time, self.date, self.duration, self.content]
        return all(x is not None for x in parameters)


def log_calendar(google_id):
    pass
    return google_id


def add_task_google(current_task):
    pass
