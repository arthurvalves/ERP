import customtkinter as ctk
from tkinter import messagebox
from erp_frontend.components.table import TableComponent
from erp_backend.services import maintenance_service, whatsapp_service
from erp_frontend import theme

class MaintenanceAlertsView(ctk.CTkFrame):
    def __init__(self, master, app_window, **kwargs):
        super().__init__(master, fg_color=theme.BG, **kwargs)
        self.app_window = app_window
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(top_frame, text="ALERTAS DE MANUTENÇÃO PREVENTIVA", font=theme.font_title(24), text_color=theme.PRIMARY).pack(side="left")

        btn_notify = ctk.CTkButton(top_frame, text="[ NOTIFICAR CLIENTE ]", command=self.notify_customer, **theme.btn_primary())
        btn_notify.pack(side="right", padx=5)

        btn_refresh = ctk.CTkButton(top_frame, text="[ ATUALIZAR ]", command=self.load_data, **theme.btn_secondary())
        btn_refresh.pack(side="right", padx=5)

        columns = ("PLACA", "VEÍCULO", "CLIENTE", "KM ATUAL", "KM ÚLTIMA REVISÃO", "STATUS")
        self.table = TableComponent(self, columns)
        self.table.column("PLACA", width=100)
        self.table.column("VEÍCULO", width=200, anchor="w")
        self.table.column("CLIENTE", width=300, anchor="w")
        self.table.column("KM ATUAL", width=120)
        self.table.column("KM ÚLTIMA REVISÃO", width=150)
        self.table.column("STATUS", width=150)
        self.table.pack(fill="both", expand=True, padx=20, pady=10)
        self.table.tag_configure("due", foreground=theme.DANGER, font=(theme.FONT_FAMILY, 12, "bold"))

    def load_data(self):
        for item in self.table.get_children():
            self.table.delete(item)

        alerts = maintenance_service.get_maintenance_alerts()
        for row in alerts:
            km_diff = (row['current_km'] or 0) - (row['km_at_last_change'] or 0)
            self.table.insert("", "end", iid=str(row['vehicle_id']), values=(
                row['plate'],
                row['model'] or "--",
                row['customer_name'],
                row['current_km'] or "N/A",
                row['km_at_last_change'] or "NUNCA FEZ",
                f"VENCIDO HÁ {km_diff} KM"
            ), tags=("due",))

    def notify_customer(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um veículo para notificar o cliente.")
            return

        vehicle_id = int(selected[0])
        alerts = maintenance_service.get_maintenance_alerts()
        alert_data = next((a for a in alerts if a['vehicle_id'] == vehicle_id), None)

        if not alert_data or not alert_data['customer_phone']:
            messagebox.showerror("Erro", "Cliente não possui um número de telefone cadastrado.")
            return

        if messagebox.askyesno("Confirmar Envio", f"Enviar alerta de manutenção via WhatsApp para {alert_data['customer_name']}?"):
            try:
                whatsapp_service.send_maintenance_alert_whatsapp(
                    telefone=alert_data['customer_phone'],
                    customer_name=alert_data['customer_name'],
                    vehicle_plate=alert_data['plate'],
                    vehicle_model=alert_data['model']
                )
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao tentar abrir o WhatsApp.\n\nDetalhes: {e}")
