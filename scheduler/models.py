import yougile
import yougile.models as models
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List


@dataclass_json
@dataclass
class Project:
    id: str
    title: str


@dataclass_json
@dataclass
class Board:
    id: str
    title: str


class AppLogicModel:
    def __init__(self):
        self.token = ""

    def auth(self, login: str, password: str, company_name: str):
        """Authorize to YouGile

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
        """Get project list

        :raises ValueError:
        :return: Project list
        :rtype: List[Project]
        """
        model = models.ProjectController_search(token=self.token)
        response = yougile.query(model)
        status = response.status_code
        if status != 200:
            raise ValueError()

        projects = Project.schema().dumps(
            response.json()["content"], many=True
        )
        return projects

    def get_boards_by_project(self, project: Project) -> List[Board]:
        model = models.BoardController_search(
            token=self.token, projectId=project.id
        )
        response = yougile.query(model)
        status = response.status_code
        if status != 200:
            raise ValueError()

        boards = Board.schema().dumps(response.json()["content"], many=True)
        return boards
