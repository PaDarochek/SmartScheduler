"""Data structures for YouGile entities."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Project:
    """YouGile project.

    :param id: Project ID
    :param title: Project name
    """

    id: str
    title: str


@dataclass
class Board:
    """YouGile board.

    :param id: Board ID
    :param title: Board name
    """

    id: str
    title: str


@dataclass
class Deadline:
    """Deadline for the task.

    :param deadline: Due date
    :param start_date: Start date
    """

    deadline: datetime
    start_date: Optional[datetime] = None


@dataclass
class TimeTracking:
    """Time tracking for the task.

    :param plan: Planned amount of hours for task
    :param work: Completed amount of hours for task
    """

    plan: int
    work: int


class Task:
    """YouGile task.

    :param id: Task ID
    :param title: Task name
    :param description: Task description
    :param archived: Flag for archived task
    :param completed: Flag for completed task
    :param deadline: Deadline for task
    :param time_tracking: Time tracking for task
    """

    id: str
    title: str
    description: str
    archived: bool
    completed: bool
    deadline: Optional[Deadline]
    time_tracking: Optional[TimeTracking]

    def __init__(self, obj: dict):
        """Create task from dict with YouGile parameters.

        :param obj: Dictionary to create task from
        :type obj: dict
        """
        self.id = obj["id"]
        self.title = obj["title"]
        self.archived = obj["archived"] if "archived" in obj else False
        self.completed = obj["completed"] if "completed" in obj else False
        self.deadline = None
        if "deadline" in obj:
            dl = obj["deadline"]
            deadline = Deadline(datetime.fromtimestamp(dl["deadline"] / 1000))
            deadline.start_date = (
                datetime.fromtimestamp(dl["startDate"] / 1000)
                if "startDate" in dl
                else None
            )
            self.deadline = deadline
        self.description = obj["description"] if "description" in obj else ""
        self.time_tracking = None
        if "timeTracking" in obj:
            time_tracking = TimeTracking(
                obj["timeTracking"]["plan"], obj["timeTracking"]["work"]
            )
            self.time_tracking = time_tracking
