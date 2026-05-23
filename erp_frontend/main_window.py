import customtkinter as ctk
from erp_frontend.dashboard_view import DashboardView
from erp_frontend.pdv_view import PDVView
from erp_frontend.nfe_view import NFeView
from erp_frontend.products_view import ProductsView
from erp_frontend.printer_view import PrinterView
from erp_frontend.os_view import OSView

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("miniERP - Frente de Caixa")
        self.geometry("1024x768")
        
        self.nav_frame = ctk.CTkFrame(self, height=60, corner_radius=0)
        self.nav_frame.pack(side="top", fill="x")
        
        self.logo = ctk.CTkLabel(self.nav_frame, text="ERP", font=("Roboto", 24, "bold"), text_color="#2ecc71")
        self.logo.pack(side="left", padx=20)
        
        self.btn_dash = ctk.CTkButton(self.nav_frame, text="[DASHBOARD]", command=lambda: self.show_view(DashboardView), width=100)
        self.btn_dash.pack(side="left", padx=10)
        
        self.btn_pdv = ctk.CTkButton(self.nav_frame, text="[PDV]", command=lambda: self.show_view(PDVView), width=100)
        self.btn_pdv.pack(side="left", padx=10)
        
        self.btn_nfe = ctk.CTkButton(self.nav_frame, text="[NF-e]", command=lambda: self.show_view(NFeView), width=100)
        self.btn_nfe.pack(side="left", padx=10)
        
        self.btn_prod = ctk.CTkButton(self.nav_frame, text="[PRODUTOS]", command=lambda: self.show_view(ProductsView), width=100)
        self.btn_prod.pack(side="left", padx=10)
        
        self.btn_os = ctk.CTkButton(self.nav_frame, text="[ORDEM DE SERVIÇO]", command=lambda: self.show_view(OSView), width=150)
        self.btn_os.pack(side="left", padx=10)
        
        self.btn_print = ctk.CTkButton(self.nav_frame, text="[IMPRESSORAS]", command=lambda: self.show_view(PrinterView), width=100)
        self.btn_print.pack(side="left", padx=10)
        
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#1e1e1e")
        self.content_frame.pack(side="top", fill="both", expand=True)
        
        self.current_view = None
        self.show_view(DashboardView)
        
    def show_view(self, view_class):
        if self.current_view:
            self.current_view.destroy()
        self.current_view = view_class(self.content_frame, self)
        self.current_view.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = MainWindow()
    # Tries to maximize on Windows
    try:
        app.state('zoomed')
    except:
        pass
    app.mainloop()