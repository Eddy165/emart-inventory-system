import tkinter as tk
from tkinter import ttk, messagebox
from app.db_connect import get_connection

def open_stock_window(parent):
    win = tk.Toplevel(parent)
    win.title("Stock Management")
    win.geometry("850x600")
    win.configure(bg="#f0f4f8")

    win.update_idletasks()
    x = (win.winfo_screenwidth() - win.winfo_width()) // 2
    y = (win.winfo_screenheight() - win.winfo_height()) // 2
    win.geometry(f'+{x}+{y}')

    # --- Header ---
    header = tk.Frame(win, bg="#1F4E79", height=50)
    header.pack(fill=tk.X)
    tk.Label(header, text="Stock Management", font=("Arial", 16, "bold"), fg="white", bg="#1F4E79").pack(pady=10)

    # --- Table ---
    table_frame = tk.Frame(win, bg="#f0f4f8")
    table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    columns = ("ID", "Product", "Quantity", "Reorder Level", "Status")
    tree = ttk.Treeview(table_frame, columns=columns, show='headings')
    for col in columns: tree.heading(col, text=col)
    
    tree.tag_configure('low', background='#FFE0E0', foreground='#C00000')
    
    sb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=sb.set)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(fill=tk.BOTH, expand=True)

    def load_stock():
        tree.delete(*tree.get_children())
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                query = """
                    SELECT s.stock_id, p.product_name, s.quantity, p.reorder_level,
                           IF(s.quantity <= p.reorder_level, 'LOW STOCK', 'OK') as status
                    FROM Stock s
                    JOIN Product p ON s.product_id = p.product_id
                """
                cursor.execute(query)
                for row in cursor.fetchall():
                    tag = 'low' if row[4] == 'LOW STOCK' else ''
                    tree.insert("", tk.END, values=row, tags=(tag,))
            finally: conn.close()

    # --- Update Form ---
    upd_frame = tk.LabelFrame(win, text="Update Stock", bg="#f0f4f8", padx=10, pady=10)
    upd_frame.pack(fill=tk.X, padx=20, pady=10)

    tk.Label(upd_frame, text="Stock ID:", bg="#f0f4f8").grid(row=0, column=0)
    stock_id_ent = tk.Entry(upd_frame, width=10)
    stock_id_ent.grid(row=0, column=1, padx=5)

    tk.Label(upd_frame, text="New Quantity:", bg="#f0f4f8").grid(row=0, column=2)
    qty_ent = tk.Entry(upd_frame, width=10)
    qty_ent.grid(row=0, column=3, padx=5)

    def update_stock():
        sid = stock_id_ent.get()
        qty = qty_ent.get()
        if not sid or not qty: return
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE Stock SET quantity=%s WHERE stock_id=%s", (qty, sid))
                conn.commit()
                messagebox.showinfo("Success", "Stock updated")
                load_stock()
            except Exception as e: messagebox.showerror("Error", str(e))
            finally: conn.close()

    tk.Button(upd_frame, text="Update Stock", bg="#1D6A38", fg="white", command=update_stock).grid(row=0, column=4, padx=10)

    def open_audit_log():
        log_win = tk.Toplevel(win)
        log_win.title("Stock Audit Log")
        log_win.geometry("700x400")
        
        cols = ("Log ID", "Prod ID", "Old Qty", "New Qty", "Changed At")
        ltree = ttk.Treeview(log_win, columns=cols, show='headings')
        for c in cols: ltree.heading(c, text=c)
        ltree.pack(fill=tk.BOTH, expand=True)

        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT log_id, product_id, old_quantity, new_quantity, changed_at FROM StockAuditLog ORDER BY changed_at DESC")
                for row in cursor.fetchall(): ltree.insert("", tk.END, values=row)
            finally: conn.close()

    tk.Button(win, text="View Audit Log", bg="#595959", fg="white", command=open_audit_log).pack(pady=5)

    load_stock()
    win.bind("<F5>", lambda e: load_stock())
