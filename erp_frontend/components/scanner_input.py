import customtkinter as ctk
from erp_frontend import theme


class InputBarScanner(ctk.CTkFrame):
    def __init__(self, master, on_submit, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_submit = on_submit
        self.keep_focus_active = True

        # Registra a função de validação
        vcmd = (self.register(self._validate_input), '%P')

        self.entry = ctk.CTkEntry(
            self, placeholder_text="LEITOR DE CÓDIGO DE BARRAS (FOCO)", height=48,
            font=(theme.FONT_FAMILY, 20), fg_color=theme.CARD, border_color=theme.PRIMARY,
            border_width=2, text_color=theme.TEXT,
            # Aplica a validação ao Entry
            validate="key",
            validatecommand=vcmd,
        )
        self.entry.pack(side="top", fill="x")
        self.entry.bind("<Return>", self._handle_submit)
        self.entry.bind("<FocusOut>", self._restore_focus)

        self.after(100, self._focus_entry)

    def _validate_input(self, new_value):
        """Permite apenas dígitos e o caractere '*' no campo."""
        # Permite que o campo fique vazio (ao apagar)
        return all(char.isdigit() or char == '*' for char in new_value)

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
