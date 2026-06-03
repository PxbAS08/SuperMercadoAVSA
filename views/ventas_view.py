import tkinter as tk
from tkinter import messagebox, ttk

from controllers.producto_controller import ProductoController
from controllers.venta_controller import VentaController
from utils.helpers import money
from views.theme import BRAND_GREEN, BRAND_GREEN_DARK, ERROR, FONT, MUTED, WHITE, make_card, make_toolbar, make_tree


class VentasView(ttk.Frame):
    def __init__(self, master, user: dict):
        super().__init__(master, padding=0)
        self.user = user
        self.products = ProductoController()
        self.sales = VentaController()
        self.product_by_iid = {}
        self.cart: dict[int, dict] = {}
        self.search = tk.StringVar()
        self.qty = tk.IntVar(value=1)
        self.discount = tk.StringVar(value="0")
        self.cash_received = tk.StringVar(value="0")
        self.change_text = tk.StringVar(value=money(0))
        self.payment = tk.StringVar()
        self.modality = tk.StringVar()
        self.current_total = 0.0
        self.canvas = tk.Canvas(self, bg="#F5F7FA", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.inner = ttk.Frame(self.canvas, padding=12, style="App.TFrame")
        self.inner_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._sync_scroll_region)
        self.canvas.bind("<Configure>", self._sync_inner_width)
        self.canvas.bind("<Enter>", lambda _event: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.canvas.bind("<Leave>", lambda _event: self.canvas.unbind_all("<MouseWheel>"))
        self._build()
        self.refresh_products()

    def _build(self):
        self.configure(style="App.TFrame")
        container = self.inner
        top = make_toolbar(container)
        ttk.Label(top, text="Buscar producto", style="Eyebrow.TLabel").pack(side="left", padx=(0, 8))
        ttk.Entry(top, textvariable=self.search, width=34).pack(side="left")
        ttk.Button(top, text="Buscar", style="Secondary.TButton", command=self.refresh_products).pack(side="left", padx=8)
        ttk.Label(top, text="Cantidad", style="Eyebrow.TLabel").pack(side="left", padx=(18, 4))
        ttk.Spinbox(top, from_=1, to=999, textvariable=self.qty, width=6).pack(side="left")
        ttk.Button(top, text="Agregar al carrito", style="Primary.TButton", command=self.add_to_cart).pack(
            side="left", padx=8
        )

        panes = ttk.PanedWindow(container, orient="horizontal")
        panes.pack(fill="x", expand=False)

        products_outer, products_frame = make_card(panes, padding=14)
        cart_outer, cart_frame = make_card(panes, padding=14)
        panes.add(products_outer, weight=3)
        panes.add(cart_outer, weight=2)

        ttk.Label(products_frame, text="Catalogo disponible", style="Title.TLabel").pack(anchor="w", pady=(0, 10))

        columns = ("codigo", "nombre", "categoria", "precio", "stock")
        headings = {
            "codigo": "Codigo",
            "nombre": "Producto",
            "categoria": "Categoria",
            "precio": "Precio",
            "stock": "Stock",
            "codigo_width": 80,
            "nombre_width": 240,
        }
        product_table = ttk.Frame(products_frame)
        product_table.pack(fill="both", expand=True)
        self.product_tree, product_scroll = make_tree(product_table, columns, headings)
        self.product_tree.configure(height=12)
        self.product_tree.pack(side="left", fill="both", expand=True)
        product_scroll.pack(side="right", fill="y")

        header = tk.Frame(cart_frame, bg=WHITE)
        header.pack(fill="x", pady=(0, 10))
        tk.Label(
            header,
            text="Resumen de venta",
            bg=WHITE,
            fg=BRAND_GREEN_DARK,
            font=(FONT, 18, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header,
            text="Carrito, forma de pago y comprobante de venta",
            bg=WHITE,
            fg=MUTED,
            font=(FONT, 9),
        ).pack(anchor="w", pady=(2, 0))

        cart_columns = ("nombre", "cantidad", "precio", "total")
        cart_headings = {
            "nombre": "Carrito",
            "cantidad": "Cant.",
            "precio": "Precio",
            "total": "Total",
            "nombre_width": 230,
        }
        cart_table = ttk.Frame(cart_frame)
        cart_table.pack(fill="x", expand=False)
        self.cart_tree, cart_scroll = make_tree(cart_table, cart_columns, cart_headings)
        self.cart_tree.configure(height=5)
        self.cart_tree.pack(side="left", fill="x", expand=True)
        cart_scroll.pack(side="right", fill="y")

        controls = tk.Frame(cart_frame, bg=WHITE)
        controls.pack(fill="x", pady=(8, 6))

        tk.Button(
            controls,
            text="Quitar producto",
            command=self.remove_item,
            relief="flat",
            bd=0,
            bg="#EEF2F6",
            fg=BRAND_GREEN_DARK,
            activebackground="#E8EEF3",
            activeforeground=BRAND_GREEN_DARK,
            padx=14,
            pady=8,
            font=(FONT, 10, "bold"),
            cursor="hand2",
        ).pack(side="left")

        tk.Button(
            controls,
            text="Vaciar carrito",
            command=self.clear_cart,
            relief="flat",
            bd=0,
            bg="#FDECEC",
            fg=ERROR,
            activebackground="#FAD2D2",
            activeforeground=ERROR,
            padx=14,
            pady=8,
            font=(FONT, 10, "bold"),
            cursor="hand2",
        ).pack(side="left", padx=8)

        pay = ttk.LabelFrame(cart_frame, text="Metodo de pago")
        pay.pack(fill="x", pady=(8, 6), padx=2, ipady=6)

        ttk.Label(pay, text="Forma de pago", style="Eyebrow.TLabel").grid(row=0, column=0, sticky="w", padx=6, pady=(4, 2))
        ttk.Label(pay, text="Pago recibido", style="Eyebrow.TLabel").grid(row=0, column=1, sticky="w", padx=6, pady=(4, 2))
        ttk.Label(pay, text="Cambio", style="Eyebrow.TLabel").grid(row=0, column=2, sticky="w", padx=6, pady=(4, 2))

        self.payment_combo = ttk.Combobox(
            pay,
            textvariable=self.payment,
            state="readonly",
            width=18,
            values=("Efectivo", "Transferencia", "Tarjeta")
        )

        self.payment_combo.grid(row=1, column=0, sticky="ew", padx=6)
        self.cash_entry = ttk.Entry(pay, textvariable=self.cash_received, width=14)
        self.cash_entry.grid(row=1, column=1, sticky="ew", padx=6)
        ttk.Label(pay, textvariable=self.change_text, style="SmallMetric.TLabel").grid(row=1, column=2, sticky="w", padx=6)

        self.payment.set("Efectivo")
        
        
        for index in range(3):
            pay.columnconfigure(index, weight=1)

        total_box = tk.Frame(cart_frame, bg="#F4FBF6")
        total_box.pack(fill="x", pady=(8, 6), ipadx=12, ipady=10)
        tk.Label(total_box, text="Total a cobrar", bg="#F4FBF6", fg=MUTED, font=(FONT, 9, "bold")).pack(anchor="w")
        self.total_label = tk.Label(total_box, text="$0.00", bg="#F4FBF6", fg=BRAND_GREEN_DARK, font=(FONT, 22, "bold"))
        self.total_label.pack(anchor="w")
        tk.Button(
            cart_frame,
            text="PAGAR VENTA",
            command=self.register_sale,
            relief="flat",
            bd=0,
            bg=BRAND_GREEN,
            fg=WHITE,
            activebackground="#178646",
            activeforeground=WHITE,
            padx=18,
            pady=12,
            font=(FONT, 12, "bold"),
            cursor="hand2",
        ).pack(fill="x", pady=(6, 4))

        self.receipt = tk.Text(cart_frame, height=3, wrap="none", bd=0, bg="#F8FAFC", fg="#1F2933", font=(FONT, 9))
        self.receipt.pack(fill="x", pady=(8, 0))

        try:
            modalities = self.sales.list_modalidades()
            if modalities:
                self.modality.set("Compra en tienda" if "Compra en tienda" in modalities else modalities[0])
        except Exception:
            pass
        self.payment_combo.bind("<<ComboboxSelected>>", lambda _event: self.update_payment_fields())
        self.discount.trace_add("write", lambda *_args: self.render_cart())
        self.cash_received.trace_add("write", lambda *_args: self.update_change())
        self.update_payment_fields()

    def _sync_scroll_region(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _sync_inner_width(self, event):
        self.canvas.itemconfigure(self.inner_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def refresh_products(self):
        for row in self.product_tree.get_children():
            self.product_tree.delete(row)
        self.product_by_iid.clear()
        try:
            products = self.products.list_products(self.search.get().strip())
        except Exception as exc:
            messagebox.showerror("Punto de venta", str(exc))
            return
        for product in products:
            iid = str(product["id"])
            self.product_by_iid[iid] = product
            self.product_tree.insert(
                "",
                "end",
                iid=iid,
                values=(
                    product["codigo"],
                    product["nombre"],
                    product["categoria"],
                    money(product["precio_venta"]),
                    product["stock_actual"],
                ),
            )

    def add_to_cart(self):
        selected = self.product_tree.selection()
        if not selected:
            messagebox.showwarning("Punto de venta", "Selecciona un producto.")
            return
        product = self.product_by_iid[selected[0]]
        qty = max(1, int(self.qty.get()))
        if qty > int(product["stock_actual"]):
            messagebox.showwarning("Stock", "No hay suficiente stock para esa cantidad.")
            return
        current = self.cart.get(product["id"])
        if current:
            current["cantidad"] += qty
        else:
            self.cart[product["id"]] = {
                "id": product["id"],
                "codigo": product["codigo"],
                "nombre": product["nombre"],
                "precio_venta": float(product["precio_venta"]),
                "cantidad": qty,
            }
        self.render_cart()

    def render_cart(self):
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)
        total = 0
        for product_id, item in self.cart.items():
            line_total = item["cantidad"] * item["precio_venta"]
            total += line_total
            self.cart_tree.insert(
                "",
                "end",
                iid=str(product_id),
                values=(item["nombre"], item["cantidad"], money(item["precio_venta"]), money(line_total)),
            )
        try:
            discount = float(self.discount.get() or 0)
        except ValueError:
            discount = 0
        self.current_total = max(total - discount, 0)
        self.total_label.configure(text=money(self.current_total))
        self.update_change()

    def update_change(self):
        try:
            paid = float(self.cash_received.get() or 0)
        except ValueError:
            paid = 0
        if "efectivo" not in self.payment.get().lower():
            self.change_text.set(money(0))
            return
        self.change_text.set(money(max(paid - self.current_total, 0)))

    def update_payment_fields(self):
        if self.payment.get() == "Efectivo":
            self.cash_entry.configure(state="normal")
        else:
            self.cash_received.set("")
            self.cash_entry.configure(state="disabled")
        self.update_change()

    def remove_item(self):
        selected = self.cart_tree.selection()
        if selected:
            self.cart.pop(int(selected[0]), None)
            self.render_cart()

    def clear_cart(self):
        self.cart.clear()
        self.render_cart()
        self.cash_received.set("0")

    def register_sale(self):
        try:
            if self.payment.get() == "Efectivo":
                try:
                    paid = float(self.cash_received.get() or 0)
                except ValueError:
                    raise ValueError("Ingresa un pago recibido valido.")
                if paid <= 0:
                    paid = self.current_total
            else:
                paid = self.current_total
            result = self.sales.register_sale(
                self.user,
                list(self.cart.values()),
                self.payment.get(),
                self.modality.get(),
                descuento=float(self.discount.get() or 0),
                pago_recibido=paid,
            )
            self.receipt.delete("1.0", "end")
            self.receipt.insert("1.0", result["comprobante"])
            self.clear_cart()
            self.refresh_products()
            messagebox.showinfo(
                "Venta cobrada",
                f"Folio {result['folio']} por {money(result['total'])}\nCambio: {money(result['cambio'])}",
            )
        except Exception as exc:
            messagebox.showerror("Venta", str(exc))
