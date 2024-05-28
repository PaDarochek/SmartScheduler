#!/usr/bin/env python3
"""Launcher."""
import locale

from customtkinter import CTkFrame, set_appearance_mode

from scheduler import controllers, models, views

locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())


class App(controllers.IApp):
    """App.

    :param controllers: App controllers
    """

    def __init__(self):
        super().__init__()
        self.title("Smart Scheduler")
        set_appearance_mode("dark")
        self.minsize(512, 512)

        self.frame: CTkFrame | None = None
        self.model = models.AppLogicModel()
        self.views = {}
        self.controllers = {}

        self.views["login"] = views.LoginView
        self.controllers["login"] = controllers.LoginController(self)

        self.views["boards"] = views.BoardView
        self.controllers["boards"] = controllers.BoardController(self)

        self.views["tasks"] = views.TasksView
        self.controllers["tasks"] = controllers.TasksController(self)

        self.show_view("login")

    def get_model(self) -> models.AppLogicModel:
        """Get app logic model.

        :return: App logic model
        :rtype: models.AppLogicModel
        """
        return self.model

    def show_view(self, id: str):
        """Show view by ID.

        :param id: View ID
        :type id: str
        """
        view_cls = self.views[id]
        controller = self.controllers[id]
        if self.frame:
            self.frame.pack_forget()
            self.frame.destroy()
        self.frame = view_cls(self, controller)
        self.frame.pack(fill="both", expand=True)


def main():
    """Launch app."""
    app = App()
    app.mainloop()
