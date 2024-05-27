import datetime
import time
import unittest

from scheduler import controllers, data_structures
from scheduler.algorithms import (
    count_deadline_metric,
    count_priority_metric,
    count_time_tracking_metric,
    get_relevant_tasks,
)
from scheduler.models import Task


class FindByTitleTests(unittest.TestCase):
    def test_projects_default_behavior(self):
        N_PROJECTS = 10
        projects = []
        for i in range(N_PROJECTS):
            prj = data_structures.Project(str(i), f"prj{i}")
            projects.append(prj)

        for i in range(N_PROJECTS):
            prj_title = f"prj{i}"
            prj = controllers.find_by_title(projects, prj_title)
            self.assertEqual(prj.id, str(i))
            self.assertEqual(prj.title, prj_title)

    def test_boards_default_behavior(self):
        N_BOARDS = 10
        boards = []
        for i in range(N_BOARDS):
            board = data_structures.Board(str(i), f"board{i}")
            boards.append(board)

        for i in range(N_BOARDS):
            board_title = f"board{i}"
            board = controllers.find_by_title(boards, board_title)
            self.assertEqual(board.id, str(i))
            self.assertEqual(board.title, board_title)

    def test_projects_exception(self):
        prj1 = data_structures.Project("1", "prj1")
        projects = [prj1, prj1]
        multiple_projects_detected = False
        try:
            controllers.find_by_title(projects, "prj1")
        except Exception:
            multiple_projects_detected = True
        self.assertTrue(multiple_projects_detected)
        no_projects_detected = False
        try:
            controllers.find_by_title(projects, "prj2")
        except Exception:
            no_projects_detected = True
        self.assertTrue(no_projects_detected)

    def test_boards_exception(self):
        board1 = data_structures.Board("1", "board1")
        boards = [board1, board1]
        multiple_boards_detected = False
        try:
            controllers.find_by_title(boards, "board1")
        except Exception:
            multiple_boards_detected = True
        self.assertTrue(multiple_boards_detected)
        no_boards_detected = False
        try:
            controllers.find_by_title(boards, "board2")
        except Exception:
            no_boards_detected = True
        self.assertTrue(no_boards_detected)


class RelevantTests(unittest.TestCase):
    def test_in_range(self):
        tasks = [
            Task(
                {
                    "id": "1",
                    "title": "task1",
                    "deadline": {
                        "deadline": time.mktime(
                            datetime.datetime.strptime(
                                "05/05/2024 18:00", "%d/%m/%Y %H:%M"
                            ).timetuple()
                        )
                        * 1000
                    },
                }
            ),
            Task(
                {
                    "id": "2",
                    "title": "task2",
                    "deadline": {
                        "deadline": time.mktime(
                            datetime.datetime.strptime(
                                "05/05/2024 18:00", "%d/%m/%Y %H:%M"
                            ).timetuple()
                        )
                        * 1000,
                        "startDate": time.mktime(
                            datetime.datetime.strptime(
                                "04/05/2024 18:00", "%d/%m/%Y %H:%M"
                            ).timetuple()
                        )
                        * 1000,
                    },
                }
            ),
        ]
        relevant_tasks = get_relevant_tasks(
            tasks,
            datetime.datetime.strptime("03/05/2024 18:00", "%d/%m/%Y %H:%M"),
            datetime.datetime.strptime("06/05/2024 18:00", "%d/%m/%Y %H:%M"),
        )
        self.assertTrue(len(relevant_tasks) == 2)

    def test_early_deadline(self):
        tasks = [
            Task(
                {
                    "id": "1",
                    "title": "task1",
                    "deadline": {
                        "deadline": time.mktime(
                            datetime.datetime.strptime(
                                "02/05/2024 18:00", "%d/%m/%Y %H:%M"
                            ).timetuple()
                        )
                        * 1000
                    },
                }
            ),
            Task(
                {
                    "id": "2",
                    "title": "task2",
                    "deadline": {
                        "deadline": time.mktime(
                            datetime.datetime.strptime(
                                "03/05/2024 18:00", "%d/%m/%Y %H:%M"
                            ).timetuple()
                        )
                        * 1000
                    },
                }
            ),
        ]
        relevant_tasks = get_relevant_tasks(
            tasks,
            datetime.datetime.strptime("03/05/2024 18:00", "%d/%m/%Y %H:%M"),
            datetime.datetime.strptime("06/05/2024 18:00", "%d/%m/%Y %H:%M"),
        )
        self.assertTrue(len(relevant_tasks) == 0)

    def test_late_start(self):
        tasks = [
            Task(
                {
                    "id": "1",
                    "title": "task1",
                    "deadline": {
                        "deadline": time.mktime(
                            datetime.datetime.strptime(
                                "10/05/2024 18:00", "%d/%m/%Y %H:%M"
                            ).timetuple()
                        )
                        * 1000,
                        "startDate": time.mktime(
                            datetime.datetime.strptime(
                                "07/05/2024 18:00", "%d/%m/%Y %H:%M"
                            ).timetuple()
                        )
                        * 1000,
                    },
                }
            ),
            Task(
                {
                    "id": "2",
                    "title": "task2",
                    "deadline": {
                        "deadline": time.mktime(
                            datetime.datetime.strptime(
                                "10/05/2024 18:00", "%d/%m/%Y %H:%M"
                            ).timetuple()
                        )
                        * 1000,
                        "startDate": time.mktime(
                            datetime.datetime.strptime(
                                "06/05/2024 18:00", "%d/%m/%Y %H:%M"
                            ).timetuple()
                        )
                        * 1000,
                    },
                }
            ),
        ]
        relevant_tasks = get_relevant_tasks(
            tasks,
            datetime.datetime.strptime("03/05/2024 18:00", "%d/%m/%Y %H:%M"),
            datetime.datetime.strptime("06/05/2024 18:00", "%d/%m/%Y %H:%M"),
        )
        self.assertTrue(len(relevant_tasks) == 0)

    def test_late_deadline(self):
        tasks = [
            Task(
                {
                    "id": "1",
                    "title": "task1",
                    "deadline": {
                        "deadline": time.mktime(
                            datetime.datetime.strptime(
                                "10/05/2024 18:00", "%d/%m/%Y %H:%M"
                            ).timetuple()
                        )
                        * 1000
                    },
                }
            )
        ]
        relevant_tasks = get_relevant_tasks(
            tasks,
            datetime.datetime.strptime("03/05/2024 18:00", "%d/%m/%Y %H:%M"),
            datetime.datetime.strptime("06/05/2024 18:00", "%d/%m/%Y %H:%M"),
        )
        self.assertTrue(len(relevant_tasks) == 1)

    def test_empty_deadline(self):
        tasks = [
            Task(
                {
                    "id": "1",
                    "title": "task1",
                }
            )
        ]
        relevant_tasks = get_relevant_tasks(
            tasks,
            datetime.datetime.strptime("03/05/2024 18:00", "%d/%m/%Y %H:%M"),
            datetime.datetime.strptime("06/05/2024 18:00", "%d/%m/%Y %H:%M"),
        )
        self.assertTrue(len(relevant_tasks) == 1)

    def test_early_start(self):
        tasks = [
            Task(
                {
                    "id": "1",
                    "title": "task1",
                    "deadline": {
                        "deadline": time.mktime(
                            datetime.datetime.strptime(
                                "10/05/2024 18:00", "%d/%m/%Y %H:%M"
                            ).timetuple()
                        )
                        * 1000,
                        "startDate": time.mktime(
                            datetime.datetime.strptime(
                                "01/05/2024 18:00", "%d/%m/%Y %H:%M"
                            ).timetuple()
                        )
                        * 1000,
                    },
                }
            ),
            Task(
                {
                    "id": "2",
                    "title": "task2",
                    "deadline": {
                        "deadline": time.mktime(
                            datetime.datetime.strptime(
                                "05/05/2024 18:00", "%d/%m/%Y %H:%M"
                            ).timetuple()
                        )
                        * 1000,
                        "startDate": time.mktime(
                            datetime.datetime.strptime(
                                "01/05/2024 18:00", "%d/%m/%Y %H:%M"
                            ).timetuple()
                        )
                        * 1000,
                    },
                }
            ),
        ]
        relevant_tasks = get_relevant_tasks(
            tasks,
            datetime.datetime.strptime("03/05/2024 18:00", "%d/%m/%Y %H:%M"),
            datetime.datetime.strptime("06/05/2024 18:00", "%d/%m/%Y %H:%M"),
        )
        self.assertTrue(len(relevant_tasks) == 2)

    def test_archived_completed(self):
        tasks = [
            Task(
                {
                    "id": "1",
                    "title": "task1",
                    "archived": True,
                    "deadline": {
                        "deadline": time.mktime(
                            datetime.datetime.strptime(
                                "05/05/2024 18:00", "%d/%m/%Y %H:%M"
                            ).timetuple()
                        )
                        * 1000
                    },
                }
            ),
            Task(
                {
                    "id": "2",
                    "title": "task2",
                    "completed": True,
                    "deadline": {
                        "deadline": time.mktime(
                            datetime.datetime.strptime(
                                "05/05/2024 18:00", "%d/%m/%Y %H:%M"
                            ).timetuple()
                        )
                        * 1000
                    },
                }
            ),
            Task(
                {
                    "id": "3",
                    "title": "task3",
                    "archived": True,
                    "completed": True,
                    "deadline": {
                        "deadline": time.mktime(
                            datetime.datetime.strptime(
                                "05/05/2024 18:00", "%d/%m/%Y %H:%M"
                            ).timetuple()
                        )
                        * 1000
                    },
                }
            ),
            Task(
                {
                    "id": "4",
                    "title": "task4",
                    "archived": True,
                    "completed": False,
                    "deadline": {
                        "deadline": time.mktime(
                            datetime.datetime.strptime(
                                "05/05/2024 18:00", "%d/%m/%Y %H:%M"
                            ).timetuple()
                        )
                        * 1000
                    },
                }
            ),
            Task(
                {
                    "id": "5",
                    "title": "task5",
                    "archived": False,
                    "completed": True,
                    "deadline": {
                        "deadline": time.mktime(
                            datetime.datetime.strptime(
                                "05/05/2024 18:00", "%d/%m/%Y %H:%M"
                            ).timetuple()
                        )
                        * 1000
                    },
                }
            ),
            Task(
                {
                    "id": "6",
                    "title": "task6",
                    "archived": False,
                    "completed": False,
                    "deadline": {
                        "deadline": time.mktime(
                            datetime.datetime.strptime(
                                "05/05/2024 18:00", "%d/%m/%Y %H:%M"
                            ).timetuple()
                        )
                        * 1000
                    },
                }
            ),
        ]
        relevant_tasks = get_relevant_tasks(
            tasks,
            datetime.datetime.strptime("03/05/2024 18:00", "%d/%m/%Y %H:%M"),
            datetime.datetime.strptime("06/05/2024 18:00", "%d/%m/%Y %H:%M"),
        )
        self.assertTrue(len(relevant_tasks) == 1)
        self.assertTrue(relevant_tasks[0].id == "6")


class DeadlineMetricTests(unittest.TestCase):
    def test_empty_deadline(self):
        task = Task(
            {
                "id": "1",
                "title": "task1",
            }
        )
        dl_metric = count_deadline_metric(
            task,
            datetime.datetime.strptime("03/05/2024 18:00", "%d/%m/%Y %H:%M"),
            datetime.datetime.strptime("06/05/2024 18:00", "%d/%m/%Y %H:%M"),
        )
        self.assertTrue(abs(dl_metric) < 1e-9)

    def test_empty_start(self):
        task = Task(
            {
                "id": "1",
                "title": "task1",
                "deadline": {
                    "deadline": time.mktime(
                        datetime.datetime.strptime(
                            "05/05/2024 18:00", "%d/%m/%Y %H:%M"
                        ).timetuple()
                    )
                    * 1000
                },
            }
        )
        dl_metric = count_deadline_metric(
            task,
            datetime.datetime.strptime("03/05/2024 18:00", "%d/%m/%Y %H:%M"),
            datetime.datetime.strptime("06/05/2024 18:00", "%d/%m/%Y %H:%M"),
        )
        self.assertTrue(abs(dl_metric - 3.35e-11) < 1e-11)

    def test_early_start(self):
        task = Task(
            {
                "id": "1",
                "title": "task1",
                "deadline": {
                    "deadline": time.mktime(
                        datetime.datetime.strptime(
                            "05/05/2024 18:00", "%d/%m/%Y %H:%M"
                        ).timetuple()
                    )
                    * 1000,
                    "startDate": time.mktime(
                        datetime.datetime.strptime(
                            "02/05/2024 18:00", "%d/%m/%Y %H:%M"
                        ).timetuple()
                    )
                    * 1000,
                },
            }
        )
        dl_metric = count_deadline_metric(
            task,
            datetime.datetime.strptime("03/05/2024 18:00", "%d/%m/%Y %H:%M"),
            datetime.datetime.strptime("06/05/2024 18:00", "%d/%m/%Y %H:%M"),
        )
        self.assertTrue(abs(dl_metric - 3.35e-11) < 1e-11)

    def test_default(self):
        task = Task(
            {
                "id": "1",
                "title": "task1",
                "deadline": {
                    "deadline": time.mktime(
                        datetime.datetime.strptime(
                            "05/05/2024 18:00", "%d/%m/%Y %H:%M"
                        ).timetuple()
                    )
                    * 1000,
                    "startDate": time.mktime(
                        datetime.datetime.strptime(
                            "04/05/2024 18:00", "%d/%m/%Y %H:%M"
                        ).timetuple()
                    )
                    * 1000,
                },
            }
        )
        dl_metric = count_deadline_metric(
            task,
            datetime.datetime.strptime("03/05/2024 18:00", "%d/%m/%Y %H:%M"),
            datetime.datetime.strptime("06/05/2024 18:00", "%d/%m/%Y %H:%M"),
        )
        self.assertTrue(abs(dl_metric - 2.23e-11) < 1e-11)


class TimeTrackingMetricTests(unittest.TestCase):
    def test_empty_time_tracking(self):
        task = Task(
            {
                "id": "1",
                "title": "task1",
            }
        )
        tt_metric = count_time_tracking_metric(task)
        self.assertTrue(abs(tt_metric) < 1e-9)

    def test_default(self):
        task = Task(
            {
                "id": "1",
                "title": "task1",
                "timeTracking": {"plan": 5, "work": 3},
            }
        )
        tt_metric = count_time_tracking_metric(task)
        self.assertTrue(abs(tt_metric - 0.4) < 1e-9)

    def test_empty_work(self):
        task = Task(
            {
                "id": "1",
                "title": "task1",
                "timeTracking": {"plan": 5, "work": 0},
            }
        )
        tt_metric = count_time_tracking_metric(task)
        self.assertTrue(abs(tt_metric - 1) < 1e-9)

    def test_full_work(self):
        task = Task(
            {
                "id": "1",
                "title": "task1",
                "timeTracking": {"plan": 5, "work": 5},
            }
        )
        tt_metric = count_time_tracking_metric(task)
        self.assertTrue(abs(tt_metric) < 1e-9)


class PriorityMetricTests(unittest.TestCase):
    def test_empty_deadline(self):
        task = Task(
            {
                "id": "1",
                "title": "task1",
                "timeTracking": {"plan": 5, "work": 3},
            }
        )
        tt_metric = count_time_tracking_metric(task)
        pr_metric = count_priority_metric(
            task,
            datetime.datetime.strptime("03/05/2024 18:00", "%d/%m/%Y %H:%M"),
            datetime.datetime.strptime("06/05/2024 18:00", "%d/%m/%Y %H:%M"),
        )
        self.assertTrue(abs(pr_metric - tt_metric) < 1e-9)

    def test_empty_time_tracking(self):
        task = Task(
            {
                "id": "1",
                "title": "task1",
                "deadline": {
                    "deadline": time.mktime(
                        datetime.datetime.strptime(
                            "05/05/2024 18:00", "%d/%m/%Y %H:%M"
                        ).timetuple()
                    )
                    * 1000
                },
            }
        )
        dl_metric = count_deadline_metric(
            task,
            datetime.datetime.strptime("03/05/2024 18:00", "%d/%m/%Y %H:%M"),
            datetime.datetime.strptime("06/05/2024 18:00", "%d/%m/%Y %H:%M"),
        )
        pr_metric = count_priority_metric(
            task,
            datetime.datetime.strptime("03/05/2024 18:00", "%d/%m/%Y %H:%M"),
            datetime.datetime.strptime("06/05/2024 18:00", "%d/%m/%Y %H:%M"),
        )
        self.assertTrue(abs(pr_metric - dl_metric) < 1e-9)

    def test_default(self):
        task = Task(
            {
                "id": "1",
                "title": "task1",
                "deadline": {
                    "deadline": time.mktime(
                        datetime.datetime.strptime(
                            "05/05/2024 18:00", "%d/%m/%Y %H:%M"
                        ).timetuple()
                    )
                    * 1000
                },
                "timeTracking": {"plan": 5, "work": 3},
            }
        )
        dl_metric = count_deadline_metric(
            task,
            datetime.datetime.strptime("03/05/2024 18:00", "%d/%m/%Y %H:%M"),
            datetime.datetime.strptime("06/05/2024 18:00", "%d/%m/%Y %H:%M"),
        )
        tt_metric = count_time_tracking_metric(task)
        pr_metric = count_priority_metric(
            task,
            datetime.datetime.strptime("03/05/2024 18:00", "%d/%m/%Y %H:%M"),
            datetime.datetime.strptime("06/05/2024 18:00", "%d/%m/%Y %H:%M"),
        )
        self.assertTrue(abs(pr_metric - dl_metric * tt_metric) < 1e-9)
        self.assertTrue(abs(pr_metric - 1.34e-11) < 1e-11)
