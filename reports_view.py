import tkinter as tk
from tkinter import ttk
import database

class ReportsView(tk.Frame):
    def __init__(self, master, bg_primary, bg_card, text_white):
        super().__init__(master, bg=bg_primary)
        self.bg_primary = bg_primary
        self.bg_card = bg_card
        self.text_white = text_white
        self.render()

    def render(self):
        tk.Label(self, text="Auditoría de Ventas y Cierre de Caja", font=("Segoe UI", 16, "bold"), bg=self.bg_primary, fg=self.text_white).pack(anchor="w", pady=10)
        
        tree = ttk.Treeview(self, columns=("id", "fecha", "tot", "metodo", "tasa"), show="headings")
        tree.heading("id", text="Factura ID"); tree.heading("fecha", text="Fecha / Hora")
        tree.heading("tot", text="Monto ($)"); tree.heading("metodo", text="Método Liquidación"); tree.heading("tasa", text="Tasa Aplicada")
        tree.pack(fill="both", expand=True)

        conn = database.get_connection()
        for r in conn.execute("SELECT id, fecha, total_usd, metodo_pago, tasa_venda FROM ventas ORDER BY id DESC").fetchall():
            tree.insert("", "end", values=(r[0], r[1], f"${r[2]:.2f}", r[3], f"{r[4]:.2f} Bs"))
        conn.close()