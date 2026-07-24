import customtkinter as ctk
from tkinter import messagebox
import re

from erp_backend.models.vehicle import Vehicle
from erp_backend.services import vehicle_service
from erp_frontend import theme


class VehicleModal(ctk.CTkToplevel):
    def __init__(self, master, customer_id, vehicle_id=None, initial_plate=""):
        super().__init__(master)
        self.title("Novo Veículo" if not vehicle_id else "Editar Veículo")
        self.configure(fg_color=theme.BG)
        self.transient(master)
        self.grab_set()

        self.customer_id = customer_id
        self.vehicle_id = vehicle_id
        self.result = None

        self.protocol("WM_DELETE_WINDOW", self._close)
        self._setup_ui(initial_plate)
        self._load_vehicle()
        self.after(10, self._center_window)

    def _center_window(self):
        self.update_idletasks()
        width = 520
        height = 400
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        self.resizable(False, False)

    def _setup_ui(self, initial_plate):
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=16, pady=16)

        self.plate_entry = self._add_field(form, "Placa", 0)
        self.plate_entry.insert(0, initial_plate)
        self.plate_entry.bind("<FocusOut>", self._format_plate)
        self.plate_entry.bind("<Return>", self._format_plate)
        self.brand_entry = self._add_field(form, "Marca", 1)
        self.model_entry = self._add_field(form, "Modelo", 2)
        self.year_entry = self._add_field(form, "Ano/Modelo", 3)
        self.color_entry = self._add_field(form, "Cor", 4)
        self.km_entry = self._add_field(form, "KM Atual", 5)

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(fill="x", padx=16, pady=(0, 16))

        ctk.CTkButton(buttons, text="Cancelar", command=self._close, **theme.btn_secondary()).pack(side="right")
        ctk.CTkButton(buttons, text="Salvar", command=self._save, **theme.btn_primary()).pack(side="right", padx=(0, 8))

    def _format_plate(self, event=None):
        plate_raw = self.plate_entry.get().strip().upper().replace('-', '')
        if not plate_raw:
            return

        formatted_plate = ""
        if len(plate_raw) == 7 and plate_raw[4].isdigit():
            formatted_plate = plate_raw
        elif len(plate_raw) == 7 and plate_raw[3:].isdigit():
            formatted_plate = f"{plate_raw[:3]}-{plate_raw[3:]}"
        else:
            formatted_plate = plate_raw

        self.plate_entry.delete(0, "end")
        self.plate_entry.insert(0, formatted_plate)

    def _add_field(self, parent, label, row):
        ctk.CTkLabel(parent, text=label, text_color=theme.TEXT).grid(row=row, column=0, sticky="w", pady=(0, 8))
        entry = ctk.CTkEntry(parent, fg_color=theme.CARD, border_color=theme.SECONDARY)
        entry.grid(row=row, column=1, sticky="ew", pady=(0, 8), padx=(12, 0))
        parent.grid_columnconfigure(1, weight=1)
        return entry

    def _load_vehicle(self):
        if not self.vehicle_id:
            return

        vehicle = vehicle_service.get_vehicle_by_id(self.vehicle_id)
        if not vehicle:
            return

        self.plate_entry.delete(0, "end")
        self.plate_entry.insert(0, vehicle.plate)
        self.brand_entry.insert(0, vehicle.brand or "")
        self.model_entry.insert(0, vehicle.model or "")
        self.year_entry.insert(0, vehicle.year or "")
        self.color_entry.insert(0, vehicle.color or "")
        self.km_entry.insert(0, str(vehicle.current_km or ""))

    def _save(self):
        self._format_plate()
        plate = self.plate_entry.get().strip().upper()
        brand = self.brand_entry.get().strip()
        model = self.model_entry.get().strip()
        year_text = self.year_entry.get().strip()
        color = self.color_entry.get().strip()
        km_text = self.km_entry.get().strip()

        if not plate:
            messagebox.showerror("Erro de Validação", "O campo 'Placa' é obrigatório.")
            return

        if not all(c.isalpha() or c.isspace() for c in brand):
            messagebox.showerror("Erro de Validação", "O campo 'Marca' deve conter apenas letras e espaços.")
            return

        if not all(c.isalpha() or c.isspace() for c in model):
            messagebox.showerror("Erro de Validação", "O campo 'Modelo' deve conter apenas letras e espaços.")
            return

        if not all(c.isalpha() or c.isspace() for c in color):
            messagebox.showerror("Erro de Validação", "O campo 'Cor' deve conter apenas letras e espaços.")
            return

        if km_text and not km_text.isdigit():
            messagebox.showerror("Erro de Validação", "O campo 'KM Atual' deve conter apenas números.")
            return

        if year_text and not year_text.isdigit():
            messagebox.showerror("Erro de Validação", "O campo 'Ano/Modelo' deve conter apenas números.")
            return

        try:
            year = int(year_text) if year_text else None
            if year and year < 1970:
                messagebox.showerror("Erro de Validação", "O ano do veículo não pode ser anterior a 1970.")
                return
        except ValueError:
            year = None

        try:
            km = int(km_text) if km_text else None
        except ValueError:
            km = None

        vehicle = Vehicle(
            plate=plate,
            brand=brand,
            model=model,
            year=year,
            color=color,
            current_km=km,
            customer_id=self.customer_id,
            id=self.vehicle_id,
        )
        self.result = vehicle_service.create_or_update_vehicle(vehicle)
        self.destroy()

    def _close(self):
        self.result = None
        self.destroy()

    def get_input(self):
        self.wait_window()
        return self.result
