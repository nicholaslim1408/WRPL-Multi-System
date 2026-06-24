-- ============================================================
-- RESET PASSWORD & TAMBAH AKUN DEMO — panennet.sellers
--
-- Catatan penting mengenai password lama:
--   Hash password pada seed data awal (setup_database.sql) ditulis
--   dengan format MD5 (32 karakter), padahal Panen.py meng-hash
--   password dengan SHA-256 (64 karakter) -- lihat fungsi
--   hash_password() di Panen.py:
--       hashlib.sha256(password.encode()).hexdigest()
--   Akibatnya, akun seed lama ('kebun_sayur', 'demo') TIDAK PERNAH
--   bisa login dengan password apapun, karena hash di database
--   tidak akan pernah cocok dengan SHA-256 dari input manapun.
--
-- Solusi :
--   1) Mereset password akun 'kebun_sayur' yang sudah ada (memakai
--      UPDATE, bukan INSERT) -> data toko, produk, dan order yang
--      sudah terhubung ke seller_id ini TETAP AMAN, tidak terhapus.
--   2) Menambahkan SATU akun admin/demo baru yang passwordnya sudah
--      pasti benar formatnya (SHA-256) dan siap dipakai untuk login.
--
-- PASSWORD BARU (CATAT, lalu segera ganti setelah login pertama):
--   Username : kebun_sayur   | Password : KebunSayur@2026!
--   Username : admin_demo    | Password : Admin@2026!
-- ============================================================

USE panennet;

-- ── 1) Reset password akun kebun_sayur yang sudah ada ──────────────────
-- Hash di bawah adalah SHA256('KebunSayur@2026!')
UPDATE sellers
SET password = '79ae02a24adfa722b0286b7a4361ae5b58c91592df0a3903ba4862d1d37bd579'
WHERE username = 'kebun_sayur';

-- ── 2) Tambah akun admin/demo baru (hanya jika belum ada) ──────────────
-- Hash di bawah adalah SHA256('Admin@2026!')
INSERT INTO sellers (username, password, email, nama_toko, kode_seller, rating, jumlah_transaksi)
SELECT 'admin_demo',
       'f0ce0e86206541c60bc47be815f83eba98004f63c883e6d71ff5cc929cb5f9ca',
       'admin_demo@panennet.com',
       'Admin Demo Toko',
       'seller_admin_demo',
       5.0,
       0
WHERE NOT EXISTS (
    SELECT 1 FROM sellers WHERE username = 'admin_demo'
);

-- ── Verifikasi hasil ────────────────────────────────────────────────────
SELECT seller_id, username, email, nama_toko, kode_seller, rating, jumlah_transaksi
FROM sellers
WHERE username IN ('kebun_sayur', 'admin_demo');