import customtkinter as ctk
<<<<<<< HEAD
from erp_frontend import theme
=======
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18


class InputBarScanner(ctk.CTkFrame):
    def __init__(self, master, on_submit, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_submit = on_submit
        self.keep_focus_active = True

<<<<<<< HEAD
        self.entry = ctk.CTkEntry(
            self, placeholder_text="LEITOR DE CÓDIGO DE BARRAS (FOCO)", height=48,
            font=(theme.FONT_FAMILY, 20), fg_color=theme.CARD, border_color=theme.PRIMARY,
            border_width=2, text_color=theme.TEXT,
        )
=======
        self.entry = ctk.CTkEntry(self, placeholder_text="LEITOR DE CÓDIGO DE BARRAS (FOCO)", height=48, font=("Roboto", 20))
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        self.entry.pack(side="top", fill="x")
        self.entry.bind("<Return>", self._handle_submit)
        self.entry.bind("<FocusOut>", self._restore_focus)

        self.after(100, self._focus_entry)

    def _focus_entry(self):
        if self.keep_focus_active and self.winfo_exists():
            self.entry.focus_set()

    def _restore_focus(self, event=None):
        if self.keep_focus_active and self.winfo_exists():
            self.after(10, self._focus_entry)

    def _handle_submit(self, event=None):
        value = self.entry.get().strip()
        if value:
            self.on_submit(value)
        self.entry.delete(0, "end")
        self._focus_entry()
<<<<<<< HEAD

=======
        
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
    def _force_focus(self):
            if not self.keep_focus_active:
                return
            current_focus = self.focus_get()
            if current_focus:
                grabbing_window = current_focus.grab_current()
                if grabbing_window and grabbing_window != self.winfo_toplevel():
                    self.after(500, self._force_focus)
                    return
                if current_focus.winfo_class() in ('Entry', 'TEntry', 'Text') and current_focus != self.entry:
                    self.after(500, self._force_focus)
                    return
            self.entry.focus_set()
            self.after(100, self._force_focus)
