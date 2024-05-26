from datetime import datetime
from typing import Optional


class Project:
    id: str
    title: str


class Board:
    id: str
    title: str


class Deadline:
    deadline: datetime
    start_date: Optional[datetime]
    with_time: Optional[bool]


class TimeTracking:
    plan: int
    work: int


class Task:
    id: str
    title: str
    description: str
    archived: bool
    completed: bool
    deadline: Optional[Deadline]
    time_tracking: Optional[TimeTracking]

    def __init__(self, obj: dict):
        self.id = obj["id"]
        self.title = obj["title"]
        self.archived = obj["archived"] if "archived" in obj else False
        self.completed = obj["completed"] if "completed" in obj else False
        self.deadline = None
        if "deadline" in obj:
            deadline = Deadline()
            dl = obj["deadline"]
            deadline.deadline = datetime.fromtimestamp(dl["deadline"] / 1000)
            deadline.start_date = (
                datetime.fromtimestamp(dl["startDate"] / 1000)
                if "startDate" in dl
                else None
            )
            deadline.with_time = dl["withTime"] if "withTime" in dl else None
            self.deadline = deadline
        self.description = obj["description"] if "description" in obj else ""
        self.time_tracking = None
        if "timeTracking" in obj:
            time_tracking = TimeTracking()
            time_tracking.plan = obj["timeTracking"]["plan"]
            time_tracking.work = obj["timeTracking"]["work"]
            self.time_tracking = time_tracking
