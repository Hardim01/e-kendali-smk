import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import base64
import time 

# ==========================================
# 1. CSS: LOCK POSISI LOGO & JAM (SUDAH FIX)
# ==========================================
st.set_page_config(page_title="SMK NASIONAL - E-KENDALI", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    .marquee-container { background-color: #002b5b; color: #ffffff; padding: 10px 0; font-weight: bold; border-bottom: 4px solid #ffc107; margin-bottom: 20px; overflow: hidden; white-space: nowrap; }
    .marquee-text { display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite; font-size: 1.1rem; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    
    .digital-clock { 
        font-family: 'Courier New', monospace; color: #ffc107; background-color: #000; font-size: 3.2em; 
        font-weight: bold; text-align: center; border: 3px solid #ffc107; border-radius: 12px; 
        padding: 10px 25px; margin: 15px auto; display: inline-block; box-shadow: 0px 0px 15px #ffc107;
    }
    
    div[data-testid="stForm"] {
        margin: 0 auto !important;
        width: 450px !important;
        border: 2px solid #ffc107 !important;
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. SISTEM DATABASE (FILESYSTEM)
# ==========================================
DB_DIR = "database"
if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)

def save_db(df, name): df.to_csv(os.path.join(DB_DIR, name), index=False)
def load_db(name):
    p = os.path.join(DB_DIR, name)
    return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()

# ==========================================
# 3. SESSION STATE & USER DATA
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
# 4. HALAMAN LOGIN (TOTAL SYMMETRY)
# ==========================================
if not st.session_state.logged_in:
    st.markdown('<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Sholat Yang Utama ✨</div></div>', unsafe_allow_html=True)
    _, l_col, _ = st.columns([1, 0.4, 1])
    with l_col: st.image("logo_smk.png", use_container_width=True)
    st.markdown("<h2 style='text-align:center; color:#ffc107;'>E-KENDALI LOGIN</h2>", unsafe_allow_html=True)
    with st.form("f_login"):
        jab = st.selectbox("Pilih Jabatan:", list(st.session_state.users.keys()))
        pw = st.text_input("Password:", type="password")
        if st.form_submit_button("MASUK SISTEM", use_container_width=True):
            if pw == st.session_state.users[jab]:
                st.session_state.logged_in = True; st.session_state.user_role = jab; st.rerun()
            else: st.error("Akses Ditolak!")
    st.stop()

# ==========================================
# 5. DASHBOARD HEADER (LOGO & JAM TETAP BAGUS)
# ==========================================
st.markdown('<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Sholat Yang Utama ✨</div></div>', unsafe_allow_html=True)
_, d_col, _ = st.columns([1, 0.3, 1])
with d_col: st.image("logo_smk.png", use_container_width=True)
st.markdown(f'<div style="text-align:center;"><div class="digital-clock">{waktu_wib}</div></div>', unsafe_allow_html=True)

# Sidebar: Fitur Logout & Ganti Password
with st.sidebar:
    st.header(f"👤 {st.session_state.user_role}")
    if st.button("🚪 KELUAR SISTEM", use_container_width=True):
        st.session_state.logged_in = False; st.rerun()
    with st.expander("🔑 Ganti Password"):
        new_pw = st.text_input("Password Baru:", type="password")
        if st.button("Simpan Password"):
            st.session_state.users[st.session_state.user_role] = new_pw
            st.success("Berhasil diubah!")

st.divider()

# ==========================================
# 6. FITUR UTAMA (MONITOR, INSTRUKSI, KEUANGAN)
# ==========================================
if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    t1, t2, t3, t4 = st.tabs(["🎥 MONITORING STAF", "📁 LAPORAN MASUK", "✍️ INSTRUKSI PIMPINAN", "💰 KEUANGAN REAL-TIME"])
    
    with t1:
        st.subheader("Aktivitas Staf Hari Ini")
        df_mon = load_db("monitor.csv")
        if not df_mon.empty: st.table(df_mon[::-1])
        else: st.info("Belum ada laporan masuk.")

    with t2:
        st.subheader("File Laporan Masuk")
        df_lap = load_db("laporan.csv")
        if not df_lap.empty:
            for i, r in df_lap.iterrows():
                with st.expander(f"Lap: {r['Staf']} ({r['Jam']})"):
                    st.write(r['Pesan'])
                    if 'File' in r and str(r['File']) != 'nan':
                        st.download_button("📥 Unduh Lampiran", r['File'], file_name=f"Lampiran_{r['Jam']}.png")
        
    with t3:
        st.subheader("Kirim Instruksi Khusus")
        target = st.multiselect("Pilih Jabatan:", list(st.session_state.users.keys()))
        pesan = st.text_area("Isi Instruksi:")
        file = st.file_uploader("Tambahkan Lampiran (Opsional):")
        if st.button("Sebarkan Instruksi"):
            df_ins = load_db("instruksi.csv")
            new_ins = pd.DataFrame([{"Jam": waktu_wib, "Target": target, "Isi": pesan}])
            save_db(pd.concat([df_ins, new_ins]), "instruksi.csv")
            st.success("Instruksi telah dikirim!")

    with t4:
        st.subheader("Ringkasan Kas Sekolah")
        df_kas = load_db("kas.csv")
        if not df_kas.empty:
            c1, c2 = st.columns(2)
            c1.metric("Total Masuk", f"Rp {df_kas['Masuk'].sum():,}")
            c2.metric("Total Keluar", f"Rp {df_kas['Keluar'].sum():,}")
            st.dataframe(df_kas[::-1], use_container_width=True)

else:
    # MENU STAF
    m1, m2 = st.tabs(["📝 LAPOR KERJA", "🔔 KOTAK INSTRUKSI"])
    with m1:
        msg = st.text_area("Apa yang Anda kerjakan?")
        up = st.file_uploader("Upload Bukti Kerja (Gambar/PDF):")
        if st.button("Kirim Laporan"):
            df_mon = load_db("monitor.csv")
            new_mon = pd.DataFrame([{"Jam": waktu_wib, "Staf": st.session_state.user_role, "Aktivitas": msg}])
            save_db(pd.concat([df_mon, new_mon]), "monitor.csv")
            st.success("Laporan terkirim!")
            
    with m2:
        st.subheader("Instruksi dari Pimpinan")
        df_ins = load_db("instruksi.csv")
        if not df_ins.empty:
            for i, r in df_ins.iterrows():
                if st.session_state.user_role in str(r['Target']):
                    st.warning(f"**[{r['Jam']}]** {r['Isi']}")

st.markdown("<p style='text-align:center; color:grey; margin-top:50px;'>E-KENDALI SMK NASIONAL | HARDIANTO - RUAS STUDIO</p>", unsafe_allow_html=True)
