import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
import database

class InventarioView(tk.Frame):
    def __init__(self, master, bg_primary, bg_card, text_white, text_muted, accent_blue, accent_green, accent_red):
        super().__init__(master, bg=bg_primary)
        self.bg_primary = bg_primary
        self.bg_card = bg_card
        self.text_white = text_white
        self.text_muted = text_muted
        self.accent_blue = accent_blue
        self.accent_green = accent_green
        self.accent_red = accent_red
        
        self.imagen_path_seleccionada = None
        self.producto_seleccionado_id = None
        self.carpeta_imagenes = "imagenes_productos"
        if not os.path.exists(self.carpeta_imagenes): os.makedirs(self.carpeta_imagenes)
        self.render_view()

    def render_view(self):
        # Título del módulo
        tk.Label(self, text="Control y Gestión de Inventario", font=("Segoe UI", 16, "bold"), bg=self.bg_primary, fg=self.text_white).pack(anchor="w", pady=(0,15))
        
        # Contenedor principal usando Grid para control proporcional absoluto
        main_frame = tk.Frame(self, bg=self.bg_primary)
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_columnconfigure(0, weight=7) # 70% para la Tabla de productos
        main_frame.grid_columnconfigure(1, weight=3) # 30% para el Formulario lateral
        main_frame.grid_rowconfigure(0, weight=1)

        # Contenedor Izquierdo (Tabla de productos)
        left_frame = tk.Frame(main_frame, bg=self.bg_primary)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        # Contenedor Derecho (Formulario - Más ancho y estilizado)
        right_frame = tk.Frame(main_frame, bg=self.bg_card, width=360)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.pack_propagate(False)

        # Configuración de la Tabla (Treeview)
        self.tree = ttk.Treeview(left_frame, columns=("id", "cod", "desc", "precio", "stock", "iva", "imagen"), show="headings")
        for col, txt in [("id","ID"),("cod","Código"),("desc","Descripción"),("precio","Precio ($)"),("stock","Stock"),("iva","Aplica IVA"),("imagen","Imagen")]:
            self.tree.heading(col, text=txt)
        
        # Ajuste dimensional de columnas de la tabla
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("cod", width=120, anchor="w")
        self.tree.column("precio", width=100, anchor="e")
        self.tree.column("stock", width=80, anchor="center")
        self.tree.column("iva", width=90, anchor="center")
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.cargar_producto_seleccionado)

        # --- Componentes del Formulario Lateral ---
        tk.Label(right_frame, text="DATOS DEL PRODUCTO", font=("Segoe UI", 12, "bold"), bg=self.bg_card, fg=self.text_white).pack(pady=(15, 15))
        
        # Campo: Código de barras
        tk.Label(right_frame, text="Código de Barras:", bg=self.bg_card, fg=self.text_white, font=("Segoe UI", 10)).pack(anchor="w", padx=20)
        self.ent_cod = tk.Entry(right_frame, font=("Segoe UI", 11), bg=self.bg_primary, fg=self.text_white, bd=0, insertbackground="white")
        self.ent_cod.pack(fill="x", padx=20, pady=(4, 10), ipady=5)

        # Campo: Descripción
        tk.Label(right_frame, text="Descripción / Nombre:", bg=self.bg_card, fg=self.text_white, font=("Segoe UI", 10)).pack(anchor="w", padx=20)
        self.ent_desc = tk.Entry(right_frame, font=("Segoe UI", 11), bg=self.bg_primary, fg=self.text_white, bd=0, insertbackground="white")
        self.ent_desc.pack(fill="x", padx=20, pady=(4, 10), ipady=5)

        # Campo: Precio
        tk.Label(right_frame, text="Precio de Venta ($):", bg=self.bg_card, fg=self.text_white, font=("Segoe UI", 10)).pack(anchor="w", padx=20)
        self.ent_precio = tk.Entry(right_frame, font=("Segoe UI", 11), bg=self.bg_primary, fg=self.text_white, bd=0, insertbackground="white")
        self.ent_precio.pack(fill="x", padx=20, pady=(4, 10), ipady=5)

        # Campo: Stock
        tk.Label(right_frame, text="Cantidad en Stock:", bg=self.bg_card, fg=self.text_white, font=("Segoe UI", 10)).pack(anchor="w", padx=20)
        self.ent_stock = tk.Entry(right_frame, font=("Segoe UI", 11), bg=self.bg_primary, fg=self.text_white, bd=0, insertbackground="white")
        self.ent_stock.pack(fill="x", padx=20, pady=(4, 10), ipady=5)

        # Checkbutton de IVA (Corregido el color del indicador selectcolor)
        self.var_iva = tk.IntVar(value=1)
        self.chk_iva = tk.Checkbutton(right_frame, text="Aplica IVA General", variable=self.var_iva, 
                                      bg=self.bg_card, fg=self.text_white, font=("Segoe UI", 10),
                                      selectcolor=self.bg_primary, activebackground=self.bg_card, activeforeground=self.text_white)
        self.chk_iva.pack(anchor="w", padx=20, pady=(0, 10))

        # Indicador de Imagen cargada
        self.lbl_img_nombre = tk.Label(right_frame, text="Sin imagen seleccionada", bg=self.bg_card, fg=self.text_muted, font=("Segoe UI", 9, "italic"))
        self.lbl_img_nombre.pack(anchor="w", padx=20, pady=(5, 2))
        
        # Botones de Acción Estilizados con padding interno uniforme
        tk.Button(right_frame, text="🖼️ Seleccionar Imagen", font=("Segoe UI", 10), bg=self.accent_blue, fg=self.text_white, bd=0, cursor="hand2", command=self.seleccionar_imagen).pack(fill="x", padx=20, pady=4, ipady=5)
        
        # Separador visual inferior
        spacer = tk.Frame(right_frame, bg=self.bg_card, height=10)
        spacer.pack(fill="x")

        tk.Button(right_frame, text="➕ Agregar Producto", font=("Segoe UI", 10, "bold"), bg=self.accent_green, fg=self.text_white, bd=0, cursor="hand2", command=self.agregar_producto).pack(fill="x", padx=20, pady=4, ipady=6)
        tk.Button(right_frame, text="✏️ Guardar Edición", font=("Segoe UI", 10, "bold"), bg=self.accent_blue, fg=self.text_white, bd=0, cursor="hand2", command=self.editar_producto).pack(fill="x", padx=20, pady=4, ipady=6)
        tk.Button(right_frame, text="🗑️ Eliminar Producto", font=("Segoe UI", 10, "bold"), bg=self.accent_red, fg=self.text_white, bd=0, cursor="hand2", command=self.eliminar_producto).pack(fill="x", padx=20, pady=4, ipady=6)
        
        self.listar_productos()

    def listar_productos(self):
        self.tree.delete(*self.tree.get_children())
        conn = database.get_connection()
        for r in conn.execute("SELECT id, codigo_barras, descripcion, precio_usd, stock, aplica_iva, imagen_path FROM productos").fetchall():
            self.tree.insert("", "end", values=(
                r[0], 
                r[1], 
                r[2], 
                f"${r[3]:.2f}", 
                r[4], 
                "SÍ" if r[5] == 1 else "NO", 
                os.path.basename(r[6]) if r[6] else "Ninguna"
            ))
        conn.close()

    def seleccionar_imagen(self):
        p = filedialog.askopenfilename(filetypes=[("Archivos de Imagen", "*.png *.jpg *.jpeg")])
        if p: self.imagen_path_seleccionada = p; self.lbl_img_nombre.config(text=os.path.basename(p))

    def cargar_producto_seleccionado(self, event):
        item = self.tree.focus()
        if not item: return
        v = self.tree.item(item, "values")
        self.producto_seleccionado_id = v[0]
        self.ent_cod.delete(0, tk.END); self.ent_cod.insert(0, v[1])
        self.ent_desc.delete(0, tk.END); self.ent_desc.insert(0, v[2])
        self.ent_precio.delete(0, tk.END); self.ent_precio.insert(0, v[3].replace("$", ""))
        self.ent_stock.delete(0, tk.END); self.ent_stock.insert(0, v[4])
        self.var_iva.set(1 if v[5] == "SÍ" else 0)
        self.lbl_img_nombre.config(text=v[6])
        self.imagen_path_seleccionada = None

    def agregar_producto(self):
        c, d, p, s, iv = self.ent_cod.get().strip(), self.ent_desc.get().strip(), self.ent_precio.get().strip(), self.ent_stock.get().strip(), self.var_iva.get()
        if not (c and d and p and s): return
        f_path = ""
        if self.imagen_path_seleccionada:
            f_path = os.path.join(self.carpeta_imagenes, f"{c}{os.path.splitext(self.imagen_path_seleccionada)[1]}")
            shutil.copy(self.imagen_path_seleccionada, f_path)
        conn = database.get_connection()
        try:
            conn.execute("INSERT INTO productos (codigo_barras, descripcion, precio_usd, stock, aplica_iva, imagen_path) VALUES (?,?,?,?,?,?)", (c,d,float(p),int(s),iv,f_path))
            conn.commit()
            self.listar_productos()
            self.limpiar_formulario()
        except Exception as e: messagebox.showerror("Error", str(e))
        finally: conn.close()

    def editar_producto(self):
        if not self.producto_seleccionado_id: return
        c, d, p, s, iv = self.ent_cod.get().strip(), self.ent_desc.get().strip(), self.ent_precio.get().strip(), self.ent_stock.get().strip(), self.var_iva.get()
        conn = database.get_connection()
        row = conn.execute("SELECT imagen_path FROM productos WHERE id = ?", (self.producto_seleccionado_id,)).fetchone()
        f_path = row[0] if row else ""
        if self.imagen_path_seleccionada:
            f_path = os.path.join(self.carpeta_imagenes, f"{c}{os.path.splitext(self.imagen_path_seleccionada)[1]}")
            shutil.copy(self.imagen_path_seleccionada, f_path)
        conn.execute("UPDATE productos SET codigo_barras=?, descripcion=?, precio_usd=?, stock=?, aplica_iva=?, imagen_path=? WHERE id=?", (c,d,float(p),int(s),iv,f_path,self.producto_seleccionado_id))
        conn.commit()
        conn.close()
        self.listar_productos()
        self.limpiar_formulario()

    def eliminar_producto(self):
        if not self.producto_seleccionado_id: return
        if messagebox.askyesno("Confirmar", "¿Eliminar producto?"):
            conn = database.get_connection()
            conn.execute("DELETE FROM productos WHERE id = ?", (self.producto_seleccionado_id,))
            conn.commit(); conn.close()
            self.listar_productos()
            self.limpiar_formulario()

    def limpiar_formulario(self):
        self.producto_seleccionado_id = None
        self.ent_cod.delete(0, tk.END)
        self.ent_desc.delete(0, tk.END)
        self.ent_precio.delete(0, tk.END)
        self.ent_stock.delete(0, tk.END)
        self.var_iva.set(1)
        self.lbl_img_nombre.config(text="Sin imagen seleccionada")
        self.imagen_path_seleccionada = None