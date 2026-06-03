import tkinter as tk
from tkinter import messagebox, ttk

from controllers.producto_controller import ProductoController
from controllers.venta_controller import VentaController
from utils.helpers import money
from views.theme import BRAND_GREEN_DARK, FONT, MUTED, WHITE, make_card, make_toolbar, make_tree


class VentasView(ttk.Frame):
    def __init__(self, master, user: dict):
        super().__init__(master, padding=12)
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
        self._build()
        self.refresh_products()

    def _build(self):
        self.configure(style="App.TFrame")
        top = make_toolbar(self)
        ttk.Label(top, text="Buscar producto", style="Eyebrow.TLabel").pack(side="left", padx=(0, 8))
        ttk.Entry(top, textvariable=self.search, width=34).pack(side="left")
        ttk.Button(top, text="Buscar", style="Secondary.TButton", command=self.refresh_products).pack(side="left", padx=8)
        ttk.Label(top, text="Cantidad", style="Eyebrow.TLabel").pack(side="left", padx=(18, 4))
        ttk.Spinbox(top, from_=1, to=999, textvariable=self.qty, width=6).pack(side="left")
        ttk.Button(top, text="Agregar al carrito", style="Primary.TButton", command=self.add_to_cart).pack(
            side="left", padx=8
        )

        panes = ttk.PanedWindow(self, orient="horizontal")
        panes.pack(fill="both", expand=True)

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
            text="Carrito, metodo de pago y comprobante",
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
        cart_table.pack(fill="both", expand=True)
        self.cart_tree, cart_scroll = make_tree(cart_table, cart_columns, cart_headings)
        self.cart_tree.pack(side="left", fill="both", expand=True)
        cart_scroll.pack(side="right", fill="y")

        controls = ttk.Frame(cart_frame)
        controls.pack(fill="x", pady=8)
        ttk.Button(controls, text="Quitar", style="Ghost.TButton", command=self.remove_item).pack(side="left")
        ttk.Button(controls, text="Vaciar", style="Danger.TButton", command=self.clear_cart).pack(side="left", padx=6)

        pay = ttk.Frame(cart_frame)
        pay.pack(fill="x", pady=(8, 4))
        ttk.Label(pay, text="Pago", style="Eyebrow.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(pay, text="Modalidad", style="Eyebrow.TLabel").grid(row=0, column=1, sticky="w", padx=(8, 0))
        ttk.Label(pay, text="Descuento", style="Eyebrow.TLabel").grid(row=0, column=2, sticky="w", padx=(8, 0))
        self.payment_combo = ttk.Combobox(pay, textvariable=self.payment, state="readonly", width=20)
        self.modality_combo = ttk.Combobox(pay, textvariable=self.modality, state="readonly", width=20)
        self.payment_combo.grid(row=1, column=0, sticky="ew")
        self.modality_combo.grid(row=1, column=1, sticky="ew", padx=(8, 0))
        ttk.Entry(pay, textvariable=self.discount, width=10).grid(row=1, column=2, padx=(8, 0))
        ttk.Label(pay, text="Pago recibido", style="Eyebrow.TLabel").grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Label(pay, text="Cambio", style="Eyebrow.TLabel").grid(row=2, column=1, sticky="w", padx=(8, 0), pady=(8, 0))
        ttk.Entry(pay, textvariable=self.cash_received, width=14).grid(row=3, column=0, sticky="ew")
        ttk.Label(pay, textvariable=self.change_text, style="SmallMetric.TLabel").grid(row=3, column=1, sticky="w", padx=(8, 0))
        for index in range(3):
            pay.columnconfigure(index, weight=1)

        total_box = tk.Frame(cart_frame, bg="#F4FBF6")
        total_box.pack(fill="x", pady=(12, 8), ipadx=12, ipady=12)
        tk.Label(total_box, text="Total a cobrar", bg="#F4FBF6", fg=MUTED, font=(FONT, 9, "bold")).pack(anchor="w")
        self.total_label = tk.Label(total_box, text="$0.00", bg="#F4FBF6", fg=BRAND_GREEN_DARK, font=(FONT, 24, "bold"))
        self.total_label.pack(anchor="w")
        ttk.Button(
            cart_frame,
            text="Cobrar / Pagar",
            style="Primary.TButton",
            command=self.register_sale,
        ).pack(fill="x")

        self.receipt = tk.Text(cart_frame, height=9, wrap="none", bd=0, bg="#F8FAFC", fg="#1F2933", font=(FONT, 9))
        self.receipt.pack(fill="x", pady=(10, 0))

        try:
            payments = self.sales.list_formas_pago()
            modalities = self.sales.list_modalidades()
            self.payment_combo["values"] = payments
            self.modality_combo["values"] = modalities
            if payments:
                self.payment.set(payments[0])
            if modalities:
                self.modality.set(modalities[0])
            self.payment_combo.bind("<<ComboboxSelected>>", lambda _event: self.update_change())
        except Exception:
            pass
        self.discount.trace_add("write", lambda *_args: self.render_cart())
        self.cash_received.trace_add("write", lambda *_args: self.update_change())

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
            try:
                paid = float(self.cash_received.get() or 0)
            except ValueError:
                raise ValueError("Ingresa un pago recibido valido.")
            if "efectivo" not in self.payment.get().lower() and paid <= 0:
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
