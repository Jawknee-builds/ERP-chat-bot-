import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "dummy.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            created_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL,
            currency TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id TEXT PRIMARY KEY,
            customer_id TEXT,
            total_amount REAL,
            status TEXT,
            issued_at TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id TEXT,
            product_id TEXT,
            quantity INTEGER,
            unit_price REAL,
            FOREIGN KEY (invoice_id) REFERENCES invoices (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Check if empty, then seed
    cursor.execute('SELECT COUNT(*) FROM invoice_items')
    if cursor.fetchone()[0] == 0:
        cursor.execute("DELETE FROM customers") # Wipe old to reseed clean relations
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM invoices")

        customers = [
            ("cust_1", "Acme Corp", "contact@acme.com", datetime.utcnow().isoformat() + "Z"),
            ("cust_2", "Global Tech", "info@globaltech.com", datetime.utcnow().isoformat() + "Z"),
            ("cust_3", "Stark Industries", "tony@stark.com", datetime.utcnow().isoformat() + "Z")
        ]
        cursor.executemany('INSERT INTO customers VALUES (?, ?, ?, ?)', customers)
        
        products = [
            ("prod_1", "Enterprise ERP License", 5000.00, "USD"),
            ("prod_2", "Consulting Hours", 1500.00, "USD"),
            ("prod_3", "Cloud Hosting", 999.00, "USD")
        ]
        cursor.executemany('INSERT INTO products VALUES (?, ?, ?, ?)', products)
        
        invoices = [
            ("inv_1", "cust_1", 5000.00, "PAID", datetime.utcnow().isoformat() + "Z"),
            ("inv_2", "cust_2", 1500.00, "UNPAID", datetime.utcnow().isoformat() + "Z"),
            ("inv_3", "cust_3", 1998.00, "PENDING", datetime.utcnow().isoformat() + "Z") # 2 * 999
        ]
        cursor.executemany('INSERT INTO invoices VALUES (?, ?, ?, ?, ?)', invoices)

        invoice_items = [
            ("inv_1", "prod_1", 1, 5000.00),
            ("inv_2", "prod_2", 1, 1500.00),
            ("inv_3", "prod_3", 2, 999.00)
        ]
        cursor.executemany('INSERT INTO invoice_items (invoice_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)', invoice_items)
        
    conn.commit()
    conn.close()

# Initialize when module loads so data is ready
init_db()
