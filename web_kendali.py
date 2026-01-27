import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import base64
import time 

# ==========================================
# 1. STYLE: FIX LOGO TENGAH & LOGIN CENTER
# ==========================================
st.set_page_config(page_title="SMK NASIONAL - E-KENDALI", layout="wide", page_icon="🏛️")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Marquee Styling */
    .marquee-container { background-color: #002b5b; color: #ffffff; padding: 10px 0; font-weight: bold; border-bottom: 4px solid #ffc107; margin-bottom: 20px; overflow: hidden; white-space: nowrap; }
    .marquee-text { display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite; font-size: 1.1rem; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    
    /* Login Box Styling */
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .stForm { 
        margin: 0 auto; 
        max-width: 450px !important; 
        border: 2px solid #ffc107 !important; 
        border-radius: 15px; 
        padding: 20px;
    }
    
    /* Digital Clock Styling */
    .digital-clock { 
        font-family: 'Courier New', monospace; 
        color: #ffc107; 
        background-color: #000; 
        font-size: 3em; 
        font-weight: bold; 
        text-align: center; 
        border: 2px solid #ffc107; 
        border-radius: 12px; 
        padding: 10px; 
        margin: 10px auto;
        display: block;
        width: fit-content;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATABASE & SESSION
# ==========================================
DB_DIR = "database"
if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)

def load_data(filename):
    path = os.path.join(DB_DIR, filename)
    if os.path.exists(path):
        try: return pd.read_csv(path).to_dict('records')
        except: return []
    return []

if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False, "user_role": None,
        "users": {"Kepala Sekolah": "kepsek123", "Ketua Tata Usaha": "ktu123", "Bendahara Bos": "bos123", "Bendahara Sekolah": "bendahara123", "ADMIN SISTEM": "admin789"},
        "data_kas": load_data("database_kas.csv"),
        "live_monitor": load_data("database_monitor.csv"),
        "laporan_masuk": load_data("database_laporan.csv"),
        "tugas_khusus": load_data("database_tugas.csv")
    })

# SINKRONISASI JAM KE WIB (Sesuai Pojok Kanan Bawah Komputer)
waktu_wib = (datetime.now() + timedelta(hours=7)).strftime("%H:%M:%S")

# ==========================================
# 3. HALAMAN LOGIN (LOGO BENAR-BENAR DI TENGAH)
# ==========================================
if not st.session_state.logged_in:
    st.markdown('<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Sholat Yang Utama ✨</div></div>', unsafe_allow_html=True)
    
    # Bungkus Logo dan Form dalam satu wadah tengah
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Baris Logo (Dibuat kolom agar benar-benar center)
    _, col_logo, _ = st.columns([1, 0.6, 1])
    with col_logo:
        try: st.image("logo_smk.png", use_container_width=True)
        except: st.markdown("<h1 style='text-align:center;'>🏛️</h1>", unsafe_allow_html=True)
    
    # Form Login
    with st.form("login_center"):
        st.markdown("<h3 style='text-align:center; color:#ffc107; margin-top:0;'>E-KENDALI LOGIN</h3>", unsafe_allow_html=True)
        jab = st.selectbox("Pilih Jabatan:", list(st.session_state.users.keys()))
        pw = st.text_input("Password:", type="password")
        if st.form_submit_button("MASUK SISTEM", use_container_width=True):
            if pw == st.session_state.users[jab]:
                st.session_state.logged_in = True
                st.session_state.user_role = jab
                st.rerun()
            else: st.error("Password Salah!")
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 4. HEADER DASHBOARD (SIMETRIS)
# ==========================================
st.markdown('<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Sholat Yang Utama ✨</div></div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 1.5, 1])

with c1:
    st.info(f"👤 {st.session_state.user_role}")

with c2:
    # Logo dan Jam Sejajar di Tengah
    st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
    try: st.image("logo_smk.png", width=80)
    except: st.write("🏛️")
    st.markdown(f'<div class="digital-clock">{waktu_wib}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    if st.button("🚪 KELUAR SISTEM", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown("<p style='text-align:right; font-size:0.8em; color:gray;'>Design by: HARDIANTO</p>", unsafe_allow_html=True)

st.divider()

# ==========================================
# 5. ISI DASHBOARD (MONITOR & KEUANGAN)
# ==========================================
if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    t1, t2, t3 = st.tabs(["🎥 MONITOR LIVE", "📁 LAPORAN", "💰 KEUANGAN"])
    with t1:
        st.subheader("Aktivitas Staf Hari Ini")
        if st.session_state.live_monitor: st.table(pd.DataFrame(st.session_state.live_monitor)[::-1])
        else: st.info("Belum ada aktivitas tercatat.")
    with t3:
        df_k = pd.DataFrame(st.session_state.data_kas)
        if not df_k.empty:
            st.write("### Jurnal Dana BOS")
            st.dataframe(df_k[df_k['Kategori']=='DANA BOS'][::-1], use_container_width=True)
            st.write("### Jurnal Dana NON-BOS")
            st.dataframe(df_k[df_k['Kategori']=='DANA NON-BOS'][::-1], use_container_width=True)
else:
    # Tampilan untuk Staf
    st.write(f"Selamat Datang, {st.session_state.user_role}")
    act = st.text_area("Input Aktivitas:")
    if st.button("Simpan"):
        st.session_state.live_monitor.append({"Jam": waktu_wib, "Staf": st.session_state.user_role, "Aktivitas": act})
        st.success("Tersimpan!"); time.sleep(1); st.rerun()

st.markdown("<p style='text-align:center; color:grey; margin-top:50px;'>E-KENDALI SMK NASIONAL | RUAS STUDIO</p>", unsafe_allow_html=True)
time.sleep(1); st.rerun()
