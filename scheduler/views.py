from datetime import date
from typing import List

import customtkinter as tk
from tkcalendar import DateEntry


class ILoginController:
    """Interface class for login controller, which requires to implement
    on_auth method."""

    def on_auth(self, view):
        raise NotImplementedError()


class LoginView(tk.CTkFrame):
    def __init__(self, parent, controller: ILoginController):
        tk.CTkFrame.__init__(self, parent)

        HEADER2_FONT = tk.CTkFont(size=22)
        PARAGRAPH_FONT = tk.CTkFont(size=16)

        # Data displayed in GUI
        self.company = tk.StringVar()
        self.user = tk.StringVar()
        self.password = tk.StringVar()
        self.error = tk.StringVar()

        # GUI setup
        tk.CTkLabel(self, text="Company", font=HEADER2_FONT).place(
            rely=0.1, relwidth=1
        )

        tk.CTkEntry(
            self, textvariable=self.company, font=PARAGRAPH_FONT
        ).place(rely=0.16, relx=0.25, relwidth=0.5)

        tk.CTkLabel(self, text="Username", font=HEADER2_FONT).place(
            rely=0.26, relwidth=1
        )
        tk.CTkEntry(self, textvariable=self.user, font=PARAGRAPH_FONT).place(
            rely=0.32, relx=0.25, relwidth=0.5
        )

        tk.CTkLabel(self, text="Password", font=HEADER2_FONT).place(
            rely=0.42, relwidth=1
        )
        tk.CTkEntry(
            self, show="*", textvariable=self.password, font=PARAGRAPH_FONT
        ).place(rely=0.48, relx=0.25, relwidth=0.5)

        tk.CTkButton(
            self,
            text="Login",
            command=lambda: controller.on_auth(self),
            font=PARAGRAPH_FONT,
        ).place(rely=0.58, relx=0.3, relwidth=0.4)

        tk.CTkLabel(
            self,
            textvariable=self.error,
            font=PARAGRAPH_FONT,
            text_color="red",
        ).place(rely=0.68, relwidth=1)

    def handle_authorization_error(self):
        self.error.set("Failed to authorize!")


class IBoardController:
    def get_project_names(self) -> List[str]:
        raise NotImplementedError()

    def get_board_names_by_project_name(
        self, view, project_name: str
    ) -> List[str]:
        raise NotImplementedError()

    def on_choose_board(self, view, board: str):
        raise NotImplementedError()


class BoardView(tk.CTkFrame):
    def __init__(self, parent, controller: IBoardController):
        tk.CTkFrame.__init__(self, parent)

        HEADER2_FONT = tk.CTkFont(size=22)
        PARAGRAPH_FONT = tk.CTkFont(size=16)

        self.controller = controller
        self.error = tk.StringVar()
        self.selected_project = None
        self.selected_board = None

        # GUI setup
        tk.CTkLabel(self, text="Project", font=HEADER2_FONT).place(
            rely=0.2, relwidth=1
        )
        self.projects_combo = tk.CTkComboBox(
            self,
            values=controller.get_project_names(),
            command=lambda choice: self.on_project_choice(choice),
            font=PARAGRAPH_FONT,
            dropdown_font=PARAGRAPH_FONT,
        )
        self.projects_combo.set("")
        self.projects_combo.place(rely=0.26, relx=0.3, relwidth=0.4)

        tk.CTkLabel(self, text="Board", font=HEADER2_FONT).place(
            rely=0.36, relwidth=1
        )
        self.boards_combo = tk.CTkComboBox(
            self,
            values=[],
            command=lambda choice: self.on_board_choice(choice),
            font=PARAGRAPH_FONT,
            dropdown_font=PARAGRAPH_FONT,
        )
        self.boards_combo.set("")
        self.boards_combo.place(
            rely=0.42,
            relx=0.3,
            relwidth=0.4,
        )

        tk.CTkButton(
            self,
            text="Choose",
            command=lambda: self.controller.on_choose_board(
                self, self.selected_board
            ),
            font=HEADER2_FONT,
        ).place(rely=0.52, relx=0.3, relwidth=0.4)

        tk.CTkLabel(
            self,
            textvariable=self.error,
            font=PARAGRAPH_FONT,
            text_color="red",
        ).place(rely=0.62, relwidth=1)

    def on_project_choice(self, choice):
        """Display list of boards connected to project."""
        self.selected_project = choice
        self.boards_combo.configure(
            values=self.controller.get_board_names_by_project_name(
                self, self.selected_project
            )
        )

    def on_board_choice(self, choice):
        self.selected_board = choice

    def display_internal_error(self):
        self.error.set("Internal error!")

    def display_no_board_chosen(self):
        self.error.set("Board is not chosen!")


class ITasksController:
    def get_filtered_tasks(
        self, view, begin_date: date, end_date: date
    ) -> List[str]:
        raise NotImplementedError()


class TasksView(tk.CTkFrame):
    def __init__(self, parent, controller):
        tk.CTkFrame.__init__(self, parent)

        HEADER2_FONT = tk.CTkFont(size=22)
        PARAGRAPH_FONT = tk.CTkFont(size=16)

        self.controller = controller

        # Setup GUI
        tk.CTkLabel(self, text="Tasks", font=HEADER2_FONT).place(
            rely=0.05, relwidth=1
        )

        self.tasks_area = tk.CTkScrollableFrame(self)
        self.tasks_area.place(rely=0.15, relheight=0.55, relwidth=1)
        self.tasks: List[tk.CTkLabel] = []

        tk.CTkLabel(self, text="From", font=PARAGRAPH_FONT).place(
            rely=0.75, relx=0.2, relwidth=0.2
        )
        self.begin_date = DateEntry(
            self, selectmode="day", locale="en_US", font=PARAGRAPH_FONT
        )
        self.begin_date.place(rely=0.8, relx=0.2, relheight=0.05, relwidth=0.2)

        tk.CTkLabel(self, text="To", font=PARAGRAPH_FONT).place(
            rely=0.75, relx=0.6, relwidth=0.2
        )
        self.end_date = DateEntry(
            self,
            selectmode="day",
            locale="en_US",
            font=PARAGRAPH_FONT,
        )
        self.end_date.place(rely=0.8, relx=0.6, relheight=0.05, relwidth=0.2)

        tk.CTkButton(
            self,
            text="Get tasks",
            font=PARAGRAPH_FONT,
            command=lambda: self.on_get_tasks(),
        ).place(rely=0.9, relx=0.4, relwidth=0.2)

    def on_get_tasks(self):
        PARAGRAPH_FONT = tk.CTkFont(size=16)

        new_task_texts = self.controller.get_filtered_tasks(
            self, self.begin_date.get_date(), self.end_date.get_date()
        )
        for task in self.tasks:
            task.pack_forget()
            task.destroy()

        self.tasks = []
        for text in new_task_texts:
            task = tk.CTkLabel(
                self.tasks_area,
                text=text,
                font=PARAGRAPH_FONT,
                anchor="w",
                justify="left",
                bg_color="gray28",
            )
            self.tasks.append(task)
            task.pack(fill="x", padx=5, pady=5)

    def on_error(self):
        PARAGRAPH_FONT = tk.CTkFont(size=16)

        self.tasks = [
            tk.CTkLabel(
                self.tasks_area,
                text="Couldn't load tasks!",
                font=PARAGRAPH_FONT,
                text_color="red",
            )
        ]
        self.tasks[0].pack()
