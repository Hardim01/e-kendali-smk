import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import base64
import ast
import time 

# 1. SETUP & CSS (Hanya untuk merapikan posisi agar simetris)
st.set_page_config(page_title="SMK NASIONAL - E-KENDALI", layout="wide", page_icon="🏛️")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .marquee-container { background-color: #002b5b; color: #ffffff; padding: 10px 0; font-weight: bold; border-bottom: 4px solid #ffc107; margin-bottom: 20px; overflow: hidden; white-space: nowrap; }
    .marquee-text { display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite; font-size: 1.1rem; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    
    /* Fokus: Menempatkan elemen di tengah secara vertikal */
    .center-wrapper { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
    
    .digital-clock { 
        font-family: 'Courier New', monospace; color: #ffc107; background-color: #000; font-size: 3.5em; 
        font-weight: bold; text-align: center; border: 3px solid #ffc107; border-radius: 15px; 
        padding: 10px 30px; margin: 10px auto; display: inline-block;
    }
    .stForm { margin: 0 auto; max-width: 500px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE & SESSION (15 JABATAN SESUAI INSTRUKSI)
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
        "users": {
            "Kepala Sekolah": "kepsek123", "Waka Kurikulum": "kurikulum123", "Waka Kesiswaan": "kesiswaan123",
            "Waka Hubin": "hubin123", "Waka Sarpras": "sarpras123", "Kepala Tata Usaha": "ktu123",
            "Bendahara Bos": "bos123", "Bendahara Sekolah": "bendahara123", "Staf Bendahara Sekolah": "stafbend123",
            "Pembina Osis": "osis123", "Ketertiban": "tertib123", "Kepala Lab": "lab123",
            "BK": "bk123", "Kepala Perpustakaan": "perpus123", "Dokumentasi dan Publikasi": "dokpub123",
            "ADMIN SISTEM": "admin789"
        },
        "data_kas": load_data("database_kas.csv"),
        "live_monitor": load_data("database_monitor.csv"),
        "laporan_masuk": load_data("database_laporan.csv"),
        "tugas_khusus": load_data("database_tugas.csv")
    })

waktu_wib = (datetime.now() + timedelta(hours=7)).strftime("%H:%M:%S")

# 3. HALAMAN LOGIN (LOGO DI TENGAH)
if not st.session_state.logged_in:
    st.markdown('<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Sholat Yang Utama ✨</div></div>', unsafe_allow_html=True)
    
    # Logo Tepat di Tengah
    st.markdown('<div class="center-wrapper">', unsafe_allow_html=True)
    try: st.image("logo_smk.png", width=120)
    except: st.write("🏛️")
    st.markdown("<h2 style='color:#ffc107;'>E-KENDALI LOGIN</h2>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.form("login_form"):
        jab = st.selectbox("Pilih Jabatan:", list(st.session_state.users.keys()))
        pw = st.text_input("Password:", type="password")
        if st.form_submit_button("MASUK SISTEM", use_container_width=True):
            if pw == st.session_state.users[jab]:
                st.session_state.logged_in = True; st.session_state.user_role = jab; st.rerun()
            else: st.error("Akses Ditolak")
    st.stop()

# 4. DASHBOARD (LOGO DI TENGAH ATAS JAM)
st.markdown('<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Sholat Yang Utama ✨</div></div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 2, 1])
with c1:
    st.info(f"👤 {st.session_state.user_role}")
with c2:
    # Logo Tepat di Tengah Atas Jam
    st.markdown('<div class="center-wrapper">', unsafe_allow_html=True)
    try: st.image("logo_smk.png", width=90)
    except: st.write("🏛️")
    st.markdown(f'<div class="digital-clock">{waktu_wib}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
with c3:
    if st.button("🚪 KELUAR SISTEM", use_container_width=True):
        st.session_state.logged_in = False; st.rerun()
    st.markdown("<p style='text-align:right; font-weight:bold; color:gray;'>HARDIANTO - RUAS STUDIO</p>", unsafe_allow_html=True)

st.divider()

# 5. MENU TETAP LENGKAP
if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    t1, t2, t3, t4 = st.tabs(["🎥 MONITOR LIVE", "📁 LAPORAN", "✍️ INSTRUKSI", "💰 KEUANGAN"])
    with t1:
        if st.session_state.live_monitor: st.table(pd.DataFrame(st.session_state.live_monitor)[::-1])
    with t2:
        for r in reversed(st.session_state.laporan_masuk):
            with st.expander(f"Lap: {r['Dari']} ({r['Jam']})"):
                st.write(r['Isi'])
    with t3:
        target = st.multiselect("Pilih Staf:", [u for u in st.session_state.users.keys() if u != "Kepala Sekolah"])
        msg = st.text_area("Instruksi:")
        if st.button("Kirim"):
            for s in target: st.session_state.tugas_khusus.append({"Jam": waktu_wib, "Untuk": s, "Instruksi": msg})
            st.success("Terkirim!")
    with t4:
        df_k = pd.DataFrame(st.session_state.data_kas)
        if not df_k.empty:
            st.subheader("DANA BOS"); st.dataframe(df_k[df_k['Kategori']=='DANA BOS'][::-1], use_container_width=True)
            st.subheader("DANA NON-BOS"); st.dataframe(df_k[df_k['Kategori']=='DANA NON-BOS'][::-1], use_container_width=True)
else:
    # VIEW STAF
    ts1, ts2 = st.tabs(["📝 INPUT KERJA", "🔔 INSTRUKSI"])
    with ts1:
        act = st.text_area("Aktivitas:")
        if st.button("Simpan"):
            st.session_state.live_monitor.append({"Jam": waktu_wib, "Staf": st.session_state.user_role, "Aktivitas": act})
            st.success("Tersimpan!"); time.sleep(1); st.rerun()
    with ts2:
        for t in reversed(st.session_state.tugas_khusus):
            if t['Untuk'] == st.session_state.user_role: st.info(f"[{t['Jam']}] {t['Instruksi']}")

st.markdown("<p style='text-align:center; color:grey; margin-top:50px;'>E-KENDALI SMK NASIONAL | BANDUNG</p>", unsafe_allow_html=True)
time.sleep(1); st.rerun()
