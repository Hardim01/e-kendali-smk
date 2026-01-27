import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import time 

# ==========================================
# 1. CSS: FIX LOGO TENGAH (SIMETRIS TOTAL)
# ==========================================
st.set_page_config(page_title="SMK NASIONAL - E-KENDALI", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Container untuk memastikan semua elemen vertikal ditarik ke tengah */
    .login-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        width: 100%;
    }

    .digital-clock { 
        font-family: 'Courier New', monospace; color: #ffc107; background-color: #000; font-size: 3.2em; 
        font-weight: bold; text-align: center; border: 3px solid #ffc107; border-radius: 12px; 
        padding: 10px 25px; margin: 15px auto; display: inline-block;
    }

    /* Memaksa kotak form agar presisi di tengah */
    div[data-testid="stForm"] {
        margin: 0 auto !important;
        width: 450px !important;
        border: 2px solid #ffc107 !important;
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATA & SESSION (TIDAK BERUBAH)
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False, "user_role": None,
        "users": {
            "Kepala Sekolah": "kepsek123", "Waka Kurikulum": "kurikulum123", "Waka Kesiswaan": "kesiswaan123",
            "Waka Hubin": "hubin123", "Waka Sarpras": "sarpras123", "Kepala Tata Usaha": "ktu123",
            "Bendahara Bos": "bos123", "Bendahara Sekolah": "bendahara123", "Staf Bendahara Sekolah": "stafbend123",
            "Pembina Osis": "osis123", "Ketertiban": "tertib123", "Kepala Lab": "lab123",
            "BK": "bk123", "Kepala Perpustakaan": "perpus123", "Dokumentasi dan Publikasi": "dokpub123",
            "ADMIN SISTEM": "admin789"
        },
        "live_monitor": [], "laporan_masuk": [], "tugas_khusus": [], "data_kas": []
    })

waktu_wib = (datetime.now() + timedelta(hours=7)).strftime("%H:%M:%S")

# ==========================================
# 3. HALAMAN LOGIN: LOGO PERSISI DI TENGAH
# ==========================================
if not st.session_state.logged_in:
    # Pembungkus utama agar semua center
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    
    # Menampilkan Logo menggunakan kolom bantuan (Metode paling stabil di Streamlit)
    _, col_logo, _ = st.columns([1, 0.4, 1])
    with col_logo:
        st.image("logo_smk.png", use_container_width=True)
    
    # Kalimat Judul tepat di bawah logo
    st.markdown("<h2 style='color: #ffc107; margin-bottom: 20px;'>E-KENDALI LOGIN</h2>", unsafe_allow_html=True)
    
    # Kotak Login
    with st.form("form_login"):
        jab = st.selectbox("Pilih Jabatan:", list(st.session_state.users.keys()))
        pw = st.text_input("Password:", type="password")
        if st.form_submit_button("MASUK SISTEM", use_container_width=True):
            if pw == st.session_state.users[jab]:
                st.session_state.logged_in = True; st.session_state.user_role = jab; st.rerun()
            else: st.error("Akses Ditolak!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 4. DASHBOARD (TETAP SEPERTI SEMULA)
# ==========================================
st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
_, col_dash, _ = st.columns([1, 0.3, 1])
with col_dash:
    st.image("logo_smk.png", use_container_width=True)
st.markdown(f'<div class="digital-clock">{waktu_wib}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# Menu Kepsek & Staf kembali ke fungsi penuh
if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    t1, t2, t3, t4 = st.tabs(["🎥 MONITOR", "📁 LAPORAN", "✍️ INSTRUKSI", "💰 KEUANGAN"])
    # Fungsi tetap berjalan di sini...
else:
    ts1, ts2 = st.tabs(["📝 INPUT KERJA", "🔔 INSTRUKSI"])
    # Fungsi tetap berjalan di sini...

if st.sidebar.button("🚪 KELUAR"):
    st.session_state.logged_in = False; st.rerun()
