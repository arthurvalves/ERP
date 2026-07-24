import customtkinter as ctk
from tkinter import messagebox
from erp_frontend.components.table import TableComponent
from erp_backend.services import vehicle_service
from .vehicle_modal import VehicleModal
from erp_frontend import theme

class CustomerVehiclesModal(ctk.CTkToplevel):
    def __init__(self, master, customer_id, customer_name):
        super().__init__(master)
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.configure(fg_color=theme.BG)

        self.title(f"Veículos de {self.customer_name}")
        self.transient(master)
        self.grab_set()

        self.setup_ui()
        self.load_vehicles()
        self.after(10, self._center_window)

    def _center_window(self):
        self.update_idletasks()
        width = 800
        height = 600
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        self.resizable(False, False)

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        actions_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(0, 10))

        btn_new = ctk.CTkButton(actions_frame, text="[ NOVO VEÍCULO ]", command=self.new_vehicle, **theme.btn_primary())
        btn_new.pack(side="left", padx=5)

        btn_edit = ctk.CTkButton(actions_frame, text="[ EDITAR VEÍCULO ]", command=self.edit_selected_vehicle, **theme.btn_secondary())
        btn_edit.pack(side="left", padx=5)

        columns = ("PLACA", "MARCA", "MODELO", "ANO", "COR", "KM ATUAL")
        self.table = TableComponent(main_frame, columns)
        self.table.column("PLACA", width=120)
        self.table.column("MARCA", width=150, anchor="w")
        self.table.column("MODELO", width=180, anchor="w")
        self.table.column("ANO", width=80)
        self.table.column("COR", width=100)
        self.table.column("KM ATUAL", width=120)
        self.table.pack(fill="both", expand=True)
        self.table.bind("<Double-1>", lambda e: self.edit_selected_vehicle())

    def load_vehicles(self):
        for item in self.table.get_children():
            self.table.delete(item)

        vehicles = vehicle_service.get_vehicles_by_customer(self.customer_id)
        for vehicle in vehicles:
            self.table.insert("", "end", iid=str(vehicle.id), values=(
                vehicle.plate,
                vehicle.brand or "--",
                vehicle.model or "--",
                vehicle.year or "--",
                vehicle.color or "--",
                vehicle.current_km or "--"
            ))

    def new_vehicle(self):
        modal = VehicleModal(self, customer_id=self.customer_id)
        modal.get_input()
        self.load_vehicles()

    def edit_selected_vehicle(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um veículo para editar.")
            return

        vehicle_id = int(selected[0])
        modal = VehicleModal(self, customer_id=self.customer_id, vehicle_id=vehicle_id)
        modal.get_input()
        self.load_vehicles()
