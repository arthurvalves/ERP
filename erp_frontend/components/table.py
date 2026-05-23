import tkinter as tk
from tkinter import ttk


class TableComponent(ttk.Treeview):
    def __init__(self, master, columns, **kwargs):
        super().__init__(master, columns=columns, show="headings", **kwargs)

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="#232323",
            foreground="#ffffff",
            fieldbackground="#232323",
            rowheight=30,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background="#2f2f2f",
            foreground="#ffffff",
            relief="flat",
            font=("Roboto", 11, "bold"),
        )
        style.map("Treeview", background=[("selected", "#2c3e50")])

        for column in columns:
            self.heading(column, text=column)
            self.column(column, anchor="center", width=120)

        scrollbar = ttk.Scrollbar(master, orient="vertical", command=self.yview)
        self.configure(yscrollcommand=scrollbar.set)
        self._scrollbar = scrollbar

    def pack(self, *args, **kwargs):
        if self._scrollbar.winfo_ismapped() is False:
            self._scrollbar.pack(side="right", fill="y")
        return super().pack(*args, **kwargs)

    def grid(self, *args, **kwargs):
        if self._scrollbar.winfo_ismapped() is False:
            self._scrollbar.grid()
        return super().grid(*args, **kwargs)
