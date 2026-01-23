import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog


class UsernameDialog(simpledialog.Dialog):

    def __init__(self, parent, title="Add usernames"):
        self.usernames: list[str] = []
        super().__init__(parent, title)

    def body(self, master):
        ttk.Label(
            master, text="Enter username:"
        ).grid(row=0, column=0, sticky="w")

        self.var = tk.StringVar()
        self.entry = ttk.Entry(master, textvariable=self.var, width=30)
        self.entry.grid(row=1, column=0, pady=(5, 0))
        self.entry.focus()

        return self.entry

    def buttonbox(self):
        box = ttk.Frame(self)

        ttk.Button(
            box, text="Next", command=self.add
        ).pack(side="left", padx=5)
        ttk.Button(
            box, text="Done", command=self.ok
        ).pack(side="right", padx=5)

        box.pack(pady=10)

    def add(self):
        name = self.var.get().strip()
        if name:
            self.usernames.append(name)
            self.var.set("")

    def ok(self, event=None):
        self.add()
        self.withdraw()
        self.update_idletasks()
        self.cancel()
