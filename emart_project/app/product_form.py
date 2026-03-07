# app/product_form.py
import tkinter as tk
from tkinter import ttk, messagebox
from db_connect import get_connection

def open_product_window(parent):
    win = tk.Toplevel(parent)
    win.title('Product Management')
    win.geometry('900x580')
    win.configure(bg='#f0f4f8')
    win.resizable(True, True)

    # Center window on screen
    win.update_idletasks()
    x = (win.winfo_screenwidth() - win.winfo_width()) // 2
    y = (win.winfo_screenheight() - win.winfo_height()) // 2
    win.geometry(f'+{x}+{y}')

    # ── Header ──────────────────────────────────────────
    header = tk.Frame(win, bg='#1F4E79', height=45)
    header.pack(fill=tk.X)
    tk.Label(header, text='Product Management',
             font=('Arial', 14, 'bold'),
             bg='#1F4E79', fg='white').pack(pady=10)

    # ── Input Form ──────────────────────────────────────
    form_frame = tk.LabelFrame(win, text='Product Details',
                                font=('Arial', 10, 'bold'),
                                bg='#f0f4f8', padx=10, pady=10)
    form_frame.pack(fill=tk.X, padx=20, pady=10)

    fields = ['Product Name', 'Price', 'Reorder Level', 'Category ID']
    entries = {}
    for i, f in enumerate(fields):
        tk.Label(form_frame, text=f + ':',
                 font=('Arial', 10),
                 bg='#f0f4f8').grid(row=0, column=i*2, padx=8, sticky='e')
        e = tk.Entry(form_frame, width=15, font=('Arial', 10))
        e.grid(row=0, column=i*2+1, padx=5)
        entries[f] = e

    # Hidden variable to store selected product_id
    selected_id = tk.IntVar(value=0)

    # ── Treeview ─────────────────────────────────────────
    tree_frame = tk.Frame(win)
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

    cols = ('ID', 'Name', 'Price', 'Reorder', 'Category')
    tree = ttk.Treeview(tree_frame, columns=cols,
                         show='headings', height=14)
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=160)

    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL,
                               command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # ── Click row → fill form ────────────────────────────
    def on_select(event):
        selected = tree.focus()
        vals = tree.item(selected)['values']
        if vals:
            selected_id.set(vals[0])
            entries['Product Name'].delete(0, tk.END)
            entries['Product Name'].insert(0, vals[1])
            entries['Price'].delete(0, tk.END)
            entries['Price'].insert(0, vals[2])
            entries['Reorder Level'].delete(0, tk.END)
            entries['Reorder Level'].insert(0, vals[3])
            entries['Category ID'].delete(0, tk.END)
            # Category ID not shown in tree — leave blank for update
    tree.bind('<<TreeviewSelect>>', on_select)

    # ── Load Products ────────────────────────────────────
    def load():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.product_id, p.product_name, p.price,
                       p.reorder_level, c.category_name
                FROM Product p
                JOIN Category c ON p.category_id = c.category_id
            ''')
            tree.delete(*tree.get_children())
            for row in cursor.fetchall():
                tree.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror('Error', str(e))
        finally:
            conn.close()

    # ── VALIDATION HELPER ────────────────────────────────
    def validate_inputs(require_category=True):
        """
        Validates all form inputs before DB operation.
        Returns True if valid, False if invalid.
        """
        name = entries['Product Name'].get().strip()
        price = entries['Price'].get().strip()
        reorder = entries['Reorder Level'].get().strip()
        category = entries['Category ID'].get().strip()

        if not name:
            messagebox.showwarning('Validation Error',
                                   'Product Name cannot be empty!')
            entries['Product Name'].focus()
            return False

        if not price:
            messagebox.showwarning('Validation Error',
                                   'Price cannot be empty!')
            entries['Price'].focus()
            return False

        try:
            price_val = float(price)
            if price_val <= 0:
                messagebox.showwarning('Validation Error',
                                       'Price must be greater than 0!')
                entries['Price'].focus()
                return False
        except ValueError:
            messagebox.showwarning('Validation Error',
                                   'Price must be a valid number!')
            entries['Price'].focus()
            return False

        if not reorder:
            messagebox.showwarning('Validation Error',
                                   'Reorder Level cannot be empty!')
            entries['Reorder Level'].focus()
            return False

        try:
            int(reorder)
        except ValueError:
            messagebox.showwarning('Validation Error',
                                   'Reorder Level must be a whole number!')
            entries['Reorder Level'].focus()
            return False

        if require_category:
            if not category:
                messagebox.showwarning('Validation Error',
                                       'Category ID cannot be empty!\n'
                                       'Available: 1=Grains, 2=Sugar, '
                                       '3=Oils, 4=Pulses, 5=Spices')
                entries['Category ID'].focus()
                return False
            try:
                int(category)
            except ValueError:
                messagebox.showwarning('Validation Error',
                                       'Category ID must be a number!')
                entries['Category ID'].focus()
                return False

        return True

    # ── ADD PRODUCT ──────────────────────────────────────
    def add_product():
        if not validate_inputs(require_category=True):
            return
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO Product '
                '(product_name, price, reorder_level, category_id)'
                ' VALUES (%s, %s, %s, %s)',
                (entries['Product Name'].get().strip(),
                 float(entries['Price'].get().strip()),
                 int(entries['Reorder Level'].get().strip()),
                 int(entries['Category ID'].get().strip()))
            )
            conn.commit()

            # Also insert into Stock table with 0 quantity
            new_id = cursor.lastrowid
            cursor.execute(
                'INSERT INTO Stock (product_id, quantity) VALUES (%s, 0)',
                (new_id,)
            )
            conn.commit()

            messagebox.showinfo('Success',
                                'Product added successfully!\n'
                                'Stock entry created with 0 quantity.')
            clear_form()
            load()
        except Exception as e:
            messagebox.showerror('Failed to Add Product', str(e))
        finally:
            conn.close()

    # ── UPDATE PRODUCT ───────────────────────────────────
    def update_product():
        if selected_id.get() == 0:
            messagebox.showwarning('No Selection',
                                   'Please click a product row first!')
            return
        if not validate_inputs(require_category=True):
            return
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE Product SET product_name=%s, price=%s, '
                'reorder_level=%s, category_id=%s '
                'WHERE product_id=%s',
                (entries['Product Name'].get().strip(),
                 float(entries['Price'].get().strip()),
                 int(entries['Reorder Level'].get().strip()),
                 int(entries['Category ID'].get().strip()),
                 selected_id.get())
            )
            conn.commit()
            messagebox.showinfo('Success', 'Product updated successfully!')
            clear_form()
            load()
        except Exception as e:
            messagebox.showerror('Failed to Update Product', str(e))
        finally:
            conn.close()

    # ── DELETE PRODUCT ───────────────────────────────────
    def delete_product():
        if selected_id.get() == 0:
            messagebox.showwarning('No Selection',
                                   'Please click a product row first!')
            return

        product_name = entries['Product Name'].get()
        confirm = messagebox.askyesno(
            'Confirm Delete',
            f'Delete "{product_name}"?\n\n'
            'This will also delete:\n'
            '• Stock record\n'
            '• Reorder requests\n'
            '• Supplier mappings\n\n'
            'This cannot be undone!'
        )
        if not confirm:
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            pid = selected_id.get()

            # Step 1: Delete ReorderRequest first (child table)
            cursor.execute(
                'DELETE FROM ReorderRequest WHERE product_id = %s',
                (pid,)
            )

            # Step 2: Delete SupplierProduct mappings
            cursor.execute(
                'DELETE FROM SupplierProduct WHERE product_id = %s',
                (pid,)
            )

            # Step 3: Delete Stock record
            cursor.execute(
                'DELETE FROM Stock WHERE product_id = %s',
                (pid,)
            )

            # Step 4: Now safe to delete Product
            cursor.execute(
                'DELETE FROM Product WHERE product_id = %s',
                (pid,)
            )

            conn.commit()
            messagebox.showinfo('Success',
                                'Product deleted successfully!')
            clear_form()
            load()
        except Exception as e:
            conn.rollback()
            messagebox.showerror('Failed to Delete Product', str(e))
        finally:
            conn.close()

    # ── CLEAR FORM ───────────────────────────────────────
    def clear_form():
        for entry in entries.values():
            entry.delete(0, tk.END)
        selected_id.set(0)

    # ── BUTTONS ──────────────────────────────────────────
    btn_frame = tk.Frame(win, bg='#f0f4f8')
    btn_frame.pack(pady=8)

    btn_style = {'width': 12, 'font': ('Arial', 10, 'bold'),
                 'relief': tk.FLAT, 'cursor': 'hand2'}

    tk.Button(btn_frame, text='➕ Add',
              command=add_product,
              bg='#1D6A38', fg='white',
              **btn_style).pack(side=tk.LEFT, padx=5)

    tk.Button(btn_frame, text='✏️ Update',
              command=update_product,
              bg='#2E75B6', fg='white',
              **btn_style).pack(side=tk.LEFT, padx=5)

    tk.Button(btn_frame, text='🗑️ Delete',
              command=delete_product,
              bg='#C00000', fg='white',
              **btn_style).pack(side=tk.LEFT, padx=5)

    tk.Button(btn_frame, text='🔄 Refresh',
              command=load,
              bg='#595959', fg='white',
              **btn_style).pack(side=tk.LEFT, padx=5)

    tk.Button(btn_frame, text='✖ Clear',
              command=clear_form,
              bg='#C55A11', fg='white',
              **btn_style).pack(side=tk.LEFT, padx=5)

    # Category hint label
    tk.Label(win,
             text='Category IDs: 1=Grains & Rice  '
                  '2=Sugar & Sweeteners  3=Oils & Ghee  '
                  '4=Pulses & Lentils  5=Spices',
             font=('Arial', 9), fg='#595959',
             bg='#f0f4f8').pack(pady=3)

    # F5 to refresh
    win.bind('<F5>', lambda e: load())

    # Load data on open
    load()