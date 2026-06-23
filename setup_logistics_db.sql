-- ============================================================
-- LOGISTIK DB — DATABASE MANDIRI UNTUK SISTEM LOGISTIK
-- Terpisah sepenuhnya dari database `panennet` (Panen.net)
--
-- Arsitektur Multi-Sistem:
--   - panennet    -> dikelola oleh Panen.net (sellers, products, orders, dst)
--   - logistik_db -> dikelola oleh perusahaan logistik mitra (tabel di file ini)
--
-- Kedua database TIDAK memiliki FOREIGN KEY satu sama lain
-- (tidak bisa, beda database). Relasi "order_id" / "order_code"
-- di tabel shipments hanyalah REFERENSI, bukan FK SQL.
-- Aplikasi (logistik.py) yang bertanggung jawab menjembatani data
-- dengan membuka 2 koneksi MySQL: satu ke panennet, satu ke logistik_db.
--
-- Jalankan file ini di MySQL SETELAH setup_database.sql (panennet) ada.
-- ============================================================

CREATE DATABASE IF NOT EXISTS logistik_db;
USE logistik_db;

-- ── Tabel Perusahaan Logistik ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS logistics_company (
    company_id   INT AUTO_INCREMENT PRIMARY KEY,
    nama_company VARCHAR(100) NOT NULL,
    kode_company VARCHAR(20)  UNIQUE NOT NULL,
    alamat       VARCHAR(255),
    no_telepon   VARCHAR(20),
    email        VARCHAR(100),
    logo_url     VARCHAR(255),
    aktif        TINYINT(1) DEFAULT 1,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Tabel Armada / Kendaraan ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id      INT AUTO_INCREMENT PRIMARY KEY,
    company_id      INT NOT NULL,
    nomor_polisi    VARCHAR(20) UNIQUE NOT NULL,
    jenis_kendaraan ENUM('Motor', 'Mobil Pick-up', 'Van', 'Truck') NOT NULL,
    kapasitas_kg    INT NOT NULL COMMENT 'kapasitas maksimum dalam kg',
    status          ENUM('Tersedia', 'Dipakai', 'Maintenance') DEFAULT 'Tersedia',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES logistics_company(company_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Tabel Kurir ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS couriers (
    courier_id       INT AUTO_INCREMENT PRIMARY KEY,
    company_id       INT NOT NULL,
    nama_kurir       VARCHAR(100) NOT NULL,
    no_telepon       VARCHAR(20)  NOT NULL,
    email            VARCHAR(100),
    no_ktp           VARCHAR(20)  UNIQUE NOT NULL,
    vehicle_id       INT NULL COMMENT 'kendaraan yang sedang dipakai',
    status           ENUM('Aktif', 'Tidak Aktif', 'Sedang Bertugas') DEFAULT 'Aktif',
    total_pengiriman INT DEFAULT 0,
    rating           FLOAT DEFAULT 0.0,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES logistics_company(company_id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Tabel Pengiriman (Shipments) ─────────────────────────────────────────
-- order_id & order_code adalah REFERENSI ke database panennet.orders,
-- BUKAN foreign key (FK cross-database tidak didukung MySQL).
-- Data nama/alamat penerima DISALIN ke sini saat shipment dibuat, supaya
-- sistem logistik tidak bergantung pada panennet untuk operasional harian.
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id      INT AUTO_INCREMENT PRIMARY KEY,
    order_id         INT NOT NULL COMMENT 'Referensi ke panennet.orders.order_id (bukan FK)',
    order_code       VARCHAR(50) NOT NULL COMMENT 'Referensi ke panennet.orders.order_code (disalin saat dibuat)',
    company_id       INT NOT NULL,
    courier_id       INT NULL,
    vehicle_id       INT NULL,
    kode_resi        VARCHAR(50) UNIQUE NOT NULL,

    -- Info penerima (disalin dari panennet.orders saat shipment dibuat)
    nama_penerima    VARCHAR(100) NOT NULL,
    no_telepon       VARCHAR(20)  NOT NULL,
    alamat           VARCHAR(255) NOT NULL,
    kota             VARCHAR(100) NOT NULL,
    provinsi         VARCHAR(100) NOT NULL,
    kode_pos         VARCHAR(10),

    -- Detail logistik
    berat_kg         DECIMAL(8,2) DEFAULT 0,
    ongkos_kirim     INT DEFAULT 0,
    jarak_km         DECIMAL(8,2) NULL,
    catatan          TEXT NULL,

    -- Status & waktu
    status           ENUM(
                        'Menunggu Pickup',
                        'Dipickup',
                        'Di Gudang',
                        'Dalam Pengiriman',
                        'Tiba di Tujuan',
                        'Terkirim',
                        'Gagal Kirim',
                        'Dikembalikan'
                     ) DEFAULT 'Menunggu Pickup',
    tgl_dibuat       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tgl_pickup       DATETIME NULL,
    tgl_dikirim      DATETIME NULL,
    tgl_terkirim     DATETIME NULL,
    estimasi_tiba    DATE NULL,

    FOREIGN KEY (company_id) REFERENCES logistics_company(company_id),
    FOREIGN KEY (courier_id) REFERENCES couriers(courier_id) ON DELETE SET NULL,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Tabel Delivery Log / Tracking ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS delivery_logs (
    log_id       INT AUTO_INCREMENT PRIMARY KEY,
    shipment_id  INT NOT NULL,
    status_baru  VARCHAR(100) NOT NULL,
    lokasi       VARCHAR(255) NULL COMMENT 'lokasi saat update status',
    keterangan   TEXT NULL,
    updated_by   VARCHAR(100) DEFAULT 'sistem' COMMENT 'nama kurir atau sistem',
    tgl_update   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Indexes ─────────────────────────────────────────────────────────────
CREATE INDEX idx_shipment_order      ON shipments(order_id);
CREATE INDEX idx_shipment_ordercode  ON shipments(order_code);
CREATE INDEX idx_shipment_courier    ON shipments(courier_id);
CREATE INDEX idx_shipment_status     ON shipments(status);
CREATE INDEX idx_shipment_resi       ON shipments(kode_resi);
CREATE INDEX idx_delivery_log_ship   ON delivery_logs(shipment_id);
CREATE INDEX idx_courier_company     ON couriers(company_id);
CREATE INDEX idx_vehicle_company     ON vehicles(company_id);

-- ── Sample Data: Perusahaan Logistik ─────────────────────────────────────
INSERT INTO logistics_company (nama_company, kode_company, alamat, no_telepon, email) VALUES
('HijauKirim Express',  'HKE-001', 'Jl. Raya Logistik No. 12, Jakarta Pusat', '02112345678', 'ops@hijaukirim.co.id'),
('TaniAntar Nusantara', 'TAN-001', 'Jl. Pertanian No. 45, Bandung',           '02298765432', 'info@taniantar.co.id');

SET @hke_company_id := (SELECT company_id FROM logistics_company WHERE kode_company = 'HKE-001' LIMIT 1);
SET @tan_company_id := (SELECT company_id FROM logistics_company WHERE kode_company = 'TAN-001' LIMIT 1);

-- ── Sample Data: Armada ───────────────────────────────────────────────────
INSERT INTO vehicles (company_id, nomor_polisi, jenis_kendaraan, kapasitas_kg, status) VALUES
(@hke_company_id, 'B 1234 HKE', 'Motor',         50,   'Tersedia'),
(@hke_company_id, 'B 5678 HKE', 'Mobil Pick-up', 500,  'Tersedia'),
(@hke_company_id, 'B 9012 HKE', 'Van',           300,  'Tersedia'),
(@hke_company_id, 'B 3456 HKE', 'Truck',         2000, 'Maintenance'),
(@tan_company_id, 'D 1111 TAN', 'Motor',         50,   'Tersedia'),
(@tan_company_id, 'D 2222 TAN', 'Mobil Pick-up', 500,  'Tersedia');

SET @v1 := (SELECT vehicle_id FROM vehicles WHERE nomor_polisi = 'B 1234 HKE' LIMIT 1);
SET @v2 := (SELECT vehicle_id FROM vehicles WHERE nomor_polisi = 'B 5678 HKE' LIMIT 1);
SET @v3 := (SELECT vehicle_id FROM vehicles WHERE nomor_polisi = 'B 9012 HKE' LIMIT 1);
SET @v5 := (SELECT vehicle_id FROM vehicles WHERE nomor_polisi = 'D 1111 TAN' LIMIT 1);
SET @v6 := (SELECT vehicle_id FROM vehicles WHERE nomor_polisi = 'D 2222 TAN' LIMIT 1);

-- ── Sample Data: Kurir ────────────────────────────────────────────────────
INSERT INTO couriers (company_id, nama_kurir, no_telepon, email, no_ktp, vehicle_id, status, total_pengiriman, rating) VALUES
(@hke_company_id, 'Riko Pratama',   '08111111111', 'riko@hijaukirim.co.id',  '3171012001010001', @v1, 'Aktif',           245, 4.8),
(@hke_company_id, 'Dewi Lestari',   '08122222222', 'dewi@hijaukirim.co.id',  '3171012001010002', @v2, 'Aktif',           189, 4.9),
(@hke_company_id, 'Bram Susanto',   '08133333333', 'bram@hijaukirim.co.id',  '3171012001010003', @v3, 'Sedang Bertugas', 312, 4.7),
(@tan_company_id, 'Yuni Kartika',   '08144444444', 'yuni@taniantar.co.id',   '3171012001010004', @v5, 'Aktif',            98, 4.6),
(@tan_company_id, 'Hendra Gunawan', '08155555555', 'hendra@taniantar.co.id', '3171012001010005', @v6, 'Aktif',            76, 4.5);

-- ============================================================
-- CATATAN PENTING:
-- Data shipments TIDAK di-seed di sini karena order_id/order_code
-- harus merujuk ke order yang BENAR-BENAR ADA di database panennet.
-- Jalankan setup_database.sql / setup_mysql.py dulu di panennet,
-- lalu buat shipment via aplikasi logistik.py (menu "Manajemen
-- Pengiriman" -> "Buat Pengiriman Baru") yang akan membaca order
-- dari panennet secara otomatis.
--
-- Jika ingin seed data contoh secara manual, jalankan blok di bawah
-- ini SETELAH memastikan order dengan kode 'ORD-001', 'ORD-002',
-- 'ORD-003' sudah ada di panennet.orders dan order_id-nya sesuai.
-- ============================================================

-- Contoh seed manual (opsional, sesuaikan order_id dengan isi panennet Anda):
-- INSERT INTO shipments (
--     order_id, order_code, company_id, courier_id, vehicle_id, kode_resi,
--     nama_penerima, no_telepon, alamat, kota, provinsi, kode_pos,
--     berat_kg, ongkos_kirim, status, tgl_pickup, tgl_dikirim, estimasi_tiba
-- ) VALUES
-- (1, 'ORD-001', @hke_company_id, @v1, @v1, 'HKE-2026060001',
--  'Budi Santoso', '08123456789', 'Jl. Mawar No. 10, RT 05/03',
--  'Jakarta Timur', 'DKI Jakarta', '13440',
--  5.00, 25000, 'Menunggu Pickup', NULL, NULL, '2026-06-08');

-- ── Tampilkan hasil setup ──────────────────────────────────────────────
SELECT 'logistics_company' AS tabel, COUNT(*) AS jumlah_data FROM logistics_company
UNION ALL SELECT 'vehicles',  COUNT(*) FROM vehicles
UNION ALL SELECT 'couriers',  COUNT(*) FROM couriers
UNION ALL SELECT 'shipments', COUNT(*) FROM shipments
UNION ALL SELECT 'delivery_logs', COUNT(*) FROM delivery_logs;
