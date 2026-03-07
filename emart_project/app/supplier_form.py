import tkinter as tk
from tkinter import ttk, messagebox
from app.db_connect import get_connection

def open_supplier_window(parent):
    win = tk.Toplevel(parent)
    win.title("Supplier Management")
    win.geometry("900x650")
    win.configure(bg="#f0f4f8")

    win.update_idletasks()
    x = (win.winfo_screenwidth() - win.winfo_width()) // 2
    y = (win.winfo_screenheight() - win.winfo_height()) // 2
    win.geometry(f'+{x}+{y}')

    # --- Variables ---
    sup_name_var = tk.StringVar()
    contact_var = tk.StringVar()
    email_var = tk.StringVar()
    selected_sup_id = None

    map_sup_id_var = tk.StringVar()
    map_prod_id_var = tk.StringVar()
    map_price_var = tk.StringVar()

    # --- Header ---
    header = tk.Frame(win, bg="#1F4E79", height=50)
    header.pack(fill=tk.X)
    tk.Label(header, text="Supplier Management", font=("Arial", 16, "bold"), fg="white", bg="#1F4E79").pack(pady=10)

    notebook = ttk.Notebook(win)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # --- TAB 1: Suppliers ---
    sup_tab = tk.Frame(notebook, bg="#f0f4f8")
    notebook.add(sup_tab, text="Suppliers")

    form_frame = tk.Frame(sup_tab, bg="#f0f4f8", pady=10)
    form_frame.pack(fill=tk.X)

    tk.Label(form_frame, text="Name:", bg="#f0f4f8").grid(row=0, column=0, padx=5, pady=5)
    tk.Entry(form_frame, textvariable=sup_name_var).grid(row=0, column=1, padx=5, pady=5)
    tk.Label(form_frame, text="Contact:", bg="#f0f4f8").grid(row=0, column=2, padx=5, pady=5)
    tk.Entry(form_frame, textvariable=contact_var).grid(row=0, column=3, padx=5, pady=5)
    tk.Label(form_frame, text="Email:", bg="#f0f4f8").grid(row=0, column=4, padx=5, pady=5)
    tk.Entry(form_frame, textvariable=email_var).grid(row=0, column=5, padx=5, pady=5)

    sup_tree = ttk.Treeview(sup_tab, columns=("ID", "Name", "Contact", "Email"), show='headings')
    for col in ("ID", "Name", "Contact", "Email"):
        sup_tree.heading(col, text=col)
    sup_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def load_suppliers():
        nonlocal selected_sup_id
        selected_sup_id = None
        sup_tree.delete(*sup_tree.get_children())
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Supplier")
                for row in cursor.fetchall():
                    sup_tree.insert("", tk.END, values=row)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load suppliers: {e}")
            finally:
                conn.close()

    def add_supplier():
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Supplier (supplier_name, contact, email) VALUES (%s, %s, %s)", 
                               (sup_name_var.get(), contact_var.get(), email_var.get()))
                conn.commit()
                messagebox.showinfo("Success", "Supplier added")
                load_suppliers()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", f"Add failed: {e}")
            finally:
                conn.close()

    def delete_supplier():
        selection = sup_tree.selection()
        if not selection: return
        sid = sup_tree.item(selection[0])['values'][0]
        if messagebox.askyesno("Confirm", "Delete supplier?"):
            conn = get_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM Supplier WHERE supplier_id=%s", (sid,))
                    conn.commit()
                    load_suppliers()
                finally: conn.close()

    btn_f = tk.Frame(sup_tab, bg="#f0f4f8")
    btn_f.pack(fill=tk.X, pady=5)
    tk.Button(btn_f, text="Add", bg="#1D6A38", fg="white", command=add_supplier, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_f, text="Delete", bg="#C00000", fg="white", command=delete_supplier, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_f, text="Refresh", bg="#2E75B6", fg="white", command=load_suppliers, width=10).pack(side=tk.LEFT, padx=5)

    # --- TAB 2: Mappings ---
    map_tab = tk.Frame(notebook, bg="#f0f4f8")
    notebook.add(map_tab, text="Product Mapping")

    map_f = tk.Frame(map_tab, bg="#f0f4f8", pady=10)
    map_f.pack(fill=tk.X)
    tk.Label(map_f, text="Sup ID:", bg="#f0f4f8").grid(row=0, column=0)
    tk.Entry(map_f, textvariable=map_sup_id_var, width=5).grid(row=0, column=1)
    tk.Label(map_f, text="Prod ID:", bg="#f0f4f8").grid(row=0, column=2)
    tk.Entry(map_f, textvariable=map_prod_id_var, width=5).grid(row=0, column=3)
    tk.Label(map_f, text="Price:", bg="#f0f4f8").grid(row=0, column=4)
    tk.Entry(map_f, textvariable=map_price_var, width=10).grid(row=0, column=5)

    map_tree = ttk.Treeview(map_tab, columns=("Sup", "Prod", "Price"), show='headings')
    for col in ("Sup", "Prod", "Price"): map_tree.heading(col, text=col)
    map_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def load_mappings():
        map_tree.delete(*map_tree.get_children())
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT supplier_id, product_id, supply_price FROM SupplierProduct")
                for row in cursor.fetchall(): map_tree.insert("", tk.END, values=row)
            finally: conn.close()

    def add_mapping():
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO SupplierProduct VALUES (%s, %s, %s)", 
                               (map_sup_id_var.get(), map_prod_id_var.get(), map_price_var.get()))
                conn.commit()
                load_mappings()
            except Exception as e: messagebox.showerror("Error", str(e))
            finally: conn.close()

    tk.Button(map_f, text="Add Mapping", command=add_mapping).grid(row=0, column=6, padx=10)

    load_suppliers()
    load_mappings()
    win.bind("<F5>", lambda e: (load_suppliers(), load_mappings()))
