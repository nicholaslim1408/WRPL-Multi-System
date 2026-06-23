import streamlit as st
import pandas as pd
import datetime
import json
import hashlib
import mysql.connector
from mysql.connector import Error
import os

st.set_page_config(
    page_title="Panen.net | Seller Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    body {
        background: linear-gradient(180deg, #f5fdf4 0%, #ecf9ee 45%, #ffffff 100%);
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
        margin: 0 auto;
    }
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .top-bar h1 {
        margin: 0;
        font-size: 2rem;
        color: #0f5132;
        letter-spacing: .04em;
    }
    .top-bar p {
        margin: 0;
        color: #14532d;
        font-size: 0.95rem;
    }
    .hero-card {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(16, 185, 129, 0.18);
        border-radius: 32px;
        padding: 2.4rem;
        box-shadow: 0 24px 60px rgba(15, 23, 42, 0.08);
        margin-bottom: 2rem;
    }
    .hero-card h2 {
        margin: 0;
        font-size: 3rem;
        color: #0f5132;
        line-height: 1.05;
    }
    .hero-card p {
        margin-top: 1rem;
        font-size: 1.2rem;
        color: #166534;
        line-height: 1.7;
    }
    .hero-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-top: 2rem;
    }
    .hero-buttons a,
    .hero-buttons button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.95rem 1.6rem;
        border-radius: 999px;
        font-weight: 700;
        text-decoration: none;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .hero-buttons a:hover,
    .hero-buttons button:hover {
        transform: translateY(-1px);
        box-shadow: 0 14px 24px rgba(15, 23, 42, 0.12);
    }
    .hero-buttons .primary {
        background: #047857;
        color: white;
        border: 1px solid transparent;
    }
    .hero-buttons .secondary {
        background: white;
        color: #0f5132;
        border: 1px solid rgba(15, 23, 42, 0.08);
    }
    .cards-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 1.25rem;
        margin-top: 1.5rem;
    }
    .feature-card {
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid rgba(16, 185, 129, 0.15);
        border-radius: 28px;
        padding: 1.75rem;
        min-height: 220px;
    }
    .feature-card h3 {
        margin-top: 0;
        color: #047857;
        font-size: 1.2rem;
    }
    .feature-card p {
        color: #334d3d;
        margin-top: 0.75rem;
        line-height: 1.7;
    }
    .section-title {
        text-align: center;
        margin-top: 3rem;
        margin-bottom: 1rem;
    }
    .section-title h3 {
        margin: 0;
        color: #0f5132;
        font-size: 2rem;
    }
    .architecture-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1.25rem;
        margin-top: 1rem;
    }
    .architecture-card {
        background: white;
        border: 1px solid rgba(16, 185, 129, 0.16);
        border-radius: 24px;
        padding: 1.5rem;
        min-height: 180px;
    }
    .architecture-card h4 {
        margin: 0 0 0.75rem;
        color: #14532d;
        font-size: 1.1rem;
    }
    .architecture-card small {
        color: #4b4b4b;
    }
    .architecture-card p {
        margin: 0.85rem 0 0;
        color: #334d3d;
        line-height: 1.6;
    }
    .stButton>button {
        border-radius: 999px !important;
        padding: 0.95rem 1.4rem !important;
        font-weight: 700 !important;
        background: #047857 !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 12px 24px rgba(4, 120, 87, 0.18);
    }
    .stButton>button:hover {
        background: #065f46 !important;
    }
    .hero-button-panel {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 1rem;
        margin-top: 2rem;
    }
    .hero-button-panel .button-spacer {
        grid-column: span 1;
    }
    .hero-button-panel .button-center {
        grid-column: span 3;
        display: flex;
        justify-content: center;
        gap: 1rem;
    }
    .stTextInput>div>div>input,
    .stTextInput>div>div>textarea,
    .stSelectbox>div>div>div>div,
    .stNumberInput>div>div>input {
        border-radius: 16px !important;
    }
    </style>
""", unsafe_allow_html=True)

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            option_files=os.path.expanduser('~/.my.cnf'),
            database='panennet'
        )
        return connection
    except Error as e:
        st.error(f"Database connection error: {e}")
        return None
    
def init_database():
    conn = get_db_connection()
    if conn is None:
        return False
    
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sellers (
                seller_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                nama_toko VARCHAR(100) NOT NULL,
                kode_seller VARCHAR(50) UNIQUE NOT NULL,
                rating FLOAT DEFAULT 0,
                jumlah_transaksi INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INT AUTO_INCREMENT PRIMARY KEY,
                seller_id INT NOT NULL,
                id_produk VARCHAR(50) UNIQUE NOT NULL,
                nama_produk VARCHAR(100) NOT NULL,
                kategori VARCHAR(50),
                harga_modal INT,
                harga_jual INT,
                stok INT,
                berat INT,
                deskripsi TEXT,
                status VARCHAR(20) DEFAULT 'Aktif',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INT AUTO_INCREMENT PRIMARY KEY,
                seller_id INT NOT NULL,
                order_code VARCHAR(50) UNIQUE NOT NULL,
                pembeli VARCHAR(100),
                email VARCHAR(100),
                no_telepon VARCHAR(20),
                alamat_pengiriman TEXT,
                kota VARCHAR(100),
                provinsi VARCHAR(100),
                kode_pos VARCHAR(10),
                berat_total INT,
                total INT,
                status VARCHAR(50),
                shipping_status VARCHAR(50) DEFAULT 'Belum Diproses',
                bank VARCHAR(50),
                tanggal_order DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stok_log (
                log_id INT AUTO_INCREMENT PRIMARY KEY,
                seller_id INT NOT NULL,
                product_id INT,
                produk_nama VARCHAR(100),
                tipe VARCHAR(20),
                jumlah INT,
                alasan VARCHAR(100),
                stok_akhir INT,
                tanggal TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INT AUTO_INCREMENT PRIMARY KEY,
                seller_id INT NOT NULL,
                nama VARCHAR(100),
                email VARCHAR(100),
                no_telepon VARCHAR(20),
                alamat VARCHAR(255),
                total_pembelian INT DEFAULT 0,
                jumlah_pesanan INT DEFAULT 0,
                last_order DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        st.error(f"Database initialization error: {e}")
        return False

init_database()

def load_seller_data(seller_id):
    conn = get_db_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id_produk AS ID, nama_produk AS `Nama Produk`, kategori AS Kategori,
                   harga_modal AS `Harga Modal`, harga_jual AS `Harga Jual`, stok AS Stok,
                   berat AS `Berat (gram)`, deskripsi AS Deskripsi, status AS Status
            FROM products WHERE seller_id = %s
        """, (seller_id,))
        rows = cursor.fetchall()
        st.session_state.products = pd.DataFrame(rows) if rows else pd.DataFrame({
            "ID": [], "Nama Produk": [], "Kategori": [], "Harga Modal": [],
            "Harga Jual": [], "Stok": [], "Berat (gram)": [], "Deskripsi": [], "Status": []
        })

        cursor.execute("""
            SELECT order_code AS `Order ID`, pembeli AS Pembeli, email AS Email,
                   no_telepon AS `No. Telepon`, alamat_pengiriman AS `Alamat Pengiriman`,
                   kota AS Kota, provinsi AS Provinsi, kode_pos AS `Kode Pos`,
                   berat_total AS `Berat Total`, total AS Total, status AS Status,
                   shipping_status AS `Status Pengiriman`, bank AS Bank, tanggal_order AS `Tanggal Order`
            FROM orders WHERE seller_id = %s
        """, (seller_id,))
        rows = cursor.fetchall()
        st.session_state.orders = pd.DataFrame(rows) if rows else pd.DataFrame({
            "Order ID": [], "Pembeli": [], "Email": [], "No. Telepon": [],
            "Alamat Pengiriman": [], "Kota": [], "Provinsi": [], "Kode Pos": [], "Berat Total": [],
            "Total": [], "Status": [], "Status Pengiriman": [], "Bank": [], "Tanggal Order": []
        })

        if not st.session_state.orders.empty:
            st.session_state.orders['Tanggal Order'] = pd.to_datetime(st.session_state.orders['Tanggal Order'], errors='coerce')
            trans = st.session_state.orders.dropna(subset=['Tanggal Order']).copy()
            if not trans.empty:
                trans['Tanggal'] = trans['Tanggal Order'].dt.normalize()
                tx = trans.groupby('Tanggal', as_index=False)['Total'].sum()
                st.session_state.transaction_history = tx.rename(columns={'Total': 'Penjualan'})

        if st.session_state.customers.empty and not st.session_state.orders.empty:
            ords = st.session_state.orders.copy()
            if 'Tanggal Order' in ords.columns:
                ords['Tanggal Order'] = pd.to_datetime(ords['Tanggal Order'], errors='coerce')
            ag = ords.groupby('Pembeli').agg({
                'Total': 'sum',
                'Order ID': 'count',
                'Tanggal Order': 'max'
            }).reset_index()
            ag.rename(columns={'Pembeli': 'Nama', 'Total': 'Total Pembelian', 'Order ID': 'Jumlah Pesanan', 'Tanggal Order': 'Last Order'}, inplace=True)
            ag['ID'] = [f"CUST-{i+1:03d}" for i in range(len(ag))]
            ag['Email'] = ''
            ag['No. Telepon'] = ''
            ag['Alamat'] = ''
            st.session_state.customers = ag[['ID', 'Nama', 'Email', 'No. Telepon', 'Alamat', 'Total Pembelian', 'Jumlah Pesanan', 'Last Order']]

        cursor.execute("""
            SELECT tanggal AS Tanggal, produk_nama AS Produk, tipe AS Tipe, jumlah AS Jumlah,
                   alasan AS Alasan, stok_akhir AS `Stok Akhir`
            FROM stok_log WHERE seller_id = %s ORDER BY tanggal DESC LIMIT 1000
        """, (seller_id,))
        rows = cursor.fetchall()
        st.session_state.stok_log = pd.DataFrame(rows) if rows else pd.DataFrame({
            "Tanggal": [], "Produk": [], "Tipe": [], "Jumlah": [], "Alasan": [], "Stok Akhir": []
        })

        cursor.execute("""
            SELECT customer_id AS ID, nama AS Nama, email AS Email, no_telepon AS `No. Telepon`,
                   alamat AS Alamat, total_pembelian AS `Total Pembelian`, jumlah_pesanan AS `Jumlah Pesanan`, last_order AS `Last Order`
            FROM customers WHERE seller_id = %s
        """, (seller_id,))
        rows = cursor.fetchall()
        st.session_state.customers = pd.DataFrame(rows) if rows else pd.DataFrame({
            "ID": [], "Nama": [], "Email": [], "No. Telepon": [], "Alamat": [],
            "Total Pembelian": [], "Jumlah Pesanan": [], "Last Order": []
        })

        cursor.close()
        conn.close()
        return True
    except Error as e:
        st.error(f"Error loading seller data: {e}")
        return False

def save_stock_change(seller_id, id_produk, tipe, jumlah, alasan):
    conn = get_db_connection()
    if conn is None:
        st.error("Koneksi database gagal saat menyimpan stok")
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT product_id, nama_produk FROM products WHERE seller_id=%s AND id_produk=%s", (seller_id, id_produk))
        prod = cursor.fetchone()
        if not prod:
            cursor.close()
            conn.close()
            st.error("Produk tidak ditemukan di database")
            return False
        product_id = prod[0]
        produk_nama = prod[1]

        matching = st.session_state.products[st.session_state.products['ID'] == id_produk]
        if len(matching) == 0:
            st.error("Produk tidak ditemukan di session state")
            return False
        stok_akhir = int(matching.iloc[0]['Stok'])

        cursor.execute("UPDATE products SET stok = %s WHERE product_id = %s", (stok_akhir, product_id))

        cursor.execute("""
            INSERT INTO stok_log (seller_id, product_id, produk_nama, tipe, jumlah, alasan, stok_akhir)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (seller_id, product_id, produk_nama, tipe, jumlah, alasan, stok_akhir))

        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        st.error(f"Error saving stock change: {e}")
        return False

def update_order_status_db(seller_id, order_code, new_status):
    conn = get_db_connection()
    if conn is None:
        st.error("Koneksi database gagal saat update order")
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET status = %s WHERE seller_id = %s AND order_code = %s", (new_status, seller_id, order_code))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        st.error(f"Error updating order status: {e}")
        return False

def save_product_update(seller_id, id_produk, row_data: dict):
    conn = get_db_connection()
    if conn is None:
        st.error("Koneksi database gagal saat menyimpan produk")
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT product_id FROM products WHERE seller_id=%s AND id_produk=%s", (seller_id, id_produk))
        prod = cursor.fetchone()
        if not prod:
            cursor.close()
            conn.close()
            st.error("Produk tidak ditemukan di database")
            return False
        product_id = prod[0]

        fields = []
        params = []
        mapping = {
            'Nama Produk': 'nama_produk',
            'Kategori': 'kategori',
            'Harga Modal': 'harga_modal',
            'Harga Jual': 'harga_jual',
            'Stok': 'stok',
            'Berat (gram)': 'berat',
            'Status': 'status'
        }
        for k, v in mapping.items():
            if k in row_data:
                fields.append(f"{v} = %s")
                params.append(row_data[k])

        if fields:
            params.append(product_id)
            sql = f"UPDATE products SET {', '.join(fields)} WHERE product_id = %s"
            cursor.execute(sql, tuple(params))
            conn.commit()

        cursor.close()
        conn.close()
        return True
    except Error as e:
        st.error(f"Error saving product update: {e}")
        return False

def add_product_db(seller_id, product):
    conn = get_db_connection()
    if conn is None:
        st.error("Koneksi database gagal saat menambah produk")
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (seller_id, id_produk, nama_produk, kategori, harga_modal, harga_jual, stok, berat, deskripsi, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            seller_id, product['ID'], product['Nama Produk'], product['Kategori'], int(product['Harga Modal']),
            int(product['Harga Jual']), int(product['Stok']), int(product['Berat (gram)']), product.get('Deskripsi', ''), product.get('Status', 'Aktif')
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        st.error(f"Error adding product: {e}")
        return False

def delete_product_db(seller_id, id_produk):
    conn = get_db_connection()
    if conn is None:
        st.error("Koneksi database gagal saat menghapus produk")
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE seller_id=%s AND id_produk=%s", (seller_id, id_produk))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        st.error(f"Error deleting product: {e}")
        return False

def add_order_db(seller_id, order):
    conn = get_db_connection()
    if conn is None:
        st.error("Koneksi database gagal saat menambah order")
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (seller_id, order_code, pembeli, email, no_telepon, alamat_pengiriman, kota, provinsi, kode_pos, berat_total, total, status, shipping_status, bank, tanggal_order)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            seller_id, order['Order ID'], order['Pembeli'], order.get('Email',''), order.get('No. Telepon',''),
            order.get('Alamat Pengiriman',''), order.get('Kota',''), order.get('Provinsi',''), order.get('Kode Pos',''),
            int(order.get('Berat Total',0)), int(order['Total']), order.get('Status','Menunggu Bayar'),
            order.get('Status Pengiriman','Belum Diproses'), order.get('Bank',''), order.get('Tanggal Order')
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        st.error(f"Error adding order: {e}")
        return False

def add_customer_db(seller_id, customer):
    conn = get_db_connection()
    if conn is None:
        st.error("Koneksi database gagal saat menambah pelanggan")
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO customers (seller_id, nama, email, no_telepon, alamat, total_pembelian, jumlah_pesanan, last_order)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            seller_id, customer['Nama'], customer.get('Email',''), customer.get('No. Telepon',''), customer.get('Alamat',''), int(customer.get('Total Pembelian',0)), int(customer.get('Jumlah Pesanan',0)), customer.get('Last Order')
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        st.error(f"Error adding customer: {e}")
        return False

def delete_customer_db(seller_id, customer_id):
    conn = get_db_connection()
    if conn is None:
        st.error("Koneksi database gagal saat menghapus pelanggan")
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM customers WHERE seller_id=%s AND customer_id=%s", (seller_id, customer_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        st.error(f"Error deleting customer: {e}")
        return False

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_seller(username, password, email, nama_toko):
    conn = get_db_connection()
    if conn is None:
        return False, "Koneksi database gagal"
    
    try:
        cursor = conn.cursor()
        hashed_password = hash_password(password)
        kode_seller = f"seller_sel{username[:3].upper()}"
        
        cursor.execute("""
            INSERT INTO sellers (username, password, email, nama_toko, kode_seller)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, hashed_password, email, nama_toko, kode_seller))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Registrasi berhasil! Silakan login."
    except Error as e:
        if "Duplicate entry" in str(e):
            return False, "Username atau email sudah terdaftar"
        return False, f"Error registrasi: {e}"

def login_seller(username, password):
    conn = get_db_connection()
    if conn is None:
        return False, None, "Koneksi database gagal"
    
    try:
        cursor = conn.cursor()
        hashed_password = hash_password(password)
        
        cursor.execute("""
            SELECT seller_id, username, email, nama_toko, kode_seller, rating, jumlah_transaksi
            FROM sellers
            WHERE username = %s AND password = %s
        """, (username, hashed_password))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            seller_data = {
                "seller_id": result[0],
                "username": result[1],
                "email": result[2],
                "nama_toko": result[3],
                "kode_seller": result[4],
                "rating": result[5],
                "jumlah_transaksi": result[6]
            }
            return True, seller_data, "Login berhasil"
        else:
            return False, None, "Username atau password salah"
    except Error as e:
        return False, None, f"Error login: {e}"

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.seller_info = None

if 'products' not in st.session_state:
    st.session_state.products = pd.DataFrame({
        "ID": ["PRD-01", "PRD-02", "PRD-03"],
        "Nama Produk": ["Beras Merah Organik 5kg", "Pupuk Kompos", "Bibit Cabai Rawit"],
        "Kategori": ["Pangan", "Perawatan", "Bibit"],
        "Harga Modal": [75000, 18000, 10000],
        "Harga Jual": [95000, 25000, 15000],
        "Stok": [40, 150, 200],
        "Berat (gram)": [5000, 1000, 500],
        "Deskripsi": [
            "Beras merah organik pilihan dari petani lokal",
            "Pupuk kompos berkualitas tinggi",
            "Bibit cabai rawit unggul berbuah lebat"
        ],
        "Status": ["Aktif", "Aktif", "Aktif"]
    })

if 'orders' not in st.session_state:
    st.session_state.orders = pd.DataFrame({
        "Order ID": ["ORD-001", "ORD-002", "ORD-003"],
        "Pembeli": ["Budi Santoso", "Siti Aminah", "Andi Wijaya"],
        "Email": ["budi@email.com", "siti@email.com", "andi@email.com"],
        "No. Telepon": ["08123456789", "08234567890", "08345678901"],
        "Alamat Pengiriman": ["Jl. Merdeka 1", "Jl. Sudirman 2", "Jl. Thamrin 3"],
        "Kota": ["Jakarta", "Bandung", "Surabaya"],
        "Provinsi": ["DKI Jakarta", "Jawa Barat", "Jawa Timur"],
        "Kode Pos": ["10110", "40111", "60111"],
        "Berat Total": [5000, 2000, 1500],
        "Total": [250000, 1200000, 75000],
        "Status": ["Menunggu Bayar", "Diproses", "Selesai"],
        "Status Pengiriman": ["Belum Diproses", "Belum Diproses", "Terkirim"],
        "Bank": ["BCA", "Mandiri", "BNI"],
        "Tanggal Order": ["2026-06-01", "2026-06-02", "2026-06-03"]
    })

if 'stok_log' not in st.session_state:
    st.session_state.stok_log = pd.DataFrame({
        "Tanggal": ["2026-06-01", "2026-06-02", "2026-06-03"],
        "Produk": ["Beras Merah Organik 5kg", "Pupuk Kompos", "Bibit Cabai Rawit"],
        "Tipe": ["Keluar", "Masuk", "Koreksi"],
        "Jumlah": [10, 50, 5],
        "Alasan": ["Order ORD-001", "Restock dari supplier", "Koreksi stok fisik"],
        "Stok Akhir": [30, 200, 205]
    })

if 'customers' not in st.session_state:
    st.session_state.customers = pd.DataFrame({
        "ID": ["CUST-001", "CUST-002", "CUST-003"],
        "Nama": ["Budi Santoso", "Siti Aminah", "Andi Wijaya"],
        "Email": ["budi@email.com", "siti@email.com", "andi@email.com"],
        "No. Telepon": ["08123456789", "08234567890", "08345678901"],
        "Alamat": ["Jakarta Timur", "Bandung", "Surabaya"],
        "Total Pembelian": [250000, 1200000, 75000],
        "Jumlah Pesanan": [2, 5, 1],
        "Last Order": ["2026-06-01", "2026-06-02", "2026-06-03"]
    })

if 'transaction_history' not in st.session_state:
    dates = pd.date_range(start='2026-05-08', end='2026-06-06', freq='D')
    st.session_state.transaction_history = pd.DataFrame({
        "Tanggal": dates,
        "Penjualan": [i * 100000 for i in range(1, len(dates)+1)]
    })

if st.session_state.get('authenticated') and st.session_state.get('seller_info'):
    if not st.session_state.get('data_loaded', False):
        seller_id = st.session_state.seller_info.get('seller_id')
        if seller_id:
            ok = load_seller_data(seller_id)
            st.session_state['data_loaded'] = True if ok else False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div style='text-align: center;'><h1>🌾 PANEN.NET</h1><p>Seller Dashboard Platform</p></div>", unsafe_allow_html=True)
        
        tab_login, tab_register = st.tabs(["🔐 Login", "📝 Registrasi"])
        
        with tab_login:
            st.subheader("Masuk ke Akun Anda")
            
            username = st.text_input("Username", placeholder="Masukkan username Anda")
            password = st.text_input("Password", type="password", placeholder="Masukkan password Anda")
            
            if st.button("🔓 Login", use_container_width=True):
                if username and password:
                    success, seller_data, message = login_seller(username, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.seller_info = seller_data
                        st.success(message)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Silakan isi username dan password")
        
        with tab_register:
            st.subheader("Buat Akun Baru")
            st.caption("Daftar sebagai seller baru di platform Panen.net")
            
            with st.form("register_form"):
                new_username = st.text_input("Username", placeholder="Pilih username unik")
                new_email = st.text_input("Email", placeholder="Email Anda")
                new_nama_toko = st.text_input("Nama Toko", placeholder="Nama toko/kebun Anda")
                new_password = st.text_input("Password", type="password", placeholder="Minimal 6 karakter")
                new_password_confirm = st.text_input("Konfirmasi Password", type="password")
                
                register_btn = st.form_submit_button("📝 Daftar Sekarang", use_container_width=True)
                
                if register_btn:
                    if not all([new_username, new_email, new_nama_toko, new_password]):
                        st.error("❌ Semua field harus diisi")
                    elif len(new_password) < 6:
                        st.error("❌ Password minimal 6 karakter")
                    elif new_password != new_password_confirm:
                        st.error("❌ Password tidak cocok")
                    else:
                        success, message = register_seller(new_username, new_password, new_email, new_nama_toko)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
    
    st.stop()

with st.sidebar:
    st.title("🌾 Panen.net")
    st.caption("Seller Tenant Portal")
    st.divider()

    seller = st.session_state.seller_info
    st.markdown(f"""
    **{seller['nama_toko']}** Kode: `{seller['kode_seller']}`  
    ⭐ Rating: {seller['rating']}/5.0  
    📊 Transaksi: {seller['jumlah_transaksi']}
    """)
    st.divider()

    menu_selection = st.radio(
        "Menu Utama",
        ["📊 Beranda", "📦 Katalog Produk", "📋 Inventori & Stok", "🛒 Pesanan", "👥 Pelanggan", "📈 Analytics"]
    )

    st.divider()
    st.caption("v1.0 - Powered by Panen.net")
    
    if st.button("🚪 Log Out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.seller_info = None
        st.success("Anda berhasil logout!")
        st.balloons()
        st.rerun()

if menu_selection == "📊 Beranda":
    st.header("📊 Ringkasan Performa")
    st.markdown("Pantau metrik penjualan dan aktivitas toko Anda di sini. Data diperbaharui secara real-time.")

    total_penjualan = st.session_state.orders['Total'].sum()
    pesanan_selesai = len(st.session_state.orders[st.session_state.orders['Status'] == 'Selesai'])
    pesanan_baru = len(st.session_state.orders[st.session_state.orders['Status'] == 'Menunggu Bayar'])
    stok_menipis = len(st.session_state.products[st.session_state.products['Stok'] < 50])
    produk_aktif = len(st.session_state.products[st.session_state.products['Status'] == 'Aktif'])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="💰 Total Penjualan",
            value=f"Rp {total_penjualan:,.0f}",
            delta=f"{pesanan_selesai} order selesai"
        )
    with col2:
        st.metric(
            label="📦 Pesanan Baru",
            value=f"{pesanan_baru}",
            delta="Perlu konfirmasi"
        )
    with col3:
        st.metric(
            label="✅ Produk Aktif",
            value=produk_aktif,
            delta=f"{len(st.session_state.products)} total produk"
        )
    with col4:
        st.metric(
            label="⚠️ Stok Menipis",
            value=stok_menipis,
            delta="< 50 unit",
            delta_color="inverse"
        )

    st.divider()
    
    st.subheader("📋 Pesanan Terbaru")
    col_ord1, col_ord2 = st.columns([3, 1])
    with col_ord1:
        st.write("")
    with col_ord2:
        filter_status = st.selectbox(
            "Filter Status",
            ["Semua", "Menunggu Bayar", "Diproses", "Dikirim", "Selesai"],
            key="beranda_filter"
        )
    
    if filter_status == "Semua":
        display_orders = st.session_state.orders
    else:
        display_orders = st.session_state.orders[st.session_state.orders['Status'] == filter_status]
    
    st.dataframe(
        display_orders[["Order ID", "Pembeli", "Total", "Status", "Tanggal Order"]],
        use_container_width=True,
        hide_index=True
    )

    st.divider()
    st.subheader("⚠️ Produk dengan Stok Rendah")
    low_stock = st.session_state.products[st.session_state.products['Stok'] < 50]
    if len(low_stock) > 0:
        st.warning(f"🔔 Ada {len(low_stock)} produk dengan stok < 50 unit")
        st.dataframe(
            low_stock[["Nama Produk", "Stok", "Kategori"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("✅ Semua produk memiliki stok yang cukup")

elif menu_selection == "📦 Katalog Produk":
    st.header("📦 Manajemen Produk")
    st.markdown("Kelola katalog produk Anda. Tambah, edit, atau hapus produk untuk dijual.")

    tab_list, tab_add = st.tabs(["📋 Daftar Produk", "➕ Tambah Produk Baru"])
    
    with tab_list:
        st.subheader("Katalog Produk Saat Ini")
        
        col_filt1, col_filt2 = st.columns(2)
        with col_filt1:
            kategori_filter = st.multiselect(
                "Filter Kategori",
                st.session_state.products['Kategori'].unique().tolist(),
                default=st.session_state.products['Kategori'].unique().tolist()
            )
        with col_filt2:
            status_filter = st.multiselect(
                "Filter Status",
                ["Aktif", "Nonaktif"],
                default=["Aktif"]
            )
        
        filtered_products = st.session_state.products[
            (st.session_state.products['Kategori'].isin(kategori_filter)) &
            (st.session_state.products['Status'].isin(status_filter))
        ].copy()
        
        st.write(f"**Total Produk:** {len(filtered_products)}")
        
        display_cols = ["Nama Produk", "Kategori", "Harga Modal", "Harga Jual", "Stok", "Berat (gram)", "Status"]
        editor_df = filtered_products[["ID"] + display_cols].copy()
        edited_df = st.data_editor(
            editor_df,
            use_container_width=True,
            hide_index=True,
            key="product_editor"
        )

        if not edited_df.empty:
            for idx, row in edited_df.iterrows():
                prod_id = row['ID']
                main_idx = st.session_state.products[st.session_state.products['ID'] == prod_id].index
                if len(main_idx) > 0:
                    for col in display_cols:
                        if col in row.index:
                            st.session_state.products.at[main_idx[0], col] = row[col]
                    try:
                        seller_id = st.session_state.seller_info['seller_id']
                        save_product_update(seller_id, prod_id, {c: row[c] for c in display_cols if c in row.index})
                    except Exception:
                        st.warning("Perubahan produk disimpan secara lokal, namun gagal disimpan ke database.")
        with st.expander("🗑️ Hapus Produk", expanded=False):
            prod_names = st.session_state.products['Nama Produk'].tolist()
            to_delete = st.selectbox("Pilih produk untuk dihapus", prod_names if prod_names else ["Tidak ada produk"], key="del_prod_select")
            if to_delete and to_delete != "Tidak ada produk":
                if st.button("Hapus Produk"):
                    sel = st.session_state.products[st.session_state.products['Nama Produk'] == to_delete].iloc[0]
                    sku = sel['ID']
                    seller_id = st.session_state.seller_info.get('seller_id') if st.session_state.seller_info else None
                    if seller_id:
                        ok = delete_product_db(seller_id, sku)
                        if ok:
                            st.success("Produk dihapus dari database")
                            load_seller_data(seller_id)
                        else:
                            st.error("Gagal menghapus produk dari database")
                    else:
                        st.session_state.products = st.session_state.products[st.session_state.products['Nama Produk'] != to_delete].reset_index(drop=True)
                        st.success("Produk dihapus dari tampilan lokal")
        
        st.divider()
        st.subheader("📊 Statistik Produk")
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("Total Produk", len(st.session_state.products))
        with col_stat2:
            avg_harga = st.session_state.products['Harga Jual'].mean()
            st.metric("Rata-rata Harga Jual", f"Rp {avg_harga:,.0f}")
        with col_stat3:
            total_stok = st.session_state.products['Stok'].sum()
            st.metric("Total Stok", f"{total_stok} unit")
    
    with tab_add:
        st.subheader("📝 Form Tambah Produk Baru")
        st.caption("Isi semua informasi produk dengan teliti. Data akan disimpan ke katalog Anda.")
        
        with st.form("Form_tambah_produk", clear_on_submit=True):
            col_form1, col_form2 = st.columns(2)

            with col_form1:
                nama_produk = st.text_input("Nama Produk *", placeholder="contoh: Beras Merah Organik")
                kategori = st.selectbox("Kategori *", ["Pangan", "Sayuran", "Buah", "Bibit", "Perawatan"])
                harga_modal = st.number_input("Harga Modal (RP) *", min_value=0, step=1000, value=0)
                harga_jual = st.number_input("Harga Jual (RP) *", min_value=0, step=1000, value=0)
            
            with col_form2:
                sku = st.text_input("SKU Produk *", placeholder="contoh: PRD-001")
                stock_awal = st.number_input("Stok Awal *", min_value=0, step=1, value=0)
                berat = st.number_input("Berat (Gram) *", min_value=0, step=50, value=100)
                status = st.selectbox("Status", ["Aktif", "Nonaktif"])

            deskripsi = st.text_area("Deskripsi Produk *", placeholder="Jelaskan keunggulan dan spesifikasi produk Anda")

            st.markdown("*) Wajib diisi")
            st.divider()
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submit_btn = st.form_submit_button("✅ Simpan Produk", use_container_width=True)
            with col_btn2:
                st.form_submit_button("❌ Batal", use_container_width=True)
            
            if submit_btn:
                if not nama_produk or not sku:
                    st.error("❌ Nama Produk dan SKU tidak boleh kosong!")
                elif not deskripsi:
                    st.error("❌ Deskripsi produk harus diisi!")
                elif harga_jual <= harga_modal:
                    st.error("❌ Harga jual harus lebih besar dari harga modal!")
                else:
                    if sku in st.session_state.products['ID'].values:
                        st.error(f"❌ SKU '{sku}' sudah terdaftar!")
                    else:
                        new_product = pd.DataFrame({
                            "ID": [sku],
                            "Nama Produk": [nama_produk],
                            "Kategori": [kategori],
                            "Harga Modal": [int(harga_modal)],
                            "Harga Jual": [int(harga_jual)],
                            "Stok": [int(stock_awal)],
                            "Berat (gram)": [int(berat)],
                            "Deskripsi": [deskripsi],
                            "Status": [status]
                        })
                        st.session_state.products = pd.concat(
                            [st.session_state.products, new_product],
                            ignore_index=True
                        )
                        seller_id = st.session_state.seller_info.get('seller_id') if st.session_state.seller_info else None
                        prod_dict = {
                            'ID': sku,
                            'Nama Produk': nama_produk,
                            'Kategori': kategori,
                            'Harga Modal': int(harga_modal),
                            'Harga Jual': int(harga_jual),
                            'Stok': int(stock_awal),
                            'Berat (gram)': int(berat),
                            'Deskripsi': deskripsi,
                            'Status': status
                        }
                        ok = add_product_db(seller_id, prod_dict) if seller_id else False
                        if ok:
                            st.success(f"✅ Produk '{nama_produk}' berhasil ditambahkan ke katalog dan disimpan ke database!")
                            if seller_id:
                                load_seller_data(seller_id)
                        else:
                            st.success(f"✅ Produk '{nama_produk}' berhasil ditambahkan ke katalog (lokal)")
                            st.warning("Namun penyimpanan ke database gagal atau Anda belum login ke DB")
                        st.balloons()

elif menu_selection == "🛒 Pesanan":
    st.header("🛒 Proses Pesanan")
    st.markdown("Kelola pesanan pelanggan dengan mudah. Update status pengiriman dan lihat detail pembayaran.")

    with st.expander("➕ Tambah Pesanan Baru", expanded=False):
        with st.form("form_add_order"):
            ao_col1, ao_col2, ao_col3 = st.columns(3)
            with ao_col1:
                new_order_code = st.text_input("Order ID", value=f"ORD-{int(datetime.datetime.now().timestamp())}")
                new_pembeli = st.text_input("Nama Pembeli")
                new_email = st.text_input("Email Pembeli")
                new_phone = st.text_input("No. Telepon")
            with ao_col2:
                new_alamat = st.text_area("Alamat Pengiriman")
                new_kota = st.text_input("Kota")
                new_provinsi = st.text_input("Provinsi")
                new_kodepos = st.text_input("Kode Pos")
            with ao_col3:
                new_berat = st.number_input("Berat Total (gram)", min_value=0, step=100, value=1000)
                new_total = st.number_input("Total (Rp)", min_value=0, step=1000, value=0)
                new_bank = st.text_input("Bank")
                new_date = st.date_input("Tanggal Order", value=datetime.date.today())
            
            new_status = st.selectbox("Status Pembayaran", ["Menunggu Bayar", "Diproses", "Selesai"], index=0)
            
            add_order_btn = st.form_submit_button("Tambah Pesanan")
            if add_order_btn:
                if not new_pembeli or new_total <= 0:
                    st.error("Nama pembeli dan total wajib diisi")
                else:
                    seller_id = st.session_state.seller_info.get('seller_id') if st.session_state.seller_info else None
                    new_order = {
                        'Order ID': new_order_code,
                        'Pembeli': new_pembeli,
                        'Email': new_email,
                        'No. Telepon': new_phone,
                        'Alamat Pengiriman': new_alamat,
                        'Kota': new_kota,
                        'Provinsi': new_provinsi,
                        'Kode Pos': new_kodepos,
                        'Berat Total': new_berat,
                        'Total': new_total,
                        'Status': new_status,
                        'Status Pengiriman': 'Belum Diproses',
                        'Bank': new_bank,
                        'Tanggal Order': new_date
                    }
                    st.session_state.orders = pd.concat([st.session_state.orders, pd.DataFrame([new_order])], ignore_index=True)
                    ok = add_order_db(seller_id, new_order) if seller_id else False
                    if ok:
                        st.success("Order berhasil ditambahkan dan disimpan ke database")
                        if seller_id:
                            load_seller_data(seller_id)
                    else:
                        st.warning("Order ditambahkan secara lokal, namun gagal disimpan ke database")

    col_filt1, col_filt2, col_filt3 = st.columns(3)
    with col_filt1:
        status_filter = st.selectbox(
            "Filter Status",
            ["Semua", "Menunggu Bayar", "Diproses", "Dikirim", "Selesai"],
            key="pesanan_filter"
        )
    with col_filt2:
        limit = st.selectbox("Tampilkan", [10, 20, 50], index=0)
    with col_filt3:
        search = st.text_input("Cari Order ID atau Pembeli", "")
    
    if status_filter == "Semua":
        filtered_orders = st.session_state.orders.copy()
    else:
        filtered_orders = st.session_state.orders[st.session_state.orders['Status'] == status_filter].copy()
    
    if search:
        filtered_orders = filtered_orders[
            (filtered_orders['Order ID'].str.contains(search, case=False)) |
            (filtered_orders['Pembeli'].str.contains(search, case=False))
        ]
    
    st.write(f"**Total Pesanan:** {len(filtered_orders)}")
    
    display_orders = filtered_orders.head(limit).copy()
    
    col_ord1, col_ord2 = st.columns([4, 1])
    with col_ord1:
        st.write("**Status Pesanan**")
    with col_ord2:
        st.write("")
    
    for idx, row in display_orders.iterrows():
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([1, 1.5, 1, 1, 1])
            
            with col1:
                st.write(f"**{row['Order ID']}**")
            with col2:
                st.write(row['Pembeli'])
            with col3:
                st.write(f"Rp {row['Total']:,.0f}")
            with col4:
                # Menampilkan status saat ini
                st.write(f"Status: **{row['Status']}**")
                st.caption(f"Logistik: {row['Status Pengiriman']}")
                
                # Jika pesanan sudah dibayar tapi belum diproses logistik
                if row['Status'] == 'Menunggu Bayar' or (row['Status'] == 'Diproses' and row['Status Pengiriman'] == 'Belum Diproses'):
                    if st.button("📦 Request Pickup", key=f"req_{idx}"):
                        try:
                            conn = get_db_connection()
                            cursor = conn.cursor()

                            # Panen.net HANYA mengubah status di database-nya SENDIRI
                            # (panennet.orders). Sistem ini TIDAK menulis ke tabel
                            # `shipments` karena tabel itu sekarang berada di
                            # database terpisah milik perusahaan logistik
                            # (logistik_db). Pembuatan shipment yang sesungguhnya
                            # dilakukan dari sisi aplikasi logistik.py, yang akan
                            # membaca order "Menunggu Pickup" ini secara otomatis
                            # dari panennet via koneksi lintas-sistem.
                            cursor.execute("""
                                UPDATE orders
                                SET status = 'Diproses', shipping_status = 'Menunggu Pickup'
                                WHERE order_code = %s
                            """, (row['Order ID'],))

                            conn.commit()
                            cursor.close()
                            conn.close()

                            # Update session state lokal agar UI langsung berubah
                            st.session_state.orders.loc[st.session_state.orders['Order ID'] == row['Order ID'], 'Status'] = 'Diproses'
                            st.session_state.orders.loc[st.session_state.orders['Order ID'] == row['Order ID'], 'Status Pengiriman'] = 'Menunggu Pickup'

                            st.success("✅ Order ditandai siap dikirim. Akan muncul otomatis di sistem Logistik (menu 'Buat Pengiriman Baru').")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal request pickup: {e}")
            with col5:
                st.write(row['Tanggal Order'])
    
    st.divider()
    st.subheader("📊 Statistik Pesanan")
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        total_order = len(st.session_state.orders)
        st.metric("Total Pesanan", total_order)
    with col_stat2:
        order_selesai = len(st.session_state.orders[st.session_state.orders['Status'] == 'Selesai'])
        st.metric("Pesanan Selesai", order_selesai)
    with col_stat3:
        order_diproses = len(st.session_state.orders[st.session_state.orders['Status'].isin(['Menunggu Bayar', 'Diproses', 'Dikirim'])])
        st.metric("Sedang Diproses", order_diproses)
    with col_stat4:
        total_revenue = st.session_state.orders[st.session_state.orders['Status'] == 'Selesai']['Total'].sum()
        st.metric("Revenue (Selesai)", f"Rp {total_revenue:,.0f}")

elif menu_selection == "📋 Inventori & Stok":
    st.header("📋 Manajemen Inventori & Stok")
    st.markdown("Monitor dan kelola stok produk Anda secara real-time dengan log lengkap.")

    tab_inventory, tab_log = st.tabs(["📊 Dashboard Stok", "📜 Riwayat Stok"])
    
    with tab_inventory:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 Ringkasan Stok")
            total_stok = st.session_state.products['Stok'].sum()
            stok_menipis = len(st.session_state.products[st.session_state.products['Stok'] < 50])
            st.metric("Total Stok", value=f"{total_stok} unit")
            st.metric("Produk Stok Menipis", value=stok_menipis)
        
        with col2:
            st.subheader("⚠️ Produk dengan Stok Kritis")
            produk_kritis = st.session_state.products[st.session_state.products['Stok'] < 50]
            if len(produk_kritis) > 0:
                st.dataframe(
                    produk_kritis[["Nama Produk", "Stok", "Kategori"]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("✅ Semua produk memiliki stok yang cukup")

        st.divider()
        st.subheader("📈 Update Stok Produk")
        
        with st.form("Form_update_stok", clear_on_submit=True):
            col_updt1, col_updt2 = st.columns(2)
            
            with col_updt1:
                produk_list = st.session_state.products['Nama Produk'].tolist()
                produk_pilih = st.selectbox(
                    "Pilih Produk *",
                    produk_list if produk_list else ["Tidak ada produk"],
                    key="stok_produk"
                )
                tipe_update = st.radio("Tipe Update *", ["Tambah Stok", "Kurangi Stok", "Koreksi"])
            
            with col_updt2:
                jumlah = st.number_input("Jumlah *", min_value=1, step=1, value=1)
                alasan = st.text_input("Alasan/Keterangan *", placeholder="Restock/Penjualan/Koreksi Fisik")
            
            submit_stok = st.form_submit_button("✅ Update Stok", use_container_width=True)
            
            if submit_stok:
                if not alasan:
                    st.error("❌ Alasan update harus diisi!")
                elif produk_pilih == "Tidak ada produk":
                    st.error("❌ Tidak ada produk untuk diupdate!")
                else:
                    matching_prods = st.session_state.products[st.session_state.products['Nama Produk'] == produk_pilih]
                    if len(matching_prods) > 0:
                        idx = matching_prods.index[0]
                        stok_lama = st.session_state.products.at[idx, 'Stok']
                        
                        if tipe_update == "Tambah Stok":
                            st.session_state.products.at[idx, 'Stok'] += jumlah
                            tipe_log = "Masuk"
                        elif tipe_update == "Kurangi Stok":
                            if stok_lama >= jumlah:
                                st.session_state.products.at[idx, 'Stok'] -= jumlah
                                tipe_log = "Keluar"
                            else:
                                st.error("❌ Stok tidak cukup untuk dikurangi!")
                                st.stop()
                        else:
                            st.session_state.products.at[idx, 'Stok'] = jumlah
                            tipe_log = "Koreksi"
                        
                        stok_baru = st.session_state.products.at[idx, 'Stok']
                        new_log = pd.DataFrame({
                            "Tanggal": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                            "Produk": [produk_pilih],
                            "Tipe": [tipe_log],
                            "Jumlah": [jumlah],
                            "Alasan": [alasan],
                            "Stok Akhir": [stok_baru]
                        })
                        st.session_state.stok_log = pd.concat(
                            [st.session_state.stok_log, new_log],
                            ignore_index=True
                        )
                        try:
                            seller_id = st.session_state.seller_info['seller_id']
                            id_produk = st.session_state.products.at[idx, 'ID']
                            save_stock_change(seller_id, id_produk, tipe_log, jumlah, alasan)
                        except Exception:
                            st.warning("Perubahan stok disimpan secara lokal, namun gagal disimpan ke database.")
                        
                        st.success(f"✅ Stok '{produk_pilih}' berhasil diupdate! ({stok_lama} → {stok_baru})")
                        st.balloons()
                    else:
                        st.error("❌ Produk tidak ditemukan!")
    
    with tab_log:
        st.subheader("📜 Riwayat Pergerakan Stok (50 Terbaru)")
        
        filter_produk_log = st.selectbox(
            "Filter Produk",
            ["Semua"] + st.session_state.products['Nama Produk'].tolist(),
            key="log_filter"
        )
        
        if filter_produk_log == "Semua":
            log_display = st.session_state.stok_log.tail(50)
        else:
            log_display = st.session_state.stok_log[st.session_state.stok_log['Produk'] == filter_produk_log].tail(50)
        
        st.dataframe(
            log_display,
            use_container_width=True,
            hide_index=True
        )

elif menu_selection == "👥 Pelanggan":
    st.header("👥 Manajemen Pelanggan & CRM")
    st.markdown("Kelola data pelanggan, lihat riwayat transaksi, dan analisis perilaku pembelian.")

    tab_list, tab_detail = st.tabs(["📋 Daftar Pelanggan", "👤 Detail Pelanggan"])
    
    with tab_list:
        st.subheader("Daftar Pelanggan")
        with st.expander("➕ Tambah Pelanggan", expanded=False):
            with st.form("form_add_customer"):
                ac_col1, ac_col2 = st.columns(2)
                with ac_col1:
                    cust_name = st.text_input("Nama")
                    cust_email = st.text_input("Email")
                with ac_col2:
                    cust_phone = st.text_input("No. Telepon")
                    cust_address = st.text_input("Alamat")
                add_cust_btn = st.form_submit_button("Tambah Pelanggan")
                if add_cust_btn:
                    if not cust_name:
                        st.error("Nama pelanggan wajib diisi")
                    else:
                        seller_id = st.session_state.seller_info.get('seller_id') if st.session_state.seller_info else None
                        new_cust = {
                            'Nama': cust_name,
                            'Email': cust_email,
                            'No. Telepon': cust_phone,
                            'Alamat': cust_address,
                            'Total Pembelian': 0,
                            'Jumlah Pesanan': 0,
                            'Last Order': None
                        }
                        new_id = f"CUST-{len(st.session_state.customers)+1:03d}"
                        row = {k: new_cust.get(k, '') for k in ['Nama','Email','No. Telepon','Alamat','Total Pembelian','Jumlah Pesanan','Last Order']}
                        row['ID'] = new_id
                        st.session_state.customers = pd.concat([st.session_state.customers, pd.DataFrame([row])], ignore_index=True)
                        if seller_id:
                            ok = add_customer_db(seller_id, new_cust)
                            if ok:
                                st.success("Pelanggan berhasil ditambahkan ke database")
                                load_seller_data(seller_id)
                            else:
                                st.warning("Pelanggan ditambahkan secara lokal, namun gagal disimpan ke database")

        with st.expander("🗑️ Hapus Pelanggan", expanded=False):
            cust_names = st.session_state.customers['Nama'].tolist()
            to_delete = st.selectbox("Pilih pelanggan untuk dihapus", cust_names if cust_names else ["Tidak ada pelanggan"]) 
            if to_delete and to_delete != "Tidak ada pelanggan":
                if st.button("Hapus Pelanggan"):
                    sel = st.session_state.customers[st.session_state.customers['Nama'] == to_delete].iloc[0]
                    cust_id = sel['ID']
                    seller_id = st.session_state.seller_info.get('seller_id') if st.session_state.seller_info else None
                    if isinstance(cust_id, int) and seller_id:
                        ok = delete_customer_db(seller_id, cust_id)
                        if ok:
                            st.success("Pelanggan dihapus dari database")
                            load_seller_data(seller_id)
                        else:
                            st.error("Gagal menghapus pelanggan dari database")
                    else:
                        st.session_state.customers = st.session_state.customers[st.session_state.customers['Nama'] != to_delete].reset_index(drop=True)
                        st.success("Pelanggan dihapus dari tampilan lokal")
        
        col_cust1, col_cust2 = st.columns(2)
        with col_cust1:
            search_cust = st.text_input("Cari Nama atau Email", "")
        with col_cust2:
            sort_by = st.selectbox("Urutkan Berdasarkan", ["Total Pembelian", "Jumlah Pesanan", "Last Order"])
        
        customers_display = st.session_state.customers.copy()
        if search_cust:
            customers_display = customers_display[
                (customers_display['Nama'].str.contains(search_cust, case=False)) |
                (customers_display['Email'].str.contains(search_cust, case=False))
            ]
        
        if sort_by == "Total Pembelian":
            customers_display = customers_display.sort_values('Total Pembelian', ascending=False)
        elif sort_by == "Jumlah Pesanan":
            customers_display = customers_display.sort_values('Jumlah Pesanan', ascending=False)
        else:
            customers_display = customers_display.sort_values('Last Order', ascending=False)
        
        st.dataframe(
            customers_display[[
                "ID", "Nama", "Email", "No. Telepon", "Total Pembelian", "Jumlah Pesanan", "Last Order"
            ]],
            use_container_width=True,
            hide_index=True
        )
        
        st.divider()
        st.subheader("📊 Statistik Pelanggan")
        col_cstat1, col_cstat2, col_cstat3, col_cstat4 = st.columns(4)
        
        with col_cstat1:
            st.metric("Total Pelanggan", value=len(st.session_state.customers))
        with col_cstat2:
            avg_pembelian = st.session_state.customers['Total Pembelian'].mean()
            st.metric("Rata-rata Pembelian", value=f"Rp {avg_pembelian:,.0f}")
        with col_cstat3:
            total_pembelian = st.session_state.customers['Total Pembelian'].sum()
            st.metric("Total Penjualan", value=f"Rp {total_pembelian:,.0f}")
        with col_cstat4:
            avg_order = st.session_state.customers['Jumlah Pesanan'].mean()
            st.metric("Rata-rata Order/Pelanggan", value=f"{avg_order:.1f}")
    
    with tab_detail:
        st.subheader("Detail Pelanggan & Riwayat Transaksi")
        
        customer_names = st.session_state.customers['Nama'].tolist()
        selected_customer = st.selectbox(
            "Pilih Pelanggan",
            customer_names if customer_names else ["Tidak ada pelanggan"],
            key="selected_cust"
        )
        
        if selected_customer != "Tidak ada pelanggan":
            cust_detail = st.session_state.customers[st.session_state.customers['Nama'] == selected_customer].iloc[0]
            
            col_det1, col_det2 = st.columns(2)
            with col_det1:
                st.write("**Informasi Pelanggan**")
                st.write(f"ID: {cust_detail['ID']}")
                st.write(f"Nama: {cust_detail['Nama']}")
                st.write(f"Email: {cust_detail['Email']}")
                st.write(f"No. Telepon: {cust_detail['No. Telepon']}")
                st.write(f"Alamat: {cust_detail['Alamat']}")
            
            with col_det2:
                st.write("**Statistik Transaksi**")
                st.metric("Total Pembelian", f"Rp {cust_detail['Total Pembelian']:,.0f}")
                st.metric("Jumlah Pesanan", cust_detail['Jumlah Pesanan'])
                last_order = cust_detail['Last Order']
                last_order_display = None
                try:
                    if pd.isna(last_order):
                        last_order_display = "-"
                    elif isinstance(last_order, (pd.Timestamp, datetime.datetime)):
                        last_order_display = pd.to_datetime(last_order).strftime("%Y-%m-%d")
                    elif isinstance(last_order, datetime.date):
                        last_order_display = last_order.strftime("%Y-%m-%d")
                    else:
                        last_order_display = str(last_order)
                except Exception:
                    last_order_display = str(last_order)

                st.metric("Last Order", last_order_display)
            
            st.divider()
            st.write("**Riwayat Pesanan**")
            
            cust_orders = st.session_state.orders[st.session_state.orders['Pembeli'] == selected_customer]
            if len(cust_orders) > 0:
                st.dataframe(
                    cust_orders[["Order ID", "Total", "Status", "Bank", "Tanggal Order"]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Pelanggan ini belum memiliki pesanan")

elif menu_selection == "📈 Analytics":
    st.header("📈 Analytics & Laporan Penjualan")
    st.markdown("Analisis performa bisnis Anda dengan visualisasi data yang komprehensif.")
    
    tab_sales, tab_product, tab_customer = st.tabs(["📊 Penjualan", "🏆 Produk Terlaris", "👥 Analisis Pelanggan"])
    
    with tab_sales:
        st.subheader("📊 Ringkasan Penjualan 30 Hari Terakhir")
        
        col_sales1, col_sales2 = st.columns(2)
        with col_sales1:
            total_sales_30 = st.session_state.transaction_history['Penjualan'].sum()
            st.metric("Total Penjualan", f"Rp {total_sales_30:,.0f}")
        with col_sales2:
            avg_sales_30 = st.session_state.transaction_history['Penjualan'].mean()
            st.metric("Rata-rata/Hari", f"Rp {avg_sales_30:,.0f}")
        
        st.line_chart(
            st.session_state.transaction_history.set_index('Tanggal'),
            use_container_width=True
        )
    
    with tab_product:
        st.subheader("🏆 10 Produk Terlaris (by Revenue)")
        
        top_products = st.session_state.products.nlargest(10, 'Harga Jual')[
            ['Nama Produk', 'Kategori', 'Harga Jual', 'Stok']
        ]
        
        st.dataframe(top_products, use_container_width=True, hide_index=True)
    
    with tab_customer:
        st.subheader("👥 Analisis Pelanggan")
        
        col_cana1, col_cana2 = st.columns(2)
        with col_cana1:
            st.write("**Distribusi Pelanggan Berdasarkan Total Pembelian**")
            high_value = len(st.session_state.customers[st.session_state.customers['Total Pembelian'] > 500000])
            medium_value = len(st.session_state.customers[
                (st.session_state.customers['Total Pembelian'] >= 200000) &
                (st.session_state.customers['Total Pembelian'] <= 500000)
            ])
            low_value = len(st.session_state.customers[st.session_state.customers['Total Pembelian'] < 200000])
            
            st.metric("High Value (>Rp 500K)", high_value)
            st.metric("Medium Value (Rp 200K-500K)", medium_value)
            st.metric("Low Value (<Rp 200K)", low_value)
        
        with col_cana2:
            st.write("**Top 5 Pelanggan**")
            top_customers = st.session_state.customers.nlargest(5, 'Total Pembelian')[
                ['Nama', 'Total Pembelian', 'Jumlah Pesanan']
            ]
            st.dataframe(top_customers, use_container_width=True, hide_index=True)