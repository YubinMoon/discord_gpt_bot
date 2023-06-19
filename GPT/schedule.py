class Schedule:
    def __init__(self):
        self.schedule = {}

    def create_schedule(self, name: str, description: str, cron: str):
        self.schedule[name] = {"description": description, "cron": cron}

    def read_schedule(self, name: str):
        return self.schedule[name]

    def update_schedule(self, name: str, description: str, cron: str):
        self.schedule[name] = {"description": description, "cron": cron}

    def delete_schedule(self, name: str):
        del self.schedule[name]
