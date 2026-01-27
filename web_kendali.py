import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import time 

# ==========================================
# 1. CSS: PENARIK LOGO KE TENGAH (FIX)
# ==========================================
st.set_page_config(page_title="SMK NASIONAL - E-KENDALI", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Container utama yang memaksa semua elemen ditarik ke tengah */
    .center-all {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        width: 100%;
    }

    /* Penarik khusus Logo agar tidak lari ke kiri */
    .logo-container {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 120px;
    }

    .login-title {
        color: #ffc107;
        font-size: 2.2rem;
        font-weight: bold;
        margin-top: 15px;
        margin-bottom: 25px;
        text-align: center;
    }

    /* Form Login agar tetap ramping dan di tengah */
    .stForm {
        width: 450px !important;
        border: 2px solid #ffc107 !important;
        border-radius: 15px;
        background-color: #0e1117;
        margin: 0 auto;
    }

    .digital-clock { 
        font-family: 'Courier New', monospace; color: #ffc107; 
        background-color: #000; font-size: 3em; font-weight: bold; 
        text-align: center; border: 3px solid #ffc107; border-radius: 12px; 
        padding: 10px 20px; margin: 20px auto; display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATA STAF (15 JABATAN)
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
# 3. HALAMAN LOGIN: SEMUA DITARIK KE TENGAH
# ==========================================
if not st.session_state.logged_in:
    # Menggunakan HTML untuk kontrol posisi logo yang lebih presisi
    st.markdown('<div class="center-all">', unsafe_allow_html=True)
    
    # Menampilkan Logo dengan kolom bantuan agar benar-benar "tertarik" ke tengah
    _, mid_col, _ = st.columns([1, 0.4, 1])
    with mid_col:
        try: st.image("logo_smk.png", use_container_width=True)
        except: st.write("🏛️")
    
    st.markdown('<div class="login-title">E-KENDALI LOGIN</div>', unsafe_allow_html=True)
    
    # Kotak Login
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
# 4. DASHBOARD HEADER
# ==========================================
st.markdown('<div class="center-all">', unsafe_allow_html=True)
_, mid_dash, _ = st.columns([1, 0.3, 1])
with mid_dash:
    try: st.image("logo_smk.png", use_container_width=True)
    except: st.write("🏛️")
st.markdown(f'<div class="digital-clock">{waktu_wib}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.info(f"👤 Aktif sebagai: {st.session_state.user_role}")
if st.button("🚪 KELUAR"):
    st.session_state.logged_in = False; st.rerun()
