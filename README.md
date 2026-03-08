# 🛒 EMart Grocery Shop — Inventory Management System

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-FF6F00?style=for-the-badge)
![License](https://img.shields.io/badge/License-Academic-green?style=for-the-badge)

A fully functional, enterprise-grade **GUI-based desktop application** built with **Python Tkinter** and **MySQL 8.0** for managing grocery inventory, billing, supplier tracking, and automated end-of-day batch processing.

---

## 📌 Table of Contents

- [Project Overview](#-project-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Database Design](#-database-design)
- [Enterprise Database Features](#-enterprise-database-features)
- [ACID Properties](#-acid-properties-demonstrated)
- [Installation & Setup](#-installation--setup)
- [Running the Application](#-running-the-application)
- [Module Walkthrough](#-module-walkthrough)
- [Screenshots](#-screenshots)
- [Future Enhancements](#-future-enhancements)
- [References](#-references)

---

## 🧾 Project Overview

Retail grocery shops like **EMart** face major operational challenges when relying on manual or paper-based inventory tracking — frequent stockouts, billing errors, no supplier records, and no automated reporting.

This project addresses all of these by delivering a complete **Inventory Management System** that:

- Digitizes all core grocery operations
- Enforces data integrity at the database level
- Implements enterprise-grade SQL features (triggers, stored procedures, views, functions)
- Demonstrates all four **ACID properties** through annotated transaction scripts
- Provides an intuitive GUI for non-technical grocery staff

---

## ✨ Features

### 🗃️ Core Functional Features
| Feature | Description |
|---|---|
| Product Management | Add, edit, delete, search products with category assignment |
| Category Management | Create and manage product categories |
| Supplier Management | Maintain supplier records and product-supplier mappings |
| Stock Tracking | Real-time stock quantity view with last-updated timestamp |
| Low Stock Alerts | Auto-flag products below reorder level via database view |
| Customer Billing | Generate itemized bills with automatic stock deduction |
| Customer Management | Register customers and track loyalty points |
| EOD Batch Processing | Automated stored procedure to flag reorder requests at day end |
| Audit Logging | Trigger-based automatic logging of all stock changes |
| Sales Reports | Daily revenue, total bills, and product-wise sales |
| Stock Valuation | SQL function to compute total stock value per product |
| ACID Transactions | All billing operations wrapped in atomic DB transactions |

### 🏢 Enterprise Database Features
- ✅ **3 Database Views** — Low Stock Alerts, Daily Sales, Product Sales
- ✅ **1 Audit Trigger** — Auto-logs every stock change to `StockAuditLog`
- ✅ **2 SQL Functions** — Stock valuation & loyalty discount calculation
- ✅ **2 Stored Procedures** — Billing transaction (`sp_GenerateBill`) & EOD batch (`sp_EOD_Reorder`)
- ✅ **Full ACID Compliance** — With annotated rollback demo scripts

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend / GUI | Python 3.10+ with Tkinter & ttk |
| Backend Database | MySQL 8.0 Community Edition |
| DB Connector | `mysql-connector-python` |
| IDE | VS Code / PyCharm |
| DB Design Tool | draw.io, dbdiagram.io |
| Version Control | Git + GitHub |

---

## 📁 Project Structure

```
emart_project/
│
├── main.py                   # 🚀 Entry point — run this to launch the app
├── config.ini                # 🔐 DB credentials (excluded from Git)
├── config.ini.example        # ✅ Safe template to share (no real password)
├── requirements.txt          # pip dependencies
├── README.md                 # This file
├── .gitignore                # Excludes config.ini and cache files
│
├── sql/
│   ├── 01_schema.sql         # CREATE TABLE scripts (all 10 tables)
│   ├── 02_sample_data.sql    # INSERT sample data
│   ├── 03_views.sql          # 3 database views
│   ├── 04_trigger.sql        # Audit trigger
│   ├── 05_functions.sql      # 2 SQL functions
│   ├── 06_procedures.sql     # 2 stored procedures
│   └── 07_acid_demo.sql      # ACID property demonstration scripts
│
└── app/
    ├── __init__.py           # Makes app a Python package
    ├── db_connect.py         # Database connection utility
    ├── dashboard.py          # Main home screen with summary tiles
    ├── product_form.py       # Product & Category CRUD module
    ├── supplier_form.py      # Supplier management module
    ├── stock_form.py         # Stock tracking & audit log viewer
    ├── billing_form.py       # Customer billing (calls sp_GenerateBill)
    └── reports.py            # Reports dashboard & EOD batch trigger
```

---

## 🗄️ Database Design

### Entity-Relationship Summary

The database is normalized to **Third Normal Form (3NF)** and consists of **10 tables**:

| # | Table | Purpose |
|---|---|---|
| 1 | `Category` | Product categories |
| 2 | `Product` | Items sold in the shop |
| 3 | `Supplier` | Vendor records |
| 4 | `SupplierProduct` | Many-to-Many junction: supplier ↔ product |
| 5 | `Stock` | Real-time quantity per product (1:1 with Product) |
| 6 | `Customer` | Walk-in customer records with loyalty points |
| 7 | `Bill` | Bill header per transaction |
| 8 | `BillItem` | Line items inside each bill |
| 9 | `StockAuditLog` | Auto-populated by trigger on every stock change |
| 10 | `ReorderRequest` | Auto-populated by EOD stored procedure |

### Key Relationships
- `Category` → `Product` : **One-to-Many**
- `Supplier` ↔ `Product` : **Many-to-Many** (via `SupplierProduct`)
- `Product` → `Stock` : **One-to-One**
- `Customer` → `Bill` : **One-to-Many**
- `Bill` → `BillItem` : **One-to-Many**

---

## ⚙️ Enterprise Database Features

### 📊 Views
```sql
vw_LowStockItems   -- Products where quantity < reorder_level
vw_DailySales      -- Total bills and revenue grouped by date
vw_ProductSales    -- Total units sold and revenue per product
```

### 🔔 Trigger
```sql
trg_StockAudit     -- AFTER UPDATE on Stock → auto-inserts into StockAuditLog
```

### 🔧 Functions
```sql
fn_GetStockValue(product_id)                          -- Returns price × quantity
fn_ApplyLoyaltyDiscount(bill_total, loyalty_points)   -- Returns discounted total
```

### 📦 Stored Procedures
```sql
sp_GenerateBill(customer_id, payment_mode, product_id, qty, OUT bill_id, OUT message)
-- Wraps all billing operations in one ACID transaction

sp_EOD_Reorder()
-- Scans all products, flags low-stock ones for reorder (skips duplicates)
```

---

## 🔒 ACID Properties Demonstrated

| Property | Guarantee | EMart Example | SQL Mechanism |
|---|---|---|---|
| **Atomicity** | All-or-nothing | Bill + BillItem + Stock deduct all succeed or all rollback | `START TRANSACTION / COMMIT / ROLLBACK` |
| **Consistency** | Valid state before & after | Stock quantity can never go below 0 | `CHECK constraint` on `Stock.quantity` |
| **Isolation** | Concurrent transactions don't interfere | Two billing clerks don't see each other's uncommitted deductions | `REPEATABLE READ` isolation level |
| **Durability** | Committed data persists forever | A committed bill persists through server restart | InnoDB Write-Ahead Log (WAL) |

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10 or higher → https://python.org/downloads
- MySQL 8.0 Community Server → https://dev.mysql.com/downloads/mysql/
- MySQL Workbench (optional but recommended) → https://dev.mysql.com/downloads/workbench/
- VS Code → https://code.visualstudio.com

### Step 1 — Clone the Repository
```bash
git clone https://github.com/Eddy165/emart-inventory-system.git
cd emart-inventory-system
```

### Step 2 — Install Python Dependencies
```bash
pip install mysql-connector-python
```

### Step 3 — Configure Database Credentials
Create a `config.ini` file in the project root (use `config.ini.example` as template):
```ini
[mysql]
host = localhost
user = root
password = your_mysql_root_password
database = emart_db
```
> ⚠️ `config.ini` is listed in `.gitignore` and will never be pushed to GitHub.

### Step 4 — Set Up the Database
Open **MySQL Workbench** and run the SQL scripts in this exact order:
```
sql/01_schema.sql        ← Creates all 10 tables
sql/02_sample_data.sql   ← Inserts sample categories, products, stock
sql/03_views.sql         ← Creates 3 reporting views
sql/04_trigger.sql       ← Creates audit trigger
sql/05_functions.sql     ← Creates 2 SQL functions
sql/06_procedures.sql    ← Creates 2 stored procedures
sql/07_acid_demo.sql     ← Optional: run to see ACID demo
```

### Step 5 — Verify Connection
```bash
python app/db_connect.py
# Expected output: ✅ Database connection successful!
```

---

## ▶️ Running the Application

```bash
python main.py
```

The **EMart Dashboard** will open with navigation buttons to all modules and live summary tiles showing total products, low-stock alerts, and today's revenue.

---

## 🧩 Module Walkthrough

| Module | File | What It Does |
|---|---|---|
| 🏠 Dashboard | `dashboard.py` | Home screen with live summary tiles and navigation |
| 📦 Products | `product_form.py` | Add/Edit/Delete/Search products with Treeview table |
| 🚚 Suppliers | `supplier_form.py` | Manage supplier records and product mappings |
| 📊 Stock | `stock_form.py` | View real-time stock, update quantities, view audit log |
| 🧾 Billing | `billing_form.py` | Generate bills via `sp_GenerateBill` stored procedure |
| 📈 Reports | `reports.py` | Low stock alerts, daily sales, EOD batch button |

---

## 📸 Screenshots

> *(Insert screenshots of each module here after running the application)*

| Screen | Description |
|---|---|
| Figure 1 | Dashboard — Home screen with summary tiles |
| Figure 2 | Product Management — CRUD form with Treeview |
| Figure 3 | Stock Management — Low stock items highlighted in red |
| Figure 4 | Billing Module — Customer selection and bill cart |
| Figure 5 | Reports Module — Low stock alert view and EOD button |

---

## 🔮 Future Enhancements

- [ ] **Barcode Scanner Integration** — USB barcode scanner support in billing
- [ ] **GST Computation** — 5%, 12%, 18% tax slabs based on product category
- [ ] **Role-Based Login** — Manager and Billing Staff access levels with hashed passwords
- [ ] **Email/SMS Alerts** — Auto-email daily reports and SMS low-stock alerts
- [ ] **Supplier Auto-Email** — Send reorder requests to suppliers when EOD batch runs
- [ ] **Web Interface** — Migrate Tkinter GUI to Flask or Django for multi-device access
- [ ] **Analytics Dashboard** — Revenue trend charts using Matplotlib or Chart.js
- [ ] **Backup & Restore** — Built-in `mysqldump` integration for scheduled backups

---

## ⚠️ Known Limitations

- Single-user desktop application — does not support concurrent multi-user access in Tkinter form
- `sp_GenerateBill` handles single-product billing per call — a production version would process a full cart atomically
- No built-in backup/restore — database admins must manage backups manually via `mysqldump`

---

## 👨‍💻 Author

**Edwin Mario. A**  

---

