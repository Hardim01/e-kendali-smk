import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="SMK NASIONAL - E-KENDALI", layout="wide", page_icon="🏛️")

# 2. FUNGSI DATABASE LOKAL (CSV)
def save_data(df, filename):
    df.to_csv(filename, index=False)

def load_data(filename):
    if os.path.exists(filename):
        return pd.read_csv(filename)
    return None

# Definisi File Penyimpanan
FILE_USERS = "database_users.csv"
FILE_KAS = "database_kas.csv"
FILE_LAPORAN = "database_laporan.csv"
FILE_MONITOR = "database_monitor.csv"
FILE_TUGAS = "database_tugas.csv"

# 3. DATABASE & SESSION STATE
if "user_db" not in st.session_state:
    df_load_users = load_data(FILE_USERS)
    if df_load_users is not None:
        st.session_state.user_db = dict(zip(df_load_users.Jabatan, df_load_users.Password))
    else:
        default_users = {
            "ADMIN SISTEM": "admin789", 
            "Kepala Sekolah": "kepsek123", "Ketua Tata Usaha": "ktu123", "Bendahara Bos": "bos123",
            "Bendahara Sekolah": "bendahara123", "Staf bendahara Sekolah": "stafbend123",
            "Staf Publikasi": "publikasi123", "Kesiswaan": "kesiswaan123", "Pembina OSIS": "osis123",
            "Ketertiban": "tertib123", "Kepala LAB": "lab123", "Kepala Perpustakaan": "perpus123",
            "BK": "bk123", "Waka Kurikulum": "kurikulum123", "Waka Kesiswaan": "wakakes123",
            "Waka Hubin": "hubin123", "Waka Sarpras": "sarpras123"
        }
        st.session_state.user_db = default_users
        save_data(pd.DataFrame(list(default_users.items()), columns=['Jabatan', 'Password']), FILE_USERS)

# Load data pendukung lainnya
for key, file in zip(["data_kas", "laporan_masuk", "live_monitor", "tugas_khusus"], [FILE_KAS, FILE_LAPORAN, FILE_MONITOR, FILE_TUGAS]):
    if key not in st.session_state:
        df_l = load_data(file)
        st.session_state[key] = df_l.to_dict('records') if df_l is not None else []

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_role" not in st.session_state: st.session_state.user_role = None

current_time = datetime.now().strftime("%H:%M:%S")

# 4. CUSTOM CSS (DESAIN ASLI RUAS STUDIO)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #000000; color: white; font-weight: bold; }
    .marquee-container {
        background-color: #002b5b; color: #ffffff; padding: 12px 0;
        font-weight: bold; font-size: 1.2em; overflow: hidden;
        white-space: nowrap; border-bottom: 4px solid #ffc107; margin-bottom: 25px;
    }
    .marquee-text { display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite; }
    .highlight-text { color: #ffc107; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    .digital-clock-main {
        font-family: 'Courier New', Courier, monospace;
        color: #ffc107; background-color: #000000;
        font-size: 3.5em; font-weight: bold; text-align: center; 
        border: 3px solid #ffc107; border-radius: 15px; padding: 10px;
    }
    .dev-label { color: #000000 !important; font-size: 1em !important; text-align: center; margin-bottom: 0px; font-weight: bold; }
    .dev-name { color: #000000 !important; font-size: 1.5em !important; font-weight: 900 !important; text-align: center; margin-top: 0px; margin-bottom: 5px; }
    .ruas-text { color: #e60000 !important; font-size: 1.2em !important; font-weight: bold !important; text-align: center; margin-top: 0px; }
    </style>
    """, unsafe_allow_html=True)

# 5. LOGIN SYSTEM
if not st.session_state.logged_in:
    st.markdown(f"""<div class="marquee-container"><div class="marquee-text"><span class="highlight-text">"Kieu Bisa, Kitu Bisa, Sagala Bisa"</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ✨ <span class="highlight-text">Sholat Yang Utama</span> ✨</div></div>""", unsafe_allow_html=True)
    _, col_login, _ = st.columns([1, 1.5, 1])
    with col_login:
        if os.path.exists("logo_smk.png"):
            st.image("logo_smk.png", width=150)
        st.markdown("<h2 style='text-align:center;'>🔐 LOGIN E-KENDALI</h2>", unsafe_allow_html=True)
        u = st.selectbox("Jabatan:", list(st.session_state.user_db.keys()))
        p = st.text_input("Password:", type="password")
        if st.button("MASUK SISTEM"):
            if p == st.session_state.user_db[u]:
                st.session_state.logged_in = True; st.session_state.user_role = u; st.rerun()
            else: st.error("Password Salah!")
    st.stop()

# 6. SIDEBAR
with st.sidebar:
    if os.path.exists("logo_smk.png"):
        st.image("logo_smk.png")
    st.markdown(f"<h3 style='text-align:center;'>SMK NASIONAL</h3>", unsafe_allow_html=True)
    st.info(f"User: {st.session_state.user_role}")
    st.markdown("---")
    st.markdown(f"<h2 style='text-align:center; color:#ffc107; background:#000; border-radius:10px;'>{current_time}</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.link_button("💻 Info GTK", "https://info.gtk.kemdikbud.go.id/")
    st.link_button("📊 Dapodik Online", "https://dapo.kemdikbud.go.id/")
    st.markdown("---")
    
    # LOGO RUAS STUDIO (SIMETRIS TENGAH)
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        if os.path.exists("logo_ruas.png"):
            st.image("logo_ruas.png", width=70)
    
    st.markdown("<p class='dev-label'>Developed by:</p><p class='dev-name'>HARDIANTO</p>", unsafe_allow_html=True)
    st.markdown("<p class='ruas-text'>RUAS STUDIO © 2026</p>", unsafe_allow_html=True)
    
    if st.button("🚪 LOGOUT"):
        st.session_state.logged_in = False; st.rerun()

# 7. DASHBOARD HEADER
st.markdown(f"""<div class="marquee-container"><div class="marquee-text"><span class="highlight-text">"Kieu Bisa, Kitu Bisa, Sagala Bisa"</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ✨ <span class="highlight-text">Pekerjaan memang penting tapi Sholat Yang Utama</span> ✨</div></div>""", unsafe_allow_html=True)
col_h, col_c = st.columns([2, 1])
with col_h: st.markdown(f"<h1 style='color: #002b5b;'>E-KENDALI SMK</h1>", unsafe_allow_html=True)
with col_c: st.markdown(f"<div class='digital-clock-main'>{current_time}</div>", unsafe_allow_html=True)
st.divider()

# 8. DASHBOARD LOGIC
if st.session_state.user_role == "ADMIN SISTEM":
    t1, t2 = st.tabs(["⚙️ KENDALI USER", "📊 DATA SEMUA"])
    with t1:
        st.subheader("Manajemen Password Staf")
        target_pw = st.selectbox("Pilih Akun:", list(st.session_state.user_db.keys()))
        pw_baru = st.text_input("Set Password Baru:", type="password")
        if st.button("Simpan Password"):
            st.session_state.user_db[target_pw] = pw_baru
            save_data(pd.DataFrame(list(st.session_state.user_db.items()), columns=['Jabatan', 'Password']), FILE_USERS)
            st.success("Password Berhasil Diperbarui!")

elif st.session_state.user_role == "Kepala Sekolah":
    t1, t2, t3, t4 = st.tabs(["🎥 MONITOR LIVE", "📁 LAPORAN", "📝 INSTRUKSI", "💰 MONITOR KAS"])
    with t1:
        for act in reversed(st.session_state.live_monitor): st.write(f"{act['Jam']} | **{act['Staf']}**: {act['Aktivitas']}")
    with t2:
        for r in reversed(st.session_state.laporan_masuk):
            with st.expander(f"Laporan {r['Dari']}"): st.write(r['Isi'])
    with t3:
        target = st.selectbox("Ke:", [s for s in st.session_state.user_db.keys() if s != "Kepala Sekolah"])
        isi = st.text_area("Tugas:")
        if st.button("Kirim"):
            st.session_state.tugas_khusus.append({"Jam": current_time, "Ke": target, "Isi": isi})
            save_data(pd.DataFrame(st.session_state.tugas_khusus), FILE_TUGAS)
            st.success("Terkirim!")
    with t4:
        if st.session_state.data_kas: st.dataframe(pd.DataFrame(st.session_state.data_kas))

elif st.session_state.user_role in ["Bendahara Bos", "Bendahara Sekolah", "Staf bendahara Sekolah"]:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("💰 Input Kas")
        jenis = st.selectbox("Tipe:", ["Cash In", "Cash Out"])
        nominal = st.number_input("Nominal:", min_value=0)
        penerima = st.text_input("Penerima:")
        if st.button("Simpan"):
            st.session_state.data_kas.append({"Waktu": current_time, "Masuk": (nominal if "In" in jenis else 0), "Keluar": (nominal if "Out" in jenis else 0), "Penerima": penerima})
            save_data(pd.DataFrame(st.session_state.data_kas), FILE_KAS)
            st.success("Data Tersimpan!")
            st.rerun()
    with c2: st.dataframe(pd.DataFrame(st.session_state.data_kas))

else:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📍 Update Aktivitas")
        act = st.text_input("Sedang mengerjakan apa?")
        if st.button("Update"):
            st.session_state.live_monitor.append({"Jam": current_time, "Staf": st.session_state.user_role, "Aktivitas": act})
            save_data(pd.DataFrame(st.session_state.live_monitor), FILE_MONITOR)
            st.success("Tercatat!")
    with col2:
        st.subheader("📤 Kirim Laporan")
        isi_lap = st.text_area("Isi Laporan:")
        if st.button("Kirim"):
            st.session_state.laporan_masuk.append({"Jam": current_time, "Dari": st.session_state.user_role, "Isi": isi_lap})
            save_data(pd.DataFrame(st.session_state.laporan_masuk), FILE_LAPORAN)
            st.success("Laporan Terkirim!")