import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime, date, timedelta
import random
import string
import os

# ══════════════════════════════════════════════════════════════════
# KONFIGURASI & KONEKSI DATABASE
# ══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="HijauKirim Express — Sistem Logistik",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS Styling ──────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Main background + BASE text color (fix: white-on-white) ── */
    .stApp {
        background-color: #f0f7f0;
        color: #1a1a1a;
    }

    /* ── Force dark text on ALL main-area elements ─────────────── */
    /* Covers: paragraphs, spans, labels, captions, markdown, etc.  */
    .main .block-container,
    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown li,
    .stMarkdown strong, .stMarkdown em, .stMarkdown a,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stText"],
    p, li, td, th,
    .element-container {
        color: #1a1a1a !important;
    }

    /* ── Input / form labels ──────────────────────────────────── */
    .stTextInput > label,
    .stTextInput > div > label,
    .stSelectbox > label,
    .stSelectbox > div > label,
    .stDateInput > label,
    .stNumberInput > label,
    .stTextArea > label,
    .stRadio > label,
    .stCheckbox > label,
    .stSlider > label,
    .stMultiSelect > label,
    label { color: #1a1a1a !important; }

    /* ── Input field text ─────────────────────────────────────── */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    .stSelectbox select,
    input, textarea, select {
        color: #1a1a1a !important;
        background-color: #ffffff !important;
    }

    /* ── Selectbox / dropdown options ────────────────────────── */
    [data-baseweb="select"] span,
    [data-baseweb="select"] div,
    [data-baseweb="menu"] li,
    [data-baseweb="menu"] span {
        color: #1a1a1a !important;
    }

    /* ── Tab labels ───────────────────────────────────────────── */
    .stTabs [data-baseweb="tab"] {
        color: #444444 !important;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #1a5c2a !important;
    }

    /* ── Metric cards ─────────────────────────────────────────── */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid #c8e6c9;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.07);
    }
    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricValue"],
    [data-testid="stMetricDelta"] {
        color: #1a1a1a !important;
    }

    /* ── Alert / info / warning / error boxes ─────────────────── */
    .stAlert, .stAlert p, .stAlert div, .stAlert span,
    [data-testid="stAlert"], [data-testid="stAlert"] p,
    [data-testid="stAlert"] span {
        color: #1a1a1a !important;
    }

    /* ── Caption / small text ─────────────────────────────────── */
    .stCaption, .stCaption p,
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p {
        color: #555555 !important;
    }

    /* ── DataTable / DataFrame text ───────────────────────────── */
    .stDataFrame { border-radius: 8px; overflow: hidden; }
    .stDataFrame td, .stDataFrame th,
    [data-testid="stDataFrameResizable"] td,
    [data-testid="stDataFrameResizable"] th {
        color: #1a1a1a !important;
    }

    /* ── Headers ─────────────────────────────────────────────── */
    h1 { color: #1a5c2a !important; }
    h2 { color: #2e7d42 !important; }
    h3 { color: #388e3c !important; }
    h4, h5, h6 { color: #1a1a1a !important; }

    /* ── Sidebar (keeps white text) ──────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a5c2a 0%, #2e7d42 100%);
    }
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] *,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div {
        color: white !important;
    }
    [data-testid="stSidebar"] .stRadio label { color: white !important; }
    [data-testid="stSidebar"] input {
        color: #1a1a1a !important;
        background-color: rgba(255,255,255,0.9) !important;
    }

    /* ── Status badges ───────────────────────────────────────── */
    .badge-menunggu { background:#fff3cd; color:#856404 !important; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:600; }
    .badge-diproses { background:#cce5ff; color:#004085 !important; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:600; }
    .badge-kirim    { background:#d4edda; color:#155724 !important; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:600; }
    .badge-selesai  { background:#d1ecf1; color:#0c5460 !important; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:600; }
    .badge-gagal    { background:#f8d7da; color:#721c24 !important; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:600; }

    /* ── Info box ─────────────────────────────────────────────── */
    .info-box {
        background: white; border-left: 4px solid #2e7d42;
        border-radius: 8px; padding: 16px; margin: 8px 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.07);
        color: #1a1a1a !important;
    }
    .info-box p, .info-box span, .info-box div {
        color: #1a1a1a !important;
    }

    /* ── Button ──────────────────────────────────────────────── */
    .stButton > button {
        background: #2e7d42 !important; color: white !important;
        border: none; border-radius: 8px; font-weight: 600;
    }
    .stButton > button:hover { background: #1a5c2a !important; }

    /* ── Divider ─────────────────────────────────────────────── */
    hr { border-color: #c8e6c9; }
</style>
""", unsafe_allow_html=True)


# ── DB Connection — DUA DATABASE TERPISAH ──────────────────────────
# logistik_db  : milik sistem Logistik (shipments, couriers, vehicles, dst)
# panennet     : milik sistem Panen.net — HANYA dibaca (read-only) dari sini
#                untuk mengambil data order (alamat, pembeli, dll).
# Kedua sistem TIDAK berbagi satu koneksi/FK — ini representasi
# multi-sistem yang sesungguhnya: dua aplikasi, dua database, saling
# bertukar data lewat query lintas-koneksi yang dikelola di level Python.

def get_logistik_connection():
    """Koneksi ke database milik sistem Logistik."""
    return mysql.connector.connect(
        option_files=os.path.expanduser('~/.my.cnf'),
        database='logistik_db',
        autocommit=True
    )

def get_panennet_connection():
    """Koneksi read-only ke database milik Panen.net (sistem lain)."""
    return mysql.connector.connect(
        option_files=os.path.expanduser('~/.my.cnf'),
        database='panennet',
        autocommit=True
    )

def get_db():
    try:
        conn = get_logistik_connection()
        if conn is None:
            return None
        if not conn.is_connected():
            conn.reconnect(attempts=3, delay=1)
        return conn
    except Error as e:
        st.error(f"❌ Koneksi database logistik gagal: {e}")
        return None

def get_panennet_db():
    try:
        conn = get_panennet_connection()
        if conn is None:
            return None
        if not conn.is_connected():
            conn.reconnect(attempts=3, delay=1)
        return conn
    except Error as e:
        st.error(f"❌ Koneksi ke database Panen.net gagal: {e}")
        return None

def run_query(sql, params=None, fetch=True):
    """Query ke database LOGISTIK (logistik_db)."""
    conn = get_db()
    if conn is None:
        st.error("❌ Tidak dapat terhubung ke database logistik.")
        return [] if fetch else None

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params or ())
        if fetch:
            return cursor.fetchall()
        return cursor.lastrowid
    except Exception as e:
        st.error(f"Query error (logistik_db): {e}")
        return [] if fetch else None
    finally:
        cursor.close()
        conn.close()

def run_panennet_query(sql, params=None, fetch=True):
    """Query ke database PANEN.NET (panennet) — dipakai untuk membaca
    data order dari sistem lain. Idealnya hanya SELECT/UPDATE status
    pengiriman, tidak pernah mengubah data inti milik Panen.net."""
    conn = get_panennet_db()
    if conn is None:
        st.warning("⚠️ Tidak dapat terhubung ke database Panen.net. "
                    "Data order dari Panen.net tidak dapat dimuat.")
        return [] if fetch else None

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params or ())
        if fetch:
            return cursor.fetchall()
        return cursor.lastrowid
    except Exception as e:
        st.error(f"Query error (panennet): {e}")
        return [] if fetch else None
    finally:
        cursor.close()
        conn.close()

def get_orders_map(order_ids):
    """Ambil beberapa order dari panennet sekaligus, dikembalikan
    sebagai dict {order_id: row} agar mudah di-'join' secara manual
    di sisi Python (pengganti SQL JOIN lintas-database)."""
    order_ids = [oid for oid in set(order_ids) if oid is not None]
    if not order_ids:
        return {}
    placeholders = ",".join(["%s"] * len(order_ids))
    rows = run_panennet_query(
        f"SELECT * FROM orders WHERE order_id IN ({placeholders})",
        order_ids
    )
    return {r['order_id']: r for r in rows} if rows else {}

def generate_resi():
    today = datetime.now().strftime("%Y%m%d")
    rand = ''.join(random.choices(string.digits, k=4))
    return f"HKE-{today}{rand}"

# ══════════════════════════════════════════════════════════════════
# SIDEBAR — LOGIN & NAVIGASI
# ══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## 🚚 HijauKirim Express")
    st.markdown("**Sistem Manajemen Logistik**")
    st.markdown("---")

    # Simple session login
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.company_id = 1
        st.session_state.company_name = ""

    if not st.session_state.logged_in:
        st.markdown("### 🔐 Login")
        username = st.text_input("Username", placeholder="admin")
        password = st.text_input("Password", type="password", placeholder="••••••")
        if st.button("Masuk", use_container_width=True):
            # Simple demo auth — ganti dengan auth DB di production
            if username == "hijaukirim" and password == "logistik123":
                st.session_state.logged_in = True
                st.session_state.company_id = 1
                st.session_state.company_name = "HijauKirim Express"
                st.rerun()
            elif username == "taniantar" and password == "logistik123":
                st.session_state.logged_in = True
                st.session_state.company_id = 2
                st.session_state.company_name = "TaniAntar Nusantara"
                st.rerun()
            else:
                st.error("Username/password salah")
        st.markdown("---")
        st.caption("Demo: hijaukirim / logistik123")
        st.stop()

    # ── Navigasi ──────────────────────────────────────────────────
    st.markdown(f"👤 **{st.session_state.company_name}**")
    st.markdown("---")

    menu = st.radio(
        "Navigasi",
        [
            "📊 Dashboard",
            "📦 Manajemen Pengiriman",
            "👤 Manajemen Kurir",
            "🚗 Manajemen Armada",
            "📍 Tracking & Riwayat",
            "📈 Laporan & Analitik",
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    st.caption(f"© 2026 {st.session_state.company_name}")

company_id = st.session_state.company_id

# ══════════════════════════════════════════════════════════════════
# HALAMAN 1 — DASHBOARD OVERVIEW
# ══════════════════════════════════════════════════════════════════

if menu == "📊 Dashboard":
    st.title("📊 Dashboard Overview")
    st.markdown(f"**{date.today().strftime('%A, %d %B %Y')}** |  {st.session_state.company_name}")
    st.markdown("---")

    # ── KPI Cards ─────────────────────────────────────────────────
    today = date.today().isoformat()

    total_shipments = run_query(
        "SELECT COUNT(*) AS c FROM shipments WHERE company_id=%s", (company_id,)
    )
    hari_ini = run_query(
        "SELECT COUNT(*) AS c FROM shipments WHERE company_id=%s AND DATE(tgl_dibuat)=%s",
        (company_id, today)
    )
    dalam_pengiriman = run_query(
        "SELECT COUNT(*) AS c FROM shipments WHERE company_id=%s AND status='Dalam Pengiriman'",
        (company_id,)
    )
    terkirim_bulan = run_query(
        "SELECT COUNT(*) AS c FROM shipments WHERE company_id=%s AND status='Terkirim' AND MONTH(tgl_terkirim)=MONTH(CURDATE())",
        (company_id,)
    )
    menunggu = run_query(
        "SELECT COUNT(*) AS c FROM shipments WHERE company_id=%s AND status='Menunggu Pickup'",
        (company_id,)
    )
    revenue = run_query(
        "SELECT COALESCE(SUM(ongkos_kirim),0) AS r FROM shipments WHERE company_id=%s AND MONTH(tgl_dibuat)=MONTH(CURDATE())",
        (company_id,)
    )
    kurir_aktif = run_query(
        "SELECT COUNT(*) AS c FROM couriers WHERE company_id=%s AND status != 'Tidak Aktif'",
        (company_id,)
    )
    armada_tersedia = run_query(
        "SELECT COUNT(*) AS c FROM vehicles WHERE company_id=%s AND status='Tersedia'",
        (company_id,)
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📦 Total Pengiriman", total_shipments[0]['c'] if total_shipments else 0)
    with col2:
        st.metric("🔄 Dalam Pengiriman", dalam_pengiriman[0]['c'] if dalam_pengiriman else 0)
    with col3:
        st.metric("✅ Terkirim Bulan Ini", terkirim_bulan[0]['c'] if terkirim_bulan else 0)
    with col4:
        st.metric("⏳ Menunggu Pickup", menunggu[0]['c'] if menunggu else 0)

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        rev = revenue[0]['r'] if revenue else 0
        st.metric("💰 Revenue Bulan Ini", f"Rp {int(rev):,}".replace(",", "."))
    with col6:
        st.metric("👤 Kurir Aktif", kurir_aktif[0]['c'] if kurir_aktif else 0)
    with col7:
        st.metric("🚗 Armada Tersedia", armada_tersedia[0]['c'] if armada_tersedia else 0)
    with col8:
        st.metric("📬 Order Baru Hari Ini", hari_ini[0]['c'] if hari_ini else 0)

    st.markdown("---")

    # ── Distribusi Status Pengiriman ──────────────────────────────
    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.subheader("📊 Distribusi Status Pengiriman")
        status_data = run_query(
            "SELECT status, COUNT(*) AS jumlah FROM shipments WHERE company_id=%s GROUP BY status",
            (company_id,)
        )
        if status_data:
            df_status = pd.DataFrame(status_data)
            st.bar_chart(df_status.set_index("status")["jumlah"])
        else:
            st.info("Belum ada data pengiriman.")

    with col_b:
        st.subheader("🚀 Pengiriman Terbaru")
        recent = run_query("""
            SELECT s.kode_resi, s.nama_penerima, s.kota, s.status,
                   DATE(s.tgl_dibuat) AS tanggal,
                   COALESCE(c.nama_kurir, '-') AS kurir
            FROM shipments s
            LEFT JOIN couriers c ON s.courier_id = c.courier_id
            WHERE s.company_id = %s
            ORDER BY s.tgl_dibuat DESC LIMIT 8
        """, (company_id,))
        if recent:
            df_recent = pd.DataFrame(recent)
            df_recent.columns = ["Resi", "Penerima", "Kota", "Status", "Tanggal", "Kurir"]
            st.dataframe(df_recent, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada pengiriman.")

    st.markdown("---")

    # ── Order Baru dari Panen.net yang Belum Diproses ─────────────
    st.subheader("🌾 Order dari Panen.net yang Belum Dibuat Pengiriman")

    # 1) Ambil order yang sudah dibayar & belum diproses dari PANENNET
    panennet_orders = run_panennet_query("""
        SELECT o.order_id, o.order_code, o.pembeli, o.no_telepon,
               o.total, o.status, o.alamat_pengiriman, o.kota,
               s.nama_toko
        FROM orders o
        JOIN sellers s ON o.seller_id = s.seller_id
        WHERE o.shipping_status = 'Belum Diproses'
          AND o.status NOT IN ('Menunggu Bayar', 'Dibatalkan')
        ORDER BY o.created_at DESC
    """)

    # 2) Ambil order_id yang SUDAH punya shipment dari LOGISTIK_DB
    existing_shipment_orders = run_query("SELECT DISTINCT order_id FROM shipments")
    existing_ids = {r['order_id'] for r in existing_shipment_orders} if existing_shipment_orders else set()

    # 3) Gabungkan secara manual di Python (pengganti SQL JOIN lintas-DB)
    new_orders = [o for o in (panennet_orders or []) if o['order_id'] not in existing_ids]

    if new_orders:
        df_new = pd.DataFrame(new_orders)
        df_new = df_new[["order_id", "order_code", "pembeli", "no_telepon", "total", "status", "alamat_pengiriman", "kota", "nama_toko"]]
        df_new.columns = ["ID", "Kode Order", "Pembeli", "Telepon", "Total (Rp)", "Status Order", "Alamat", "Kota", "Toko"]
        st.dataframe(df_new, use_container_width=True, hide_index=True)
        st.info(f"💡 Ada **{len(new_orders)} order** menunggu dibuatkan pengiriman. Buka menu **Manajemen Pengiriman** untuk memproses.")
    else:
        st.success("✅ Semua order sudah diproses!")


# ══════════════════════════════════════════════════════════════════
# HALAMAN 2 — MANAJEMEN PENGIRIMAN
# ══════════════════════════════════════════════════════════════════

elif menu == "📦 Manajemen Pengiriman":
    st.title("📦 Manajemen Pengiriman")
    st.markdown("Lihat, buat, dan update status pengiriman dari order Panen.net.")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📋 Daftar Pengiriman", "➕ Buat Pengiriman Baru", "✏️ Update Status"])

    # ── Tab 1: Daftar Pengiriman ───────────────────────────────────
    with tab1:
        col_f1, col_f2 = st.columns([1, 3])
        with col_f1:
            filter_status = st.selectbox("Filter Status", [
                "Semua", "Menunggu Pickup", "Dipickup", "Di Gudang",
                "Dalam Pengiriman", "Tiba di Tujuan", "Terkirim",
                "Gagal Kirim", "Dikembalikan"
            ])
        with col_f2:
            search = st.text_input("🔍 Cari resi / nama penerima / kota", placeholder="HKE-... atau nama...")

        sql = """
            SELECT s.shipment_id, s.kode_resi, s.order_id, s.order_code,
                   s.nama_penerima, s.no_telepon, s.kota, s.provinsi,
                   s.berat_kg, s.ongkos_kirim, s.status,
                   COALESCE(c.nama_kurir, '-') AS kurir,
                   DATE(s.tgl_dibuat) AS tgl_buat,
                   s.estimasi_tiba
            FROM shipments s
            LEFT JOIN couriers c ON s.courier_id = c.courier_id
            WHERE s.company_id = %s
        """
        params = [company_id]

        if filter_status != "Semua":
            sql += " AND s.status = %s"
            params.append(filter_status)
        if search:
            sql += " AND (s.kode_resi LIKE %s OR s.nama_penerima LIKE %s OR s.kota LIKE %s)"
            params += [f"%{search}%", f"%{search}%", f"%{search}%"]

        sql += " ORDER BY s.tgl_dibuat DESC"
        rows = run_query(sql, params)
        # Catatan: order_code sudah tersimpan langsung di tabel shipments
        # (disalin saat shipment dibuat), jadi TIDAK perlu JOIN ke panennet
        # untuk menampilkan daftar ini — lebih cepat & tidak bergantung
        # pada koneksi ke sistem lain.

        if rows:
            df = pd.DataFrame(rows)
            df = df[["shipment_id", "kode_resi", "order_code", "nama_penerima", "no_telepon",
                     "kota", "provinsi", "berat_kg", "ongkos_kirim", "status", "kurir",
                     "tgl_buat", "estimasi_tiba"]]
            df.columns = ["ID", "No. Resi", "Kode Order", "Penerima", "Telepon",
                          "Kota", "Provinsi", "Berat (kg)", "Ongkir (Rp)",
                          "Status", "Kurir", "Tgl Buat", "Est. Tiba"]
            df["Ongkir (Rp)"] = df["Ongkir (Rp)"].apply(lambda x: f"Rp {int(x):,}".replace(",", "."))
            st.dataframe(df.drop(columns=["ID"]), use_container_width=True, hide_index=True)
            st.caption(f"Menampilkan {len(rows)} pengiriman")
        else:
            st.info("Tidak ada data pengiriman yang sesuai filter.")

    # ── Tab 2: Buat Pengiriman Baru ────────────────────────────────
    with tab2:
        st.subheader("➕ Buat Pengiriman dari Order Panen.net")

        # 1) Ambil order yang sudah dibayar dari PANENNET (sistem lain)
        panennet_pending = run_panennet_query("""
            SELECT o.order_id, o.order_code, o.pembeli, o.no_telepon,
                   o.alamat_pengiriman, o.kota, o.provinsi, o.kode_pos, o.berat_total
            FROM orders o
            WHERE o.status NOT IN ('Menunggu Bayar', 'Dibatalkan')
            ORDER BY o.created_at DESC
        """)

        # 2) Ambil order_id yang SUDAH ada shipment-nya dari LOGISTIK_DB
        already_shipped = run_query("SELECT DISTINCT order_id FROM shipments")
        shipped_ids = {r['order_id'] for r in already_shipped} if already_shipped else set()

        # 3) Saring manual di Python — pengganti "NOT EXISTS" lintas-database
        pending_orders = [o for o in (panennet_pending or []) if o['order_id'] not in shipped_ids]
        for o in pending_orders:
            o['label'] = f"{o['order_code']} — {o['pembeli']} ({o['kota']})"

        if not pending_orders:
            st.success("✅ Tidak ada order baru yang perlu dibuatkan pengiriman.")
        else:
            order_map = {r['label']: r for r in pending_orders}
            selected_label = st.selectbox("Pilih Order dari Panen.net", list(order_map.keys()))
            selected = order_map[selected_label]

            st.markdown("**📋 Info Penerima (dari Panen.net):**")
            col1, col2 = st.columns(2)
            with col1:
                nama = st.text_input("Nama Penerima", value=selected['pembeli'] or "")
                telepon = st.text_input("No. Telepon", value=selected['no_telepon'] or "")
                alamat = st.text_area("Alamat Lengkap", value=selected['alamat_pengiriman'] or "")
            with col2:
                kota = st.text_input("Kota", value=selected['kota'] or "")
                provinsi = st.text_input("Provinsi", value=selected['provinsi'] or "")
                kode_pos = st.text_input("Kode Pos", value=selected['kode_pos'] or "")

            st.markdown("**🚚 Info Pengiriman:**")
            col3, col4 = st.columns(2)
            with col3:
                berat = st.number_input("Berat Paket (kg)", min_value=0.1, value=max(float((selected['berat_total'] or 1000)) / 1000, 0.1), step=0.1)
                ongkir = st.number_input("Ongkos Kirim (Rp)", min_value=0, value=25000, step=5000)
            with col4:
                estimasi = st.date_input("Estimasi Tiba", value=date.today() + timedelta(days=3))
                catatan = st.text_area("Catatan", placeholder="Opsional...")

            # Pilih kurir & kendaraan (dari logistik_db)
            couriers_avail = run_query(
                "SELECT courier_id, nama_kurir, status FROM couriers WHERE company_id=%s AND status='Aktif'",
                (company_id,)
            )
            vehicles_avail = run_query(
                "SELECT vehicle_id, nomor_polisi, jenis_kendaraan, kapasitas_kg FROM vehicles WHERE company_id=%s AND status='Tersedia'",
                (company_id,)
            )

            col5, col6 = st.columns(2)
            with col5:
                courier_opt = {f"{r['nama_kurir']} ({r['status']})": r['courier_id'] for r in couriers_avail}
                courier_opt["— Belum assign —"] = None
                sel_kurir_label = st.selectbox("Assign Kurir", list(courier_opt.keys()))
                sel_kurir_id = courier_opt[sel_kurir_label]
            with col6:
                vehicle_opt = {f"{r['nomor_polisi']} — {r['jenis_kendaraan']} ({r['kapasitas_kg']}kg)": r['vehicle_id'] for r in vehicles_avail}
                vehicle_opt["— Belum assign —"] = None
                sel_vehicle_label = st.selectbox("Assign Kendaraan", list(vehicle_opt.keys()))
                sel_vehicle_id = vehicle_opt[sel_vehicle_label]

            if st.button("💾 Buat Pengiriman", use_container_width=True):
                kode_resi = generate_resi()
                now = datetime.now()

                # 1) Tulis shipment baru ke LOGISTIK_DB
                #    order_id & order_code disimpan sebagai REFERENSI saja
                run_query(
                    """
                        INSERT INTO shipments (
                            order_id, order_code, company_id, courier_id, vehicle_id,
                            kode_resi, nama_penerima, no_telepon, alamat, kota,
                            provinsi, kode_pos, berat_kg, ongkos_kirim,
                            estimasi_tiba, status, catatan, tgl_dibuat
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        selected['order_id'], selected['order_code'], company_id, sel_kurir_id, sel_vehicle_id,
                        kode_resi, nama, telepon, alamat, kota,
                        provinsi, kode_pos, berat, ongkir, estimasi,
                        "Menunggu Pickup", catatan or None, now
                    ),
                    fetch=False
                )

                # 2) Sinkronkan status ke PANENNET (sistem lain) —
                #    ini satu-satunya tulis-silang yang dilakukan logistik
                #    ke database Panen.net, sebatas kolom status pengiriman.
                run_panennet_query(
                    "UPDATE orders SET shipping_status=%s, status=%s WHERE order_id=%s",
                    ("Menunggu Pickup", "Dikirim", selected['order_id']),
                    fetch=False
                )

                st.success(f"✅ Pengiriman baru berhasil dibuat dengan resi **{kode_resi}**")
                st.rerun()

    # ── Tab 3: Update Status ───────────────────────────────────────
    with tab3:
        st.subheader("✏️ Update Status Pengiriman")

        resi_input = st.text_input("Masukkan No. Resi", placeholder="HKE-20260600XX")

        if resi_input:
            ship = run_query("""
                SELECT s.*, COALESCE(c.nama_kurir,'-') AS kurir_nama
                FROM shipments s
                LEFT JOIN couriers c ON s.courier_id = c.courier_id
                WHERE s.kode_resi = %s AND s.company_id = %s
            """, (resi_input, company_id))
            # order_code sudah ada langsung di tabel shipments (kolom s.order_code)
            # jadi tidak perlu JOIN ke panennet untuk menampilkan info ini.

            if not ship:
                st.warning("Resi tidak ditemukan atau bukan milik perusahaan ini.")
            else:
                s = ship[0]
                col_i1, col_i2, col_i3 = st.columns(3)
                col_i1.markdown(f"**Order:** `{s['order_code']}`")
                col_i2.markdown(f"**Penerima:** {s['nama_penerima']}")
                col_i3.markdown(f"**Status Saat Ini:** `{s['status']}`")

                status_flow = [
                    "Menunggu Pickup", "Dipickup", "Di Gudang",
                    "Dalam Pengiriman", "Tiba di Tujuan",
                    "Terkirim", "Gagal Kirim", "Dikembalikan"
                ]

                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    new_status = st.selectbox("Status Baru", status_flow,
                                              index=status_flow.index(s['status']) if s['status'] in status_flow else 0)
                    lokasi = st.text_input("Lokasi Saat Ini", placeholder="Misal: Gudang Bandung / Tol KM 100")
                with col_u2:
                    keterangan = st.text_area("Keterangan", placeholder="Opsional...")
                    updated_by = st.text_input("Diupdate Oleh", value=s['kurir_nama'])

                if st.button("💾 Simpan Update Status", use_container_width=True):
                    # 1) Update di LOGISTIK_DB
                    now = datetime.now()
                    extra_sql = ""
                    extra_params = []
                    if new_status == "Dipickup":
                        extra_sql = ", tgl_pickup=%s"
                        extra_params = [now]
                    elif new_status == "Dalam Pengiriman":
                        extra_sql = ", tgl_dikirim=%s"
                        extra_params = [now]
                    elif new_status == "Terkirim":
                        extra_sql = ", tgl_terkirim=%s"
                        extra_params = [now]

                    run_query(
                        f"UPDATE shipments SET status=%s{extra_sql} WHERE shipment_id=%s",
                        [new_status] + extra_params + [s['shipment_id']], fetch=False
                    )

                    # 2) Insert log di LOGISTIK_DB
                    run_query("""
                        INSERT INTO delivery_logs (shipment_id, status_baru, lokasi, keterangan, updated_by)
                        VALUES (%s,%s,%s,%s,%s)
                    """, (s['shipment_id'], new_status, lokasi or None, keterangan or None, updated_by), fetch=False)

                    # 3) Sinkronkan ke PANENNET (sistem lain, koneksi terpisah)
                    sync_map = {
                        "Menunggu Pickup": "Menunggu Pickup",
                        "Dalam Pengiriman": "Dalam Pengiriman",
                        "Terkirim": "Terkirim",
                        "Gagal Kirim": "Gagal Kirim",
                    }
                    if new_status in sync_map:
                        run_panennet_query(
                            "UPDATE orders SET shipping_status=%s WHERE order_id=%s",
                            (sync_map[new_status], s['order_id']), fetch=False
                        )

                    st.success(f"✅ Status diupdate menjadi **{new_status}**")
                    st.rerun()


# ══════════════════════════════════════════════════════════════════
# HALAMAN 3 — MANAJEMEN KURIR
# ══════════════════════════════════════════════════════════════════

elif menu == "👤 Manajemen Kurir":
    st.title("👤 Manajemen Kurir")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📋 Daftar Kurir", "➕ Tambah Kurir", "🔗 Assign ke Pengiriman"])

    # ── Tab 1: Daftar Kurir ───────────────────────────────────────
    with tab1:
        couriers = run_query("""
            SELECT c.courier_id, c.nama_kurir, c.no_telepon, c.email,
                   c.status, c.total_pengiriman, c.rating,
                   COALESCE(v.nomor_polisi, '-') AS kendaraan,
                   COALESCE(v.jenis_kendaraan, '-') AS jenis_kendaraan
            FROM couriers c
            LEFT JOIN vehicles v ON c.vehicle_id = v.vehicle_id
            WHERE c.company_id = %s
            ORDER BY c.nama_kurir
        """, (company_id,))

        if couriers:
            df_c = pd.DataFrame(couriers)
            df_c.columns = ["ID", "Nama Kurir", "Telepon", "Email", "Status",
                            "Total Kirim", "Rating", "Kendaraan", "Jenis"]
            df_c = df_c.drop(columns=["ID"])
            df_c["Rating"] = df_c["Rating"].apply(lambda x: f"⭐ {x:.1f}")

            # Color status
            def style_status(val):
                colors = {
                    "Aktif": "background-color:#d4edda; color:#155724",
                    "Sedang Bertugas": "background-color:#cce5ff; color:#004085",
                    "Tidak Aktif": "background-color:#f8d7da; color:#721c24",
                }
                return colors.get(val, "")

            styled = df_c.style.map(style_status, subset=["Status"])
            st.dataframe(styled, use_container_width=True, hide_index=True)

            # Summary
            col1, col2, col3 = st.columns(3)
            aktif = sum(1 for r in couriers if r['status'] == 'Aktif')
            bertugas = sum(1 for r in couriers if r['status'] == 'Sedang Bertugas')
            col1.metric("✅ Kurir Aktif", aktif)
            col2.metric("🔄 Sedang Bertugas", bertugas)
            col3.metric("⭐ Rating Rata-rata",
                        f"{sum(r['rating'] for r in couriers)/len(couriers):.1f}" if couriers else "0")
        else:
            st.info("Belum ada kurir terdaftar.")

    # ── Tab 2: Tambah Kurir ───────────────────────────────────────
    with tab2:
        st.subheader("➕ Tambah Kurir Baru")
        with st.form("form_kurir"):
            col1, col2 = st.columns(2)
            with col1:
                nama_k = st.text_input("Nama Lengkap *")
                telepon_k = st.text_input("No. Telepon *")
                email_k = st.text_input("Email")
            with col2:
                no_ktp = st.text_input("No. KTP *")
                status_k = st.selectbox("Status Awal", ["Aktif", "Tidak Aktif"])

            vehicles_all = run_query(
                "SELECT vehicle_id, nomor_polisi, jenis_kendaraan FROM vehicles WHERE company_id=%s AND status='Tersedia'",
                (company_id,)
            )
            v_opts = {"— Tidak ada / belum assign —": None}
            v_opts.update({f"{v['nomor_polisi']} ({v['jenis_kendaraan']})": v['vehicle_id'] for v in vehicles_all})
            sel_v = st.selectbox("Kendaraan", list(v_opts.keys()))

            submitted = st.form_submit_button("💾 Simpan Kurir", use_container_width=True)
            if submitted:
                if not nama_k or not telepon_k or not no_ktp:
                    st.error("Nama, telepon, dan No. KTP wajib diisi.")
                else:
                    run_query("""
                        INSERT INTO couriers (company_id, nama_kurir, no_telepon, email, no_ktp, vehicle_id, status)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)
                    """, (company_id, nama_k, telepon_k, email_k or None, no_ktp, v_opts[sel_v], status_k), fetch=False)
                    st.success(f"✅ Kurir **{nama_k}** berhasil ditambahkan!")
                    st.rerun()

    # ── Tab 3: Assign ke Pengiriman ───────────────────────────────
    with tab3:
        st.subheader("🔗 Assign Kurir ke Pengiriman")

        unassigned = run_query("""
            SELECT s.shipment_id, s.kode_resi, s.nama_penerima, s.kota, s.status
            FROM shipments s
            WHERE s.company_id = %s AND s.courier_id IS NULL
              AND s.status NOT IN ('Terkirim','Gagal Kirim','Dikembalikan')
            ORDER BY s.tgl_dibuat
        """, (company_id,))

        if not unassigned:
            st.success("✅ Semua pengiriman sudah memiliki kurir.")
        else:
            st.warning(f"Ada **{len(unassigned)}** pengiriman belum memiliki kurir.")
            ship_opts = {f"{r['kode_resi']} — {r['nama_penerima']} ({r['kota']})": r['shipment_id'] for r in unassigned}
            sel_ship = st.selectbox("Pilih Pengiriman", list(ship_opts.keys()))

            avail_couriers = run_query(
                "SELECT courier_id, nama_kurir, rating FROM couriers WHERE company_id=%s AND status='Aktif'",
                (company_id,)
            )
            if not avail_couriers:
                st.error("Tidak ada kurir aktif yang tersedia.")
            else:
                c_opts = {f"{r['nama_kurir']} (⭐{r['rating']:.1f})": r['courier_id'] for r in avail_couriers}
                sel_c = st.selectbox("Pilih Kurir", list(c_opts.keys()))

                if st.button("✅ Assign Kurir", use_container_width=True):
                    run_query(
                        "UPDATE shipments SET courier_id=%s WHERE shipment_id=%s",
                        (c_opts[sel_c], ship_opts[sel_ship]), fetch=False
                    )
                    run_query(
                        "UPDATE couriers SET status='Sedang Bertugas' WHERE courier_id=%s",
                        (c_opts[sel_c],), fetch=False
                    )
                    st.success("✅ Kurir berhasil diassign!")
                    st.rerun()


# ══════════════════════════════════════════════════════════════════
# HALAMAN 4 — MANAJEMEN ARMADA
# ══════════════════════════════════════════════════════════════════

elif menu == "🚗 Manajemen Armada":
    st.title("🚗 Manajemen Armada / Kendaraan")
    st.markdown("---")

    tab1, tab2 = st.tabs(["📋 Daftar Armada", "➕ Tambah Kendaraan"])

    with tab1:
        vehicles = run_query("""
            SELECT v.vehicle_id, v.nomor_polisi, v.jenis_kendaraan,
                   v.kapasitas_kg, v.status,
                   COALESCE(c.nama_kurir, '-') AS kurir_pakai,
                   (SELECT COUNT(*) FROM shipments s
                    WHERE s.vehicle_id = v.vehicle_id AND s.status NOT IN ('Terkirim','Gagal Kirim','Dikembalikan')
                   ) AS aktif_pengiriman
            FROM vehicles v
            LEFT JOIN couriers c ON c.vehicle_id = v.vehicle_id AND c.status='Sedang Bertugas'
            WHERE v.company_id = %s
            ORDER BY v.jenis_kendaraan, v.nomor_polisi
        """, (company_id,))

        if vehicles:
            # Summary cards
            col1, col2, col3, col4 = st.columns(4)
            tersedia = sum(1 for v in vehicles if v['status'] == 'Tersedia')
            dipakai = sum(1 for v in vehicles if v['status'] == 'Dipakai')
            maintenance = sum(1 for v in vehicles if v['status'] == 'Maintenance')
            col1.metric("🚗 Total Armada", len(vehicles))
            col2.metric("✅ Tersedia", tersedia)
            col3.metric("🔄 Dipakai", dipakai)
            col4.metric("🔧 Maintenance", maintenance)

            st.markdown("---")

            # Tampilkan per jenis kendaraan
            for jenis in ["Motor", "Mobil Pick-up", "Van", "Truck"]:
                subset = [v for v in vehicles if v['jenis_kendaraan'] == jenis]
                if subset:
                    icon = {"Motor": "🏍️", "Mobil Pick-up": "🛻", "Van": "🚐", "Truck": "🚛"}.get(jenis, "🚗")
                    st.subheader(f"{icon} {jenis} ({len(subset)} unit)")
                    df_v = pd.DataFrame(subset)
                    df_v = df_v[["nomor_polisi", "kapasitas_kg", "status", "kurir_pakai", "aktif_pengiriman"]]
                    df_v.columns = ["No. Polisi", "Kapasitas (kg)", "Status", "Kurir Aktif", "Pengiriman Aktif"]

                    def style_v_status(val):
                        colors = {
                            "Tersedia": "background-color:#d4edda;color:#155724",
                            "Dipakai": "background-color:#cce5ff;color:#004085",
                            "Maintenance": "background-color:#fff3cd;color:#856404"
                        }
                        return colors.get(val, "")

                    st.dataframe(
                        df_v.style.map(style_v_status, subset=["Status"]),
                        use_container_width=True, hide_index=True
                    )
        else:
            st.info("Belum ada kendaraan terdaftar.")

        # ── Update Status Kendaraan ───────────────────────────────
        st.markdown("---")
        st.subheader("🔧 Update Status Kendaraan")
        if vehicles:
            v_opts = {f"{v['nomor_polisi']} — {v['jenis_kendaraan']} (saat ini: {v['status']})": v['vehicle_id'] for v in vehicles}
            sel_v = st.selectbox("Pilih Kendaraan", list(v_opts.keys()))
            new_v_status = st.selectbox("Status Baru", ["Tersedia", "Dipakai", "Maintenance"])
            if st.button("💾 Update Status Armada"):
                run_query(
                    "UPDATE vehicles SET status=%s WHERE vehicle_id=%s",
                    (new_v_status, v_opts[sel_v]), fetch=False
                )
                st.success("✅ Status kendaraan diupdate!")
                st.rerun()

    with tab2:
        st.subheader("➕ Tambah Kendaraan Baru")
        with st.form("form_vehicle"):
            col1, col2 = st.columns(2)
            with col1:
                nopol = st.text_input("Nomor Polisi *", placeholder="B 1234 ABC")
                jenis_v = st.selectbox("Jenis Kendaraan", ["Motor", "Mobil Pick-up", "Van", "Truck"])
            with col2:
                kapasitas = st.number_input("Kapasitas Maksimum (kg) *", min_value=1, value=50)
                status_v = st.selectbox("Status Awal", ["Tersedia", "Maintenance"])

            submitted_v = st.form_submit_button("💾 Tambah Kendaraan", use_container_width=True)
            if submitted_v:
                if not nopol:
                    st.error("Nomor polisi wajib diisi.")
                else:
                    run_query("""
                        INSERT INTO vehicles (company_id, nomor_polisi, jenis_kendaraan, kapasitas_kg, status)
                        VALUES (%s,%s,%s,%s,%s)
                    """, (company_id, nopol.upper(), jenis_v, kapasitas, status_v), fetch=False)
                    st.success(f"✅ Kendaraan **{nopol.upper()}** berhasil ditambahkan!")
                    st.rerun()


# ══════════════════════════════════════════════════════════════════
# HALAMAN 5 — TRACKING & RIWAYAT
# ══════════════════════════════════════════════════════════════════

elif menu == "📍 Tracking & Riwayat":
    st.title("📍 Tracking & Riwayat Pengiriman")
    st.markdown("---")

    tab1, tab2 = st.tabs(["🔍 Lacak Pengiriman", "📜 Riwayat Lengkap"])

    # ── Tab 1: Lacak per Resi ──────────────────────────────────────
    with tab1:
        resi_track = st.text_input("🔍 Masukkan No. Resi", placeholder="HKE-20260600XX")
        if st.button("Lacak", use_container_width=False):
            if not resi_track:
                st.warning("Masukkan nomor resi terlebih dahulu.")
            else:
                ship_info = run_query("""
                    SELECT s.*,
                           COALESCE(c.nama_kurir,'-') AS kurir_nama,
                           COALESCE(c.no_telepon,'-') AS kurir_telp,
                           COALESCE(v.nomor_polisi,'-') AS kendaraan
                    FROM shipments s
                    LEFT JOIN couriers c ON s.courier_id = c.courier_id
                    LEFT JOIN vehicles v ON s.vehicle_id = v.vehicle_id
                    WHERE s.kode_resi = %s AND s.company_id = %s
                """, (resi_track, company_id))
                # order_code & total sudah cukup dari kolom shipments.order_code;
                # jika butuh "total" order asli, ambil terpisah dari panennet (opsional).

                if not ship_info:
                    st.error("Resi tidak ditemukan.")
                else:
                    s = ship_info[0]

                    # Header info
                    st.markdown(f"""
                    <div class="info-box">
                        <h3>📦 {s['kode_resi']}</h3>
                        <table style="width:100%">
                            <tr>
                                <td><b>Order:</b> {s['order_code']}</td>
                                <td><b>Penerima:</b> {s['nama_penerima']}</td>
                                <td><b>Status:</b> <span style="font-weight:700;color:#2e7d42">{s['status']}</span></td>
                            </tr>
                            <tr>
                                <td><b>Tujuan:</b> {s['kota']}, {s['provinsi']}</td>
                                <td><b>Kurir:</b> {s['kurir_nama']} ({s['kurir_telp']})</td>
                                <td><b>Kendaraan:</b> {s['kendaraan']}</td>
                            </tr>
                            <tr>
                                <td><b>Berat:</b> {s['berat_kg']} kg</td>
                                <td><b>Ongkir:</b> Rp {int(s['ongkos_kirim']):,}</td>
                                <td><b>Est. Tiba:</b> {s['estimasi_tiba']}</td>
                            </tr>
                        </table>
                    </div>
                    """, unsafe_allow_html=True)

                    # Timeline log
                    st.markdown("### 📍 Perjalanan Pengiriman")
                    logs = run_query("""
                        SELECT status_baru, lokasi, keterangan, updated_by,
                               tgl_update
                        FROM delivery_logs
                        WHERE shipment_id = %s
                        ORDER BY tgl_update ASC
                    """, (s['shipment_id'],))

                    status_icons = {
                        "Menunggu Pickup": "⏳",
                        "Dipickup": "📤",
                        "Di Gudang": "🏭",
                        "Dalam Pengiriman": "🚚",
                        "Tiba di Tujuan": "📍",
                        "Terkirim": "✅",
                        "Gagal Kirim": "❌",
                        "Dikembalikan": "↩️",
                    }

                    if logs:
                        for i, log in enumerate(logs):
                            icon = status_icons.get(log['status_baru'], "📌")
                            is_last = (i == len(logs) - 1)
                            color = "#2e7d42" if is_last else "#888"
                            st.markdown(f"""
                            <div style="display:flex; margin-bottom:12px; align-items:flex-start;">
                                <div style="font-size:22px; margin-right:12px;">{icon}</div>
                                <div style="border-left: 2px solid {color}; padding-left:12px; flex:1;">
                                    <b style="color:{color}">{log['status_baru']}</b><br>
                                    <span style="color:#444">{log['lokasi'] or ''}</span><br>
                                    <span style="color:#666; font-size:13px">{log['keterangan'] or ''}</span><br>
                                    <span style="color:#999; font-size:12px">
                                        {str(log['tgl_update'])[:16]} — oleh {log['updated_by']}
                                    </span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("Belum ada log perjalanan untuk pengiriman ini.")

    # ── Tab 2: Riwayat Lengkap ─────────────────────────────────────
    with tab2:
        st.subheader("📜 Riwayat Semua Pengiriman")

        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            date_from = st.date_input("Dari Tanggal", value=date.today() - timedelta(days=30))
        with col_f2:
            date_to = st.date_input("Sampai Tanggal", value=date.today())
        with col_f3:
            hist_status = st.selectbox("Status", ["Semua", "Terkirim", "Gagal Kirim", "Dikembalikan", "Dalam Pengiriman"])

        sql_hist = """
            SELECT s.kode_resi, s.order_code, s.nama_penerima,
                   s.kota, s.provinsi, s.berat_kg,
                   s.ongkos_kirim, s.status,
                   COALESCE(c.nama_kurir,'-') AS kurir,
                   DATE(s.tgl_dibuat) AS tgl_buat,
                   DATE(s.tgl_terkirim) AS tgl_terkirim
            FROM shipments s
            LEFT JOIN couriers c ON s.courier_id = c.courier_id
            WHERE s.company_id = %s
              AND DATE(s.tgl_dibuat) BETWEEN %s AND %s
        """
        params_hist = [company_id, date_from, date_to]
        if hist_status != "Semua":
            sql_hist += " AND s.status = %s"
            params_hist.append(hist_status)
        sql_hist += " ORDER BY s.tgl_dibuat DESC"

        hist_data = run_query(sql_hist, params_hist)
        if hist_data:
            df_hist = pd.DataFrame(hist_data)
            df_hist.columns = ["No. Resi", "Kode Order", "Penerima", "Kota", "Provinsi",
                               "Berat (kg)", "Ongkir (Rp)", "Status", "Kurir", "Tgl Buat", "Tgl Terkirim"]
            df_hist["Ongkir (Rp)"] = df_hist["Ongkir (Rp)"].apply(lambda x: f"Rp {int(x):,}".replace(",", "."))
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
            st.caption(f"Total: {len(hist_data)} pengiriman dalam rentang ini")
        else:
            st.info("Tidak ada data pada rentang tanggal ini.")


# ══════════════════════════════════════════════════════════════════
# HALAMAN 6 — LAPORAN & ANALITIK
# ══════════════════════════════════════════════════════════════════

elif menu == "📈 Laporan & Analitik":
    st.title("📈 Laporan & Analitik")
    st.markdown("---")

    # ── Filter Periode ─────────────────────────────────────────────
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        lap_from = st.date_input("Periode Dari", value=date.today().replace(day=1))
    with col_p2:
        lap_to = st.date_input("Periode Sampai", value=date.today())

    st.markdown("---")

    # ── KPI Periode ────────────────────────────────────────────────
    st.subheader("📊 Ringkasan Periode")

    kpi = run_query("""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN status='Terkirim' THEN 1 ELSE 0 END) AS terkirim,
            SUM(CASE WHEN status='Gagal Kirim' THEN 1 ELSE 0 END) AS gagal,
            SUM(CASE WHEN status='Dalam Pengiriman' THEN 1 ELSE 0 END) AS on_delivery,
            COALESCE(SUM(ongkos_kirim),0) AS total_revenue,
            COALESCE(AVG(berat_kg),0) AS avg_berat,
            COALESCE(SUM(CASE WHEN status='Terkirim' THEN ongkos_kirim ELSE 0 END),0) AS revenue_selesai
        FROM shipments
        WHERE company_id = %s AND DATE(tgl_dibuat) BETWEEN %s AND %s
    """, (company_id, lap_from, lap_to))

    if kpi:
        k = kpi[0]
        success_rate = (k['terkirim'] / k['total'] * 100) if k['total'] > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📦 Total Pengiriman", k['total'])
        col2.metric("✅ Terkirim", int(k['terkirim'] or 0))
        col3.metric("❌ Gagal", int(k['gagal'] or 0))
        col4.metric("📈 Success Rate", f"{success_rate:.1f}%")

        col5, col6, col7, col8 = st.columns(4)
        col5.metric("💰 Total Revenue", f"Rp {int(k['total_revenue']):,}".replace(",", "."))
        col6.metric("💵 Revenue Selesai", f"Rp {int(k['revenue_selesai']):,}".replace(",", "."))
        col7.metric("⚖️ Avg Berat Paket", f"{float(k['avg_berat'] or 0):.2f} kg")
        col8.metric("🚚 Sedang Dikirim", int(k['on_delivery'] or 0))

    st.markdown("---")

    # ── Grafik Pengiriman Harian ───────────────────────────────────
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("📅 Pengiriman Harian")
        daily = run_query("""
            SELECT DATE(tgl_dibuat) AS tanggal, COUNT(*) AS jumlah,
                   SUM(ongkos_kirim) AS revenue
            FROM shipments
            WHERE company_id=%s AND DATE(tgl_dibuat) BETWEEN %s AND %s
            GROUP BY DATE(tgl_dibuat)
            ORDER BY tanggal
        """, (company_id, lap_from, lap_to))

        if daily:
            df_daily = pd.DataFrame(daily)
            df_daily['tanggal'] = pd.to_datetime(df_daily['tanggal'])
            df_daily = df_daily.set_index('tanggal')
            st.bar_chart(df_daily['jumlah'], color="#2e7d42")
        else:
            st.info("Tidak ada data pada periode ini.")

    with col_g2:
        st.subheader("📊 Distribusi Status")
        dist = run_query("""
            SELECT status, COUNT(*) AS jumlah
            FROM shipments
            WHERE company_id=%s AND DATE(tgl_dibuat) BETWEEN %s AND %s
            GROUP BY status
        """, (company_id, lap_from, lap_to))

        if dist:
            df_dist = pd.DataFrame(dist).set_index('status')
            st.bar_chart(df_dist['jumlah'])
        else:
            st.info("Tidak ada data.")

    st.markdown("---")

    # ── Performa Kurir ─────────────────────────────────────────────
    st.subheader("👤 Performa Kurir")
    perf = run_query("""
        SELECT c.nama_kurir,
               COUNT(s.shipment_id) AS total_assign,
               SUM(CASE WHEN s.status='Terkirim' THEN 1 ELSE 0 END) AS sukses,
               SUM(CASE WHEN s.status='Gagal Kirim' THEN 1 ELSE 0 END) AS gagal,
               COALESCE(SUM(CASE WHEN s.status='Terkirim' THEN s.ongkos_kirim ELSE 0 END),0) AS revenue,
               c.rating
        FROM couriers c
        LEFT JOIN shipments s ON c.courier_id = s.courier_id
            AND DATE(s.tgl_dibuat) BETWEEN %s AND %s
        WHERE c.company_id = %s
        GROUP BY c.courier_id, c.nama_kurir, c.rating
        ORDER BY sukses DESC
    """, (lap_from, lap_to, company_id))

    if perf:
        df_perf = pd.DataFrame(perf)
        df_perf['success_rate'] = df_perf.apply(
            lambda r: f"{r['sukses']/r['total_assign']*100:.0f}%" if r['total_assign'] > 0 else "0%", axis=1
        )
        df_perf['revenue'] = df_perf['revenue'].apply(lambda x: f"Rp {int(x):,}".replace(",", "."))
        df_perf['rating'] = df_perf['rating'].apply(lambda x: f"⭐ {x:.1f}")
        df_perf.columns = ["Nama Kurir", "Total Assign", "Sukses", "Gagal", "Revenue", "Rating", "Success Rate"]
        st.dataframe(df_perf, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data performa kurir.")

    st.markdown("---")

    # ── Revenue Harian (line chart) ────────────────────────────────
    st.subheader("💰 Tren Revenue Harian")
    rev_daily = run_query("""
        SELECT DATE(tgl_dibuat) AS tanggal,
               SUM(ongkos_kirim) AS revenue
        FROM shipments
        WHERE company_id=%s AND status='Terkirim'
          AND DATE(tgl_dibuat) BETWEEN %s AND %s
        GROUP BY DATE(tgl_dibuat)
        ORDER BY tanggal
    """, (company_id, lap_from, lap_to))

    if rev_daily:
        df_rev = pd.DataFrame(rev_daily)
        df_rev['tanggal'] = pd.to_datetime(df_rev['tanggal'])
        df_rev = df_rev.set_index('tanggal')
        st.line_chart(df_rev['revenue'], color="#2e7d42")
    else:
        st.info("Belum ada revenue terkirim pada periode ini.")

    # ── Distribusi Kota Tujuan ─────────────────────────────────────
    st.markdown("---")
    st.subheader("🏙️ Top 10 Kota Tujuan")
    kota_data = run_query("""
        SELECT kota, COUNT(*) AS jumlah,
               SUM(ongkos_kirim) AS total_revenue
        FROM shipments
        WHERE company_id=%s AND DATE(tgl_dibuat) BETWEEN %s AND %s
        GROUP BY kota
        ORDER BY jumlah DESC
        LIMIT 10
    """, (company_id, lap_from, lap_to))

    if kota_data:
        df_kota = pd.DataFrame(kota_data)
        df_kota['total_revenue'] = df_kota['total_revenue'].apply(lambda x: f"Rp {int(x):,}".replace(",", "."))
        df_kota.columns = ["Kota", "Jumlah Pengiriman", "Total Revenue"]
        col_k1, col_k2 = st.columns([1, 1])
        with col_k1:
            st.dataframe(df_kota, use_container_width=True, hide_index=True)
        with col_k2:
            df_chart = pd.DataFrame(kota_data).set_index('kota')
            st.bar_chart(df_chart['jumlah'])
    else:
        st.info("Belum ada data kota tujuan.")