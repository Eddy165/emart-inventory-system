# app/dashboard.py
import tkinter as tk
from tkinter import messagebox
import mysql.connector
from app.db_connect import get_connection

# ← REMOVED the wrong import from top


class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('EMart Grocery Shop - Inventory System')
        self.geometry('1100x700')
        self.configure(bg='#f0f4f8')
        self.resizable(True, True)

        self._build_header()
        self._build_navbar()
        self._build_summary_tiles()
        self._build_statusbar()
        self.refresh_summary()

    def _build_header(self):
        header = tk.Frame(self, bg='#1F4E79', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(
            header,
            text='EMart Grocery Shop - Inventory System',
            font=('Arial', 18, 'bold'),
            fg='white',
            bg='#1F4E79'
        ).pack(expand=True)

    def _build_navbar(self):
        nav = tk.Frame(self, bg='#f0f4f8', pady=20)
        nav.pack(fill=tk.X)
        buttons = [
            ('Products',     self._open_products),
            ('Suppliers',    self._open_suppliers),
            ('Stock',        self._open_stock),
            ('Billing',      self._open_billing),
            ('Reports',      self._open_reports),
            ('📊 View Data', self._open_data_viewer),
        ]
        for text, command in buttons:
            tk.Button(
                nav,
                text=text,
                command=command,
                bg='#2E75B6',
                fg='white',
                width=14,
                height=3,
                font=('Arial', 12, 'bold'),
                relief=tk.FLAT,
                cursor='hand2'
            ).pack(side=tk.LEFT, padx=12)

    def _build_summary_tiles(self):
        body = tk.Frame(self, bg='#f0f4f8', pady=40)
        body.pack(fill=tk.BOTH, expand=True)

        self.products_tile  = self._create_tile(body, '#2E75B6', '0 Products')
        self.low_stock_tile = self._create_tile(body, '#C55A11', '0 Low Stock Alerts')
        self.revenue_tile   = self._create_tile(body, '#1D6A38', 'Rs.0.00 Today')

        self.products_tile.pack(side=tk.LEFT,  expand=True, padx=16)
        self.low_stock_tile.pack(side=tk.LEFT, expand=True, padx=16)
        self.revenue_tile.pack(side=tk.LEFT,   expand=True, padx=16)

        tk.Button(
            body,
            text='Refresh Summary',
            command=self.refresh_summary,
            bg='#595959',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.BOTTOM, pady=20)

    def _create_tile(self, parent, bg, text):
        tile = tk.Frame(parent, bg=bg, width=300, height=120)
        tile.pack_propagate(False)
        label = tk.Label(
            tile, text=text, bg=bg,
            fg='white', font=('Arial', 14, 'bold')
        )
        label.pack(expand=True)
        tile.label = label
        return tile

    def _build_statusbar(self):
        status = tk.Frame(self, bg='#1F4E79', height=28)
        status.pack(side=tk.BOTTOM, fill=tk.X)
        status.pack_propagate(False)
        tk.Label(
            status,
            text='Connected to emart_db | MySQL 8.0 | Ready',
            bg='#1F4E79',
            fg='white',
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=12)

    def refresh_summary(self):
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM Product')
            product_count = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM vw_LowStockItems')
            low_stock_count = cursor.fetchone()[0]

            cursor.execute(
                'SELECT IFNULL(SUM(total_amount), 0) '
                'FROM Bill WHERE DATE(bill_date)=CURDATE()'
            )
            today_revenue = float(cursor.fetchone()[0] or 0)

            self.products_tile.label.config(
                text=f'{product_count} Products')
            self.low_stock_tile.label.config(
                text=f'{low_stock_count} Low Stock Alerts')
            self.revenue_tile.label.config(
                text=f'Rs.{today_revenue:.2f} Today')

        except mysql.connector.Error as err:
            messagebox.showerror('Database Error', str(err))
        except Exception as err:
            messagebox.showerror('Error', str(err))
        finally:
            if conn is not None:
                conn.close()

    def _open_products(self):
        from app.product_form import open_product_window
        open_product_window(self)

    def _open_suppliers(self):
        from app.supplier_form import open_supplier_window
        open_supplier_window(self)

    def _open_stock(self):
        from app.stock_form import open_stock_window
        open_stock_window(self)

    def _open_billing(self):
        from app.billing_form import open_billing_window
        open_billing_window(self)

    def _open_reports(self):
        from app.reports import open_reports_window
        open_reports_window(self)

    def _open_data_viewer(self):
        from app.data_viewer import open_data_viewer
        open_data_viewer(self)


if __name__ == '__main__':
    app = Dashboard()
    app.mainloop()