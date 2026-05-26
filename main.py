import tkinter as tk
from tkinter import ttk, messagebox
import database
from auth import SessionManager
from sales_room import SalesRoomView
from reports_view import ReportsView
from settings_view import SettingsView
from inventario import InventarioView

BG_PRIMARY = "#1e1e2f"
BG_SIDEBAR = "#11111b"
BG_CARD = "#27273f"
TEXT_WHITE = "#ffffff"
TEXT_MUTED = "#a5a5b5"
ACCENT_BLUE = "#5865f2"
ACCENT_GREEN = "#23a55a"
ACCENT_RED = "#f23f43"

class ModernPOSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Araguaney POS - Enterprise Edition")
        self.geometry("1280x720")
        self.configure(bg=BG_PRIMARY)
        database.init_db()
        self.show_login_screen()

    def show_login_screen(self):
        self.login_frame = tk.Frame(self, bg=BG_SIDEBAR, bd=2, relief="groove")
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=420)

        tk.Label(self.login_frame, text="ARAGUANEY POS", font=("Segoe UI", 18, "bold"), bg=BG_SIDEBAR, fg=ACCENT_BLUE).pack(pady=25)
        
        tk.Label(self.login_frame, text="Usuario", bg=BG_SIDEBAR, fg=TEXT_WHITE).pack(anchor="w", padx=40, pady=5)
        self.ent_user = tk.Entry(self.login_frame, font=("Segoe UI", 11), bg=BG_CARD, fg=TEXT_WHITE, bd=0)
        self.ent_user.pack(fill="x", padx=40, ipady=4)

        tk.Label(self.login_frame, text="Contraseña", bg=BG_SIDEBAR, fg=TEXT_WHITE).pack(anchor="w", padx=40, pady=5)
        self.ent_pass = tk.Entry(self.login_frame, font=("Segoe UI", 11), bg=BG_CARD, fg=TEXT_WHITE, bd=0, show="*")
        self.ent_pass.pack(fill="x", padx=40, ipady=4)

        tk.Button(self.login_frame, text="Ingresar al Sistema", font=("Segoe UI", 11, "bold"), bg=ACCENT_BLUE, fg=TEXT_WHITE, bd=0, command=self.process_login).pack(fill="x", padx=40, pady=35, ipady=6)

    def process_login(self):
        if SessionManager.login(self.ent_user.get(), self.ent_pass.get()):
            self.login_frame.destroy()
            self.build_interface()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

    def build_interface(self):
        self.sidebar = tk.Frame(self, bg=BG_SIDEBAR, width=210)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        user_info = SessionManager.get_user()
        tk.Label(self.sidebar, text=f"👤 {user_info['nombre']}", font=("Segoe UI", 10, "bold"), bg=BG_SIDEBAR, fg=TEXT_WHITE).pack(pady=(15,2), padx=10, anchor="w")
        tk.Label(self.sidebar, text=f"Rol: {user_info['rol']}", font=("Segoe UI", 9), bg=BG_SIDEBAR, fg=TEXT_MUTED).pack(pady=(0,15), padx=10, anchor="w")

        modules = [
            ("Dashboard", self.show_dashboard),
            ("Punto de Venta", self.open_sales),
            ("Inventario", self.show_inventory),
            ("Proveedores", self.show_suppliers),
            ("Estadísticas", self.open_reports),
            ("Configuración Comercio", self.show_settings)
        ]

        for name, func in modules:
            btn = tk.Button(self.sidebar, text=name, font=("Segoe UI", 10), bg=BG_SIDEBAR, fg=TEXT_WHITE, bd=0, anchor="w", padx=15, cursor="hand2")
            btn.pack(fill="x", ipady=10)
            btn.bind("<Button-1>", lambda e, f=func: f())

        btn_logout = tk.Button(self.sidebar, text="❌ Cerrar Sesión", font=("Segoe UI", 10, "bold"), bg=ACCENT_RED, fg=TEXT_WHITE, bd=0, command=self.process_logout)
        btn_logout.pack(side="bottom", fill="x", ipady=10)

        self.main_container = tk.Frame(self, bg=BG_PRIMARY)
        self.main_container.pack(side="right", expand=True, fill="both", padx=15, pady=15)
        self.show_dashboard()

    def clear_container(self):
        for w in self.main_container.winfo_children(): w.destroy()

    def process_logout(self):
        SessionManager.logout()
        self.sidebar.destroy(); self.main_container.destroy()
        self.show_login_screen()

    def show_dashboard(self):
        self.clear_container()
        tk.Label(self.main_container, text="Panel Informativo Principal (Dashboard)", font=("Segoe UI", 16, "bold"), bg=BG_PRIMARY, fg=TEXT_WHITE).pack(anchor="w", pady=10)
        conn = database.get_connection()
        total_ventas = conn.execute("SELECT SUM(total_usd) FROM ventas").fetchone()[0] or 0.0
        cant_prod = conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0]
        conn.close()

        cards_frame = tk.Frame(self.main_container, bg=BG_PRIMARY)
        cards_frame.pack(fill="x", pady=20)
        for title, value, col in [("Ventas Consolidadas", f"$ {total_ventas:,.2f}", ACCENT_GREEN), ("Items en Catálogo", str(cant_prod), ACCENT_BLUE)]:
            card = tk.Frame(cards_frame, bg=BG_CARD, width=260, height=100)
            card.pack(side="left", padx=10, fill="both", expand=True); card.pack_propagate(False)
            tk.Label(card, text=title, bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w", padx=15, pady=(15,2))
            tk.Label(card, text=value, font=("Segoe UI", 18, "bold"), bg=BG_CARD, fg=col).pack(anchor="w", padx=15)

    def open_sales(self):
        self.clear_container()
        SalesRoomView(self.main_container, BG_PRIMARY, BG_CARD, TEXT_WHITE, TEXT_MUTED, ACCENT_BLUE, ACCENT_GREEN, ACCENT_RED).pack(fill="both", expand=True)

    def open_reports(self):
        self.clear_container()
        ReportsView(self.main_container, BG_PRIMARY, BG_CARD, TEXT_WHITE).pack(fill="both", expand=True)

    def show_inventory(self):
        self.clear_container()
        InventarioView(self.main_container, BG_PRIMARY, BG_CARD, TEXT_WHITE, TEXT_MUTED, ACCENT_BLUE, ACCENT_GREEN, ACCENT_RED).pack(fill="both", expand=True)

    def show_suppliers(self):
        self.clear_container()
        tk.Label(self.main_container, text="Gestión y Registro de Proveedores de Mercancía", font=("Segoe UI", 16, "bold"), bg=BG_PRIMARY, fg=TEXT_WHITE).pack(anchor="w", pady=(0, 10))
        
        form_frame = tk.Frame(self.main_container, bg=BG_CARD); form_frame.pack(fill="x", pady=10)
        inner_form = tk.Frame(form_frame, bg=BG_CARD); inner_form.pack(fill="x", padx=15, pady=15)
        tk.Label(inner_form, text="RIF (Ej: J-12345678-0):", bg=BG_CARD, fg=TEXT_WHITE).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ent_rif = tk.Entry(inner_form, font=("Segoe UI", 10), width=15); ent_rif.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(inner_form, text="Nombre / Razón Social:", bg=BG_CARD, fg=TEXT_WHITE).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ent_razon = tk.Entry(inner_form, font=("Segoe UI", 10), width=25); ent_razon.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(inner_form, text="Teléfono de Contacto:", bg=BG_CARD, fg=TEXT_WHITE).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ent_tlf = tk.Entry(inner_form, font=("Segoe UI", 10), width=15); ent_tlf.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(inner_form, text="Stock Adquirido (Cantidades):", bg=BG_CARD, fg=TEXT_WHITE).grid(row=1, column=2, padx=5, pady=5, sticky="w")
        ent_stock_prov = tk.Entry(inner_form, font=("Segoe UI", 10), width=10); ent_stock_prov.grid(row=1, column=3, padx=5, pady=5)

        def guardar_proveedor():
            r, rz, t, st = ent_rif.get().strip(), ent_razon.get().strip(), ent_tlf.get().strip(), ent_stock_prov.get().strip()
            if not (r and rz and t): return
            conn = database.get_connection()
            try:
                conn.execute("INSERT INTO proveedores (rif, razon_social, telefono, direccion) VALUES (?, ?, ?, ?)", (r, rz, t, st if st else "0"))
                conn.commit(); self.show_suppliers()
            except Exception as e: messagebox.showerror("Error", str(e))
            finally: conn.close()

        tk.Button(inner_form, text="➕ Registrar Proveedor", bg=ACCENT_BLUE, fg=TEXT_WHITE, font=("Segoe UI", 10, "bold"), bd=0, command=guardar_proveedor).grid(row=0, column=4, rowspan=2, padx=20, pady=5, ipady=8)

        tree = ttk.Treeview(self.main_container, columns=("id", "rif", "razon", "telefono", "stock"), show="headings")
        for c, tx in [("id","ID"),("rif","RIF"),("razon","Razón Social"),("telefono","Teléfono"),("stock","Lote Suministrado")]: tree.heading(c, text=tx)
        tree.pack(fill="both", expand=True, pady=10)
        conn = database.get_connection()
        for row in conn.execute("SELECT * FROM proveedores").fetchall(): tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4]))
        conn.close()

    def show_settings(self):
        self.clear_container()
        SettingsView(self.main_container, BG_PRIMARY, BG_CARD, TEXT_WHITE, TEXT_MUTED, ACCENT_BLUE, ACCENT_RED).pack(fill="both", expand=True)

if __name__ == "__main__":
    app = ModernPOSApp()
    app.mainloop()