import tkinter as tk
from tkinter import ttk
<<<<<<< HEAD
from erp_frontend import theme
=======
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18


class TableComponent(ttk.Treeview):
    def __init__(self, master, columns, **kwargs):
<<<<<<< HEAD
        style_name = kwargs.pop("style", None) or "Treeview"
        super().__init__(master, columns=columns, show="headings", style=style_name, **kwargs)

        style = ttk.Style()
        style.theme_use("default")

        # Estilo padrão: fundo escuro, cabeçalho em destaque com borda amber
        style.configure(
            "Treeview",
            background=theme.CARD_ALT,
            foreground=theme.TEXT,
            fieldbackground=theme.CARD_ALT,
            rowheight=32,
            borderwidth=0,
            font=(theme.FONT_FAMILY, 11),
        )
        style.configure(
            "Treeview.Heading",
            background=theme.CARD,
            foreground=theme.TEXT,
            relief="flat",
            font=(theme.FONT_FAMILY, 11, "bold"),
            bordercolor=theme.PRIMARY,
        )
        style.map(
            "Treeview.Heading",
            background=[("active", theme.SECONDARY)],
        )
        # Linha selecionada destacada na cor primária (com texto escuro p/ contraste)
        style.map(
            "Treeview",
            background=[("selected", theme.PRIMARY)],
            foreground=[("selected", theme.PRIMARY_FOREGROUND)],
        )

        for column in columns:
            self.heading(column, text=column.upper())
=======
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
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
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
