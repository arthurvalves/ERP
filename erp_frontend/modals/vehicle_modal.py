import customtkinter as ctk

from erp_backend.models.vehicle import Vehicle
from erp_backend.services import vehicle_service


class VehicleModal(ctk.CTkToplevel):
    def __init__(self, master, customer_id, vehicle_id=None, initial_plate=""):
        super().__init__(master)
        self.title("Veículo")
        self.geometry("520x360")
        self.transient(master)
        self.grab_set()

        self.customer_id = customer_id
        self.vehicle_id = vehicle_id
        self.result = None

        self.protocol("WM_DELETE_WINDOW", self._close)
        self._setup_ui(initial_plate)
        self._load_vehicle()

    def _setup_ui(self, initial_plate):
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=16, pady=16)

        self.plate_entry = self._add_field(form, "Placa", 0)
        self.plate_entry.insert(0, initial_plate)
        self.brand_entry = self._add_field(form, "Marca", 1)
        self.model_entry = self._add_field(form, "Modelo", 2)
        self.year_entry = self._add_field(form, "Ano", 3)

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(fill="x", padx=16, pady=(0, 16))

        ctk.CTkButton(buttons, text="Cancelar", command=self._close).pack(side="right")
        ctk.CTkButton(buttons, text="Salvar", command=self._save).pack(side="right", padx=(0, 8))

    def _add_field(self, parent, label, row):
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, sticky="w", pady=(0, 8))
        entry = ctk.CTkEntry(parent)
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

    def _save(self):
        plate = self.plate_entry.get().strip().upper()
        if not plate:
            return

        brand = self.brand_entry.get().strip()
        model = self.model_entry.get().strip()
        year_text = self.year_entry.get().strip()
        try:
            year = int(year_text) if year_text else None
        except ValueError:
            year = None

        vehicle = Vehicle(
            plate=plate,
            brand=brand,
            model=model,
            year=year,
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
