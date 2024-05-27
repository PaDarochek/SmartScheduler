"""Scheduling algorithms module.

Provides functions for getting relevant tasks according to dates,
computing metrics and sorting tasks according to the metrics values.
"""

from datetime import datetime
from typing import List

from scheduler.data_structures import Task


def relevant(task: Task, start_date: datetime, end_date: datetime) -> bool:
    """Check if task may be done during time interval.

    :param task: Task to check
    :type task: Task
    :param start_date: Start date of time interval
    :type start_date: datetime
    :param end_date: End date of time interval
    :type end_date: datetime
    :return: True if task may be done during time interval, False
        otherwise
    :rtype: bool
    """
    result = not task.archived and not task.completed
    if task.deadline is not None:
        result = result and task.deadline.deadline > start_date
        if task.deadline.start_date is not None:
            result = result and task.deadline.start_date < end_date
    return result


def get_relevant_tasks(
    tasks: List[Task], start_date: datetime, end_date: datetime
) -> List[Task]:
    """Filter tasks that may be done between start_date and end_date.

    :param tasks: List of tasks to filter
    :type tasks: List[Task]
    :param start_date: Start date of time interval
    :type start_date: datetime
    :param end_date: End date of time interval
    :type end_date: datetime
    :return: Filtered list of tasks
    :rtype: List[Task]
    """
    tasks = list(filter(lambda x: relevant(x, start_date, end_date), tasks))
    return tasks


def count_deadline_metric(
    task: Task, start_date: datetime, end_date: datetime
) -> float:
    """Compute metric based on task deadline and time interval.

    :param task: Task for metric computation
    :type task: Task
    :param start_date: Start date of time interval
    :type start_date: datetime
    :param end_date: End date of time interval
    :type end_date: datetime
    :return: Metric value corresponding to task urgency
    :rtype: float
    """
    if task.deadline is None:
        return 0
    delta_deadline = (task.deadline.deadline - start_date).total_seconds()
    delta_start = (
        (end_date - task.deadline.start_date).total_seconds()
        / (end_date - start_date).total_seconds()
        if task.deadline.start_date is not None
        else 1
    )
    if delta_start > 1:
        delta_start = 1
    return delta_start / (delta_deadline**2)


def count_time_tracking_metric(task: Task) -> float:
    """Compute metric based on task time tracking values.

    :param task: Task for metric computation
    :type task: Task
    :return: Metric value corresponding to the percentage of completed
        work
    :rtype: float
    """
    if task.time_tracking is None:
        return 0
    left = task.time_tracking.plan - task.time_tracking.work
    return left / task.time_tracking.plan


def count_priority_metric(
    task: Task, start_date: datetime, end_date: datetime
) -> float:
    """Compute priority metric based on the values of deadline metric and time
    tracking metric for task.

    :param task: Task for metric computation
    :type task: Task
    :param start_date: Start date of time interval
    :type start_date: datetime
    :param end_date: End date of time interval
    :type end_date: datetime
    :return: Metric value corresponding to task priority
    :rtype: float
    """
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
    """Sort tasks according to their priority.

    :param tasks: List of tasks to sort
    :type tasks: List[Task]
    :param start_date: Start date of time interval
    :type start_date: datetime
    :param end_date: End date of time interval
    :type end_date: datetime
    :return: Sorted list of tasks with most prioritized tasks in the
        beginning
    :rtype: List[Task]
    """
    relevant_tasks = get_relevant_tasks(tasks, start_date, end_date)
    return sorted(
        relevant_tasks,
        key=lambda x: count_priority_metric(x, start_date, end_date),
        reverse=True,
    )
