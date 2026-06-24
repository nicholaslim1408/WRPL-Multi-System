# Panen.net & HijauKirim Express — Panduan Penggunaan

Dokumen ini menjelaskan cara menjalankan dan menggunakan dua aplikasi yang saling terhubung:

- **Panen.net** (`Panen.py`) — portal penjual hasil pertanian (produk, pesanan, stok, pelanggan, analytics).
- **HijauKirim Express** (`logistik.py`) — sistem manajemen logistik pihak ketiga (pengiriman, kurir, armada, tracking).

Kedua aplikasi memiliki basis data MySQL **terpisah** (`panennet` dan `logistik_db`) dan saling terhubung melalui koneksi lintas-sistem pada kode `logistik.py`.

---

## 1. Persiapan Awal (Sekali Saja)

### 1.1. Prasyarat

- Python 3.9+
- MySQL Server (lokal atau remote) yang sudah berjalan
- Pip packages: `streamlit`, `mysql-connector-python`, `pandas`

```bash
pip install streamlit mysql-connector-python pandas
```

### 1.2. Konfigurasi Koneksi Database

Pastikan kredensial MySQL pada `_my.cnf` (atau konfigurasi koneksi di dalam `Panen.py` / `logistik.py`) sudah sesuai dengan environment Anda (host, user, password, port).

### 1.3. Setup Database — Urutan WAJIB

Jalankan skrip SQL **dengan urutan berikut**, karena `logistik_db` membaca referensi dari `panennet`:

```bash
# 1) Buat & isi database panennet (Panen.net) terlebih dahulu
mysql -u root -p < "setup_database (2).sql"
# lalu
mysql -u root -p < "setup_database (2.1).sql"


# 2) Baru kemudian buat & isi database logistik_db (HijauKirim Express)
mysql -u root -p < setup_logistics_db.sql
```

> **Catatan penting:** Jika tabel `orders` pada `panennet` sebelumnya sudah pernah dibuat oleh skrip lama yang skemanya tidak memiliki kolom `alamat_pengiriman`, `kota`, `provinsi`, `kode_pos`, `berat_total`, atau `shipping_status`, jalankan juga skrip migrasi tambahan (`fix_orders_table.sql`, jika tersedia) sebelum membuka aplikasi. Tanpa ini, Panen.net akan menampilkan error `Unknown column` saat memuat atau menyimpan pesanan.

### 1.4. Menjalankan Aplikasi

Jalankan kedua aplikasi sebagai dua proses Streamlit terpisah (bisa di terminal berbeda, atau di port berbeda di komputer/server yang sama):

```bash
# Terminal 1 — Panen.net (default port 8501)
streamlit run Panen.py

# Terminal 2 — HijauKirim Express (gunakan port lain agar tidak bentrok)
streamlit run logistik.py --server.port 8502
```

Setelah berjalan, buka browser ke:
- Panen.net → `http://localhost:8501`
- HijauKirim Express → `http://localhost:8502`

---

## 2. Cara Menggunakan Panen.net (Portal Penjual)

### 2.1. Registrasi & Login

1. Buka aplikasi Panen.net.
2. Jika belum punya akun, pilih tab **Buat Akun Baru**, isi username, password, email, dan nama toko.
3. Jika sudah punya akun, masuk lewat tab **Masuk ke Akun Anda**.
4. Akun contoh (seed data) yang sudah tersedia:
   - Username: `kebun_sayur` (toko "Kebun Sayur Segar")
   - Username: `demo` (toko "Demo Toko")

- Note : Password yang ada di kode di hash, jika tidak tahu atau lupa password demo maka jalankan :
```bash
mysql -u root -p < "RessetPasswordAdmindanKebunsayurdemo.sql"
```

maka untuk akun demo Panen.net akan memiliki password sebagai berikut : 

| Username | Password |
|---|---|
| `kebun_sayur` | `KebunSayur@2026!` |
| `admin_demo` | `Admin@2026!` |

### 2.2. Menu Beranda

Menampilkan ringkasan performa toko: total penjualan, jumlah pesanan, pesanan terbaru, dan peringatan produk dengan stok rendah.

### 2.3. Menu Katalog Produk

- **Lihat produk**: tabel seluruh produk milik toko Anda.
- **Tambah produk baru**: isi form di bagian bawah (nama produk, kategori, harga modal, harga jual, stok awal, berat, deskripsi), lalu klik **Simpan**.
- **Edit/Hapus produk**: gunakan kontrol pada tabel produk untuk memperbarui data atau menghapus produk yang sudah tidak dijual.

### 2.4. Menu Inventori & Stok

- Gunakan form **Update Stok Produk** untuk mencatat perubahan stok: pilih tipe (**Tambah Stok**, **Kurangi Stok**, atau **Koreksi**), masukkan jumlah dan alasan.
- Setiap perubahan otomatis tercatat di **Riwayat Pergerakan Stok** (50 transaksi terakhir).
- Bagian atas halaman menampilkan ringkasan stok dan produk dengan stok kritis.

### 2.5. Menu Pesanan — Memproses Pesanan & Mengirim ke Logistik

Ini adalah titik integrasi utama ke HijauKirim Express:

1. Pesanan baru masuk dengan status **Menunggu Bayar**.
2. Setelah pembayaran dikonfirmasi, ubah status menjadi **Diproses** melalui dropdown **Status Pembayaran**.
3. Klik tombol **📦 Request Pickup** pada pesanan yang sudah diproses. Ini akan:
   - Mengubah `status` pesanan menjadi **Diproses**.
   - Mengubah `shipping_status` menjadi **Menunggu Pickup**.
4. Pesanan dengan status ini akan **otomatis muncul** di HijauKirim Express, menu **Manajemen Pengiriman → Buat Pengiriman Baru**, siap diproses oleh tim logistik.

> Panen.net **tidak** membuat data pengiriman (shipment) secara langsung — itu sepenuhnya dilakukan dari sisi HijauKirim Express setelah membaca order yang berstatus "Menunggu Pickup".

### 2.6. Menu Pelanggan (CRM)

Menampilkan daftar pelanggan, total pembelian, jumlah pesanan, dan riwayat transaksi per pelanggan. Anda juga dapat menambah atau menghapus data pelanggan secara manual.

### 2.7. Menu Analytics

Menampilkan ringkasan penjualan 30 hari terakhir, 10 produk terlaris berdasarkan pendapatan, dan analisis sederhana terhadap data pelanggan.

---

## 3. Cara Menggunakan HijauKirim Express (Sistem Logistik)

### 3.1. Login

Gunakan salah satu akun demo berikut (login sederhana, bukan akun database):

| Username | Password | Perusahaan |
|---|---|---|
| `hijaukirim` | `logistik123` | HijauKirim Express |
| `taniantar` | `logistik123` | TaniAntar Nusantara |

### 3.2. Menu Dashboard

Ringkasan operasional: jumlah pengiriman per status, serta metrik kinerja kurir dan armada milik perusahaan yang sedang login.

### 3.3. Menu Manajemen Pengiriman — Inti Integrasi dengan Panen.net

Menu ini memiliki tiga tab:

**Tab "Daftar Pengiriman"**
Menampilkan seluruh pengiriman milik perusahaan Anda. Dapat difilter berdasarkan status (Menunggu Pickup, Dipickup, Di Gudang, Dalam Pengiriman, Tiba di Tujuan, Terkirim, Gagal Kirim, Dikembalikan) atau dicari berdasarkan nomor resi/nama penerima/kota.

**Tab "Buat Pengiriman Baru"** — *di sinilah Anda mengambil order dari Panen.net:*
1. Sistem otomatis menampilkan daftar pesanan dari Panen.net yang sudah berstatus siap kirim namun **belum** memiliki shipment.
2. Pilih satu pesanan dari dropdown.
3. Lengkapi/koreksi data penerima (nama, telepon, alamat, kota, provinsi, kode pos) — data ini terisi otomatis dari Panen.net dan bisa Anda sunting.
4. Isi data pengiriman: berat paket, ongkos kirim, estimasi tiba, dan catatan (opsional).
5. Pilih kurir dan kendaraan yang tersedia (status "Aktif"/"Tersedia") dari dropdown.
6. Klik **💾 Buat Pengiriman**. Sistem akan:
   - Membuat data shipment baru di `logistik_db` dengan nomor resi otomatis.
   - Memperbarui status pesanan terkait di Panen.net menjadi "Dikirim"/"Menunggu Pickup", sehingga penjual bisa melihat progresnya tanpa membuka HijauKirim Express.

**Tab "Update Status"**
Gunakan tab ini untuk memperbarui status perjalanan pengiriman (misalnya dari "Menunggu Pickup" menjadi "Dipickup", lalu "Di Gudang", "Dalam Pengiriman", hingga "Terkirim" atau "Gagal Kirim"/"Dikembalikan" jika ada masalah). Setiap update tercatat ke riwayat (delivery log).

### 3.4. Menu Manajemen Kurir

Tambah, lihat, atau perbarui data kurir: nama, telepon, status (Aktif/Tidak Aktif/Sedang Bertugas), dan kendaraan yang sedang ditugaskan.

### 3.5. Menu Manajemen Armada

Kelola data kendaraan: nomor polisi, jenis kendaraan (Motor/Mobil Pick-up/Van/Truck), kapasitas (kg), dan status (Tersedia/Dipakai/Maintenance).

### 3.6. Menu Tracking & Riwayat

- **Lacak Pengiriman**: masukkan nomor resi (format `HKE-...` atau sesuai kode perusahaan) untuk melihat detail pengiriman beserta lini masa (*timeline*) perjalanan dari "Menunggu Pickup" hingga status terakhir.
- **Riwayat Lengkap**: daftar seluruh pengiriman yang pernah dibuat oleh perusahaan Anda.

### 3.7. Menu Laporan & Analitik

Menampilkan ringkasan kinerja pengiriman perusahaan logistik (jumlah pengiriman per status, performa kurir, dan metrik terkait lainnya).

---

## 4. Alur Kerja End-to-End (Ringkasan)

```
[Panen.net]                                   [HijauKirim Express]
   |
   |  1. Pembeli membuat pesanan
   |     -> status: Menunggu Bayar
   |
   |  2. Penjual konfirmasi bayar
   |     -> status: Diproses
   |
   |  3. Penjual klik "Request Pickup"
   |     -> shipping_status: Menunggu Pickup  ------->  4. Order otomatis muncul di
   |                                                       "Buat Pengiriman Baru"
   |                                                  5. Petugas logistik assign
   |                                                     kurir + kendaraan, buat shipment
   |  6. status pesanan ter-update             <-------  (sinkron otomatis ke panennet)
   |     -> "Dikirim"
   |
   |                                                  7. Update status pengiriman
   |                                                     bertahap hingga "Terkirim"
   |
   |  (Penjual & pembeli bisa lihat              8. Tracking via nomor resi
   |   shipping_status di Panen.net)               di HijauKirim Express
```

---

## 5. Troubleshooting Umum

| Gejala | Kemungkinan Sebab | Solusi |
|---|---|---|
| `Unknown column 'alamat_pengiriman'` / `'shipping_status'` | Tabel `orders` di `panennet` dibuat dari skrip SQL versi lama yang skemanya tidak lengkap | Jalankan skrip migrasi `ALTER TABLE` untuk menambahkan kolom yang hilang, lalu restart aplikasi |
| Pesanan baru hanya muncul di tampilan tapi hilang setelah refresh | Order gagal tersimpan ke MySQL (biasanya karena error skema di atas) | Perbaiki skema tabel `orders` terlebih dahulu, lalu coba buat ulang pesanan |
| Order sudah "Menunggu Pickup" di Panen.net tapi tidak muncul di HijauKirim Express | Koneksi `get_panennet_connection()` di `logistik.py` gagal, atau kredensial database salah | Cek konfigurasi koneksi MySQL di `logistik.py`, pastikan host/port/database `panennet` dapat diakses dari server HijauKirim Express |
| Tombol "Buat Pengiriman" gagal disimpan | Tidak ada kurir/kendaraan dengan status tersedia, atau koneksi ke `logistik_db` terputus | Pastikan ada minimal satu kurir berstatus "Aktif" dan satu kendaraan berstatus "Tersedia" untuk perusahaan yang login |
| Login HijauKirim Express gagal terus | Username/password tidak sesuai akun demo, atau session browser belum direset | Gunakan kredensial demo yang benar (lihat bagian 3.1), atau refresh halaman |

---

## 6. Catatan Arsitektur Penting

- `panennet` dan `logistik_db` adalah **dua basis data MySQL yang sepenuhnya terpisah**. Tidak ada foreign key SQL antar keduanya — relasi `order_id`/`order_code` pada tabel `shipments` hanyalah referensi yang dikelola di level aplikasi.
- Data penerima (nama, alamat, kota, dll.) **disalin** ke `logistik_db.shipments` saat shipment dibuat, sehingga HijauKirim Express tidak selalu butuh koneksi aktif ke `panennet` untuk operasi harian seperti tracking.
- Satu-satunya operasi tulis lintas-database adalah ketika HijauKirim Express memperbarui `status` dan `shipping_status` pada `panennet.orders` setelah shipment dibuat atau status pickup diminta.
- Jika basis data `panennet` tidak dapat diakses, modul HijauKirim Express yang **tidak** bergantung padanya (Tracking, Manajemen Kurir, Manajemen Armada) tetap berfungsi normal; hanya tab "Buat Pengiriman Baru" yang akan terganggu.
