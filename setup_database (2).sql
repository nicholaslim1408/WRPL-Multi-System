-- Create Panen.net Database
CREATE DATABASE IF NOT EXISTS panennet;
USE panennet;

-- Create Sellers Table
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create Products Table
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
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create Orders Table
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    seller_id INT NOT NULL,
    order_code VARCHAR(50) UNIQUE NOT NULL,
    pembeli VARCHAR(100),
    email VARCHAR(100),
    no_telepon VARCHAR(20),
    total INT,
    status VARCHAR(50),
    bank VARCHAR(50),
    tanggal_order DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create Stock Log Table
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
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create Customers Table
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
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create Indexes for better performance
CREATE INDEX idx_seller_username ON sellers(username);
CREATE INDEX idx_seller_email ON sellers(email);
CREATE INDEX idx_product_seller ON products(seller_id);
CREATE INDEX idx_order_seller ON orders(seller_id);
CREATE INDEX idx_order_status ON orders(status);
CREATE INDEX idx_stok_log_seller ON stok_log(seller_id);
CREATE INDEX idx_customer_seller ON customers(seller_id);

-- Insert Sample Data
INSERT INTO sellers (username, password, email, nama_toko, kode_seller, rating, jumlah_transaksi) 
VALUES 
('kebun_sayur', '4a8c1b6c7d2e9f3a5b8d1c4e6f9a2b5d', 'kebun@email.com', 'Kebun Sayur Segar', 'seller_sel001_db', 4.8, 150);

INSERT INTO products (seller_id, id_produk, nama_produk, kategori, harga_modal, harga_jual, stok, berat, deskripsi, status)
VALUES
(1, 'PRD-01', 'Beras Merah Organik 5kg', 'Pangan', 75000, 95000, 40, 5000, 'Beras merah organik pilihan dari petani lokal', 'Aktif'),
(1, 'PRD-02', 'Pupuk Kompos', 'Perawatan', 18000, 25000, 150, 1000, 'Pupuk kompos berkualitas tinggi', 'Aktif'),
(1, 'PRD-03', 'Bibit Cabai Rawit', 'Bibit', 10000, 15000, 200, 500, 'Bibit cabai rawit unggul berbuah lebat', 'Aktif');

INSERT INTO orders (seller_id, order_code, pembeli, email, no_telepon, total, status, bank, tanggal_order)
VALUES
(1, 'ORD-001', 'Budi Santoso', 'budi@email.com', '08123456789', 250000, 'Menunggu Bayar', 'BCA', '2026-06-01'),
(1, 'ORD-002', 'Siti Aminah', 'siti@email.com', '08234567890', 1200000, 'Diproses', 'Mandiri', '2026-06-02'),
(1, 'ORD-003', 'Andi Wijaya', 'andi@email.com', '08345678901', 75000, 'Selesai', 'BNI', '2026-06-03');

INSERT INTO customers (seller_id, nama, email, no_telepon, alamat, total_pembelian, jumlah_pesanan, last_order)
VALUES
(1, 'Budi Santoso', 'budi@email.com', '08123456789', 'Jakarta Timur', 250000, 2, '2026-06-01'),
(1, 'Siti Aminah', 'siti@email.com', '08234567890', 'Bandung', 1200000, 5, '2026-06-02'),
(1, 'Andi Wijaya', 'andi@email.com', '08345678901', 'Surabaya', 75000, 1, '2026-06-03');

-- Create Admin User (optional - for testing)
INSERT INTO sellers (username, password, email, nama_toko, kode_seller, rating, jumlah_transaksi)
VALUES
('demo', '25f43b1486a834d3653ff954c1e2328e', 'demo@panennet.com', 'Demo Toko', 'seller_demo_db', 5.0, 100);

-- Display sample data
SELECT * FROM sellers;
SELECT * FROM products;
SELECT * FROM orders;
SELECT * FROM customers;
