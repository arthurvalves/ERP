import customtkinter as ctk


class InputBarScanner(ctk.CTkFrame):
    def __init__(self, master, on_submit, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_submit = on_submit
        self.keep_focus_active = True

        self.entry = ctk.CTkEntry(self, placeholder_text="LEITOR DE CÓDIGO DE BARRAS (FOCO)", height=48, font=("Roboto", 20))
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
