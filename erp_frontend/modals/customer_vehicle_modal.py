import customtkinter as ctk
from tkinter import messagebox
from erp_frontend.components.table import TableComponent
from erp_backend.services import vehicle_service
from .vehicle_modal import VehicleModal
<<<<<<< HEAD
from erp_frontend import theme
=======
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18

class CustomerVehiclesModal(ctk.CTkToplevel):
    def __init__(self, master, customer_id, customer_name):
        super().__init__(master)
        self.customer_id = customer_id
        self.customer_name = customer_name
<<<<<<< HEAD
        self.configure(fg_color=theme.BG)
=======
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18

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

<<<<<<< HEAD
        btn_new = ctk.CTkButton(actions_frame, text="[ NOVO VEÍCULO ]", command=self.new_vehicle, **theme.btn_primary())
        btn_new.pack(side="left", padx=5)

        btn_edit = ctk.CTkButton(actions_frame, text="[ EDITAR VEÍCULO ]", command=self.edit_selected_vehicle, **theme.btn_secondary())
=======
        btn_new = ctk.CTkButton(actions_frame, text="[ NOVO VEÍCULO ]", font=("Roboto", 14, "bold"), command=self.new_vehicle)
        btn_new.pack(side="left", padx=5)

        btn_edit = ctk.CTkButton(actions_frame, text="[ EDITAR VEÍCULO ]", font=("Roboto", 14, "bold"), fg_color="#f39c12", hover_color="#d68910", command=self.edit_selected_vehicle)
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
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
<<<<<<< HEAD
=======
        """Carrega e exibe os veículos do cliente na tabela."""
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
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
<<<<<<< HEAD
        modal = VehicleModal(self, customer_id=self.customer_id)
        modal.get_input()
        self.load_vehicles()

    def edit_selected_vehicle(self):
=======
        """Abre a modal para cadastrar um novo veículo para este cliente."""
        modal = VehicleModal(self, customer_id=self.customer_id)
        modal.get_input()  # Espera a modal fechar
        self.load_vehicles() # Atualiza a lista

    def edit_selected_vehicle(self):
        """Abre a modal para editar o veículo selecionado."""
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um veículo para editar.")
            return
<<<<<<< HEAD

        vehicle_id = int(selected[0])
        modal = VehicleModal(self, customer_id=self.customer_id, vehicle_id=vehicle_id)
        modal.get_input()
        self.load_vehicles()
=======
        
        vehicle_id = int(selected[0])
        modal = VehicleModal(self, customer_id=self.customer_id, vehicle_id=vehicle_id)
        modal.get_input() # Espera a modal fechar
        self.load_vehicles() # Atualiza a lista
>>>>>>> b8696156ad077242d2bbfc43a202beb2b9ea5c18
