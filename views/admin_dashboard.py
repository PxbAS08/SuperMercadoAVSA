import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from config.db_config import describe_config
from controllers.auth_controller import AuthController
from controllers.pedido_controller import PedidoController
from controllers.reporte_controller import ReporteController
from controllers.venta_controller import VentaController
from utils.helpers import money
from utils.permissions import ADMIN, can, require_permission
from views.categorias_view import CategoriasView
from views.productos_view import ProductosView
from views.ventas_view import VentasView
from views.theme import (
    ACCENT,
    BRAND_GREEN,
    BRAND_GREEN_DARK,
    BRAND_GREEN_DEEP,
    BRAND_GREEN_SOFT,
    FONT,
    INK,
    LINE,
    MUTED,
    SURFACE,
    WHITE,
    clear,
    logo_image,
    make_card,
    make_tree,
)


class AdminDashboard(ttk.Frame):
    def __init__(self, master, user: dict, on_logout):
        super().__init__(master)
        self.user = user
        self.on_logout = on_logout
        self.reports = ReporteController()
        self.sales = VentaController()
        self.auth = AuthController()
        self.orders = PedidoController()
        self.content = None
        self.nav_logo = None
        self.nav_buttons = {}
        self._build()
        self.show_pos()


    def _build(self):
        self.configure(style="App.TFrame")
        shell = ttk.Frame(self, style="App.TFrame")
        shell.pack(fill="both", expand=True)

        nav = tk.Frame(shell, width=268, bg=WHITE, highlightbackground=LINE, highlightthickness=1)
        nav.pack(side="left", fill="y")
        nav.pack_propagate(False)

        brand = tk.Frame(nav, bg=WHITE)
        brand.pack(fill="x", padx=18, pady=(22, 20))
        self.nav_logo = logo_image(subsample=4)
        if self.nav_logo:
            tk.Label(brand, image=self.nav_logo, bg=WHITE).pack(anchor="center")

        menu_frame = tk.Frame(nav, bg=WHITE)
        menu_frame.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        for label, command in self._menu_items():
            button = self._nav_button(menu_frame, label, command)
            button.pack(fill="x", pady=4)
            self.nav_buttons[label] = button

        self._build_profile(nav)

        main = ttk.Frame(shell, style="App.TFrame")
        main.pack(side="left", fill="both", expand=True)
        header_outer = tk.Frame(main, bg=WHITE, highlightbackground=LINE, highlightthickness=1, bd=0)
        header_outer.pack(fill="x", padx=18, pady=(18, 0))
        header = ttk.Frame(header_outer, style="Header.TFrame", padding=(18, 14))
        header.pack(fill="x")
        ttk.Label(
            header,
            text="AVSAware / SuperMercado ONIX",
            style="Header.TLabel",
            font=(FONT, 14, "bold"),
        ).pack(side="left")
        ttk.Label(
            header,
            text="Administracion interna con cliente opcional",
            style="Header.TLabel",
        ).pack(side="right")

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

        self.content = ttk.Frame(main, padding=18, style="App.TFrame")
        self.content.pack(fill="both", expand=True)

    def _nav_button(self, parent, label, command):
        button = tk.Button(
            parent,
            text=f"   {label}",
            anchor="w",
            command=lambda: self._navigate(label, command),
            relief="flat",
            bd=0,
            bg=WHITE,
            fg=BRAND_GREEN_DARK,
            activebackground=BRAND_GREEN_SOFT,
            activeforeground=BRAND_GREEN_DARK,
            padx=14,
            pady=11,
            font=(FONT, 11, "bold"),
            cursor="hand2",
        )
        return button

    def _navigate(self, label, command):
        self._set_active_nav(label)
        command()

    def _set_active_nav(self, active_label):
        for label, button in self.nav_buttons.items():
            if label == active_label:
                button.configure(bg=BRAND_GREEN_DARK, fg=WHITE, activebackground=BRAND_GREEN)
            else:
                button.configure(bg=WHITE, fg=BRAND_GREEN_DARK, activebackground=BRAND_GREEN_SOFT)

    def _build_profile(self, nav):
        profile = tk.Frame(nav, bg=BRAND_GREEN_SOFT, highlightbackground="#C9EAD5", highlightthickness=1)
        profile.pack(side="bottom", fill="x", padx=14, pady=16)
        top = tk.Frame(profile, bg=BRAND_GREEN_SOFT)
        top.pack(fill="x", padx=12, pady=12)
        initial = (self.user.get("nombre") or self.user.get("username") or "U")[0].upper()
        avatar = tk.Label(
            top,
            text=initial,
            bg=BRAND_GREEN,
            fg=WHITE,
            width=3,
            height=1,
            font=(FONT, 16, "bold"),
        )
        avatar.pack(side="left", padx=(0, 10), ipady=5)
        identity = tk.Frame(top, bg=BRAND_GREEN_SOFT)
        identity.pack(side="left", fill="x", expand=True)
        name_label = tk.Label(
            identity,
            text=self.user.get("nombre") or self.user.get("username"),
            bg=BRAND_GREEN_SOFT,
            fg=INK,
            font=(FONT, 10, "bold"),
        )
        name_label.pack(anchor="w")
        role_label = tk.Label(
            identity,
            text=self.user.get("rol"),
            bg=BRAND_GREEN_SOFT,
            fg=MUTED,
            font=(FONT, 9),
        )
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
        for widget in (profile, top, avatar, identity, name_label, role_label):
            widget.bind("<Button-1>", lambda _event: self._logout())
            widget.configure(cursor="hand2")

    def _logout(self):
        self.on_logout()

    def _menu_items(self):
        if self.user["rol"] == ADMIN:
            return [
                ("Punto de venta", self.show_pos),
                ("Usuarios", self.show_users),
                ("Productos", self.show_products),
                ("Categorias", self.show_categories),
                ("Inventario", self.show_inventory),
                ("Pedidos", self.show_orders),
                ("Reportes", self.show_reports),
            ]
        return []

    def _screen(self, title: str, subtitle: str | None = None):
        clear(self.content)
        ttk.Label(self.content, text=title, style="PageTitle.TLabel").pack(anchor="w")
        if subtitle:
            ttk.Label(self.content, text=subtitle, style="PageSubtitle.TLabel").pack(anchor="w", pady=(2, 0))
        body = ttk.Frame(self.content, style="App.TFrame")
        body.pack(fill="both", expand=True)
        return body

    def _guard(self, permission: str) -> bool:
        try:
            require_permission(self.user, permission)
            return True
        except PermissionError as exc:
            messagebox.showwarning("Permisos", str(exc))
            return False

    def show_home(self):
        self._set_active_nav("Panel")
        body = self._screen("Panel de control", "Resumen general visible solo para administrador.")
        try:
            summary = self.reports.get_dashboard_summary(self.user)
        except Exception as exc:
            messagebox.showerror("Panel", str(exc))
            return

        self._metric_row(
            body,
            [
                ("Productos activos", summary["productos"]),
                ("Stock bajo", summary["stock_bajo"]),
                ("Pedidos de hoy", money(summary["ventas_hoy"])),
                ("Pedidos pendientes", summary["pedidos_pendientes"]),
            ],
        )
        chart_outer, chart_card = make_card(body, padding=18)
        chart_outer.pack(fill="x", pady=(20, 0))
        ttk.Label(chart_card, text="Pedidos por dia", style="Title.TLabel").pack(anchor="w", pady=(0, 8))
        canvas = tk.Canvas(chart_card, height=230, bg=WHITE, highlightthickness=0)
        canvas.pack(fill="x")
        try:
            self._draw_sales_chart(canvas, self.reports.sales_by_day())
        except Exception as exc:
            canvas.create_text(20, 20, anchor="nw", text=f"No fue posible cargar grafica: {exc}", fill="#991B1B")

        quick = ttk.Frame(body, style="App.TFrame")
        quick.pack(fill="x", pady=18)
        for label, command in [
            ("Gestionar productos", self.show_products),
            ("Categorias", self.show_categories),
            ("Historial completo", self.show_history),
        ]:
            ttk.Button(quick, text=label, style="Primary.TButton", command=command).pack(side="left", padx=6)

    def show_pos(self):
        if not self._guard("sales_write"):
            return
        self._set_active_nav("Punto de venta")
        body = self._screen(
            "Punto de venta",
            "Venta directa para administrador."
        )
        VentasView(body, self.user).pack(fill="both", expand=True)

    def _metric_row(self, parent, items):
        metrics = ttk.Frame(parent, style="App.TFrame")
        metrics.pack(fill="x", pady=(14, 0))
        for index, (label, value) in enumerate(items):
            outer, box = make_card(metrics, padding=16)
            outer.grid(row=0, column=index, sticky="ew", padx=(0 if index == 0 else 10, 0))
            metrics.columnconfigure(index, weight=1)
            tk.Label(
                box,
                text=label,
                bg=WHITE,
                fg=MUTED,
                font=(FONT, 9, "bold"),
            ).pack(anchor="w")
            tk.Label(
                box,
                text=str(value),
                bg=WHITE,
                fg=BRAND_GREEN_DARK,
                font=(FONT, 22, "bold"),
            ).pack(anchor="w", pady=(6, 0))

    def _draw_sales_chart(self, canvas: tk.Canvas, rows: list[dict]):
        canvas.update_idletasks()
        width = max(canvas.winfo_width(), 760)
        height = 230
        canvas.delete("all")
        if not rows:
            canvas.create_text(20, 20, anchor="nw", text="Sin pedidos registrados para graficar.", fill="#6B7280")
            return
        max_total = max(float(row["total"]) for row in rows) or 1
        margin = 34
        bar_gap = 18
        bar_width = max(34, int((width - margin * 2) / max(len(rows), 1)) - bar_gap)
        canvas.create_line(margin, height - margin, width - margin, height - margin, fill=LINE)
        for index, row in enumerate(rows):
            total = float(row["total"])
            x = margin + index * (bar_width + bar_gap)
            bar_h = int((height - margin * 2) * total / max_total)
            y = height - margin - bar_h
            canvas.create_rectangle(x, y, x + bar_width, height - margin, fill=BRAND_GREEN, outline="")
            canvas.create_text(x + bar_width / 2, y - 10, text=money(total), fill=BRAND_GREEN_DARK, font=(FONT, 8))
            canvas.create_text(
                x + bar_width / 2,
                height - margin + 12,
                text=str(row["fecha"])[5:],
                fill=MUTED,
                font=(FONT, 8),
            )

    def show_products(self):
        if not self._guard("products_read"):
            return
        body = self._screen("Productos", "Alta, edicion y consulta de productos.")
        ProductosView(body, self.user, mode="productos").pack(fill="both", expand=True)

    def show_categories(self):
        if not self._guard("categories_manage"):
            return
        body = self._screen("Categorias y subcategorias")
        CategoriasView(body, self.user).pack(fill="both", expand=True)

    def show_inventory(self):
        if not self._guard("inventory_read"):
            return
        body = self._screen("Inventario / existencias", "Control completo de inventario.")
        ProductosView(body, self.user, mode="inventario").pack(fill="both", expand=True)

    def show_history(self):
        if not self._guard("history_full"):
            return
        body = self._screen("Historial de operaciones", "Registro completo de actividad administrativa.")
        columns = ("fecha", "usuario", "modulo", "operacion", "descripcion")
        headings = {
            "fecha": "Fecha",
            "usuario": "Usuario",
            "modulo": "Modulo",
            "operacion": "Operacion",
            "descripcion": "Descripcion",
            "descripcion_width": 380,
        }
        tree, scroll = make_tree(body, columns, headings)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        try:
            for row in self.reports.list_history(self.user):
                tree.insert(
                    "",
                    "end",
                    values=(row["created_at"], row["username"] or "sistema", row["modulo"], row["operacion"], row["descripcion"]),
                )
        except Exception as exc:
            messagebox.showerror("Historial", str(exc))

    def show_sales_history(self):
        if not can(self.user, "sales_read_all"):
            messagebox.showwarning("Permisos", "No tienes permisos para acceder a esta seccion.")
            return
        subtitle = "Consulta tickets, detalle de productos, pagos y cancelaciones."
        body = self._screen("Historial de ventas", subtitle)

        sales_frame = ttk.Frame(body)
        sales_frame.pack(fill="both", expand=True)
        detail_frame = ttk.Frame(body)
        detail_frame.pack(fill="both", expand=True, pady=(12, 0))

        columns = ("id", "folio", "fecha", "usuario", "cliente", "pago", "total", "estado")
        headings = {
            "id": "ID",
            "folio": "Folio",
            "fecha": "Fecha",
            "usuario": "Usuario",
            "cliente": "Cliente",
            "pago": "Pago",
            "total": "Total",
            "estado": "Estado",
            "folio_width": 170,
            "fecha_width": 150,
            "cliente_width": 130,
        }
        sales_tree, sales_scroll = make_tree(sales_frame, columns, headings)
        sales_tree.pack(side="left", fill="both", expand=True)
        sales_scroll.pack(side="right", fill="y")

        detail_columns = ("codigo", "producto", "cantidad", "devuelta", "precio", "subtotal")
        detail_headings = {
            "codigo": "Codigo",
            "producto": "Producto",
            "cantidad": "Cant.",
            "devuelta": "Devuelta",
            "precio": "Precio",
            "subtotal": "Subtotal",
            "producto_width": 260,
        }
        detail_tree, detail_scroll = make_tree(detail_frame, detail_columns, detail_headings)
        detail_tree.pack(side="left", fill="both", expand=True)
        detail_scroll.pack(side="right", fill="y")

        summary = tk.Label(body, text="Selecciona un ticket para ver su detalle.", bg=SURFACE, fg=MUTED, font=(FONT, 10))
        summary.pack(anchor="w", pady=(8, 0))

        actions = ttk.Frame(body, style="App.TFrame")
        actions.pack(fill="x", pady=10)
        ttk.Button(actions, text="Cancelar ticket", style="Danger.TButton", command=lambda: cancel()).pack(side="left", padx=8)
        ttk.Button(actions, text="Actualizar", style="Ghost.TButton", command=lambda: load_sales()).pack(side="right")

        def load_sales():
            for row in sales_tree.get_children():
                sales_tree.delete(row)
            for row in detail_tree.get_children():
                detail_tree.delete(row)
            try:
                for sale in self.sales.list_sales(user=self.user):
                    sales_tree.insert(
                        "",
                        "end",
                        iid=str(sale["id"]),
                        values=(
                            sale["id"],
                            sale["folio"],
                            sale["created_at"],
                            sale["usuario"],
                            sale["cliente"],
                            sale["forma_pago"],
                            money(sale["total"]),
                            sale["estado"],
                        ),
                    )
            except Exception as exc:
                messagebox.showerror("Historial de ventas", str(exc))

        def load_details(_event=None):
            for row in detail_tree.get_children():
                detail_tree.delete(row)
            selected = sales_tree.selection()
            if not selected:
                return
            try:
                sale = self.sales.get_sale(int(selected[0]))
                details = self.sales.get_sale_details(int(selected[0]))
                for detail in details:
                    detail_tree.insert(
                        "",
                        "end",
                        values=(
                            detail["codigo"],
                            detail["nombre"],
                            detail["cantidad"],
                            detail["cantidad_devuelta"],
                            money(detail["precio_unitario"]),
                            money(detail["subtotal"]),
                        ),
                    )
                summary.configure(
                    text=(
                        f"Ticket {sale['folio']} | Cliente: {sale['cliente']} | "
                        f"Pago: {sale['forma_pago']} | Modalidad: {sale['modalidad']} | "
                        f"Subtotal {money(sale['subtotal'])} | Descuento {money(sale['descuento'])} | Total {money(sale['total'])}"
                    )
                )
            except Exception as exc:
                messagebox.showerror("Detalle de venta", str(exc))

        def cancel():
            selected = sales_tree.selection()
            if not selected:
                messagebox.showwarning("Cancelacion", "Selecciona un ticket.")
                return
            motivo = simpledialog.askstring(
                "Motivo de cancelacion",
                "Motivo: error en pedido, cancelacion solicitada, producto incorrecto u otro",
            )
            if not motivo:
                return
            try:
                amount = self.sales.cancel_sale(int(selected[0]), self.user, motivo)
                messagebox.showinfo("Ticket cancelado", f"Ticket cancelado por {money(amount)}.")
                load_sales()
            except Exception as exc:
                messagebox.showerror("Cancelacion", str(exc))

        sales_tree.bind("<<TreeviewSelect>>", load_details)
        load_sales()

    def show_returns(self):
        if not self._guard("returns_write"):
            return
        body = self._screen("Devoluciones y cancelaciones")
        sales_frame = ttk.Frame(body)
        sales_frame.pack(fill="both", expand=True)
        detail_frame = ttk.Frame(body)
        detail_frame.pack(fill="both", expand=True, pady=(12, 0))

        sales_tree = self._render_sales_table(sales_frame, user_filter=self.user)

        detail_columns = ("id", "codigo", "nombre", "cantidad", "devuelta", "subtotal")
        detail_headings = {
            "id": "ID",
            "codigo": "Codigo",
            "nombre": "Producto",
            "cantidad": "Cant.",
            "devuelta": "Devuelta",
            "subtotal": "Subtotal",
            "nombre_width": 260,
        }
        detail_tree, detail_scroll = make_tree(detail_frame, detail_columns, detail_headings)
        detail_tree.pack(side="left", fill="both", expand=True)
        detail_scroll.pack(side="right", fill="y")

        actions = ttk.Frame(body)
        actions.pack(fill="x", pady=10)
        ttk.Button(actions, text="Devolver producto", command=lambda: refund()).pack(side="left")
        ttk.Button(actions, text="Cancelar venta", style="Danger.TButton", command=lambda: cancel()).pack(side="left", padx=8)
        ttk.Button(actions, text="Actualizar", command=lambda: load_sales()).pack(side="right")

        def load_sales():
            for row in sales_tree.get_children():
                sales_tree.delete(row)
            try:
                for sale in self.sales.list_sales(user=self.user):
                    sales_tree.insert(
                        "",
                        "end",
                        iid=str(sale["id"]),
                        values=(sale["id"], sale["folio"], sale["created_at"], sale["estado"], money(sale["total"]), sale["usuario"]),
                    )
            except Exception as exc:
                messagebox.showerror("Ventas", str(exc))

        def load_details(_event=None):
            for row in detail_tree.get_children():
                detail_tree.delete(row)
            selected = sales_tree.selection()
            if not selected:
                return
            try:
                for detail in self.sales.get_sale_details(int(selected[0])):
                    detail_tree.insert(
                        "",
                        "end",
                        iid=str(detail["id"]),
                        values=(detail["id"], detail["codigo"], detail["nombre"], detail["cantidad"], detail["cantidad_devuelta"], money(detail["subtotal"])),
                    )
            except Exception as exc:
                messagebox.showerror("Detalle", str(exc))

        def refund():
            selected = detail_tree.selection()
            if not selected:
                messagebox.showwarning("Devolucion", "Selecciona un producto del detalle.")
                return
            motivo = simpledialog.askstring(
                "Motivo",
                "Motivo: producto defectuoso, danado, incorrecto, error pedido, cancelacion solicitada u otro",
            )
            if not motivo:
                return
            tipo = simpledialog.askstring("Reembolso", "Tipo de reembolso:", initialvalue="Efectivo")
            try:
                amount = self.sales.refund_detail(int(selected[0]), self.user, motivo, tipo or "Efectivo")
                messagebox.showinfo("Devolucion", f"Devolucion aplicada por {money(amount)}.")
                load_details()
                load_sales()
            except Exception as exc:
                messagebox.showerror("Devolucion", str(exc))

        def cancel():
            selected = sales_tree.selection()
            if not selected:
                messagebox.showwarning("Cancelacion", "Selecciona una venta.")
                return
            motivo = simpledialog.askstring("Motivo", "Motivo de cancelacion:")
            if not motivo:
                return
            try:
                amount = self.sales.cancel_sale(int(selected[0]), self.user, motivo)
                messagebox.showinfo("Cancelacion", f"Venta cancelada por {money(amount)}.")
                load_details()
                load_sales()
            except Exception as exc:
                messagebox.showerror("Cancelacion", str(exc))

        sales_tree.bind("<<TreeviewSelect>>", load_details)
        load_sales()

    def _render_sales_table(self, parent, user_filter: dict | None = None):
        columns = ("id", "folio", "fecha", "estado", "total", "usuario")
        headings = {
            "id": "ID",
            "folio": "Folio",
            "fecha": "Fecha",
            "estado": "Estado",
            "total": "Total",
            "usuario": "Usuario",
            "folio_width": 160,
        }
        tree, scroll = make_tree(parent, columns, headings)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        try:
            for sale in self.sales.list_sales(user=user_filter):
                tree.insert(
                    "",
                    "end",
                    iid=str(sale["id"]),
                    values=(sale["id"], sale["folio"], sale["created_at"], sale["estado"], money(sale["total"]), sale["usuario"]),
                )
        except Exception as exc:
            messagebox.showerror("Ventas", str(exc))
        return tree

    def show_users(self):
        if not self._guard("users_manage"):
            return
        body = self._screen("Administracion de usuarios")
        columns = ("id", "username", "nombre", "email", "telefono", "direccion", "rol", "activo", "saldo")
        headings = {
            "id": "ID",
            "username": "Usuario",
            "nombre": "Nombre",
            "email": "Correo",
            "telefono": "Telefono",
            "direccion": "Direccion",
            "rol": "Rol",
            "activo": "Activo",
            "saldo": "Saldo",
            "nombre_width": 180,
            "email_width": 190,
            "direccion_width": 230,
        }
        table_frame = ttk.Frame(body)
        table_frame.pack(fill="both", expand=True)
        tree, scroll = make_tree(table_frame, columns, headings)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        form = ttk.Frame(body)
        form.pack(fill="x", pady=12)
        username = tk.StringVar()
        password = tk.StringVar()
        nombre = tk.StringVar()
        email = tk.StringVar()
        telefono = tk.StringVar()
        direccion = tk.StringVar()
        rol = tk.StringVar(value="CLIENTE")
        labels = [
            ("Usuario", username),
            ("Contrasena", password),
            ("Nombre", nombre),
            ("Correo", email),
            ("Telefono", telefono),
            ("Direccion", direccion),
            ("Rol", rol),
        ]
        for index, (label, var) in enumerate(labels):
            row = 0 if index < 4 else 2
            column = index if index < 4 else index - 4
            ttk.Label(form, text=label).grid(row=row, column=column, sticky="w", padx=4)
            if label == "Rol":
                role_combo = ttk.Combobox(form, textvariable=var, state="readonly")
                role_combo.grid(row=row + 1, column=column, sticky="ew", padx=4)
            else:
                ttk.Entry(form, textvariable=var, show="*" if label == "Contrasena" else "").grid(
                    row=row + 1,
                    column=column,
                    sticky="ew",
                    padx=4,
                )
            form.columnconfigure(column, weight=1)
        ttk.Button(form, text="Crear usuario", style="Primary.TButton", command=lambda: create()).grid(row=3, column=3, padx=(8, 0), sticky="ew")
        ttk.Button(form, text="Eliminar usuario", style="Danger.TButton", command=lambda: delete()).grid(row=3, column=4, padx=(8, 0), sticky="ew")

        def load():
            for row in tree.get_children():
                tree.delete(row)
            try:
                role_combo["values"] = self.auth.list_roles(self.user)
                for item in self.auth.list_users(self.user):
                    tree.insert(
                        "",
                        "end",
                        iid=str(item["id"]),
                        values=(
                            item["id"],
                            item["username"],
                            item["nombre"],
                            item.get("email") or "",
                            item.get("telefono") or "",
                            item.get("direccion") or "",
                            item["rol"],
                            "Si" if item["activo"] else "No",
                            money(item["saldo_electronico"]),
                        ),
                    )
            except Exception as exc:
                messagebox.showerror("Usuarios", str(exc))

        def create():
            try:
                self.auth.create_user(
                    username.get(),
                    password.get(),
                    nombre.get() or username.get(),
                    rol.get(),
                    email=email.get().strip() or None,
                    telefono=telefono.get().strip() or None,
                    direccion=direccion.get().strip() or None,
                    actor=self.user,
                )
                username.set("")
                password.set("")
                nombre.set("")
                email.set("")
                telefono.set("")
                direccion.set("")
                load()
            except Exception as exc:
                messagebox.showerror("Usuarios", str(exc))

        def delete():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Usuarios", "Selecciona un usuario.")
                return
            values = tree.item(selected[0], "values")
            if not messagebox.askyesno("Eliminar usuario", f"Estas seguro de eliminar este usuario?\n\n{values[1]}"):
                return
            try:
                self.auth.deactivate_user(int(selected[0]), self.user)
                load()
                messagebox.showinfo("Usuarios", "Usuario desactivado.")
            except Exception as exc:
                messagebox.showerror("Usuarios", str(exc))

        load()

    def show_reports(self):
        if not can(self.user, "reports_admin"):
            messagebox.showwarning("Permisos", "No tienes permisos para acceder a esta seccion.")
            return

        body = self._screen(
            "Reportes administrativos",
            "Ventas por dia y productos que requieren compra."
        )

        try:
            ventas_por_dia = self.reports.sales_by_day(30)
            stock_faltante = self.reports.low_stock()
        except Exception as exc:
            messagebox.showerror("Reportes", str(exc))
            return

        ttk.Label(body, text="Ventas por dia", style="Title.TLabel").pack(anchor="w", pady=(0, 8))

        ventas_frame = ttk.Frame(body)
        ventas_frame.pack(fill="both", expand=True, pady=(0, 18))

        ventas_columns = ("fecha", "cantidad", "total")
        ventas_headings = {
            "fecha": "Fecha",
            "cantidad": "Ventas",
            "total": "Total vendido",
        }

        ventas_tree, ventas_scroll = make_tree(ventas_frame, ventas_columns, ventas_headings)
        ventas_tree.pack(side="left", fill="both", expand=True)
        ventas_scroll.pack(side="right", fill="y")

        for row in ventas_por_dia:
            ventas_tree.insert(
                "",
                "end",
                values=(
                    row["fecha"],
                    row["cantidad_ventas"],
                    money(row["total"]),
                ),
            )

        ttk.Label(body, text="Stock faltante por comprar", style="Title.TLabel").pack(anchor="w", pady=(8, 8))

        stock_frame = ttk.Frame(body)
        stock_frame.pack(fill="both", expand=True)

        stock_columns = ("codigo", "nombre", "categoria", "stock", "minimo", "sugerida")
        stock_headings = {
            "codigo": "Codigo",
            "nombre": "Producto",
            "categoria": "Categoria",
            "stock": "Stock actual",
            "minimo": "Stock minimo",
            "sugerida": "Comprar",
            "nombre_width": 280,
        }

        stock_tree, stock_scroll = make_tree(stock_frame, stock_columns, stock_headings)
        stock_tree.pack(side="left", fill="both", expand=True)
        stock_scroll.pack(side="right", fill="y")

        for item in stock_faltante:
            stock_tree.insert(
                "",
                "end",
                values=(
                    item["codigo"],
                    item["nombre"],
                    item["categoria"],
                    item["stock_actual"],
                    item["stock_minimo"],
                    item["cantidad_sugerida"],
                ),
            )

    def show_orders(self):
        if not self._guard("orders_manage"):
            return
        body = self._screen("Pedidos de cliente", "Modulo complementario para negocios que requieren pedidos.")
        columns = ("id", "fecha", "cliente", "modalidad", "pago", "estado", "total", "direccion")
        headings = {
            "id": "ID",
            "fecha": "Fecha",
            "cliente": "Cliente",
            "modalidad": "Modalidad",
            "pago": "Pago",
            "estado": "Estado",
            "total": "Total",
            "direccion": "Direccion",
            "modalidad_width": 170,
            "direccion_width": 240,
        }
        table_frame = ttk.Frame(body)
        table_frame.pack(fill="both", expand=True)
        tree, scroll = make_tree(table_frame, columns, headings)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        actions = ttk.Frame(body)
        actions.pack(fill="x", pady=8)
        for label, status in [
            ("En proceso", "EN PROCESO"),
            ("Listo para entrega", "LISTO PARA ENTREGA"),
            ("Entregado", "ENTREGADO"),
            ("Cancelado", "CANCELADO"),
            ("Devuelto", "DEVUELTO"),
        ]:
            style = "Danger.TButton" if status in {"CANCELADO", "DEVUELTO"} else "Secondary.TButton"
            ttk.Button(actions, text=label, style=style, command=lambda s=status: update(s)).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Actualizar", style="Ghost.TButton", command=lambda: load()).pack(side="right")

        def load():
            for row in tree.get_children():
                tree.delete(row)
            try:
                for order in self.orders.list_orders():
                    tree.insert(
                        "",
                        "end",
                        iid=str(order["id"]),
                        values=(
                            order["id"],
                            order["created_at"],
                            order["cliente"],
                            order["modalidad"],
                            order["forma_pago"],
                            order["estado"],
                            money(order["total"]),
                            order["direccion_entrega"] or "-",
                        ),
                    )
            except Exception as exc:
                messagebox.showerror("Pedidos", str(exc))

        def update(status):
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Pedidos", "Selecciona un pedido.")
                return
            motivo = None
            if status in {"CANCELADO", "DEVUELTO"}:
                motivo = simpledialog.askstring(
                    "Motivo",
                    "Motivo: producto defectuoso, danado, incorrecto, error pedido, cancelacion solicitada u otro",
                )
                if not motivo:
                    return
            try:
                self.orders.update_status(int(selected[0]), status, self.user, motivo=motivo)
                load()
            except Exception as exc:
                messagebox.showerror("Pedidos", str(exc))

        load()

    def show_config(self):
        if not self._guard("settings_manage"):
            return
        body = self._screen("Configuracion general")
        ttk.Label(body, text="Conexion MySQL", style="Title.TLabel").pack(anchor="w")
        ttk.Label(body, text=describe_config(), style="Metric.TLabel").pack(anchor="w", pady=(6, 16))
        ttk.Label(
            body,
            text="Las credenciales se centralizan en config/db_config.py o variables de entorno AVSAWARE_DB_*.",
            style="Subtitle.TLabel",
        ).pack(anchor="w")
