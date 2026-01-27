import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import time 

# ==========================================
# 1. CSS: TOTAL CENTER ALIGNMENT
# ==========================================
st.set_page_config(page_title="SMK NASIONAL - E-KENDALI", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Memaksa semua elemen di dalam container utama jadi tengah */
    .stApp {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .main-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        max-width: 500px;
        margin: 0 auto;
    }

    .login-title {
        color: #ffc107;
        font-size: 2rem;
        font-weight: bold;
        margin: 20px 0;
        text-align: center;
        width: 100%;
    }

    /* Kotak Login Tetap di Tengah */
    .stForm {
        width: 100% !important;
        border: 2px solid #ffc107 !important;
        border-radius: 15px;
        background-color: #0e1117;
        padding: 30px;
    }

    .digital-clock { 
        font-family: 'Courier New', monospace; color: #ffc107; 
        background-color: #000; font-size: 3em; font-weight: bold; 
        text-align: center; border: 3px solid #ffc107; border-radius: 12px; 
        padding: 10px 20px; margin: 20px auto; display: block;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATA STAF (15 JABATAN LENGKAP)
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False, "user_role": None,
        "users": {
            "Kepala Sekolah": "kepsek123", "Waka Kurikulum": "kurikulum123", 
            "Waka Kesiswaan": "kesiswaan123", "Waka Hubin": "hubin123", 
            "Waka Sarpras": "sarpras123", "Kepala Tata Usaha": "ktu123",
            "Bendahara Bos": "bos123", "Bendahara Sekolah": "bendahara123", 
            "Staf Bendahara Sekolah": "stafbend123", "Pembina Osis": "osis123", 
            "Ketertiban": "tertib123", "Kepala Lab": "lab123",
            "BK": "bk123", "Kepala Perpustakaan": "perpus123", 
            "Dokumentasi dan Publikasi": "dokpub123", "ADMIN SISTEM": "admin789"
        }
    })

waktu_wib = (datetime.now() + timedelta(hours=7)).strftime("%H:%M:%S")

# ==========================================
# 3. HALAMAN LOGIN: LOGO -> JUDUL -> FORM (LURUS TENGAH)
# ==========================================
if not st.session_state.logged_in:
    # Menggunakan wrapper untuk memastikan urutan vertikal di tengah
    st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)
    
    # A. Logo di Tengah
    try:
        st.image("logo_smk.png", width=120)
    except:
        st.write("🏛️")
    
    # B. Judul di Tengah
    st.markdown('<div class="login-title">E-KENDALI LOGIN</div>', unsafe_allow_html=True)
    
    # C. Form di Tengah
    with st.form("login_center"):
        jab = st.selectbox("Pilih Jabatan:", list(st.session_state.users.keys()))
        pw = st.text_input("Password:", type="password")
        if st.form_submit_button("MASUK SISTEM", use_container_width=True):
            if pw == st.session_state.users[jab]:
                st.session_state.logged_in = True; st.session_state.user_role = jab; st.rerun()
            else: st.error("Password Salah!")
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 4. DASHBOARD: LOGO -> JAM (LURUS TENGAH)
# ==========================================
st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)
try:
    st.image("logo_smk.png", width=100)
except:
    st.write("🏛️")
st.markdown(f'<div class="digital-clock">{waktu_wib}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.info(f"Login Sebagai: {st.session_state.user_role}")
if st.button("🚪 KELUAR"):
    st.session_state.logged_in = False; st.rerun()
