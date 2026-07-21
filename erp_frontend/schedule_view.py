import customtkinter as ctk
from datetime import datetime, timedelta
from erp_backend.services import schedule_service
from erp_frontend.os_view import OSModal

class ScheduleView(ctk.CTkFrame):
    def __init__(self, master, app_window, **kwargs):
        super().__init__(master, fg_color="#1e1e1e", **kwargs)
        self.app_window = app_window
        self.current_date = datetime.today()
        self.setup_ui()
        self.load_schedule()

    def setup_ui(self):
        # Cabeçalho com navegação de semana
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=10)

        btn_prev = ctk.CTkButton(header, text="<< Semana Anterior", command=self.prev_week)
        btn_prev.pack(side="left")

        self.week_label = ctk.CTkLabel(header, text="", font=("Roboto", 18, "bold"))
        self.week_label.pack(side="left", expand=True)

        btn_next = ctk.CTkButton(header, text="Próxima Semana >>", command=self.next_week)
        btn_next.pack(side="right")

        # Container da Agenda
        self.schedule_container = ctk.CTkScrollableFrame(self, fg_color="#2b2b2b")
        self.schedule_container.pack(fill="both", expand=True, padx=20, pady=10)

    def load_schedule(self):
        # Limpa a agenda anterior
        for widget in self.schedule_container.winfo_children():
            widget.destroy()

        # Define o período da semana
        start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        self.week_label.configure(text=f"Semana de {start_of_week.strftime('%d/%m')} a {end_of_week.strftime('%d/%m/%Y')}")

        # Busca os dados
        scheduled_orders = schedule_service.get_scheduled_orders_for_period(start_of_week, end_of_week)

        # Cria as colunas dos dias
        days_of_week = [(start_of_week + timedelta(days=i)) for i in range(7)]
        for i, day in enumerate(days_of_week):
            day_frame = ctk.CTkFrame(self.schedule_container, fg_color="#333333", border_width=1, border_color="#444444")
            day_frame.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)
            self.schedule_container.grid_columnconfigure(i, weight=1)

            day_str = day.strftime("%A").upper()
            date_str = day.strftime("%d/%m")
            ctk.CTkLabel(day_frame, text=f"{day_str}\n{date_str}", font=("Roboto", 14, "bold")).pack(fill="x", pady=5)

            # Adiciona os cards de OS para aquele dia
            orders_for_day = [
                order for order in scheduled_orders
                if datetime.strptime(order['scheduled_start_time'], '%Y-%m-%d %H:%M:%S').date() == day.date()
            ]
            
            if not orders_for_day:
                ctk.CTkLabel(day_frame, text="Nenhum agendamento", text_color="#7f8c8d").pack(pady=20)
            else:
                for order in orders_for_day:
                    self.create_os_card(day_frame, order)

    def create_os_card(self, parent_frame, order_data):
        start_time = datetime.strptime(order_data['scheduled_start_time'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M')
        
        card_color = "#2980b9" # Azul para agendado
        if order_data['status'] == 'Concluída':
            card_color = "#27ae60" # Verde
        elif order_data['status'] == 'Cancelada':
            card_color = "#7f8c8d" # Cinza

        card = ctk.CTkFrame(parent_frame, fg_color=card_color, corner_radius=8)
        card.pack(fill="x", padx=5, pady=5)

        time_label = ctk.CTkLabel(card, text=start_time, font=("Roboto", 16, "bold"))
        time_label.pack(anchor="w", padx=10, pady=(5, 0))

        plate_label = ctk.CTkLabel(card, text=f"Placa: {order_data['plate']}", font=("Roboto", 14))
        plate_label.pack(anchor="w", padx=10)

        customer_label = ctk.CTkLabel(card, text=f"Cliente: {order_data['nome_razao_social'][:15]}...", font=("Roboto", 12))
        customer_label.pack(anchor="w", padx=10, pady=(0, 5))

        card.bind("<Button-1>", lambda e, oid=order_data['id']: self.open_os(oid))
        time_label.bind("<Button-1>", lambda e, oid=order_data['id']: self.open_os(oid))
        plate_label.bind("<Button-1>", lambda e, oid=order_data['id']: self.open_os(oid))
        customer_label.bind("<Button-1>", lambda e, oid=order_data['id']: self.open_os(oid))

    def open_os(self, os_id):
        OSModal(self, os_id=os_id, on_save=self.load_schedule)

    def prev_week(self):
        self.current_date -= timedelta(weeks=1)
        self.load_schedule()

    def next_week(self):
        self.current_date += timedelta(weeks=1)
        self.load_schedule()