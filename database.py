import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "calc_business.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabela de Usuários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        role TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Tabela de Produtos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        category TEXT,
        supplier TEXT,
        c_base REAL NOT NULL,
        tax_pct REAL NOT NULL,
        marketplace_pct REAL NOT NULL,
        shipping_fixed REAL NOT NULL,
        margin_desired_pct REAL NOT NULL,
        min_stock INTEGER DEFAULT 5,
        current_stock INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Tabela de Movimentações de Estoque
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_movements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        type TEXT NOT NULL, -- 'ENTRADA' ou 'SAIDA'
        quantity INTEGER NOT NULL,
        user TEXT NOT NULL,
        notes TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    """)

    # Tabela de Trilha de Auditoria
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user TEXT NOT NULL,
        action TEXT NOT NULL,
        details TEXT
    )
    """)

    conn.commit()
    conn.close()

def log_audit(user: str, action: str, details: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO audit_logs (user, action, details) VALUES (?, ?, ?)",
        (user, action, details)
    )
    conn.commit()
    conn.close()

def get_audit_logs():
    conn = get_connection()
    df = pd.read_sql_query("SELECT timestamp as 'Data/Hora', user as 'Usuário', action as 'Ação', details as 'Detalhes' FROM audit_logs ORDER BY id DESC", conn)
    conn.close()
    return df

def get_all_products():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM products ORDER BY name ASC", conn)
    conn.close()
    return df

def insert_product(data: dict, username: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO products (sku, name, category, supplier, c_base, tax_pct, marketplace_pct, shipping_fixed, margin_desired_pct, min_stock, current_stock)
    VALUES (:sku, :name, :category, :supplier, :c_base, :tax_pct, :marketplace_pct, :shipping_fixed, :margin_desired_pct, :min_stock, :current_stock)
    """, data)
    conn.commit()
    conn.close()
    log_audit(username, "Cadastro de Produto", f"SKU: {data['sku']} | Nome: {data['name']}")

def update_stock(product_id: int, movement_type: str, qty: int, username: str, notes: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    
    if movement_type == "ENTRADA":
        cursor.execute("UPDATE products SET current_stock = current_stock + ? WHERE id = ?", (qty, product_id))
    elif movement_type == "SAIDA":
        cursor.execute("UPDATE products SET current_stock = current_stock - ? WHERE id = ?", (qty, product_id))
    
    cursor.execute("""
    INSERT INTO stock_movements (product_id, type, quantity, user, notes)
    VALUES (?, ?, ?, ?, ?)
    """, (product_id, movement_type, qty, username, notes))
    
    conn.commit()
    
    cursor.execute("SELECT sku, name FROM products WHERE id = ?", (product_id,))
    prod = cursor.fetchone()
    conn.close()
    
    log_audit(username, f"Ajuste de Estoque ({movement_type})", f"Produto: {prod['name']} (SKU: {prod['sku']}) | Qtd: {qty} | Obs: {notes}")