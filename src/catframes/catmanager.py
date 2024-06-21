#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import ttk


class WindowSettings:
    def __init__(self, root, name, width, height):
        """
        Sets the size and position of the main window.
        """
        self.root = root
        self.name = name
        # Get the screen size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate the center position of the window
        center_x = int(screen_width / 2 - width / 2)
        center_y = int(screen_height / 2 - height / 2)

        # Set the window title and geometry
        self.root.title(f"{self.name}")
        self.root.geometry(f"{width}x{height}+{center_x}+{center_y}")


# noinspection PyAttributeOutsideInit
class CatManager:
    def __init__(self):
        self.root = Tk()
        self.root.title("Task manager for CatFrames")
        WindowSettings(self.root, "Task manager for CatFrames", 1280, 720)
        self.conf_grid()
        self.task_list = []

    def conf_grid(self):
        for c in range(5):
            self.root.columnconfigure(index=c, weight=1)
        for r in range(10):
            self.root.rowconfigure(index=r, weight=1)

    def create_ui(self):
        # Create buttons
        Button(
            master=self.root,
            text="Settings"
        ).grid(
            row=0,
            column=4,
            pady=(30, 10)
        )
        Button(
            master=self.root,
            text="New Task",
            command=lambda: NewTaskFrame(self.root, self)
        ).grid(
            row=0,
            column=0,
            pady=(30, 10)
        )

        # Create main frame
        self.main_frame = Frame(self.root)
        self.main_frame.grid(row=1, columnspan=5, rowspan=10, sticky="we", padx=100)

        # Create canvas
        self.canvas = Canvas(self.main_frame)
        self.canvas.pack(side=LEFT, fill=BOTH)

        # Create canvas frame
        self.canvas_frame = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.canvas_frame, anchor='w')

        # Create scrollbar
        self.canvas.scrollbar = Scrollbar(self.main_frame, orient=VERTICAL, command=self.canvas.yview)
        self.canvas.scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas.configure(yscrollcommand=self.canvas.scrollbar.set)
        # Configure canvas to scroll
        self.canvas_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.update_task_list()

    def add_task(self, task_name):
        self.task_list.append(task_name)
        self.update_task_list()

    def update_task_list(self):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        for i, task_name in enumerate(self.task_list):
            inner_frame = Frame(self.canvas_frame, width=self.canvas_frame.winfo_width())
            inner_frame.pack(side=TOP, expand=True, fill=BOTH, padx=10, pady=10)

            name_label = Label(master=inner_frame, text=task_name)
            name_label.pack(side=LEFT, fill=BOTH, expand=True)

            progress_bar = ttk.Progressbar(
                master=inner_frame,
                orient="horizontal",
                length=100,
                mode="determinate",
                value=int(i + 1)
            )
            progress_bar.pack(side=LEFT, fill=BOTH, expand=True)

            cancel_button = Button(
                master=inner_frame,
                text="Cancel",
            )
            cancel_button.pack(side=LEFT, fill=BOTH, expand=True)

    def run(self):
        self.root.mainloop()


class NewTaskFrame:
    def __init__(self, root, cm):
        self.root = Toplevel(root)
        self.root.title("New Task")
        WindowSettings(self.root, "New Task", 800, 600)
        self.cat_manager = cm

        # Create entry for task name
        self.entry_for_name = Entry(master=self.root, width=40)
        self.entry_for_name.pack()

        # Create button to create task
        Button(
            master=self.root,
            text="Create Task",
            command=self.create_task
        ).pack()

    def create_task(self):
        task_name = self.entry_for_name.get()
        self.cat_manager.add_task(task_name)
        self.root.destroy()


if __name__ == "__main__":
    cat_manager = CatManager()
    cat_manager.create_ui()
    cat_manager.run()
