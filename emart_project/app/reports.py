import tkinter as tk
from tkinter import ttk, messagebox
from app.db_connect import get_connection

def open_reports_window(parent):
    win = tk.Toplevel(parent)
    win.title("Reports & Analytics")
    win.geometry("900x600")
    win.configure(bg="#f0f4f8")

    win.update_idletasks()
    x = (win.winfo_screenwidth() - win.winfo_width()) // 2
    y = (win.winfo_screenheight() - win.winfo_height()) // 2
    win.geometry(f'+{x}+{y}')

    # --- Header ---
    header = tk.Frame(win, bg="#1F4E79", height=50)
    header.pack(fill=tk.X)
    tk.Label(header, text="Reports & Analytics", font=("Arial", 16, "bold"), fg="white", bg="#1F4E79").pack(pady=10)

    notebook = ttk.Notebook(win)
    notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    # --- TAB 1: Low Stock Alerts ---
    tab1 = tk.Frame(notebook, bg="#f0f4f8")
    notebook.add(tab1, text="Low Stock Alerts")
    
    t1_cols = ("ID", "Product", "Reorder Level", "Current Stock", "Shortage")
    t1_tree = ttk.Treeview(tab1, columns=t1_cols, show='headings')
    for c in t1_cols: t1_tree.heading(c, text=c)
    t1_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def load_low_stock():
        t1_tree.delete(*t1_tree.get_children())
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM vw_LowStockItems")
                for row in cursor.fetchall():
                    # Calculate shortage if not in view
                    # Assuming row format: id, name, reorder, qty
                    shortage = row[2] - row[3]
                    t1_tree.insert("", tk.END, values=(*row, shortage))
            finally: conn.close()

    # --- TAB 2: Daily Sales ---
    tab2 = tk.Frame(notebook, bg="#f0f4f8")
    notebook.add(tab2, text="Daily Sales")
    
    t2_cols = ("Date", "Total Bills", "Total Revenue")
    t2_tree = ttk.Treeview(tab2, columns=t2_cols, show='headings')
    for c in t2_cols: t2_tree.heading(c, text=c)
    t2_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def load_daily_sales():
        t2_tree.delete(*t2_tree.get_children())
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM vw_DailySales ORDER BY sale_date DESC")
                for row in cursor.fetchall(): t2_tree.insert("", tk.END, values=row)
            finally: conn.close()

    # --- TAB 3: Product Sales ---
    tab3 = tk.Frame(notebook, bg="#f0f4f8")
    notebook.add(tab3, text="Product Sales")
    
    t3_cols = ("Product", "Units Sold", "Total Revenue")
    t3_tree = ttk.Treeview(tab3, columns=t3_cols, show='headings')
    for c in t3_cols: t3_tree.heading(c, text=c)
    t3_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def load_product_sales():
        t3_tree.delete(*t3_tree.get_children())
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM vw_ProductSales")
                for row in cursor.fetchall(): t3_tree.insert("", tk.END, values=row)
            finally: conn.close()

    # --- Bottom Actions ---
    btm_frame = tk.Frame(win, bg="#f0f4f8", pady=10)
    btm_frame.pack(fill=tk.X)

    def run_eod():
        if messagebox.askyesno("Confirm", "Run End of Day reorder processing?"):
            conn = get_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.callproc('sp_EOD_Reorder')
                    conn.commit()
                    messagebox.showinfo("Success", "EOD Batch processed successfully.")
                except Exception as e: messagebox.showerror("Error", str(e))
                finally: conn.close()

    tk.Button(btm_frame, text="Run EOD Batch", bg="#C55A11", fg="white", font=("Arial", 10, "bold"), command=run_eod).pack(side=tk.LEFT, padx=20)

    # --- Valuation ---
    tk.Label(btm_frame, text="Stock Valuation (Prod ID):", bg="#f0f4f8").pack(side=tk.LEFT)
    val_ent = tk.Entry(btm_frame, width=5)
    val_ent.pack(side=tk.LEFT, padx=5)
    
    val_res = tk.Label(btm_frame, text="Rs. 0.00", bg="#f0f4f8", font=("Arial", 10, "bold"))
    
    def get_val():
        pid = val_ent.get()
        if not pid: return
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT fn_GetStockValue(%s)", (pid,))
                val = cursor.fetchone()[0]
                val_res.config(text=f"Rs. {val:.2f}" if val else "Rs. 0.00")
            finally: conn.close()

    tk.Button(btm_frame, text="Get Value", command=get_val).pack(side=tk.LEFT, padx=5)
    val_res.pack(side=tk.LEFT, padx=10)

    # Load initial tab data
    load_low_stock()
    load_daily_sales()
    load_product_sales()

    win.bind("<F5>", lambda e: (load_low_stock(), load_daily_sales(), load_product_sales()))
