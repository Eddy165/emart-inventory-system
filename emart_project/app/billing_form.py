import tkinter as tk
from tkinter import ttk, messagebox
from app.db_connect import get_connection

def open_billing_window(parent):
    win = tk.Toplevel(parent)
    win.title("Billing Module")
    win.geometry("800x600")
    win.configure(bg="#f0f4f8")

    win.update_idletasks()
    x = (win.winfo_screenwidth() - win.winfo_width()) // 2
    y = (win.winfo_screenheight() - win.winfo_height()) // 2
    win.geometry(f'+{x}+{y}')

    # --- Variables ---
    cust_id_var = tk.StringVar()
    prod_id_var = tk.StringVar()
    qty_var = tk.StringVar()
    pay_mode_var = tk.StringVar(value="CASH")

    # --- Header ---
    header = tk.Frame(win, bg="#1F4E79", height=50)
    header.pack(fill=tk.X)
    tk.Label(header, text="Billing Module", font=("Arial", 16, "bold"), fg="white", bg="#1F4E79").pack(pady=10)

    # --- Form ---
    form_f = tk.Frame(win, bg="#f0f4f8", pady=20)
    form_f.pack(fill=tk.X)

    tk.Label(form_f, text="Customer ID:", bg="#f0f4f8").grid(row=0, column=0, padx=5)
    tk.Entry(form_f, textvariable=cust_id_var, width=10).grid(row=0, column=1)
    
    tk.Label(form_f, text="Product ID:", bg="#f0f4f8").grid(row=0, column=2, padx=5)
    tk.Entry(form_f, textvariable=prod_id_var, width=10).grid(row=0, column=3)
    
    tk.Label(form_f, text="Quantity:", bg="#f0f4f8").grid(row=0, column=4, padx=5)
    tk.Entry(form_f, textvariable=qty_var, width=10).grid(row=0, column=5)
    
    tk.Label(form_f, text="Payment:", bg="#f0f4f8").grid(row=0, column=6, padx=5)
    tk.Entry(form_f, textvariable=pay_mode_var, width=10).grid(row=0, column=7)

    tk.Label(win, text="Payment Mode Options: CASH / CARD / UPI", font=("Arial", 9, "italic"), bg="#f0f4f8").pack()

    res_label = tk.Label(win, text="", font=("Arial", 11, "bold"), bg="#f0f4f8")
    res_label.pack(pady=10)

    def generate_bill():
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # sp_GenerateBill(IN customer_id, payment_mode, product_id, qty, OUT bill_id, OUT message)
                args = (int(cust_id_var.get()), pay_mode_var.get(), int(prod_id_var.get()), int(qty_var.get()), 0, '')
                result = cursor.callproc('sp_GenerateBill', args)
                conn.commit()
                
                bill_id = result[4]
                msg = result[5]
                
                if bill_id > 0:
                    res_label.config(text=f"Success: {msg} (Bill #{bill_id})", fg="#1D6A38")
                    load_recent_bills()
                else:
                    res_label.config(text=f"Error: {msg}", fg="#C00000")
            except Exception as e:
                res_label.config(text=f"System Error: {e}", fg="#C00000")
            finally: conn.close()

    tk.Button(win, text="Generate Bill", bg="#1D6A38", fg="white", font=("Arial", 12, "bold"), width=20, height=2, command=generate_bill).pack(pady=10)

    # --- Recent Bills ---
    tk.Label(win, text="Recent Transactions", font=("Arial", 12, "bold"), bg="#f0f4f8").pack(pady=(20, 5))
    columns = ("ID", "Customer", "Total", "Payment", "Date")
    tree = ttk.Treeview(win, columns=columns, show='headings', height=8)
    for col in columns: tree.heading(col, text=col)
    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def load_recent_bills():
        tree.delete(*tree.get_children())
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                query = """
                    SELECT b.bill_id, c.customer_name, b.total_amount, b.payment_mode, b.bill_date 
                    FROM Bill b
                    JOIN Customer c ON b.customer_id = c.customer_id
                    ORDER BY b.bill_id DESC LIMIT 10
                """
                cursor.execute(query)
                for row in cursor.fetchall(): tree.insert("", tk.END, values=row)
            finally: conn.close()

    load_recent_bills()
    win.bind("<F5>", lambda e: load_recent_bills())
