import tkinter as tk

from scheduler import models
from scheduler import views


class IApp(tk.Tk):
    def __init__(self):
        super().__init__()

    def get_model(self) -> models.AppLogicModel:
        raise NotImplementedError()


class LoginController(views.ILoginController):
    def __init__(self, app: IApp):
        self.app = app

    def on_auth(self, view: views.LoginView):
        try:
            self.app.get_model().auth(
                view.user.get(),
                view.password.get(),
                view.company.get(),
            )
        except ValueError:
            view.handle_authorization_error()
            return
        view.error.set("Success!")
