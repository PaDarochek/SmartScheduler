"""App controllers."""

import gettext
import locale
import os
from datetime import date, datetime, time
from typing import List

from customtkinter import CTk

from scheduler import data_structures, models, views

locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())

translation = gettext.translation(
    "Scheduler", os.path.join(os.path.dirname(__file__), "po"), fallback=True
)
_ = translation.gettext


class IApp(CTk):
    """Interface of application to be used in controllers."""

    def __init__(self):
        """Constructor."""
        super().__init__()

    def get_model(self) -> models.AppLogicModel:
        """This method provides access to the logic model of the app.

        :raises NotImplementedError: interface is not intended to be
            called
        :return: return the instance of models.AppLogicModel
        :rtype: models.AppLogicModel
        """
        raise NotImplementedError()

    def show_view(self, id: str):
        """Show the view with the given id.

        :param id: Id of the view
        :type id: str
        """
        raise NotImplementedError()


class LoginController(views.ILoginController):
    """Controller implementing communication between LoginView and models."""

    def __init__(self, app: IApp):
        """Constructor initializing controller by the instance of implemented
        IApp interface.

        :param app: the instance of implemented IApp interface
        :type app: IApp
        """
        self.app = app

    def on_auth(self, view: views.LoginView):
        """Callback which is invoked when login button is pressed. If login
        failed, call views method to display authorization failure. Otherwise
        show page allowing to choose project and board.

        :param view: Login page, which should call this method.
        :type view: views.LoginView
        """
        try:
            self.app.get_model().auth(
                view.user.get(),
                view.password.get(),
                view.company.get(),
            )
        except ValueError:
            view.handle_authorization_error()
            return
        self.app.show_view("boards")


def find_by_title(
    entities: List[data_structures.Project | data_structures.Board], title: str
) -> data_structures.Project | None:
    """Get project with a name mathes the given one.

    :param entities: list of projects
    :type entities: List[data_structures.Project |
        data_structures.Board]
    :param title: searched project_name
    :type title: str
    :raises RuntimeError: raises when there are two projects with the
        same name
    """
    found_projects = [ent for ent in entities if ent.title == title]
    if len(found_projects) != 1:
        raise RuntimeError(
            _("No projects found or unexpected projects having the same names")
        )
    return found_projects[0]


class BoardController(views.IBoardController):
    """COntroller implementing communication between BoardView and models."""

    def __init__(self, app: IApp):
        """Constructor initializing controller with the instance of app.

        :param app: instance of the implemented interface IApp
        :type app: IApp
        """
        self.app = app
        self.projects: List[data_structures.Project] = []
        self.boards: List[data_structures.Board] = []

    def get_project_names(self) -> List[str]:
        """Returns project names. Always requested by BoardView.

        :return: list of project names
        :rtype: List[str]
        """
        self.projects = self.app.get_model().get_projects()
        return [prj.title for prj in self.projects]

    def get_board_names_by_project_name(
        self, view: views.BoardView, project_name: str
    ) -> List[str]:
        """Given the project name returns list of borad names to display in
        BoardView.

        :param view: the view
        :type view: views.BoardView
        :param project_name: project name
        :type project_name: str
        :return: list of board names
        :rtype: List[str]
        """
        try:
            self.boards = self.app.get_model().get_boards_by_project(
                find_by_title(self.projects, project_name)
            )
        except Exception:
            view.display_internal_error()
            return []
        return [board.title for board in self.boards]

    def on_choose_board(self, view: views.BoardView, board_name: str):
        """Given a board name execute the app logic and move to TasksView.

        :param view: the view
        :type view: views.BoardView
        :param board_name: board name
        :type board_name: str
        """
        if not board_name:
            view.display_no_board_chosen()
            return
        try:
            self.app.get_model().save_board(
                find_by_title(self.boards, board_name)
            )
        except Exception:
            view.display_internal_error()
            return
        self.app.show_view("tasks")


class TasksController(views.ITasksController):
    """Controller implementing communication between TasksView and models."""

    def __init__(self, app: IApp):
        """Constructor initializing the instance by app.

        :param app: instance of implemented IApp interface
        :type app: IApp
        """
        self.app = app

    def get_filtered_tasks(
        self, view: views.TasksView, begin_date: date, end_date: date
    ) -> List[str]:
        """Get card texts by the begin and end dates. Should be called from
        TasksView.

        :param view: the view
        :type view: views.TasksView
        :param begin_date: the begin date
        :type begin_date: date
        :param end_date: the end date
        :type end_date: date
        :return: list of card texts
        :rtype: List[str]
        """
        begin_date = datetime.combine(
            begin_date, time(hour=0, minute=0, second=0)
        )
        end_date = datetime.combine(
            end_date, time(hour=23, minute=59, second=59)
        )
        if begin_date > end_date:
            view.on_error()
            return []
        try:
            board = self.app.get_model().get_board()
            filtered_tasks = self.app.get_model().get_tasks_by_board(
                board, begin_date, end_date
            )
        except Exception as e:
            print(e)
            view.on_error()
            return []
        result_texts = []
        for task in filtered_tasks:
            text = f"{task.title.strip()}\n\n{task.description.strip()}\n"
            if task.archived:
                text += _("Task is archived\n")
            if task.completed:
                text += _("Completed\n")
            if task.deadline is not None:
                if task.deadline.start_date is not None:
                    text += _("\tStart date: {}\n").format(
                        task.deadline.start_date.strftime("%d/%m/%Y %H:%M")
                    )
                text += _("\tDeadline: {}\n").format(
                    task.deadline.deadline.strftime("%d/%m/%Y %H:%M")
                )
            if task.time_tracking is not None:
                text += _("Planned time: {} hours\n").format(
                    task.time_tracking.plan
                )
                text += _("Work time: {} hours\n").format(
                    task.time_tracking.work
                )
            result_texts.append(text)
        return result_texts

    def back_to_board_view(self):
        """Go back to board view."""
        self.app.show_view("boards")
