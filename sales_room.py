import tkinter as tk
from tkinter import ttk, messagebox
import os
import requests
from PIL import Image, ImageTk
import database
from ticket_generator import generar_ticket_pdf 

class SalesRoomView(tk.Frame):
    def __init__(self, master, bg_primary, bg_card, text_white, text_muted, accent_blue, accent_green, accent_red):
        super().__init__(master, bg=bg_primary)
        self.bg_primary = bg_primary
        self.bg_card = bg_card
        self.text_white = text_white
        self.text_muted = text_muted
        self.accent_blue = accent_blue
        self.accent_green = accent_green
        self.accent_red = accent_red
        
        # --- RESOLUCIÓN INTELIGENTE DE USUARIO_ID ---
        self.usuario_id = self._detectar_usuario_id(master)
        
        self.carrito = []  # Estructura: [id, codigo, descripcion, precio, cantidad]
        self.imagen_defecto = None
        self.render_view()

    def _detectar_usuario_id(self, master):
        """ Detecta el ID del usuario logueado en la app o busca un respaldo en la BD """
        for attr in ["current_user_id", "usuario_id", "user_id"]:
            if hasattr(master, attr) and getattr(master, attr) is not None:
                return getattr(master, attr)
            if hasattr(master.master, attr) and getattr(master.master, attr) is not None:
                return getattr(master.master, attr)
        
        conn = database.get_connection()
        try:
            row = conn.execute("SELECT id FROM usuarios ORDER BY id ASC LIMIT 1").fetchone()
            if row:
                return row[0]
        except Exception:
            pass
        finally:
            conn.close()
            
        return 1

    def _obtener_tasa_bcv_api(self):
        """ Consume la API oficial de DolarAPI para Venezuela con fallback seguro """
        try:
            response = requests.get("https://ve.dolarapi.com/v1/dolares/oficial", timeout=3)
            if response.status_code == 200:
                data = response.json()
                return float(data.get("promedio", 36.50))
        except Exception:
            pass
        
        conn = database.get_connection()
        tasa = 36.50
        try:
            row = conn.execute("SELECT tasa_cambio FROM configuracion WHERE id = 1").fetchone()
            if row and row[0]: tasa = float(row[0])
        except Exception:
            try:
                row = conn.execute("SELECT tasa_bcv FROM configuracion WHERE id = 1").fetchone()
                if row and row[0]: tasa = float(row[0])
            except Exception:
                pass
        finally:
            conn.close()
        return tasa

    def render_view(self):
        # --- DISEÑO DE PASARELA Y FILAS PROPORCIONALES ---
        main_frame = tk.Frame(self, bg=self.bg_primary)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=6)  # 60% Catálogo y Carrito
        main_frame.grid_columnconfigure(1, weight=4)  # 40% Facturación y Visor de Imagen
        main_frame.grid_rowconfigure(0, weight=1)

        # ==========================================
        # PANEL IZQUIERDO: SELECCIÓN Y CARRITO
        # ==========================================
        left_panel = tk.Frame(main_frame, bg=self.bg_primary)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        search_frame = tk.LabelFrame(left_panel, text=" BÚSQUEDA DE PRODUCTOS ", bg=self.bg_primary, fg=self.text_white, font=("Segoe UI", 10, "bold"))
        search_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(search_frame, text="Seleccione un producto para añadir al carrito:", bg=self.bg_primary, fg=self.text_muted).pack(anchor="w", padx=10, pady=2)
        
        self.tree_productos = ttk.Treeview(search_frame, columns=("id", "cod", "desc", "precio", "stock"), show="headings", height=5)
        for col, txt in [("id","ID"), ("cod","Código"), ("desc","Producto"), ("precio","Precio ($)"), ("stock","Disponibilidad")]:
            self.tree_productos.heading(col, text=txt)
        self.tree_productos.column("id", width=40, anchor="center")
        self.tree_productos.column("precio", width=80, anchor="e")
        self.tree_productos.column("stock", width=90, anchor="center")
        self.tree_productos.pack(fill="x", padx=10, pady=5)
        self.tree_productos.bind("<<TreeviewSelect>>", self.on_producto_seleccionado)
        
        tk.Button(search_frame, text="🛒 Añadir al Carrito", font=("Segoe UI", 10, "bold"), bg=self.accent_blue, fg=self.text_white, bd=0, cursor="hand2", command=self.añadir_al_carrito).pack(fill="x", padx=10, pady=8, ipady=4)

        cart_frame = tk.LabelFrame(left_panel, text=" ITEMS EN EL CARRITO ACTUAL ", bg=self.bg_primary, fg=self.text_white, font=("Segoe UI", 10, "bold"))
        cart_frame.pack(fill="both", expand=True)

        self.tree_carrito = ttk.Treeview(cart_frame, columns=("id", "cod", "desc", "precio", "cant", "total"), show="headings")
        for col, txt in [("id","ID"), ("cod","Código"), ("desc","Descripción"), ("precio","Precio ($)"), ("cant","Cant"), ("total","Total ($)")]:
            self.tree_carrito.heading(col, text=txt)
        self.tree_carrito.column("id", width=40, anchor="center")
        self.tree_carrito.column("cant", width=50, anchor="center")
        self.tree_carrito.column("precio", width=80, anchor="e")
        self.tree_carrito.column("total", width=90, anchor="e")
        self.tree_carrito.pack(fill="both", expand=True, padx=10, pady=5)

        tk.Button(cart_frame, text="❌ Quitar ítem del Carrito", font=("Segoe UI", 9), bg=self.accent_red, fg=self.text_white, bd=0, cursor="hand2", command=self.quitar_del_carrito).pack(anchor="e", padx=10, pady=5, ipadx=10, ipady=2)

        # ==========================================
        # PANEL DERECHO: DETALLES, IMAGEN Y COBRO
        # ==========================================
        right_panel = tk.Frame(main_frame, bg=self.bg_card, width=380)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.pack_propagate(False)

        # 1. Multimedia Fija Proporcional
        img_frame = tk.LabelFrame(right_panel, text=" MULTIMEDIA DE PRODUCTO ", bg=self.bg_card, fg=self.text_white, font=("Segoe UI", 9, "bold"))
        img_frame.pack(fill="x", padx=15, pady=10)
        
        self.lbl_imagen_prod = tk.Label(img_frame, text="Seleccione un producto del catálogo\npara visualizar su imagen", bg=self.bg_card, fg=self.text_muted, font=("Segoe UI", 10, "italic"), height=10, width=30)
        self.lbl_imagen_prod.pack(padx=10, pady=10, expand=True)

        # 2. Selector de Métodos de Pago
        pay_config_frame = tk.LabelFrame(right_panel, text=" PARÁMETROS DE PAGO ", bg=self.bg_card, fg=self.text_white, font=("Segoe UI", 9, "bold"))
        pay_config_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(pay_config_frame, text="Método de Pago:", bg=self.bg_card, fg=self.text_muted, font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.cmb_metodo_pago = ttk.Combobox(pay_config_frame, values=["Efectivo $", "Efectivo Bs.", "Tarjeta Débito", "Pago Móvil", "Punto de Venta"], state="readonly", font=("Segoe UI", 10))
        self.cmb_metodo_pago.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        self.cmb_metodo_pago.set("Efectivo $")
        self.cmb_metodo_pago.bind("<<ComboboxSelected>>", lambda e: self.actualizar_tabla_carrito())

        # 3. Panel Contable con API BCV e Impuestos Desglosados
        totals_frame = tk.Frame(right_panel, bg=self.bg_card)
        totals_frame.pack(fill="x", padx=15, pady=10)
        totals_frame.grid_columnconfigure(0, weight=1)
        totals_frame.grid_columnconfigure(1, weight=1)

        tk.Label(totals_frame, text="SUBTOTAL NETO:", bg=self.bg_card, fg=self.text_muted, font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=2)
        self.lbl_subtotal = tk.Label(totals_frame, text="$0.00", bg=self.bg_card, fg=self.text_white, font=("Segoe UI", 10, "bold"))
        self.lbl_subtotal.grid(row=0, column=1, sticky="e", pady=2)

        self.lbl_titulo_iva = tk.Label(totals_frame, text="IVA (16%):", bg=self.bg_card, fg=self.text_muted, font=("Segoe UI", 10))
        self.lbl_titulo_iva.grid(row=1, column=0, sticky="w", pady=2)
        self.lbl_iva = tk.Label(totals_frame, text="$0.00", bg=self.bg_card, fg=self.text_white, font=("Segoe UI", 10))
        self.lbl_iva.grid(row=1, column=1, sticky="e", pady=2)

        self.lbl_titulo_igtf = tk.Label(totals_frame, text="IGTF (3%):", bg=self.bg_card, fg=self.text_muted, font=("Segoe UI", 10))
        self.lbl_titulo_igtf.grid(row=2, column=0, sticky="w", pady=2)
        self.lbl_igtf = tk.Label(totals_frame, text="$0.00", bg=self.bg_card, fg=self.text_white, font=("Segoe UI", 10))
        self.lbl_igtf.grid(row=2, column=1, sticky="e", pady=2)

        tk.Label(totals_frame, text="TOTAL EN DIVISAS:", bg=self.bg_card, fg=self.text_white, font=("Segoe UI", 12, "bold")).grid(row=3, column=0, sticky="w", pady=(10,0))
        self.lbl_total = tk.Label(totals_frame, text="$0.00", bg=self.bg_card, fg=self.accent_green, font=("Segoe UI", 14, "bold"))
        self.lbl_total.grid(row=3, column=1, sticky="e", pady=(10,0))

        tk.Label(totals_frame, text="TOTAL EN BS:", bg=self.bg_card, fg=self.text_white, font=("Segoe UI", 12, "bold")).grid(row=4, column=0, sticky="w", pady=2)
        self.lbl_total_bs = tk.Label(totals_frame, text="Bs. 0.00", bg=self.bg_card, fg="#FFB300", font=("Segoe UI", 14, "bold"))
        self.lbl_total_bs.grid(row=4, column=1, sticky="e", pady=2)

        # 4. Botón Ejecutor
        tk.Button(right_panel, text="⚡ PROCESAR VENTA E IMPRIMIR", font=("Segoe UI", 12, "bold"), bg=self.accent_green, fg=self.text_white, bd=0, cursor="hand2", command=self.procesar_venta).pack(fill="x", padx=15, pady=(10, 5), ipady=8)
        
        self.cargar_catalogo_productos()

    def cargar_catalogo_productos(self):
        self.tree_productos.delete(*self.tree_productos.get_children())
        conn = database.get_connection()
        for r in conn.execute("SELECT id, codigo_barras, descripcion, precio_usd, stock FROM productos").fetchall():
            self.tree_productos.insert("", "end", values=(r[0], r[1], r[2], f"${r[3]:.2f}", r[4]))
        conn.close()

    def on_producto_seleccionado(self, event):
        item = self.tree_productos.focus()
        if not item: return
        v = self.tree_productos.item(item, "values")
        
        conn = database.get_connection()
        row = conn.execute("SELECT imagen_path FROM productos WHERE id = ?", (v[0],)).fetchone()
        conn.close()
        
        if row and row[0] and os.path.exists(row[0]):
            try:
                img = Image.open(row[0])
                img.thumbnail((240, 160), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                self.lbl_imagen_prod.config(image=img_tk, text="", width=240, height=160)
                self.lbl_imagen_prod.image = img_tk
            except Exception:
                self.lbl_imagen_prod.config(image="", text="⚠️ Error al abrir imagen", width=30, height=10)
        else:
            self.lbl_imagen_prod.config(image="", text="📁 Producto sin imagen", width=30, height=10)

    def añadir_al_carrito(self):
        item = self.tree_productos.focus()
        if not item:
            messagebox.showwarning("Selección requerida", "Por favor seleccione un producto del catálogo.")
            return
        v = self.tree_productos.item(item, "values")
        
        if int(v[4]) <= 0:
            messagebox.showerror("Sin Stock", "Este producto no cuenta con existencias para la venta.")
            return

        for prod in self.carrito:
            if prod[0] == v[0]:
                if prod[4] + 1 > int(v[4]):
                    messagebox.showerror("Límite excedido", "No puedes vender más unidades que las disponibles en stock.")
                    return
                prod[4] += 1
                self.actualizar_tabla_carrito()
                return

        self.carrito.append([v[0], v[1], v[2], float(v[3].replace("$", "")), 1])
        self.actualizar_tabla_carrito()

    def quitar_del_carrito(self):
        item = self.tree_carrito.focus()
        if not item: return
        v = self.tree_carrito.item(item, "values")
        
        self.carrito = [prod for prod in self.carrito if str(prod[0]) != str(v[0])]
        self.actualizar_tabla_carrito()

    def actualizar_tabla_carrito(self):
        self.tree_carrito.delete(*self.tree_carrito.get_children())
        subtotal = 0.0
        
        for p in self.carrito:
            total_item = p[3] * p[4]
            subtotal += total_item
            self.tree_carrito.insert("", "end", values=(p[0], p[1], p[2], f"${p[3]:.2f}", p[4], f"${total_item:.2f}"))
        
        conn = database.get_connection()
        try:
            cfg = conn.execute("SELECT iva_general, igtf FROM configuracion WHERE id = 1").fetchone()
            tasa_iva = cfg[0] if (cfg and cfg[0]) else 16.0
            tasa_igtf = cfg[1] if (cfg and cfg[1]) else 3.0
        except Exception:
            tasa_iva = 16.0
            tasa_igtf = 3.0
        finally:
            conn.close()
        
        tasa_bcv = self._obtener_tasa_bcv_api()

        metodo = self.cmb_metodo_pago.get()
        aplica_igtf = tasa_igtf if metodo == "Efectivo $" else 0.0

        monto_iva = subtotal * (tasa_iva / 100.0)
        monto_igtf = subtotal * (aplica_igtf / 100.0)
        total_usd = subtotal + monto_iva + monto_igtf
        total_bs = total_usd * tasa_bcv

        self.lbl_subtotal.config(text=f"${subtotal:.2f}")
        self.lbl_titulo_iva.config(text=f"IVA ({tasa_iva}%):")
        self.lbl_iva.config(text=f"${monto_iva:.2f}")
        self.lbl_titulo_igtf.config(text=f"IGTF ({aplica_igtf}%):")
        self.lbl_igtf.config(text=f"${monto_igtf:.2f}")
        self.lbl_total.config(text=f"${total_usd:.2f}")
        self.lbl_total_bs.config(text=f"Bs. {total_bs:.2f}")

    def procesar_venta(self):
        if not self.carrito:
            messagebox.showwarning("Carrito Vacío", "No hay productos agregados a la orden actual.")
            return
            
        conn = database.get_connection()
        try:
            subtotal = sum(p[3] * p[4] for p in self.carrito)
            
            cfg = conn.execute("SELECT iva_general FROM configuracion WHERE id = 1").fetchone()
            tasa_iva = cfg[0] if (cfg and cfg[0]) else 16.0
            
            metodo_pago = self.cmb_metodo_pago.get()
            tasa_igtf_aplicada = 3.0 if metodo_pago == "Efectivo $" else 0.0
            
            monto_iva = subtotal * (tasa_iva / 100.0)
            monto_igtf = subtotal * (tasa_igtf_aplicada / 100.0)
            total_usd = subtotal + monto_iva + monto_igtf
            
            # Obtener la tasa de cambio actual desde la API o BD
            tasa_bcv = self._obtener_tasa_bcv_api()
            
            # --- INSERCIÓN EN LA TABLA VENTAS ---
            try:
                cursor = conn.execute(
                    """
                    INSERT INTO ventas 
                    (fecha, subtotal_usd, iva_usd, igtf_usd, total_usd, tasa_venta, metodo_pago, usuario_id) 
                    VALUES (datetime('now', 'localtime'), ?, ?, ?, ?, ?, ?, ?)
                    """, 
                    (subtotal, monto_iva, monto_igtf, total_usd, tasa_bcv, metodo_pago, self.usuario_id)
                )
            except Exception as sql_err:
                if "tasa_venda" in str(sql_err).lower() or "no such column: tasa_venta" in str(sql_err).lower():
                    cursor = conn.execute(
                        """
                        INSERT INTO ventas 
                        (fecha, subtotal_usd, iva_usd, igtf_usd, total_usd, tasa_venda, metodo_pago, usuario_id) 
                        VALUES (datetime('now', 'localtime'), ?, ?, ?, ?, ?, ?, ?)
                        """, 
                        (subtotal, monto_iva, monto_igtf, total_usd, tasa_bcv, metodo_pago, self.usuario_id)
                    )
                else:
                    raise sql_err

            id_venta = cursor.lastrowid
            
            # --- INSERCIÓN EN LOS DETALLES (Soporta singular 'detalles_venta' y plural 'detalles_ventas') ---
            for p in self.carrito:
                try:
                    # Intento 1: Tabla en plural (detalles_ventas)
                    conn.execute(
                        "INSERT INTO detalles_ventas (id_venta, id_producto, cantidad, precio_unitario) VALUES (?, ?, ?, ?)", 
                        (id_venta, p[0], p[4], p[3])
                    )
                except Exception as detail_err:
                    if "no such table" in str(detail_err).lower():
                        # Intento 2: Fallback a tabla en singular (detalles_venta)
                        conn.execute(
                            "INSERT INTO detalles_venta (id_venta, id_producto, cantidad, precio_unitario) VALUES (?, ?, ?, ?)", 
                            (id_venta, p[0], p[4], p[3])
                        )
                    else:
                        raise detail_err
                
                # Actualizar el stock del producto
                conn.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (p[4], p[0]))
                
            conn.commit()
            
            # Generación física del comprobante
            ruta_ticket = generar_ticket_pdf(id_venta, self.carrito)
            
            messagebox.showinfo("Venta Éxito", f"🎉 Venta #{id_venta} procesada de forma correcta.\n\nTicket PDF creado en la carpeta 'facturas'.")
            os.startfile(os.path.abspath(ruta_ticket))
            
            # Resetear la vista limpia
            self.carrito.clear()
            self.actualizar_tabla_carrito()
            self.cargar_catalogo_productos()
            self.lbl_imagen_prod.config(image="", text="Seleccione un producto del catálogo\npara visualizar su imagen", width=30, height=10)
            
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error de base de datos", f"Error crítico al guardar la transacción:\n{str(e)}")
        finally:
            conn.close()