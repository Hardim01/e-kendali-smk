import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import base64
import ast
import time 

# ==========================================
# 1. STYLE: KEMBALI KE DESAIN ASLI (CLEAN)
# ==========================================
st.set_page_config(page_title="SMK NASIONAL - E-KENDALI", layout="wide", page_icon="🏛️")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    .marquee-container { background-color: #002b5b; color: #ffffff; padding: 10px 0; font-weight: bold; border-bottom: 4px solid #ffc107; margin-bottom: 20px; overflow: hidden; white-space: nowrap; }
    .marquee-text { display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite; font-size: 1.1rem; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    
    .digital-clock { font-family: 'Courier New', monospace; color: #ffc107; background-color: #000; font-size: 3em; font-weight: bold; text-align: center; border: 2px solid #ffc107; border-radius: 12px; padding: 10px; min-width: 250px; margin: 10px auto; }
    
    .stForm { margin: 0 auto; max-width: 500px !important; border-radius: 15px; }
    .centered-logo { display: flex; justify-content: center; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATABASE & SESSION (TIDAK BERUBAH)
# ==========================================
DB_DIR = "database"
if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)

def save_data(data_list, filename): pd.DataFrame(data_list).to_csv(os.path.join(DB_DIR, filename), index=False)
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

# FIX JAM: Sesuai jam komputer Bapak (WIB)
waktu_skrg = (datetime.now() + timedelta(hours=7)).strftime("%H:%M:%S")

# ==========================================
# 3. HALAMAN LOGIN (SIMETRIS)
# ==========================================
if not st.session_state.logged_in:
    st.markdown('<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Sholat Yang Utama ✨</div></div>', unsafe_allow_html=True)
    
    # Logo SMK di Tengah
    st.markdown('<div class="centered-logo">', unsafe_allow_html=True)
    try: st.image("logo_smk.png", width=120)
    except: st.title("🏛️ SMK NASIONAL")
    st.markdown('</div>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.markdown("<h3 style='text-align:center;'>E-KENDALI LOGIN</h3>", unsafe_allow_html=True)
        jab = st.selectbox("Pilih Jabatan:", list(st.session_state.users.keys()))
        pw = st.text_input("Password:", type="password")
        if st.form_submit_button("MASUK SISTEM", use_container_width=True):
            if pw == st.session_state.users[jab]:
                st.session_state.logged_in = True; st.session_state.user_role = jab; st.rerun()
            else: st.error("Akses Ditolak!")
    st.stop()

# ==========================================
# 4. HEADER DASHBOARD (KEMBALI KE DESAIN BAGUS)
# ==========================================
st.markdown('<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Sholat Yang Utama ✨</div></div>', unsafe_allow_html=True)

# Grid Header: Info - Logo/Jam - Tombol
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.info(f"👤 {st.session_state.user_role}")
    if st.button("🔑 Ganti PW", use_container_width=True):
        st.toast("Fitur dalam pengembangan")

with col2:
    # Logo SMK dan Jam Digital di Tengah
    st.markdown('<div class="centered-logo">', unsafe_allow_html=True)
    try: st.image("logo_smk.png", width=100)
    except: st.write("🏛️")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="digital-clock">{waktu_skrg}</div>', unsafe_allow_html=True)

with col3:
    if st.button("🚪 KELUAR SISTEM", use_container_width=True):
        st.session_state.logged_in = False; st.rerun()
    st.markdown("<br><p style='text-align:right; color:red; font-weight:bold;'>HARDIANTO<br>RUAS STUDIO</p>", unsafe_allow_html=True)

st.divider()

# ==========================================
# 5. KONTEN (TIDAK BERUBAH)
# ==========================================
# (Konten Dashboard tetap seperti versi Bapak yang lama agar tidak bingung)
if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    t1, t2, t3, t4 = st.tabs(["🎥 MONITOR", "📁 LAPORAN", "✍️ INSTRUKSI", "💰 KEUANGAN"])
    with t1:
        if st.session_state.live_monitor: st.table(pd.DataFrame(st.session_state.live_monitor)[::-1])
    with t4:
        df_k = pd.DataFrame(st.session_state.data_kas)
        if not df_k.empty:
            st.subheader("Jurnal Dana BOS"); st.dataframe(df_k[df_k['Kategori']=='DANA BOS'][::-1], use_container_width=True)
            st.subheader("Jurnal Dana NON-BOS"); st.dataframe(df_k[df_k['Kategori']=='DANA NON-BOS'][::-1], use_container_width=True)
else:
    ts1, ts2 = st.tabs(["📝 INPUT KERJA", "🔔 INSTRUKSI"])
    with ts1:
        act = st.text_area("Aktivitas Anda:")
        if st.button("Simpan"):
            st.session_state.live_monitor.append({"Jam": waktu_skrg, "Staf": st.session_state.user_role, "Aktivitas": act})
            save_data(st.session_state.live_monitor, "database_monitor.csv"); st.rerun()

st.markdown("<p style='text-align:center; color:grey; margin-top:50px;'>E-KENDALI SMK NASIONAL | BANDUNG</p>", unsafe_allow_html=True)
time.sleep(2); st.rerun()
