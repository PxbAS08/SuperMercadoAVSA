import tkinter as tk
from tkinter import messagebox, ttk

from controllers.producto_controller import ProductoController
from utils.permissions import require_permission
from views.theme import make_card, make_tree


class CategoriasView(ttk.Frame):
    def __init__(self, master, user: dict):
        super().__init__(master, padding=12)
        require_permission(user, "categories_manage")
        self.user = user
        self.controller = ProductoController()
        self.category = tk.StringVar()
        self.description = tk.StringVar()
        self.subcategory = tk.StringVar()
        self.selected_category = tk.StringVar()
        self.configure(style="App.TFrame")
        self._build()
        self.refresh()

    def _build(self):
        outer, form = make_card(self, padding=16)
        outer.pack(fill="x", pady=(0, 12))

        ttk.Label(form, text="Gestion de categorias", style="Title.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))
        ttk.Label(form, text="Categoria", style="Eyebrow.TLabel").grid(row=1, column=0, sticky="w")
        ttk.Label(form, text="Descripcion", style="Eyebrow.TLabel").grid(row=1, column=1, sticky="w", padx=(8, 0))
        ttk.Entry(form, textvariable=self.category).grid(row=2, column=0, sticky="ew")
        ttk.Entry(form, textvariable=self.description).grid(row=2, column=1, sticky="ew", padx=(8, 0))
        ttk.Button(form, text="Guardar categoria", style="Primary.TButton", command=self.save_category).grid(
            row=2, column=2, padx=(8, 0)
        )

        ttk.Label(form, text="Categoria para subcategoria", style="Eyebrow.TLabel").grid(row=3, column=0, sticky="w", pady=(10, 0))
        ttk.Label(form, text="Subcategoria", style="Eyebrow.TLabel").grid(row=3, column=1, sticky="w", padx=(8, 0), pady=(10, 0))
        self.category_combo = ttk.Combobox(form, textvariable=self.selected_category, state="readonly")
        self.category_combo.grid(row=4, column=0, sticky="ew")
        ttk.Entry(form, textvariable=self.subcategory).grid(row=4, column=1, sticky="ew", padx=(8, 0))
        ttk.Button(form, text="Guardar subcategoria", style="Secondary.TButton", command=self.save_subcategory).grid(
            row=4, column=2, padx=(8, 0)
        )
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=2)

        panes = ttk.PanedWindow(self, orient="horizontal")
        panes.pack(fill="both", expand=True)

        cat_outer, cat_frame = make_card(panes, padding=14)
        sub_outer, sub_frame = make_card(panes, padding=14)
        panes.add(cat_outer, weight=1)
        panes.add(sub_outer, weight=1)
        ttk.Label(cat_frame, text="Categorias", style="Title.TLabel").pack(anchor="w", pady=(0, 10))

        cat_columns = ("id", "nombre", "subcategorias", "estado")
        cat_headings = {
            "id": "ID",
            "nombre": "Categoria",
            "subcategorias": "Subcategorias",
            "estado": "Estado",
            "nombre_width": 220,
        }
        cat_grid = ttk.Frame(cat_frame)
        cat_grid.pack(fill="both", expand=True)
        self.cat_tree, cat_scroll = make_tree(cat_grid, cat_columns, cat_headings)
        self.cat_tree.pack(side="left", fill="both", expand=True)
        cat_scroll.pack(side="right", fill="y")
        self.cat_tree.bind("<<TreeviewSelect>>", self.on_category_select)

        ttk.Label(sub_frame, text="Subcategorias", style="Title.TLabel").pack(anchor="w", pady=(0, 10))
        sub_columns = ("id", "categoria", "nombre", "estado")
        sub_headings = {
            "id": "ID",
            "categoria": "Categoria",
            "nombre": "Subcategoria",
            "estado": "Estado",
            "nombre_width": 220,
        }
        sub_grid = ttk.Frame(sub_frame)
        sub_grid.pack(fill="both", expand=True)
        self.sub_tree, sub_scroll = make_tree(sub_grid, sub_columns, sub_headings)
        self.sub_tree.pack(side="left", fill="both", expand=True)
        sub_scroll.pack(side="right", fill="y")

    def refresh(self):
        for tree in (self.cat_tree, self.sub_tree):
            for row in tree.get_children():
                tree.delete(row)
        try:
            categories = self.controller.list_category_rows()
            names = []
            for row in categories:
                names.append(row["nombre"])
                self.cat_tree.insert(
                    "",
                    "end",
                    iid=str(row["id"]),
                    values=(
                        row["id"],
                        row["nombre"],
                        row["subcategorias"],
                        "Activa" if row["activo"] else "Inactiva",
                    ),
                )
            self.category_combo["values"] = names
            if names and not self.selected_category.get():
                self.selected_category.set(names[0])
            self.refresh_subcategories()
        except Exception as exc:
            messagebox.showerror("Categorias", str(exc))

    def refresh_subcategories(self, category_name: str | None = None):
        for row in self.sub_tree.get_children():
            self.sub_tree.delete(row)
        for row in self.controller.list_subcategory_rows(category_name):
            self.sub_tree.insert(
                "",
                "end",
                values=(
                    row["id"],
                    row["categoria"],
                    row["nombre"],
                    "Activa" if row["activa"] else "Inactiva",
                ),
            )

    def on_category_select(self, _event=None):
        selected = self.cat_tree.selection()
        if not selected:
            return
        values = self.cat_tree.item(selected[0], "values")
        self.category.set(values[1])
        self.selected_category.set(values[1])
        self.refresh_subcategories(values[1])

    def save_category(self):
        try:
            self.controller.save_category(self.category.get(), self.description.get(), self.user)
            self.category.set("")
            self.description.set("")
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Categorias", str(exc))

    def save_subcategory(self):
        try:
            self.controller.save_subcategory(
                self.selected_category.get(),
                self.subcategory.get(),
                self.user,
            )
            self.subcategory.set("")
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Subcategorias", str(exc))
