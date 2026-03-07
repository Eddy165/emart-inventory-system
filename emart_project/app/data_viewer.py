# app/data_viewer.py
import tkinter as tk
from tkinter import ttk, messagebox
from app.db_connect import get_connection

def open_data_viewer(parent):
    win = tk.Toplevel(parent)
    win.title('EMart — Complete Data Viewer')
    win.geometry('1000x600')
    win.configure(bg='#f0f4f8')
    win.resizable(True, True)

    win.update_idletasks()
    x = (win.winfo_screenwidth() - win.winfo_width()) // 2
    y = (win.winfo_screenheight() - win.winfo_height()) // 2
    win.geometry(f'+{x}+{y}')

    header = tk.Frame(win, bg='#1F4E79', height=45)
    header.pack(fill=tk.X)
    tk.Label(header,
             text='📊 Complete Database Viewer — All Tables & Views',
             font=('Arial', 13, 'bold'),
             bg='#1F4E79', fg='white').pack(pady=10)

    notebook = ttk.Notebook(win)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def sort_tree(tree, col, reverse):
        data = [(tree.set(child, col), child)
                for child in tree.get_children('')]
        try:
            data.sort(key=lambda x: float(x[0]), reverse=reverse)
        except ValueError:
            data.sort(reverse=reverse)
        for index, (val, child) in enumerate(data):
            tree.move(child, '', index)
        tree.heading(col,
                     command=lambda: sort_tree(tree, col,
                                               not reverse))

    def make_tab(tab_name, query, columns):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=tab_name)

        count_label = tk.Label(frame, text='',
                                font=('Arial', 9),
                                fg='#595959', bg='white')
        count_label.pack(anchor='w', padx=10, pady=2)

        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tree = ttk.Treeview(tree_frame, columns=columns,
                             show='headings', height=18)

        col_width = max(80, int(900 / len(columns)))
        for col in columns:
            tree.heading(col, text=col,
                         command=lambda c=col: sort_tree(
                             tree, c, False))
            tree.column(col, width=col_width, anchor='w')

        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL,
                             command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL,
                             command=tree.xview)
        tree.configure(yscrollcommand=vsb.set,
                       xscrollcommand=hsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        def load_tab():
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                tree.delete(*tree.get_children())
                for row in rows:
                    row = [str(v) if v is not None else 'NULL'
                           for v in row]
                    tree.insert('', 'end', values=row)
                count_label.config(
                    text=f'Total records: {len(rows)}')
                conn.close()
            except Exception as e:
                messagebox.showerror('Error', str(e))

        load_tab()

        btn_frame = tk.Frame(frame, bg='white')
        btn_frame.pack(fill=tk.X, padx=5, pady=3)

        tk.Button(btn_frame, text='🔄 Refresh',
                  command=load_tab,
                  bg='#2E75B6', fg='white',
                  font=('Arial', 9, 'bold'),
                  relief=tk.FLAT,
                  cursor='hand2').pack(side=tk.LEFT, padx=5)

        def export_csv():
            import csv
            from tkinter import filedialog
            filepath = filedialog.asksaveasfilename(
                defaultextension='.csv',
                filetypes=[('CSV files', '*.csv')],
                initialfile=f'{tab_name}.csv'
            )
            if filepath:
                with open(filepath, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(columns)
                    for row_id in tree.get_children():
                        writer.writerow(
                            tree.item(row_id)['values'])
                messagebox.showinfo('Exported',
                                    f'Saved to:\n{filepath}')

        tk.Button(btn_frame, text='📥 Export CSV',
                  command=export_csv,
                  bg='#1D6A38', fg='white',
                  font=('Arial', 9, 'bold'),
                  relief=tk.FLAT,
                  cursor='hand2').pack(side=tk.LEFT, padx=5)

        return tree, load_tab

    # TAB 1
    make_tab('📦 Category',
             'SELECT * FROM Category',
             ('category_id', 'category_name', 'description'))

    # TAB 2
    make_tab('🛒 Product',
             '''SELECT p.product_id, p.product_name, p.price,
                       p.reorder_level, c.category_name
                FROM Product p
                JOIN Category c ON p.category_id = c.category_id
                ORDER BY p.product_id''',
             ('ID', 'Product Name', 'Price',
              'Reorder Level', 'Category'))

    # TAB 3
    make_tab('🏭 Supplier',
             'SELECT * FROM Supplier ORDER BY supplier_id',
             ('supplier_id', 'supplier_name',
              'contact', 'email'))

    # TAB 4
    make_tab('🔗 Supplier Mapping',
             '''SELECT s.supplier_name, p.product_name,
                       sp.supply_price
                FROM SupplierProduct sp
                JOIN Supplier s ON sp.supplier_id = s.supplier_id
                JOIN Product p  ON sp.product_id  = p.product_id
                ORDER BY s.supplier_name''',
             ('Supplier', 'Product', 'Supply Price'))

    # TAB 5
    make_tab('📊 Stock',
             '''SELECT s.stock_id, p.product_name,
                       s.quantity, p.reorder_level,
                       IF(s.quantity < p.reorder_level,
                          'LOW STOCK', 'OK') AS status,
                       s.last_updated
                FROM Stock s
                JOIN Product p ON s.product_id = p.product_id
                ORDER BY s.stock_id''',
             ('ID', 'Product', 'Quantity',
              'Reorder Level', 'Status', 'Last Updated'))

    # TAB 6
    make_tab('👤 Customer',
             'SELECT * FROM Customer ORDER BY customer_id',
             ('customer_id', 'customer_name',
              'phone', 'loyalty_points'))

    # TAB 7
    make_tab('🧾 Bill',
             '''SELECT b.bill_id, c.customer_name,
                       b.total_amount, b.payment_mode,
                       b.bill_date
                FROM Bill b
                JOIN Customer c ON b.customer_id = c.customer_id
                ORDER BY b.bill_date DESC''',
             ('Bill ID', 'Customer', 'Total',
              'Payment Mode', 'Date'))

    # TAB 8
    make_tab('📋 Bill Items',
             '''SELECT bi.billitem_id, bi.bill_id,
                       p.product_name, bi.quantity,
                       bi.unit_price,
                       (bi.quantity * bi.unit_price) AS subtotal
                FROM BillItem bi
                JOIN Product p ON bi.product_id = p.product_id
                ORDER BY bi.bill_id''',
             ('Item ID', 'Bill ID', 'Product',
              'Quantity', 'Unit Price', 'Subtotal'))

    # TAB 9
    make_tab('🔍 Audit Log',
             '''SELECT l.log_id, p.product_name,
                       l.old_quantity, l.new_quantity,
                       (l.new_quantity - l.old_quantity) AS change_qty,
                       l.changed_at, l.changed_by
                FROM StockAuditLog l
                LEFT JOIN Product p ON l.product_id = p.product_id
                ORDER BY l.changed_at DESC''',
             ('Log ID', 'Product', 'Old Qty',
              'New Qty', 'Change', 'Changed At', 'Changed By'))

    # TAB 10
    make_tab('🔔 Reorder',
             '''SELECT r.request_id, p.product_name,
                       r.requested_qty, r.request_date,
                       r.status
                FROM ReorderRequest r
                JOIN Product p ON r.product_id = p.product_id
                ORDER BY r.request_date DESC''',
             ('Request ID', 'Product', 'Requested Qty',
              'Date', 'Status'))

    # TAB 11
    make_tab('⚠️ Low Stock',
             'SELECT * FROM vw_LowStockItems',
             ('ID', 'Product', 'Reorder Level',
              'Current Stock', 'Shortage'))

    # TAB 12
    make_tab('💰 Daily Sales',
             'SELECT * FROM vw_DailySales ORDER BY sale_date DESC',
             ('Date', 'Total Bills', 'Total Revenue'))

    # TAB 13
    make_tab('📈 Product Sales',
             'SELECT * FROM vw_ProductSales',
             ('Product', 'Units Sold', 'Total Revenue'))

    bottom = tk.Frame(win, bg='#f0f4f8')
    bottom.pack(fill=tk.X, padx=10, pady=5)
    tk.Label(bottom,
             text='💡 Click column header to sort  |  '
                  '📥 Export CSV  |  🔄 Refresh each tab',
             font=('Arial', 9), fg='#595959',
             bg='#f0f4f8').pack(side=tk.LEFT, padx=10)

    win.bind('<F5>', lambda e: notebook.select(
        notebook.index(notebook.select())))