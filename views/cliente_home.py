import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from controllers.cliente_controller import ClienteController
from controllers.pedido_controller import PedidoController
from controllers.producto_controller import ProductoController
from utils.helpers import money
from views.cliente_carrito import ClienteCarritoView
from views.theme import (
    BRAND_GREEN,
    BRAND_GREEN_DARK,
    BRAND_GREEN_SOFT,
    FONT,
    INK,
    LINE,
    MUTED,
    WHITE,
    clear,
    logo_image,
    make_card,
    make_tree,
)


class ClienteHome(ttk.Frame):
    def __init__(self, master, user: dict, on_logout):
        super().__init__(master, style="App.TFrame")
        self.user = user
        self.on_logout = on_logout
        self.products = ProductoController()
        self.orders = PedidoController()
        self.client = ClienteController()
        self.cart: dict[int, dict] = {}
        self.product_by_iid = {}
        self.search = tk.StringVar()
        self.qty = tk.IntVar(value=1)
        self.logo = None
        self.nav_buttons = {}
        self.content = None
        self.header_title = tk.StringVar()
        self.header_subtitle = tk.StringVar()
        self.product_tree = None
        self.products_status = None
        self.cart_view = None
        self.orders_tree = None
        self.order_detail_tree = None
        self.order_summary = None
        self._build()
        self.show_shopping()

    def _build(self):
        shell = ttk.Frame(self, style="App.TFrame")
        shell.pack(fill="both", expand=True)

        nav = tk.Frame(shell, width=268, bg=WHITE, highlightbackground=LINE, highlightthickness=1)
        nav.pack(side="left", fill="y")
        nav.pack_propagate(False)

        brand = tk.Frame(nav, bg=WHITE)
        brand.pack(fill="x", padx=18, pady=(22, 20))
        self.logo = logo_image(subsample=4)
        if self.logo:
            tk.Label(brand, image=self.logo, bg=WHITE).pack(anchor="center")

        menu = tk.Frame(nav, bg=WHITE)
        menu.pack(fill="both", expand=True, padx=12)
        for label, command in [
            ("Compras", self.show_shopping),
            ("Mis pedidos", self.show_orders),
            ("Saldo", self.show_wallet),
        ]:
            button = tk.Button(
                menu,
                text=f"   {label}",
                anchor="w",
                command=lambda l=label, c=command: self.navigate(l, c),
                relief="flat",
                bd=0,
                bg=WHITE,
                fg=BRAND_GREEN_DARK,
                activebackground=BRAND_GREEN_SOFT,
                activeforeground=BRAND_GREEN_DARK,
                padx=14,
                pady=12,
                font=(FONT, 11, "bold"),
                cursor="hand2",
            )
            button.pack(fill="x", pady=4)
            self.nav_buttons[label] = button

        self._build_profile(nav)

        main = ttk.Frame(shell, style="App.TFrame")
        main.pack(side="left", fill="both", expand=True)

        footer = tk.Frame(main, bg=BRAND_GREEN_DARK)
        footer.pack(side="bottom", fill="x")
        tk.Label(
            footer,
            text="SuperMercado ONIX   |   Sistema de gestion",
            bg=BRAND_GREEN_DARK,
            fg=WHITE,
            font=(FONT, 10, "bold"),
        ).pack(side="left", padx=18, pady=12)
        tk.Label(
            footer,
            text="Version 1.0.0   |   Conectado",
            bg=BRAND_GREEN_DARK,
            fg="#DDFBE8",
            font=(FONT, 10),
        ).pack(side="right", padx=18, pady=12)

        header = ttk.Frame(main, style="App.TFrame", padding=(18, 18, 18, 0))
        header.pack(fill="x")
        ttk.Label(header, textvariable=self.header_title, style="PageTitle.TLabel").pack(anchor="w")
        ttk.Label(header, textvariable=self.header_subtitle, style="PageSubtitle.TLabel").pack(anchor="w")

        self.content = ttk.Frame(main, padding=18, style="App.TFrame")
        self.content.pack(fill="both", expand=True)

    def _build_profile(self, nav):
        profile = tk.Frame(nav, bg=BRAND_GREEN_SOFT, highlightbackground="#C9EAD5", highlightthickness=1)
        profile.pack(side="bottom", fill="x", padx=14, pady=16)
        top = tk.Frame(profile, bg=BRAND_GREEN_SOFT)
        top.pack(fill="x", padx=12, pady=12)
        initial = (self.user.get("nombre") or self.user.get("username") or "U")[0].upper()
        avatar = tk.Label(top, text=initial, bg=BRAND_GREEN, fg=WHITE, width=3, font=(FONT, 16, "bold"))
        avatar.pack(side="left", padx=(0, 10), ipady=5)
        identity = tk.Frame(top, bg=BRAND_GREEN_SOFT)
        identity.pack(side="left", fill="x", expand=True)
        name_label = tk.Label(identity, text=self.user.get("nombre") or self.user.get("username"), bg=BRAND_GREEN_SOFT, fg=INK, font=(FONT, 10, "bold"))
        name_label.pack(anchor="w")
        role_label = tk.Label(identity, text=self.user.get("rol"), bg=BRAND_GREEN_SOFT, fg=MUTED, font=(FONT, 9))
        role_label.pack(anchor="w")
        logout_button = tk.Button(
            top,
            text="Salir",
            command=self._logout,
            relief="flat",
            bd=0,
            bg=BRAND_GREEN_SOFT,
            fg=BRAND_GREEN_DARK,
            activebackground="#DDF3E6",
            padx=8,
            pady=6,
            font=(FONT, 9, "bold"),
            cursor="hand2",
        )
        logout_button.pack(side="right")
        actions = tk.Frame(profile, bg=BRAND_GREEN_SOFT)
        actions.pack(fill="x", padx=12, pady=(0, 10))
        tk.Button(
            actions,
            text="Perfil",
            command=self.show_profile,
            relief="flat",
            bd=0,
            bg=WHITE,
            fg=BRAND_GREEN_DARK,
            activebackground="#DDF3E6",
            padx=8,
            pady=5,
            font=(FONT, 9, "bold"),
            cursor="hand2",
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Button(
            actions,
            text="Tarjetas",
            command=self.show_cards,
            relief="flat",
            bd=0,
            bg=WHITE,
            fg=BRAND_GREEN_DARK,
            activebackground="#DDF3E6",
            padx=8,
            pady=5,
            font=(FONT, 9, "bold"),
            cursor="hand2",
        ).pack(side="left", fill="x", expand=True)
        for widget in (profile, top, avatar, identity, name_label, role_label):
            widget.bind("<Button-1>", lambda _event: self._logout())
            widget.configure(cursor="hand2")

    def _logout(self):
        self.on_logout()

    def navigate(self, label, command):
        self.set_active(label)
        command()

    def set_active(self, active_label):
        for label, button in self.nav_buttons.items():
            if label == active_label:
                button.configure(bg=BRAND_GREEN_DARK, fg=WHITE, activebackground=BRAND_GREEN)
            else:
                button.configure(bg=WHITE, fg=BRAND_GREEN_DARK, activebackground=BRAND_GREEN_SOFT)

    def _set_page(self, title: str, subtitle: str):
        self.header_title.set(title)
        self.header_subtitle.set(subtitle)
        clear(self.content)
        self.product_tree = None
        self.products_status = None
        self.orders_tree = None
        self.order_detail_tree = None
        self.order_summary = None

    def show_shopping(self):
        self.set_active("Compras")
        self._set_page(
            f"Compras de {self.user['nombre']}",
            "Selecciona productos y registra tu pedido.",
        )
        body = ttk.Frame(self.content, style="App.TFrame")
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=3, minsize=620)
        body.columnconfigure(1, weight=2, minsize=430)
        body.rowconfigure(0, weight=1)

        left_outer, left = make_card(body, padding=14)
        right_outer, right = make_card(body, padding=0)
        left_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        right_outer.grid(row=0, column=1, sticky="nsew")

        tk.Label(left, text="Productos disponibles", bg=WHITE, fg=INK, font=(FONT, 18, "bold")).pack(anchor="w")
        tk.Label(left, text="Elige un producto y agregalo al carrito.", bg=WHITE, fg=MUTED, font=(FONT, 9)).pack(anchor="w", pady=(2, 10))

        toolbar = ttk.Frame(left)
        toolbar.pack(fill="x", pady=(0, 10))
        toolbar.columnconfigure(0, weight=1)
        ttk.Entry(toolbar, textvariable=self.search).grid(row=0, column=0, sticky="ew")
        ttk.Button(toolbar, text="Buscar", style="Secondary.TButton", command=self.refresh_products).grid(row=0, column=1, padx=(8, 0))
        ttk.Label(toolbar, text="Cant.", style="Eyebrow.TLabel").grid(row=0, column=2, padx=(14, 4))
        ttk.Spinbox(toolbar, from_=1, to=99, textvariable=self.qty, width=5).grid(row=0, column=3)
        ttk.Button(toolbar, text="Agregar al carrito", style="Primary.TButton", command=self.add_to_cart).grid(row=0, column=4, padx=(8, 0))

        columns = ("codigo", "nombre", "categoria", "precio")
        headings = {
            "codigo": "Codigo",
            "nombre": "Producto",
            "categoria": "Categoria",
            "precio": "Precio",
            "nombre_width": 260,
        }
        grid = ttk.Frame(left)
        grid.pack(fill="both", expand=True)
        self.product_tree, scroll = make_tree(grid, columns, headings)
        self.product_tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.products_status = tk.Label(left, text="", bg=WHITE, fg=MUTED, font=(FONT, 9))
        self.products_status.pack(anchor="w", pady=(8, 0))

        self.cart_view = ClienteCarritoView(right, self.checkout)
        self.cart_view.pack(fill="both", expand=True)
        try:
            self.cart_view.set_options(self.orders.list_client_modalidades(), self.orders.list_formas_pago())
            self.cart_view.set_cards(self.client.list_cards(self.user))
        except Exception:
            self.cart_view.set_options(["Recoger en tienda", "Pedido a domicilio"], [])
            self.cart_view.set_cards([])
        self.cart_view.set_cart(self.cart)
        self.refresh_products()

    def show_orders(self):
        self.set_active("Mis pedidos")
        self._set_page("Mis pedidos", "Consulta el detalle de tus pedidos o cancela uno pendiente.")

        orders_outer, orders_card = make_card(self.content, padding=16)
        orders_outer.pack(fill="both", expand=True)
        orders_card.rowconfigure(1, weight=1)
        orders_card.rowconfigure(4, weight=1)
        orders_card.columnconfigure(0, weight=1)

        tk.Label(orders_card, text="Pedidos realizados", bg=WHITE, fg=BRAND_GREEN_DARK, font=(FONT, 17, "bold")).grid(row=0, column=0, sticky="w")
        order_columns = ("id", "fecha", "modalidad", "pago", "estado", "total", "direccion")
        order_headings = {
            "id": "ID",
            "fecha": "Fecha",
            "modalidad": "Modalidad",
            "pago": "Pago",
            "estado": "Estado",
            "total": "Total",
            "direccion": "Direccion",
            "fecha_width": 150,
            "modalidad_width": 150,
            "direccion_width": 220,
        }
        order_frame = ttk.Frame(orders_card)
        order_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 8))
        self.orders_tree, orders_scroll = make_tree(order_frame, order_columns, order_headings)
        self.orders_tree.pack(side="left", fill="both", expand=True)
        orders_scroll.pack(side="right", fill="y")

        actions = ttk.Frame(orders_card)
        actions.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        ttk.Button(actions, text="Cancelar pedido", style="Danger.TButton", command=self.cancel_selected_order).pack(side="left", padx=8)
        ttk.Button(actions, text="Actualizar", style="Ghost.TButton", command=self.refresh_orders).pack(side="right")

        self.order_summary = tk.Label(
            orders_card,
            text="Selecciona un pedido para ver sus productos.",
            bg=WHITE,
            fg=MUTED,
            font=(FONT, 10),
        )
        self.order_summary.grid(row=3, column=0, sticky="w", pady=(0, 8))

        detail_columns = ("codigo", "producto", "cantidad", "precio", "subtotal")
        detail_headings = {
            "codigo": "Codigo",
            "producto": "Producto",
            "cantidad": "Cant.",
            "precio": "Precio",
            "subtotal": "Subtotal",
            "producto_width": 320,
        }
        detail_frame = ttk.Frame(orders_card)
        detail_frame.grid(row=4, column=0, sticky="nsew")
        self.order_detail_tree, detail_scroll = make_tree(detail_frame, detail_columns, detail_headings)
        self.order_detail_tree.pack(side="left", fill="both", expand=True)
        detail_scroll.pack(side="right", fill="y")
        self.orders_tree.bind("<<TreeviewSelect>>", lambda _event: self.load_selected_order_detail(show_warning=False))
        self.orders_tree.bind("<Double-1>", lambda _event: self.load_selected_order_detail())
        self.refresh_orders()

    def show_wallet(self):
        self.set_active("Saldo")
        self._set_page("Saldo electronico", "Consulta el saldo disponible para compras.")
        outer, wallet = make_card(self.content, padding=22)
        outer.pack(fill="x")
        tk.Label(wallet, text="Saldo disponible", bg=WHITE, fg=MUTED, font=(FONT, 10, "bold")).pack(anchor="w")
        tk.Label(
            wallet,
            text=money(self.user.get("saldo_electronico", 0)),
            bg=WHITE,
            fg=BRAND_GREEN_DARK,
            font=(FONT, 34, "bold"),
        ).pack(anchor="w", pady=(8, 0))

    def show_profile(self):
        self._set_page("Configurar perfil", "Edita tus datos personales.")
        profile = self.client.get_profile(self.user["id"])
        nombre = tk.StringVar(value=profile.get("nombre") or "")
        email = tk.StringVar(value=profile.get("email") or "")
        telefono = tk.StringVar(value=profile.get("telefono") or "")
        direccion = tk.StringVar(value=profile.get("direccion") or "")

        outer, form = make_card(self.content, padding=22)
        outer.pack(fill="x")
        for index, (label, var) in enumerate(
            [
                ("Nombre", nombre),
                ("Correo", email),
                ("Telefono", telefono),
                ("Direccion", direccion),
            ]
        ):
            ttk.Label(form, text=label, style="Eyebrow.TLabel").grid(row=index * 2, column=0, sticky="w")
            ttk.Entry(form, textvariable=var).grid(row=index * 2 + 1, column=0, sticky="ew", pady=(4, 12))
        form.columnconfigure(0, weight=1)
        ttk.Button(
            form,
            text="Guardar perfil",
            style="Primary.TButton",
            command=lambda: save(),
        ).grid(row=8, column=0, sticky="ew")

        def save():
            try:
                self.client.update_profile(
                    self.user,
                    nombre.get().strip() or self.user["username"],
                    email.get().strip(),
                    telefono.get().strip(),
                    direccion.get().strip(),
                )
                self.user.update(
                    {
                        "nombre": nombre.get().strip() or self.user["username"],
                        "email": email.get().strip(),
                        "telefono": telefono.get().strip(),
                        "direccion": direccion.get().strip(),
                    }
                )
                messagebox.showinfo("Perfil", "Perfil actualizado.")
            except Exception as exc:
                messagebox.showerror("Perfil", str(exc))

    def show_cards(self):
        self._set_page("Tarjetas guardadas", "Agrega, edita o elimina tarjetas de pago.")
        selected_card = {"id": None}
        alias = tk.StringVar()
        numero = tk.StringVar()
        titular = tk.StringVar()
        vencimiento = tk.StringVar()
        favorita = tk.BooleanVar(value=False)

        outer, card = make_card(self.content, padding=18)
        outer.pack(fill="both", expand=True)
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)
        card.rowconfigure(1, weight=1)

        ttk.Label(card, text="Tus tarjetas", style="Title.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
        columns = ("id", "alias", "titular", "marca", "ultimos4", "vencimiento", "favorita")
        headings = {
            "id": "ID",
            "alias": "Alias",
            "titular": "Titular",
            "marca": "Marca",
            "ultimos4": "Terminacion",
            "vencimiento": "Vence",
            "favorita": "Favorita",
            "alias_width": 220,
            "titular_width": 180,
        }
        table_frame = ttk.Frame(card)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 14), pady=12)
        tree, scroll = make_tree(table_frame, columns, headings)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        form = ttk.Frame(card)
        form.grid(row=1, column=1, sticky="nsew", pady=12)
        form.columnconfigure(0, weight=1)
        for index, (label, var) in enumerate(
            [
                ("Alias", alias),
                ("Numero de tarjeta", numero),
                ("Titular", titular),
                ("Vencimiento", vencimiento),
            ]
        ):
            ttk.Label(form, text=label, style="Eyebrow.TLabel").grid(row=index * 2, column=0, sticky="w")
            ttk.Entry(form, textvariable=var).grid(row=index * 2 + 1, column=0, sticky="ew", pady=(4, 10))
        ttk.Checkbutton(form, text="Usar como favorita", variable=favorita).grid(row=8, column=0, sticky="w", pady=(0, 10))
        ttk.Button(form, text="Guardar tarjeta", style="Primary.TButton", command=lambda: save()).grid(row=9, column=0, sticky="ew")
        ttk.Button(form, text="Nueva", style="Secondary.TButton", command=lambda: clear_form()).grid(row=10, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(form, text="Eliminar tarjeta", style="Danger.TButton", command=lambda: delete()).grid(row=11, column=0, sticky="ew", pady=(8, 0))

        def load():
            for row in tree.get_children():
                tree.delete(row)
            for item in self.client.list_cards(self.user):
                tree.insert(
                    "",
                    "end",
                    iid=str(item["id"]),
                    values=(
                        item["id"],
                        item["alias"],
                        item["titular"],
                        item["marca"],
                        f"****{item['ultimos4']}",
                        item["vencimiento"],
                        "Si" if item["favorita"] else "No",
                    ),
                )

        def select(_event=None):
            selected = tree.selection()
            if not selected:
                return
            values = tree.item(selected[0], "values")
            selected_card["id"] = int(selected[0])
            alias.set(values[1])
            numero.set("")
            titular.set(values[2])
            vencimiento.set(values[5])
            favorita.set(values[6] == "Si")

        def clear_form():
            selected_card["id"] = None
            alias.set("")
            numero.set("")
            titular.set("")
            vencimiento.set("")
            favorita.set(False)
            tree.selection_remove(tree.selection())

        def save():
            try:
                self.client.save_card(
                    self.user,
                    numero.get().strip(),
                    titular.get().strip(),
                    vencimiento.get().strip(),
                    alias=alias.get().strip() or None,
                    favorita=favorita.get(),
                    card_id=selected_card["id"],
                )
                clear_form()
                load()
            except Exception as exc:
                messagebox.showerror("Tarjetas", str(exc))

        def delete():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Tarjetas", "Selecciona una tarjeta.")
                return
            if not messagebox.askyesno("Eliminar tarjeta", "Estas seguro de eliminar esta tarjeta?"):
                return
            try:
                self.client.delete_card(self.user, int(selected[0]))
                clear_form()
                load()
            except Exception as exc:
                messagebox.showerror("Tarjetas", str(exc))

        tree.bind("<<TreeviewSelect>>", select)
        load()

    def refresh_products(self):
        if self.product_tree is None:
            return
        for row in self.product_tree.get_children():
            self.product_tree.delete(row)
        self.product_by_iid.clear()
        try:
            products = self.products.list_products(self.search.get().strip())
        except Exception as exc:
            messagebox.showerror("Cliente", str(exc))
            return
        visible_count = 0
        for product in products:
            if int(product.get("stock_actual") or 0) <= 0:
                continue
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
                ),
            )
            visible_count += 1
        if self.products_status:
            text = f"Mostrando {visible_count} productos disponibles." if visible_count else "No hay productos disponibles. Producto agotado o sin coincidencias."
            self.products_status.configure(text=text)

    def add_to_cart(self):
        if self.product_tree is None:
            return
        selected = self.product_tree.selection()
        if not selected:
            messagebox.showwarning("Compras", "Selecciona un producto.")
            return
        product = self.product_by_iid[selected[0]]
        qty = max(1, int(self.qty.get()))
        stock = int(product.get("stock_actual") or 0)
        if qty > stock:
            messagebox.showwarning("Producto agotado", "No hay unidades suficientes para agregar ese producto.")
            return
        current = self.cart.get(product["id"])
        if current:
            if current["cantidad"] + qty > stock:
                messagebox.showwarning("Producto agotado", "No hay unidades suficientes para agregar mas cantidad.")
                return
            current["cantidad"] += qty
        else:
            self.cart[product["id"]] = {
                "id": product["id"],
                "nombre": product["nombre"],
                "precio_venta": float(product["precio_venta"]),
                "cantidad": qty,
            }
        if self.cart_view:
            self.cart_view.set_cart(self.cart)

    def checkout(self, modality: str, payment: str, address: str, payment_data: dict | None = None):
        try:
            payment_data = payment_data or {}
            if payment == "Tarjeta" and payment_data.get("guardar"):
                self.client.save_card(
                    self.user,
                    payment_data.get("numero", ""),
                    payment_data.get("titular", ""),
                    payment_data.get("vencimiento", ""),
                    favorita=True,
                )
            order_id = self.orders.create_order(
                self.user,
                list(self.cart.values()),
                modality,
                payment,
                address,
            )
            self.cart.clear()
            if self.cart_view:
                self.cart_view.set_cart(self.cart)
            messagebox.showinfo("Pedido registrado", f"Pedido #{order_id} registrado como pendiente.")
            self.show_orders()
        except Exception as exc:
            messagebox.showerror("Pedido", str(exc))

    def refresh_orders(self):
        if self.orders_tree is None:
            return
        for row in self.orders_tree.get_children():
            self.orders_tree.delete(row)
        self.clear_order_detail()
        try:
            for order in self.orders.list_orders(self.user["id"]):
                self.orders_tree.insert(
                    "",
                    "end",
                    iid=str(order["id"]),
                    values=(
                        order["id"],
                        order["created_at"],
                        order["modalidad"],
                        order["forma_pago"],
                        order["estado"],
                        money(order["total"]),
                        order["direccion_entrega"] or "-",
                    ),
                )
        except Exception as exc:
            messagebox.showerror("Mis pedidos", str(exc))

    def clear_order_detail(self):
        if self.order_detail_tree is not None:
            for row in self.order_detail_tree.get_children():
                self.order_detail_tree.delete(row)
        if self.order_summary is not None:
            self.order_summary.configure(text="Selecciona un pedido para ver sus productos.")

    def load_selected_order_detail(self, show_warning: bool = True):
        if self.orders_tree is None or self.order_detail_tree is None:
            return
        selected = self.orders_tree.selection()
        if not selected:
            if show_warning:
                messagebox.showwarning("Mis pedidos", "Selecciona un pedido.")
            return
        self.clear_order_detail()
        pedido_id = int(selected[0])
        try:
            details = self.orders.get_order_details(pedido_id, self.user["id"])
            for detail in details:
                self.order_detail_tree.insert(
                    "",
                    "end",
                    values=(
                        detail["codigo"],
                        detail["nombre"],
                        detail["cantidad"],
                        money(detail["precio_unitario"]),
                        money(detail["subtotal"]),
                    ),
                )
            values = self.orders_tree.item(selected[0], "values")
            self.order_summary.configure(
                text=f"Pedido #{pedido_id} | Estado: {values[4]} | Total: {values[5]}"
            )
        except Exception as exc:
            messagebox.showerror("Detalle de pedido", str(exc))

    def cancel_selected_order(self):
        if self.orders_tree is None:
            return
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("Cancelar pedido", "Selecciona un pedido.")
            return
        motivo = simpledialog.askstring(
            "Cancelar pedido",
            "Motivo de cancelacion:",
        )
        if not motivo:
            return
        try:
            self.orders.cancel_order(int(selected[0]), self.user, motivo)
            messagebox.showinfo("Pedido cancelado", "Tu pedido fue cancelado.")
            self.refresh_orders()
        except Exception as exc:
            messagebox.showerror("Cancelar pedido", str(exc))
