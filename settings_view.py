import tkinter as tk
from tkinter import ttk, messagebox
import database
from auth import SessionManager

class SettingsView(tk.Frame):
    def __init__(self, master, bg_primary, bg_card, text_white, text_muted, accent_blue, accent_red):
        super().__init__(master, bg=bg_primary)
        self.bg_primary = bg_primary
        self.bg_card = bg_card
        self.text_white = text_white
        self.text_muted = text_muted
        self.accent_blue = accent_blue
        self.accent_red = accent_red
        self.render_view()

    def render_view(self):
        tk.Label(self, text="Configuración del Establecimiento e Impuestos (SENIAT)", 
                 font=("Segoe UI", 16, "bold"), bg=self.bg_primary, fg=self.text_white).pack(anchor="w", pady=(0,10))

        if not SessionManager.is_admin():
            tk.Label(self, text="⚠️ Solo Administradores tienen acceso a este panel fiscal.", 
                     fg=self.accent_red, bg=self.bg_primary, font=("Segoe UI", 11, "bold")).pack(pady=20)
            return

        canvas_container = tk.Frame(self, bg=self.bg_primary)
        canvas_container.pack(fill="both", expand=True)

        canvas = tk.Canvas(canvas_container, bg=self.bg_primary, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        
        scrollable_frame = tk.Frame(canvas, bg=self.bg_primary)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        conn = database.get_connection()
        cfg = conn.execute("SELECT iva_general, igtf, nombre_comercio, rif, direccion FROM configuracion WHERE id = 1").fetchone()
        conn.close()

        frame = tk.Frame(scrollable_frame, bg=self.bg_card)
        frame.pack(fill="x", pady=5)
        sub = tk.Frame(frame, bg=self.bg_card)
        sub.pack(fill="x", padx=20, pady=20)

        tk.Label(sub, text="Razón Social (Nombre del Comercio):", bg=self.bg_card, fg=self.text_white, font=("Segoe UI", 10)).pack(anchor="w", pady=2)
        ent_name = tk.Entry(sub, font=("Segoe UI", 11)); ent_name.insert(0, cfg[2]); ent_name.pack(fill="x", pady=4)

        tk.Label(sub, text="RIF Jurídico (Ej: J-40012345-6):", bg=self.bg_card, fg=self.text_white, font=("Segoe UI", 10)).pack(anchor="w", pady=2)
        ent_rif = tk.Entry(sub, font=("Segoe UI", 11)); ent_rif.insert(0, cfg[3]); ent_rif.pack(fill="x", pady=4)

        tk.Label(sub, text="Dirección Comercial Física Completa:", bg=self.bg_card, fg=self.text_white, font=("Segoe UI", 10)).pack(anchor="w", pady=2)
        ent_dir = tk.Entry(sub, font=("Segoe UI", 11)); ent_dir.insert(0, cfg[4]); ent_dir.pack(fill="x", pady=4)

        tk.Label(sub, text="Alícuota IVA General (%):", bg=self.bg_card, fg=self.text_white, font=("Segoe UI", 10)).pack(anchor="w", pady=2)
        ent_iva = tk.Entry(sub, font=("Segoe UI", 11)); ent_iva.insert(0, str(cfg[0])); ent_iva.pack(fill="x", pady=4)

        tk.Label(sub, text="Impuesto IGTF sobre Divisas (%):", bg=self.bg_card, fg=self.text_white, font=("Segoe UI", 10)).pack(anchor="w", pady=2)
        ent_igtf = tk.Entry(sub, font=("Segoe UI", 11)); ent_igtf.insert(0, str(cfg[1])); ent_igtf.pack(fill="x", pady=4)

        def save():
            try:
                n, r, d = ent_name.get().strip(), ent_rif.get().strip(), ent_dir.get().strip()
                iv, ig = float(ent_iva.get()), float(ent_igtf.get())
                if not (n and r and d): return messagebox.showwarning("Atención", "Campos obligatorios vacíos.")
                
                db_conn = database.get_connection()
                db_conn.execute("UPDATE configuracion SET nombre_comercio=?, rif=?, direccion=?, iva_general=?, igtf=? WHERE id=1", (n, r, d, iv, ig))
                db_conn.commit()
                db_conn.close()
                messagebox.showinfo("Hecho", "¡Configuración fiscal actualizada!")
            except ValueError: messagebox.showerror("Error", "Formatos numéricos incorrectos.")

        tk.Button(sub, text="💾 Guardar Todos los Cambios", font=("Segoe UI", 11, "bold"), bg=self.accent_blue, fg=self.text_white, bd=0, cursor="hand2", command=save).pack(fill="x", pady=20, ipady=6)