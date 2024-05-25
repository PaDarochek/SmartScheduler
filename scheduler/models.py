from typing import List

import yougile
import yougile.models as models


class Project:
    id: str
    title: str


class Board:
    id: str
    title: str


class Deadline:
    deadline: int
    start_date: int
    with_time: bool


class TimeTracking:
    plan: int
    work: int


class Task:
    id: str
    title: str
    description: str
    archived: bool
    completed: bool
    deadline: Deadline
    time_tracking: TimeTracking


class AppLogicModel:
    def __init__(self):
        self.token = ""

    def auth(self, login: str, password: str, company_name: str):
        """Authorize to YouGile.

        :param login: User login
        :type login: str
        :param password: User password
        :type password: str
        :param company_name: Company name
        :type company_name: str
        :raises ValueError: Authorization error
        """
        model = models.AuthKeyController_companiesList(
            login=login, password=password, name=company_name
        )
        response = yougile.query(model)
        if response.status_code != 200:
            raise ValueError()

        companies = response.json()["content"]
        if len(companies) != 1:
            raise ValueError()
        company_id = companies[0]["id"]

        model = models.AuthKeyController_create(
            login=login, password=password, companyId=company_id
        )
        response = yougile.query(model)
        if response.status_code != 201:
            raise ValueError()
        self.token = response.json()["key"]

    def get_projects(self) -> List[Project]:
        """Get project list.

        :raises ValueError:
        :return: Project list
        :rtype: List[Project]
        """
        model = models.ProjectController_search(token=self.token)
        response = yougile.query(model)
        status = response.status_code
        if status != 200:
            raise ValueError()

        projects = list()
        for obj in response.json()["content"]:
            pr = Project()
            pr.id = obj["id"]
            pr.title = obj["title"]
            projects.append(pr)
        return projects

    def get_boards_by_project(self, project: Project) -> List[Board]:
        """Get boards list by project.

        :param project: YouGile project
        :type project: Project
        :raises ValueError: Bad response
        :return: Boards list
        :rtype: List[Board]
        """
        model = models.BoardController_search(
            token=self.token, projectId=project.id
        )
        response = yougile.query(model)
        status = response.status_code
        if status != 200:
            raise ValueError()

        boards = list()
        for obj in response.json()["content"]:
            bd = Board()
            bd.id = obj["id"]
            bd.title = obj["title"]
            boards.append(bd)
        return boards

    def get_tasks_by_board(self, board: Board) -> List[Task]:
        """Get tasks list from all columns of board.

        :param board: YouGile board
        :type board: Board
        :raises ValueError: Bad response
        :return: Tasks list
        :rtype: List[Task]
        """
        model = models.BoardController_get(token=self.token, id=board.id)
        response = yougile.query(model)
        status = response.status_code
        if status != 200:
            raise ValueError()

        board = response.json()["content"]

        model = models.ColumnController_search(
            token=self.token, boardId=board["id"]
        )
        response = yougile.query(model)
        status = response.status_code
        if status != 200:
            raise ValueError()

        board_tasks = list()
        for column in response.json()["content"]:
            model = models.TaskController_search(
                token=self.token, columnId=column["id"]
            )
            response = yougile.query(model)
            status = response.status_code
            if status != 200:
                raise ValueError()

            tasks = list()
            for obj in response.json()["content"]:
                task = Task()
                task.id = obj["id"]
                task.title = obj["title"]
                task.archived = obj["archived"]
                task.completed = obj["completed"]
                task.deadline = obj["deadline"]
                task.description = obj["description"]
                task.time_tracking = obj["timeTracking"]
                tasks.append(task)
            board_tasks.append(tasks)

        return board_tasks
