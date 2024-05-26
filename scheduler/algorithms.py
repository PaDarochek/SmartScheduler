from datetime import datetime
from typing import List

from scheduler.data_structures import Task


def relevant(task: Task, start_date: datetime, end_date: datetime) -> bool:
    result = not task.archived and not task.completed
    if task.deadline is not None:
        result = result and task.deadline.deadline > start_date
        if task.deadline.start_date is not None:
            result = result and task.deadline.start_date < end_date
    return result


def get_relevant_tasks(
    tasks: List[Task], start_date: datetime, end_date: datetime
) -> List[Task]:
    tasks = list(filter(lambda x: relevant(x, start_date, end_date), tasks))
    return tasks


def count_deadline_metric(
    task: Task, start_date: datetime, end_date: datetime
) -> float:
    if task.deadline is None:
        return 0
    delta_deadline = (task.deadline.deadline - start_date).total_seconds()
    delta_start = (
        (end_date - task.deadline.start_date).total_seconds()
        / (end_date - start_date).total_seconds()
        if task.deadline.start_date is not None
        else 1
    )
    return delta_start / (delta_deadline**2)


def count_time_tracking_metric(task: Task) -> float:
    if task.time_tracking is None:
        return 0
    left = task.time_tracking.plan - task.time_tracking.work
    return left / task.time_tracking.plan


def count_priority_metric(
    task: Task, start_date: datetime, end_date: datetime
) -> float:
    m_deadline = count_deadline_metric(task, start_date, end_date)
    m_time_tracking = count_time_tracking_metric(task)
    if m_deadline == 0:
        return m_time_tracking
    elif m_time_tracking == 0:
        return m_deadline
    return m_deadline * m_time_tracking


def sort_tasks(
    tasks: List[Task], start_date: datetime, end_date: datetime
) -> List[Task]:
    relevant_tasks = get_relevant_tasks(tasks, start_date, end_date)
    return sorted(
        relevant_tasks,
        key=lambda x: count_priority_metric(x, start_date, end_date),
        reverse=True,
    )
