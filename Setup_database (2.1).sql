

USE panennet;


-- ============================================================
-- ── BAGIAN B: Versi manual (kompatibel semua versi MySQL/MariaDB) ──────
-- HANYA jalankan blok ini jika BAGIAN A di atas gagal karena syntax
-- error "IF NOT EXISTS" tidak dikenali pada ADD COLUMN.
-- Hapus tanda komentar (--) pada baris yang dibutuhkan saja, SATU PER
-- SATU, dan jalankan. Jika kolom sudah ada, MySQL akan menampilkan
-- error "Duplicate column name" — abaikan saja dan lanjut ke baris
-- berikutnya.
-- ============================================================

ALTER TABLE orders ADD COLUMN alamat_pengiriman TEXT          AFTER no_telepon;
ALTER TABLE orders ADD COLUMN kota              VARCHAR(100)  AFTER alamat_pengiriman;
ALTER TABLE orders ADD COLUMN provinsi          VARCHAR(100)  AFTER kota;
ALTER TABLE orders ADD COLUMN kode_pos          VARCHAR(10)   AFTER provinsi;
ALTER TABLE orders ADD COLUMN berat_total       INT           AFTER kode_pos;
ALTER TABLE orders ADD COLUMN shipping_status   VARCHAR(50) DEFAULT 'Belum Diproses' AFTER status;
UPDATE orders SET shipping_status = 'Belum Diproses' WHERE shipping_status IS NULL;

-- ── Verifikasi hasil akhir ───────────────────────────────────────────────
DESCRIBE orders;
SELECT order_id, order_code, pembeli, status, shipping_status,
       alamat_pengiriman, kota, provinsi, kode_pos, berat_total
FROM orders;
