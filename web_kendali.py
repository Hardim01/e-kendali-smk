import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import time 

# ==========================================
# 1. CSS KHUSUS HALAMAN LOGIN (CENTERED FOCUS)
# ==========================================
st.set_page_config(page_title="SMK NASIONAL - E-KENDALI", layout="wide", page_icon="🏛️")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Container utama untuk memusatkan semuanya */
    .main-login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        margin-top: 50px;
    }
    
    .login-title {
        color: #ffc107;
        font-size: 2.2rem;
        font-weight: bold;
        margin-bottom: 25px;
        text-align: center;
    }

    /* Memaksa form streamlit agar tidak melebar */
    .stForm {
        width: 450px !important;
        border: 2px solid #ffc107 !important;
        border-radius: 15px;
        background-color: #0e1117;
    }
    
    .digital-clock { 
        font-family: 'Courier New', monospace; color: #ffc107; background-color: #000; font-size: 3em; 
        font-weight: bold; text-align: center; border: 3px solid #ffc107; border-radius: 12px; 
        padding: 10px 20px; margin: 15px auto; display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATABASE & SESSION (15 JABATAN TETAP)
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
        }
    })

waktu_wib = (datetime.now() + timedelta(hours=7)).strftime("%H:%M:%S")

# ==========================================
# 3. HALAMAN LOGIN (SUSUNAN VERTIKAL TENGAH)
# ==========================================
if not st.session_state.logged_in:
    # Pembungkus Tengah
    st.markdown('<div class="main-login-container">', unsafe_allow_html=True)
    
    # 1. Logo (Di paling atas tengah)
    try: st.image("logo_smk.png", width=130)
    except: st.write("🏛️")
    
    # 2. Tulisan E-KENDALI LOGIN (Tepat di bawah logo)
    st.markdown('<div class="login-title">E-KENDALI LOGIN</div>', unsafe_allow_html=True)
    
    # 3. Kotak Login (Tepat di bawah tulisan)
    with st.form("form_login"):
        jab = st.selectbox("Pilih Jabatan:", list(st.session_state.users.keys()))
        pw = st.text_input("Password:", type="password")
        if st.form_submit_button("MASUK SISTEM", use_container_width=True):
            if pw == st.session_state.users[jab]:
                st.session_state.logged_in = True; st.session_state.user_role = jab; st.rerun()
            else: st.error("Akses Ditolak")
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 4. DASHBOARD (SETELAH LOGIN)
# ==========================================
st.markdown(f'<div style="text-align:center;"><div class="digital-clock">{waktu_wib}</div></div>', unsafe_allow_html=True)
st.divider()
st.write(f"### Selamat Datang, {st.session_state.user_role}")

if st.button("🚪 KELUAR"):
    st.session_state.logged_in = False; st.rerun()
