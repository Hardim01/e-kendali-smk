import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import time 

# ==========================================
# 1. CSS: KUNCI POSISI TENGAH
# ==========================================
st.set_page_config(page_title="SMK NASIONAL - E-KENDALI", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Paksa semua elemen di halaman login untuk rata tengah */
    .stDeployButton {display:none;}
    
    .center-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }
    
    .login-title {
        color: #ffc107;
        font-size: 2.2rem;
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 20px;
        text-align: center;
    }

    div[data-testid="stForm"] {
        margin: 0 auto !important;
        width: 450px !important;
        border: 2px solid #ffc107 !important;
        border-radius: 15px;
    }

    .digital-clock { 
        font-family: 'Courier New', monospace; color: #ffc107; background-color: #000; font-size: 3.2em; 
        font-weight: bold; text-align: center; border: 3px solid #ffc107; border-radius: 12px; 
        padding: 10px 25px; margin: 15px auto; display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATA & SESSION (TIDAK BOLEH BERUBAH)
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
# 3. HALAMAN LOGIN: LOGO & JUDUL PAS DI TENGAH
# ==========================================
if not st.session_state.logged_in:
    # Gunakan kolom untuk memaksa logo ke tengah sumbu layar
    col1, col2, col3 = st.columns([1, 0.6, 1])
    
    with col2:
        # LOGO DI TENGAH
        st.image("logo_smk.png", use_container_width=True)
    
    # JUDUL DI TENGAH (Tepat di bawah logo)
    st.markdown('<div class="login-title">E-KENDALI LOGIN</div>', unsafe_allow_html=True)
    
    # FORM DI TENGAH
    with st.form("form_login"):
        jab = st.selectbox("Pilih Jabatan:", list(st.session_state.users.keys()))
        pw = st.text_input("Password:", type="password")
        if st.form_submit_button("MASUK SISTEM", use_container_width=True):
            if pw == st.session_state.users[jab]:
                st.session_state.logged_in = True; st.session_state.user_role = jab; st.rerun()
            else: st.error("Password Salah!")
    st.stop()

# ==========================================
# 4. DASHBOARD (SEMUA MENU KEMBALI NORMAL)
# ==========================================
# Header Dashboard Logo Tengah + Jam
d1, d2, d3 = st.columns([1, 0.5, 1])
with d2:
    st.image("logo_smk.png", use_container_width=True)

st.markdown(f'<div style="text-align:center;"><div class="digital-clock">{waktu_wib}</div></div>', unsafe_allow_html=True)
st.divider()

# KEMBALIKAN SEMUA MENU SESUAI JABATAN (KEPSEK & STAF)
if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    t1, t2, t3, t4 = st.tabs(["🎥 MONITOR", "📁 LAPORAN", "✍️ INSTRUKSI", "💰 KEUANGAN"])
    with t1: st.write("Monitoring Live...")
    with t2: st.write("Laporan Masuk...")
    with t3: st.write("Input Instruksi...")
    with t4: st.write("Data Keuangan...")
else:
    ts1, ts2 = st.tabs(["📝 INPUT KERJA", "🔔 INSTRUKSI"])
    with ts1: st.write("Input Aktivitas...")
    with ts2: st.write("Cek Instruksi...")

if st.sidebar.button("🚪 KELUAR"):
    st.session_state.logged_in = False; st.rerun()
