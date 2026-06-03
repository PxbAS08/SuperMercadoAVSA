import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from controllers.producto_controller import ProductoController
from utils.helpers import money
from utils.permissions import can
from views.theme import FONT, MUTED, WHITE, make_card, make_toolbar, make_tree


class ProductosView(ttk.Frame):
    def __init__(self, master, user: dict, mode: str = "productos"):
        super().__init__(master, padding=12)
        self.user = user
        self.mode = mode
        self.controller = ProductoController()
        self.product_by_iid = {}
        self.can_edit_products = can(user, "products_write")
        self.can_adjust_stock = can(user, "inventory_write")
        self.vars = {
            "codigo": tk.StringVar(),
            "nombre": tk.StringVar(),
            "marca": tk.StringVar(),
            "categoria": tk.StringVar(),
            "subcategoria": tk.StringVar(),
            "presentacion": tk.StringVar(),
            "precio_venta": tk.StringVar(),
            "precio_compra": tk.StringVar(value="0"),
            "stock_actual": tk.StringVar(value="0"),
            "stock_minimo": tk.StringVar(value="5"),
            "search": tk.StringVar(),
        }
        self.category_combo = None
        self.subcategory_combo = None
        self.configure(style="App.TFrame")
        self._build()
        self.load_categories()
        self.refresh()

    def _build(self):
        if self.can_edit_products:
            self._build_form()
        else:
            ttk.Label(
                self,
                text="Consulta operativa de existencias, precios y disponibilidad.",
                style="PageSubtitle.TLabel",
            ).pack(anchor="w", pady=(0, 10))

        actions = make_toolbar(self)
        ttk.Label(actions, text="Buscar", style="Eyebrow.TLabel").pack(side="left", padx=(0, 8))
        ttk.Entry(actions, textvariable=self.vars["search"], width=34).pack(side="left")
        ttk.Button(actions, text="Buscar", style="Secondary.TButton", command=self.refresh).pack(side="left", padx=8)
        ttk.Button(actions, text="Limpiar", style="Ghost.TButton", command=self.clear_form).pack(side="left")

        if self.can_adjust_stock:
            ttk.Button(actions, text="Ajustar stock", style="Secondary.TButton", command=self.adjust_stock).pack(side="right", padx=6)
        if self.can_edit_products:
            ttk.Button(actions, text="Guardar producto", style="Primary.TButton", command=self.save).pack(
                side="right"
            )

        table_outer, table_frame = make_card(self, padding=14)
        table_outer.pack(fill="both", expand=True)
        header = tk.Frame(table_frame, bg=WHITE)
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="Listado de productos", bg=WHITE, fg="#17202A", font=(FONT, 16, "bold")).pack(anchor="w")
        tk.Label(header, text="Existencias, categorias, precios y merma", bg=WHITE, fg=MUTED, font=(FONT, 9)).pack(anchor="w")
        columns = ("codigo", "nombre", "marca", "categoria", "subcategoria", "presentacion", "precio", "stock", "merma")
        headings = {
            "codigo": "Codigo",
            "nombre": "Producto",
            "marca": "Marca",
            "categoria": "Categoria",
            "subcategoria": "Subcategoria",
            "presentacion": "Presentacion",
            "precio": "Precio",
            "stock": "Stock",
            "merma": "Merma",
            "codigo_width": 80,
            "nombre_width": 220,
            "stock_width": 70,
        }
        grid = ttk.Frame(table_frame)
        grid.pack(fill="both", expand=True)
        self.tree, scroll = make_tree(grid, columns, headings)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def _build_form(self):
        outer, form = make_card(self, padding=16)
        outer.pack(fill="x", pady=(0, 12))
        ttk.Label(form, text="Registro y edicion de producto", style="Title.TLabel").grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 10))

        row_one = [
            ("Codigo", "codigo"),
            ("Nombre", "nombre"),
            ("Marca", "marca"),
            ("Categoria", "categoria"),
            ("Subcategoria", "subcategoria"),
        ]
        row_two = [
            ("Presentacion", "presentacion"),
            ("Precio venta", "precio_venta"),
            ("Precio compra", "precio_compra"),
            ("Stock", "stock_actual"),
            ("Minimo", "stock_minimo"),
        ]
        for index, (label, key) in enumerate(row_one):
            ttk.Label(form, text=label, style="Eyebrow.TLabel").grid(row=1, column=index, sticky="w", padx=4)
            if key == "categoria":
                self.category_combo = ttk.Combobox(
                    form,
                    textvariable=self.vars[key],
                    state="readonly",
                    width=22,
                )
                self.category_combo.grid(row=2, column=index, sticky="ew", padx=4, pady=(2, 8))
                self.category_combo.bind("<<ComboboxSelected>>", self.on_category_change)
            elif key == "subcategoria":
                self.subcategory_combo = ttk.Combobox(
                    form,
                    textvariable=self.vars[key],
                    state="readonly",
                    width=22,
                )
                self.subcategory_combo.grid(row=2, column=index, sticky="ew", padx=4, pady=(2, 8))
            else:
                ttk.Entry(form, textvariable=self.vars[key], width=22).grid(
                    row=2, column=index, sticky="ew", padx=4, pady=(2, 8)
                )

        for index, (label, key) in enumerate(row_two):
            ttk.Label(form, text=label, style="Eyebrow.TLabel").grid(row=3, column=index, sticky="w", padx=4)
            ttk.Entry(form, textvariable=self.vars[key], width=22).grid(
                row=4, column=index, sticky="ew", padx=4, pady=(2, 8)
            )

        for column in range(5):
            form.columnconfigure(column, weight=1)

    def load_categories(self):
        if not self.can_edit_products:
            return
        try:
            categories = self.controller.list_categories()
            self.category_combo["values"] = categories
            if categories and not self.vars["categoria"].get():
                self.vars["categoria"].set(categories[0])
                self.on_category_change()
        except Exception as exc:
            messagebox.showerror("Categorias", str(exc))

    def on_category_change(self, _event=None):
        if not self.can_edit_products:
            return
        category = self.vars["categoria"].get()
        try:
            subcategories = self.controller.list_subcategories(category)
            self.subcategory_combo["values"] = subcategories
            if subcategories:
                self.vars["subcategoria"].set(subcategories[0])
            else:
                self.vars["subcategoria"].set("")
        except Exception as exc:
            messagebox.showerror("Subcategorias", str(exc))

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.product_by_iid.clear()
        try:
            products = self.controller.list_products(self.vars["search"].get().strip())
        except Exception as exc:
            messagebox.showerror("Productos", str(exc))
            return
        for product in products:
            iid = str(product["id"])
            self.product_by_iid[iid] = product
            self.tree.insert(
                "",
                "end",
                iid=iid,
                values=(
                    product["codigo"],
                    product["nombre"],
                    product["marca"],
                    product["categoria"],
                    product["subcategoria"],
                    product["presentacion"],
                    money(product["precio_venta"]),
                    product["stock_actual"],
                    product["merma"],
                ),
            )

    def on_select(self, _event=None):
        selected = self.tree.selection()
        if not selected or not self.can_edit_products:
            return
        product = self.product_by_iid[selected[0]]
        for key in self.vars:
            if key == "search":
                continue
            value = product.get(key)
            self.vars[key].set("" if value is None else str(value))
        self.on_category_change()
        self.vars["subcategoria"].set(product.get("subcategoria") or "")

    def clear_form(self):
        for key, var in self.vars.items():
            if key == "stock_minimo":
                var.set("5")
            elif key == "precio_compra":
                var.set("0")
            elif key != "search":
                var.set("")
        self.load_categories()

    def save(self):
        data = {key: var.get() for key, var in self.vars.items() if key != "search"}
        try:
            self.controller.save_product(data, self.user)
            self.load_categories()
            self.refresh()
            messagebox.showinfo("Productos", "Producto guardado.")
        except Exception as exc:
            messagebox.showerror("Productos", str(exc))

    def adjust_stock(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Inventario", "Selecciona un producto.")
            return
        product = self.product_by_iid[selected[0]]
        amount = simpledialog.askinteger(
            "Ajuste de stock",
            "Cantidad a sumar o restar (usa negativo para salida):",
            parent=self,
        )
        if amount is None:
            return
        motivo = simpledialog.askstring("Motivo", "Motivo del ajuste:", parent=self) or "Ajuste manual"
        try:
            self.controller.adjust_stock(product["id"], amount, self.user, motivo)
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Inventario", str(exc))
