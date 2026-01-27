import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# ==========================================
# 1. CSS: KUNCI LOGO & JAM (TENGAH MATI)
# ==========================================
st.set_page_config(page_title="SMK NASIONAL - E-KENDALI", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .digital-clock { 
        font-family: 'Courier New', monospace; color: #ffc107; background-color: #000; font-size: 3.2em; 
        font-weight: bold; text-align: center; border: 3px solid #ffc107; border-radius: 12px; 
        padding: 10px 25px; margin: 15px auto; display: inline-block; box-shadow: 0px 0px 15px #ffc107;
    }
    /* Tombol Logout Merah di Sidebar */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #d9534f !important;
        color: white !important;
        font-weight: bold;
    }
    div[data-testid="stForm"] { margin: 0 auto !important; width: 450px !important; border: 2px solid #ffc107 !important; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATABASE AUTO-SAVE
# ==========================================
DB_DIR = "database"
if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)

def load_db(name):
    p = os.path.join(DB_DIR, name)
    return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()

def save_db(df, name):
    df.to_csv(os.path.join(DB_DIR, name), index=False)

# ==========================================
# 3. SESSION & USER (15 JABATAN)
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
# 4. HALAMAN LOGIN
# ==========================================
if not st.session_state.logged_in:
    _, l_col, _ = st.columns([1, 0.4, 1])
    with l_col: st.image("logo_smk.png", use_container_width=True)
    st.markdown("<h3 style='text-align:center; color:#ffc107;'>E-KENDALI LOGIN</h3>", unsafe_allow_html=True)
    with st.form("f_login"):
        jab = st.selectbox("Pilih Jabatan:", list(st.session_state.users.keys()))
        pw = st.text_input("Password:", type="password")
        if st.form_submit_button("MASUK SISTEM", use_container_width=True):
            if pw == st.session_state.users[jab]:
                st.session_state.logged_in = True; st.session_state.user_role = jab; st.rerun()
            else: st.error("Akses Ditolak!")
    st.stop()

# ==========================================
# 5. SIDEBAR: LOGOUT & PASSWORD (DI SINI GANTENG!)
# ==========================================
with st.sidebar:
    st.image("logo_smk.png", width=80)
    st.write(f"### 👤 {st.session_state.user_role}")
    st.divider()
    
    # TOMBOL LOGOUT
    if st.button("🚪 KELUAR SISTEM", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
        
    st.divider()
    # FITUR GANTI PASSWORD
    with st.expander("🔑 Ganti Password"):
        new_pw = st.text_input("PW Baru:", type="password")
        if st.button("Simpan PW"):
            st.session_state.users[st.session_state.user_role] = new_pw
            st.success("Tersimpan!")

# ==========================================
# 6. DASHBOARD (ARSIP REAL-TIME)
# ==========================================
_, d_col, _ = st.columns([1, 0.3, 1])
with d_col: st.image("logo_smk.png", use_container_width=True)
st.markdown(f'<div style="text-align:center;"><div class="digital-clock">{waktu_wib}</div></div>', unsafe_allow_html=True)

if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    t1, t2, t3, t4, t5 = st.tabs(["🎥 MONITOR LIVE", "✍️ INSTRUKSI", "💰 KEUANGAN", "📁 ARSIP LAPORAN", "📚 ARSIP INSTRUKSI"])
    
    with t1:
        st.subheader("Pekerjaan Staf Hari Ini")
        df_mon = load_db("monitor.csv")
        st.table(df_mon[::-1] if not df_mon.empty else pd.DataFrame(columns=["Jam", "Staf", "Aktivitas"]))

    with t2:
        st.subheader("Kirim Instruksi & Lampiran")
        target = st.multiselect("Pilih Staf:", list(st.session_state.users.keys()))
        msg = st.text_area("Instruksi:")
        up = st.file_uploader("Lampiran (Gambar/PDF):")
        if st.button("Kirim Instruksi"):
            df_ins = load_db("instruksi.csv")
            new_data = pd.DataFrame([{"Jam": waktu_wib, "Target": str(target), "Isi": msg, "Lampiran": "Ada" if up else "-"}])
            save_db(pd.concat([df_ins, new_data], ignore_index=True), "instruksi.csv")
            st.success("Instruksi masuk arsip!")

    with t3:
        st.subheader("Monitoring Keuangan")
        df_kas = load_db("kas.csv")
        if not df_kas.empty:
            st.metric("Total Saldo Kas", f"Rp {df_kas['Masuk'].sum() - df_kas['Keluar'].sum():,}")
            st.dataframe(df_kas[::-1], use_container_width=True)

    with t4:
        st.subheader("Database Semua Laporan")
        st.dataframe(load_db("monitor.csv")[::-1], use_container_width=True)

    with t5:
        st.subheader("Database Semua Instruksi")
        st.dataframe(load_db("instruksi.csv")[::-1], use_container_width=True)

else:
    # MENU STAF
    st1, st2, st3 = st.tabs(["📝 LAPOR KERJA", "🔔 INSTRUKSI", "📚 ARSIP SAYA"])
    with st1:
        akt = st.text_area("Update pekerjaan:")
        if st.button("Kirim Laporan"):
            df_mon = load_db("monitor.csv")
            save_db(pd.concat([df_mon, pd.DataFrame([{"Jam": waktu_wib, "Staf": st.session_state.user_role, "Aktivitas": akt}])], ignore_index=True), "monitor.csv")
            st.success("Tersimpan!")
    with st2:
        df_ins = load_db("instruksi.csv")
        if not df_ins.empty:
            for i, r in df_ins.iterrows():
                if st.session_state.user_role in r['Target']: st.warning(f"**[{r['Jam']}]** {r['Isi']}")
    with st3:
        df_all = load_db("monitor.csv")
        if not df_all.empty:
            st.dataframe(df_all[df_all['Staf'] == st.session_state.user_role][::-1], use_container_width=True)

st.markdown("<p style='text-align:center; color:grey; margin-top:50px;'>E-KENDALI SMK NASIONAL | FULL SYSTEM</p>", unsafe_allow_html=True)
