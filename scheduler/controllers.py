from datetime import date, datetime, time
from typing import List

from customtkinter import CTk

from scheduler import data_structures, models, views


class IApp(CTk):
    def __init__(self):
        super().__init__()

    def get_model(self) -> models.AppLogicModel:
        raise NotImplementedError()

    def show_view(self, id: str):
        """Show the view with the given id.

        :param id: Id of the view
        :type id: str
        """
        raise NotImplementedError()


class LoginController(views.ILoginController):
    def __init__(self, app: IApp):
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
            "No projects found or unexpected projects having the same names"
        )
    return found_projects[0]


class BoardController(views.IBoardController):
    def __init__(self, app: IApp):
        self.app = app
        self.projects: List[data_structures.Project] = []
        self.boards: List[data_structures.Board] = []

    def get_project_names(self) -> List[str]:
        self.projects = self.app.get_model().get_projects()
        return [prj.title for prj in self.projects]

    def get_board_names_by_project_name(
        self, view: views.BoardView, project_name: str
    ) -> List[str]:
        try:
            self.boards = self.app.get_model().get_boards_by_project(
                find_by_title(self.projects, project_name)
            )
        except Exception:
            view.display_internal_error()
            return []
        return [board.title for board in self.boards]

    def on_choose_board(self, view: views.BoardView, board_name: str):
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
    def __init__(self, app: IApp):
        self.app = app

    def get_filtered_tasks(
        self, view: views.TasksView, begin_date: date, end_date: date
    ) -> List[str]:
        begin_date = datetime.combine(
            begin_date, time(hour=0, minute=0, second=0)
        )
        end_date = datetime.combine(
            end_date, time(hour=23, minute=59, second=59)
        )
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
            text = f"{task.title.strip()}\n{task.description.strip()}\n"
            if task.archived:
                text += "Task is archived\n"
            if task.completed:
                text += "Completed\n"
            if task.deadline is not None:
                text += f"Deadline: {task.deadline.deadline}\n"
                if task.deadline.start_date is not None:
                    text += f"\tStart date: {task.deadline.start_date}\n"
            if task.time_tracking is not None:
                text += f"Planned time: {task.time_tracking.plan} hours\n"
                text += f"Work time: {task.time_tracking.work} hours\n"
            result_texts.append(text)
        return result_texts
