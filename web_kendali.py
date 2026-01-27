import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# ==========================================
# 1. CSS: LOCK POSISI TENGAH & SIDEBAR
# ==========================================
st.set_page_config(page_title="SMK NASIONAL - E-KENDALI", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Jam Digital Glow Tetap di Tengah */
    .digital-clock { 
        font-family: 'Courier New', monospace; color: #ffc107; background-color: #000; font-size: 3.2em; 
        font-weight: bold; text-align: center; border: 3px solid #ffc107; border-radius: 12px; 
        padding: 10px 25px; margin: 15px auto; display: inline-block; box-shadow: 0px 0px 15px #ffc107;
    }
    
    /* Paksa Sidebar Selalu Terbuka & Style Tombol Logout */
    [data-testid="stSidebarNav"] {display: none;}
    .stSidebar [data-testid="stButton"] button {
        background-color: #d9534f !important;
        color: white !important;
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        padding: 10px;
    }
    
    /* Style Form Login */
    div[data-testid="stForm"] { margin: 0 auto !important; width: 450px !important; border: 2px solid #ffc107 !important; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. SISTEM DATABASE & SESSION
# ==========================================
DB_DIR = "database"
if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)

def load_db(name):
    p = os.path.join(DB_DIR, name)
    return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()

def save_db(df, name):
    df.to_csv(os.path.join(DB_DIR, name), index=False)

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
# 3. HALAMAN LOGIN
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
# 4. SIDEBAR: TEMPAT LOGOUT & GANTI PW
# ==========================================
with st.sidebar:
    st.image("logo_smk.png", width=100)
    st.markdown(f"### 👤 {st.session_state.user_role}")
    st.divider()
    
    # Fitur Ganti Password
    with st.expander("🔑 Ganti Password"):
        new_pw = st.text_input("PW Baru:", type="password")
        if st.button("Simpan Password"):
            st.session_state.users[st.session_state.user_role] = new_pw
            st.success("Berhasil!")
            
    st.divider()
    # Tombol Logout Permanen di Sidebar
    if st.button("🚪 KELUAR SISTEM"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.rerun()

# ==========================================
# 5. DASHBOARD: LOGO & JAM TETAP TENGAH
# ==========================================
_, d_col, _ = st.columns([1, 0.3, 1])
with d_col: st.image("logo_smk.png", use_container_width=True)
st.markdown(f'<div style="text-align:center;"><div class="digital-clock">{waktu_wib}</div></div>', unsafe_allow_html=True)

# TAMPILAN MENU (Sama seperti gambar keren Mas Bro)
if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    t1, t2, t3, t4, t5 = st.tabs(["🎥 MONITOR LIVE", "✍️ INSTRUKSI", "💰 KEUANGAN", "📁 ARSIP LAPORAN", "📚 ARSIP INSTRUKSI"])
    
    with t1:
        st.subheader("Monitoring Pekerjaan Staf")
        df_mon = load_db("monitor.csv")
        st.table(df_mon[::-1] if not df_mon.empty else pd.DataFrame(columns=["Jam", "Staf", "Aktivitas"]))
    # ... (Tab lainnya tetap sama sesuai arsip) ...
    with t2:
        st.subheader("Kirim Instruksi")
        target = st.multiselect("Pilih Staf:", list(st.session_state.users.keys()))
        msg = st.text_area("Isi Instruksi:")
        if st.button("Kirim & Simpan"):
            df_ins = load_db("instruksi.csv")
            save_db(pd.concat([df_ins, pd.DataFrame([{"Jam": waktu_wib, "Target": str(target), "Isi": msg}])], ignore_index=True), "instruksi.csv")
            st.success("Tersimpan!")
    with t3:
        st.subheader("Keuangan")
        df_kas = load_db("kas.csv")
        if not df_kas.empty:
            st.metric("Saldo", f"Rp {df_kas['Masuk'].sum() - df_kas['Keluar'].sum():,}")
            st.dataframe(df_kas[::-1], use_container_width=True)
    with t4: st.dataframe(load_db("monitor.csv")[::-1], use_container_width=True)
    with t5: st.dataframe(load_db("instruksi.csv")[::-1], use_container_width=True)

else:
    # VIEW STAF
    st1, st2, st3 = st.tabs(["📝 LAPOR KERJA", "🔔 INSTRUKSI", "📚 ARSIP SAYA"])
    with st1:
        akt = st.text_area("Update Pekerjaan:")
        if st.button("Kirim"):
            df_mon = load_db("monitor.csv")
            save_db(pd.concat([df_mon, pd.DataFrame([{"Jam": waktu_wib, "Staf": st.session_state.user_role, "Aktivitas": akt}])], ignore_index=True), "monitor.csv")
            st.success("Laporan Masuk!")
    with st2:
        df_ins = load_db("instruksi.csv")
        if not df_ins.empty:
            for i, r in df_ins.iterrows():
                if st.session_state.user_role in str(r['Target']): st.warning(f"**[{r['Jam']}]** {r['Isi']}")
    with st3:
        df_all = load_db("monitor.csv")
        if not df_all.empty:
            st.dataframe(df_all[df_all['Staf'] == st.session_state.user_role][::-1], use_container_width=True)

# KREDIT DI BAWAH (BUKAN TOMBOL LOGOUT)
st.markdown("<p style='text-align:center; color:grey; margin-top:50px;'>E-KENDALI SMK NASIONAL | LOGO RUAS STUDIO | HARDIANTO - PENGEMBANG</p>", unsafe_allow_html=True)import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# ==========================================
# 1. CSS: LOCK SEMUA POSISI KEREN (TENGAH)
# ==========================================
st.set_page_config(page_title="SMK NASIONAL - E-KENDALI", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Jam Digital Glow */
    .digital-clock { 
        font-family: 'Courier New', monospace; color: #ffc107; background-color: #000; font-size: 3.2em; 
        font-weight: bold; text-align: center; border: 3px solid #ffc107; border-radius: 12px; 
        padding: 10px 25px; margin: 15px auto; display: inline-block; box-shadow: 0px 0px 15px #ffc107;
    }
    
    /* Form Login Tetap di Tengah */
    div[data-testid="stForm"] { margin: 0 auto !important; width: 450px !important; border: 2px solid #ffc107 !important; border-radius: 15px; }
    
    /* Styling Khusus Tombol Logout di Sidebar */
    .stSidebar [data-testid="stButton"] button {
        background-color: #d9534f !important;
        color: white !important;
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATABASE & SESSION (TIDAK BERUBAH)
# ==========================================
DB_DIR = "database"
if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)

def load_db(name):
    p = os.path.join(DB_DIR, name)
    return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()

def save_db(df, name):
    df.to_csv(os.path.join(DB_DIR, name), index=False)

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
# 3. HALAMAN LOGIN (POSISI TETAP TENGAH)
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
            else: st.error("Password Salah!")
    st.stop()

# ==========================================
# 4. SIDEBAR: LOGOUT & GANTI PASSWORD (AKTIF!)
# ==========================================
with st.sidebar:
    st.image("logo_smk.png", width=100)
    st.markdown(f"### 👤 {st.session_state.user_role}")
    st.divider()
    
    # Fitur Ganti Password
    with st.expander("🔑 Ganti Password"):
        new_pw = st.text_input("Password Baru:", type="password")
        if st.button("Simpan Perubahan"):
            st.session_state.users[st.session_state.user_role] = new_pw
            st.success("Berhasil diubah!")
            
    st.divider()
    # Tombol Logout
    if st.button("🚪 KELUAR SISTEM"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.rerun()

# ==========================================
# 5. DASHBOARD (SAMA SEPERTI GAMBAR KEREN MAS BRO)
# ==========================================
_, d_col, _ = st.columns([1, 0.3, 1])
with d_col: st.image("logo_smk.png", use_container_width=True)
st.markdown(f'<div style="text-align:center;"><div class="digital-clock">{waktu_wib}</div></div>', unsafe_allow_html=True)

# Tabs Utama (Arsip, Monitor, dll tetap ada)
if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    t1, t2, t3, t4, t5 = st.tabs(["🎥 MONITOR LIVE", "✍️ INSTRUKSI", "💰 KEUANGAN", "📁 ARSIP LAPORAN", "📚 ARSIP INSTRUKSI"])
    
    with t1:
        st.subheader("Monitoring Pekerjaan Staf")
        df_mon = load_db("monitor.csv")
        st.table(df_mon[::-1] if not df_mon.empty else pd.DataFrame(columns=["Jam", "Staf", "Aktivitas"]))

    with t2:
        st.subheader("Kirim Instruksi & Arsipkan")
        target = st.multiselect("Pilih Jabatan:", list(st.session_state.users.keys()))
        msg = st.text_area("Isi Instruksi:")
        if st.button("Sebarkan Instruksi"):
            df_ins = load_db("instruksi.csv")
            new_data = pd.DataFrame([{"Jam": waktu_wib, "Target": str(target), "Isi": msg}])
            save_db(pd.concat([df_ins, new_data], ignore_index=True), "instruksi.csv")
            st.success("Terkirim dan Masuk Arsip!")

    with t3:
        st.subheader("Laporan Kas Keuangan")
        df_kas = load_db("kas.csv")
        if not df_kas.empty:
            st.metric("Saldo Kas", f"Rp {df_kas['Masuk'].sum() - df_kas['Keluar'].sum():,}")
            st.dataframe(df_kas[::-1], use_container_width=True)

    with t4:
        st.subheader("Database Arsip Laporan Pekerjaan")
        st.dataframe(load_db("monitor.csv")[::-1], use_container_width=True)

    with t5:
        st.subheader("Database Arsip Instruksi Pimpinan")
        st.dataframe(load_db("instruksi.csv")[::-1], use_container_width=True)

else:
    # TAMPILAN UNTUK STAF
    st1, st2, st3 = st.tabs(["📝 LAPOR KERJA", "🔔 INSTRUKSI", "📚 ARSIP SAYA"])
    with st1:
        akt = st.text_area("Update Pekerjaan Hari Ini:")
        if st.button("Simpan Laporan"):
            df_mon = load_db("monitor.csv")
            save_db(pd.concat([df_mon, pd.DataFrame([{"Jam": waktu_wib, "Staf": st.session_state.user_role, "Aktivitas": akt}])], ignore_index=True), "monitor.csv")
            st.success("Berhasil Dilaporkan!")
    with st2:
        df_ins = load_db("instruksi.csv")
        if not df_ins.empty:
            for i, r in df_ins.iterrows():
                if st.session_state.user_role in str(r['Target']): st.warning(f"**[{r['Jam']}]** {r['Isi']}")
    with st3:
        df_all = load_db("monitor.csv")
        if not df_all.empty:
            st.dataframe(df_all[df_all['Staf'] == st.session_state.user_role][::-1], use_container_width=True)

st.markdown("<p style='text-align:center; color:grey; margin-top:50px;'>E-KENDALI SMK NASIONAL | LOGOUT & PW READY</p>", unsafe_allow_html=True)

