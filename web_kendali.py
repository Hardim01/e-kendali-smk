import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64
import ast
import time 

# ==========================================
# 1. PAGE CONFIG & CLEAN UI
# ==========================================
st.set_page_config(page_title="SMK NASIONAL - E-KENDALI", layout="wide", page_icon="🏛️")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    [data-testid="stStatusWidget"] {display: none;} .stDeployButton {display: none;}
    .marquee-container { background-color: #002b5b; color: #ffffff; padding: 12px 0; font-weight: bold; border-bottom: 4px solid #ffc107; margin-bottom: 25px; overflow: hidden; white-space: nowrap; }
    .marquee-text { display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite; font-size: 1.2rem; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    .digital-clock-main { font-family: 'Courier New', monospace; color: #ffc107; background-color: #000; font-size: 3em; font-weight: bold; text-align: center; border: 3px solid #ffc107; border-radius: 15px; padding: 10px; }
    .welcome-text-gold { color: #ffc107; font-weight: bold; font-size: 1.8rem; text-align: center; text-shadow: 2px 2px 4px #000; margin-bottom: 0px; }
    .school-text-gold { color: #ffc107; font-weight: bold; font-size: 1.6rem; text-align: center; text-shadow: 2px 2px 4px #000; margin-top: 0px; }
    .dev-name { color: #000; font-weight: 900; text-align: center; margin-bottom: 0px; }
    .ruas-text { color: #e60000; font-weight: bold; text-align: center; margin-top: -5px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATABASE HANDLER
# ==========================================
DB_DIR = "database"
if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)

DEFAULT_USERS = {
    "Kepala Sekolah": "kepsek123", "Ketua Tata Usaha": "ktu123", "Bendahara Bos": "bos123", 
    "Bendahara Sekolah": "bendahara123", "Staf bendahara Sekolah": "stafbend123",
    "Waka Kurikulum": "kurikulum123", "Waka Kesiswaan": "wakakes123", 
    "Waka Hubin": "hubin123", "Waka Sarpras": "sarpras123", "ADMIN SISTEM": "admin789"
}

def load_users():
    path = os.path.join(DB_DIR, "database_users.csv")
    if os.path.exists(path):
        try:
            df_u = pd.read_csv(path)
            return dict(zip(df_u.Role, df_u.Password))
        except: return DEFAULT_USERS
    return DEFAULT_USERS

def save_users(users_dict):
    pd.DataFrame(list(users_dict.items()), columns=['Role', 'Password']).to_csv(os.path.join(DB_DIR, "database_users.csv"), index=False)

def save_data(data_list, filename):
    pd.DataFrame(data_list).to_csv(os.path.join(DB_DIR, filename), index=False)

def load_data(filename):
    path = os.path.join(DB_DIR, filename)
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            if filename == "database_kas.csv":
                if 'Kategori' not in df.columns: df['Kategori'] = 'DANA NON-BOS'
            return df.to_dict('records')
        except: return []
    return []

# ==========================================
# 3. SESSION INITIALIZATION
# ==========================================
if "users" not in st.session_state: st.session_state.users = load_users()
if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False, "user_role": None,
        "data_kas": load_data("database_kas.csv"),
        "live_monitor": load_data("database_monitor.csv"),
        "laporan_masuk": load_data("database_laporan.csv"),
        "tugas_khusus": load_data("database_tugas.csv")
    })

waktu_skrg = datetime.now().strftime("%H:%M:%S")
teks_marquee = '<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Sholat Yang Utama ✨</div></div>'

if not st.session_state.logged_in:
    st.markdown(teks_marquee, unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 1, 1])
    with col_log:
        st.markdown('<p class="welcome-text-gold">E-KENDALI SEKOLAH</p>', unsafe_allow_html=True)
        jab = st.selectbox("Pilih Jabatan:", ["--- Pilih ---"] + list(st.session_state.users.keys()))
        pw = st.text_input("Kode Akses:", type="password")
        if st.button("MASUK SISTEM", use_container_width=True):
            if jab in st.session_state.users and pw == st.session_state.users[jab]:
                st.session_state.logged_in = True
                st.session_state.user_role = jab
                st.rerun()
            else: st.error("Akses Ditolak!")
    st.stop()

# ==========================================
# 4. HEADER & PENGATURAN (DESAIN AWAL)
# ==========================================
st.markdown(teks_marquee, unsafe_allow_html=True)
col_h1, col_h2, col_h3 = st.columns([2, 2, 1])
with col_h1:
    st.markdown(f"<h2 class='digital-clock-main'>{waktu_skrg}</h2>", unsafe_allow_html=True)
with col_h2:
    st.success(f"Login Sebagai: **{st.session_state.user_role}**")
    with st.expander("🔑 Ganti Password"):
        n_pw = st.text_input("Sandi Baru:", type="password")
        if st.button("Update Sandi"):
            st.session_state.users[st.session_state.user_role] = n_pw
            save_users(st.session_state.users)
            st.success("Tersimpan!"); time.sleep(1); st.rerun()
with col_h3:
    if st.button("🚪 KELUAR", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
st.divider()

# ==========================================
# 5. DATA PROCESSING (PROTECTED)
# ==========================================
df_kas = pd.DataFrame(st.session_state.data_kas)
# Cek proteksi kolom kategori kembali sebelum render
if not df_kas.empty:
    if 'Kategori' not in df_kas.columns:
        df_kas['Kategori'] = 'DANA NON-BOS'

# ==========================================
# 6. DASHBOARD CONTENT
# ==========================================
if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    t1, t2, t3, t4 = st.tabs(["🎥 MONITOR LIVE", "📁 ARSIP LAPORAN", "✍️ KIRIM INSTRUKSI", "💰 KEUANGAN"])
    
    with t1:
        st.subheader("Aktivitas Staf Hari Ini")
        if st.session_state.live_monitor: st.table(pd.DataFrame(st.session_state.live_monitor)[::-1])
        else: st.info("Belum ada aktivitas.")
        
    with t2:
        st.subheader("Laporan Masuk")
        for r in reversed(st.session_state.laporan_masuk):
            with st.expander(f"Laporan: {r['Dari']} ({r['Jam']})"): st.write(r['Isi'])
            
    with t3:
        target = st.multiselect("Pilih Staf:", [u for u in st.session_state.users.keys() if u != "Kepala Sekolah"])
        msg = st.text_area("Isi Pesan:")
        if st.button("Kirim Instruksi"):
            for s in target:
                st.session_state.tugas_khusus.append({"Jam": waktu_skrg, "Untuk": s, "Instruksi": msg})
            save_data(st.session_state.tugas_khusus, "database_tugas.csv"); st.success("Terkirim!"); st.rerun()

    with t4:
        if not df_kas.empty:
            st.subheader("BOS")
            st.dataframe(df_kas[df_kas['Kategori']=='DANA BOS'][::-1], use_container_width=True)
            st.subheader("NON-BOS")
            st.dataframe(df_kas[df_kas['Kategori']=='DANA NON-BOS'][::-1], use_container_width=True)
        else: st.info("Belum ada data keuangan.")

else:
    ts1, ts2, ts3 = st.tabs(["📝 INPUT TUGAS", "🔔 INSTRUKSI", "📚 ARSIP"])
    with ts1:
        if "Bendahara" in st.session_state.user_role:
            with st.form("f_kas"):
                kat = st.radio("Kategori:", ["DANA BOS", "DANA NON-BOS"], horizontal=True)
                tipe = st.selectbox("Jenis:", ["Masuk", "Keluar"])
                nom = st.number_input("Nominal:", min_value=0)
                ket = st.text_input("Keterangan:")
                if st.form_submit_button("Simpan Transaksi"):
                    st.session_state.data_kas.append({"Waktu": waktu_skrg, "Kategori": kat, "Masuk": nom if tipe=="Masuk" else 0, "Keluar": nom if tipe=="Keluar" else 0, "Keterangan": ket})
                    save_data(st.session_state.data_kas, "database_kas.csv"); st.rerun()
        
        ca, cb = st.columns(2)
        with ca:
            act = st.text_area("Update Aktivitas:")
            if st.button("Simpan Aktivitas"):
                st.session_state.live_monitor.append({"Jam": waktu_skrg, "Staf": st.session_state.user_role, "Aktivitas": act})
                save_data(st.session_state.live_monitor, "database_monitor.csv"); st.rerun()
        with cb:
            lap = st.text_area("Laporan ke Kepsek:")
            if st.button("Kirim Laporan"):
                st.session_state.laporan_masuk.append({"Jam": waktu_skrg, "Dari": st.session_state.user_role, "Isi": lap})
                save_data(st.session_state.laporan_masuk, "database_laporan.csv"); st.rerun()

    with ts2:
        for t in reversed(st.session_state.tugas_khusus):
            if t['Untuk'] == st.session_state.user_role: st.info(f"[{t['Jam']}] {t['Instruksi']}")
    with ts3:
        my_data = [a for a in st.session_state.live_monitor if a['Staf'] == st.session_state.user_role]
        if my_data: st.table(pd.DataFrame(my_data)[::-1])

st.markdown(f"<p style='text-align:center; color:grey;'>{st.session_state.user_role} | HARDIANTO - RUAS STUDIO</p>", unsafe_allow_html=True)
time.sleep(1)
st.rerun()
