import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import base64
import time 

# ==========================================
# 1. CSS: STABIL & RAPI (NO MORE ACAK-ACAKAN)
# ==========================================
st.set_page_config(page_title="SMK NASIONAL - E-KENDALI", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    .marquee-container { background-color: #002b5b; color: #ffffff; padding: 10px 0; font-weight: bold; border-bottom: 4px solid #ffc107; margin-bottom: 20px; overflow: hidden; white-space: nowrap; }
    .marquee-text { display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite; font-size: 1.1rem; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    
    .digital-clock { 
        font-family: 'Courier New', monospace; color: #ffc107; background-color: #000; font-size: 3em; 
        font-weight: bold; text-align: center; border: 3px solid #ffc107; border-radius: 12px; 
        padding: 10px 20px; margin-top: 10px; display: inline-block;
    }
    
    /* Memastikan Form Login Selalu Tengah & Rapi */
    div[data-testid="stForm"] {
        border: 2px solid #ffc107 !important;
        border-radius: 15px !important;
        padding: 30px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATA (15 JABATAN)
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
# 3. HALAMAN LOGIN (TOTAL CENTERED)
# ==========================================
if not st.session_state.logged_in:
    st.markdown('<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Sholat Yang Utama ✨</div></div>', unsafe_allow_html=True)
    
    # Teknik 3 Kolom untuk memaksa Logo & Judul ke tengah
    _, tengah, _ = st.columns([1, 1.5, 1])
    
    with tengah:
        # Menampilkan Logo Tepat di Tengah
        st.image("logo_smk.png", width=120)
        
        # Judul Tepat di Bawah Logo
        st.markdown("<h2 style='text-align: center; color: #ffc107; margin-bottom: 20px;'>E-KENDALI LOGIN</h2>", unsafe_allow_html=True)
        
        # Kotak Login Tepat di Bawah Judul
        with st.form("login_center"):
            jab = st.selectbox("Pilih Jabatan:", list(st.session_state.users.keys()))
            pw = st.text_input("Password:", type="password")
            if st.form_submit_button("MASUK SISTEM", use_container_width=True):
                if pw == st.session_state.users[jab]:
                    st.session_state.logged_in = True; st.session_state.user_role = jab; st.rerun()
                else: st.error("Password Salah!")
    st.stop()

# ==========================================
# 4. DASHBOARD (LOGO TENGAH + MENU LENGKAP)
# ==========================================
st.markdown('<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Sholat Yang Utama ✨</div></div>', unsafe_allow_html=True)

# Header Dashboard Tetap Tengah
_, dash_tengah, _ = st.columns([1, 1, 1])
with dash_tengah:
    st.image("logo_smk.png", width=100)
    st.markdown(f'<div class="digital-clock">{waktu_wib}</div>', unsafe_allow_html=True)

st.divider()

# Logika Menu (Kepsek & Staf)
if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    st.subheader(f"DASHBOARD UTAMA: {st.session_state.user_role}")
    t1, t2, t3, t4 = st.tabs(["🎥 MONITOR", "📁 LAPORAN", "✍️ INSTRUKSI", "💰 KEUANGAN"])
    # ... isi menu kepsek (Monitor, Laporan, dll)
else:
    st.subheader(f"MENU KERJA: {st.session_state.user_role}")
    ts1, ts2 = st.tabs(["📝 INPUT KERJA", "🔔 INSTRUKSI"])
    # ... isi menu staf (Input, Instruksi)

if st.sidebar.button("🚪 KELUAR"):
    st.session_state.logged_in = False; st.rerun()
