"""Models for communication with YouGile API and invoking algorithms."""

from datetime import datetime
from typing import List, Optional

import yougile
import yougile.models as models

from scheduler.algorithms import sort_tasks
from scheduler.data_structures import Board, Project, Task


class AppLogicModel:
    """Logic for communication with YouGile and invoking algorithms.

    :param token: Token for YouGile authorization
    :param chosen_board: Board user project to sort tasks from
    """

    def __init__(self):
        """Create AppLogicModel instance with empty fields."""
        self.token = ""
        self.chosen_board: Optional[Board] = None

    def auth(self, login: str, password: str, company_name: str):
        """Authorize to YouGile and save token.

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

        model = models.AuthKeyController_search(
            login=login, password=password, companyId=company_id
        )
        response = yougile.query(model)
        if response.status_code != 200:
            raise ValueError()
        if len(response.json()) != 0:
            self.token = response.json()[0]["key"]
        else:
            model = models.AuthKeyController_create(
                login=login, password=password, companyId=company_id
            )
            response = yougile.query(model)
            if response.status_code != 201:
                raise ValueError()
            self.token = response.json()["key"]

    def get_projects(self) -> List[Project]:
        """Get project list in user company.

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
            pr = Project(obj["id"], obj["title"])
            projects.append(pr)
        return projects

    def get_boards_by_project(self, project: Project) -> List[Board]:
        """Get boards list by specified project.

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
            bd = Board(obj["id"], obj["title"])
            boards.append(bd)
        return boards

    def get_tasks_by_board(
        self, board: Board, start_date: datetime, end_date: datetime
    ) -> List[Task]:
        """Get tasks list from all columns of specified board.

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

        board = response.json()

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

            board_tasks += [Task(obj) for obj in response.json()["content"]]

        sorted_tasks = sort_tasks(board_tasks, start_date, end_date)

        return sorted_tasks

    def save_board(self, board: Board):
        """Save board chosen by the user.

        :param board: Chosen board
        :type board: Board
        """
        self.chosen_board = board

    def get_board(self) -> Board:
        """Get board chosen by the user.

        :raises ValueError: Board was not chosen yet
        :return: Board chosen by the user
        :rtype: Board
        """
        if self.chosen_board is None:
            raise ValueError()
        return self.chosen_board
