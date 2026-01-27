import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import base64
import ast
import time 

# ==========================================
# 1. CSS: STABIL & SEMUA DI TENGAH
# ==========================================
st.set_page_config(page_title="SMK NASIONAL - E-KENDALI", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    .marquee-container { background-color: #002b5b; color: #ffffff; padding: 10px 0; font-weight: bold; border-bottom: 4px solid #ffc107; margin-bottom: 20px; overflow: hidden; white-space: nowrap; }
    .marquee-text { display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite; font-size: 1.1rem; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    
    /* Container Utama untuk Penyelarasan Tengah */
    .center-container { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; width: 100%; }
    
    .digital-clock { 
        font-family: 'Courier New', monospace; color: #ffc107; background-color: #000; font-size: 3.2em; 
        font-weight: bold; text-align: center; border: 3px solid #ffc107; border-radius: 12px; 
        padding: 10px 25px; margin: 15px auto; display: inline-block; box-shadow: 0px 0px 15px #ffc107;
    }
    
    .login-title { color: #ffc107; font-size: 2.2rem; font-weight: bold; margin-bottom: 20px; }
    .stForm { margin: 0 auto; max-width: 450px !important; border: 2px solid #ffc107 !important; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATABASE & SESSION (15 JABATAN LENGKAP)
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

# ==========================================
# 3. HALAMAN LOGIN (SUDAH BAGUS)
# ==========================================
if not st.session_state.logged_in:
    st.markdown('<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Sholat Yang Utama ✨</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="center-container">', unsafe_allow_html=True)
    try: st.image("logo_smk.png", width=120)
    except: st.write("🏛️")
    st.markdown('<div class="login-title">E-KENDALI LOGIN</div>', unsafe_allow_html=True)
    with st.form("login_center"):
        jab = st.selectbox("Pilih Jabatan:", list(st.session_state.users.keys()))
        pw = st.text_input("Password:", type="password")
        if st.form_submit_button("MASUK SISTEM", use_container_width=True):
            if pw == st.session_state.users[jab]:
                st.session_state.logged_in = True; st.session_state.user_role = jab; st.rerun()
            else: st.error("Akses Ditolak!")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 4. DASHBOARD HEADER (LOGO TENGAH + JAM)
# ==========================================
st.markdown('<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Sholat Yang Utama ✨</div></div>', unsafe_allow_html=True)

st.markdown('<div class="center-container">', unsafe_allow_html=True)
try: st.image("logo_smk.png", width=100)
except: st.write("🏛️")
st.markdown(f'<div class="digital-clock">{waktu_wib}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

c_info, c_out = st.columns([4, 1])
with c_info: st.info(f"👤 Login Sebagai: **{st.session_state.user_role}**")
with c_out: 
    if st.button("🚪 KELUAR", use_container_width=True):
        st.session_state.logged_in = False; st.rerun()

st.divider()

# ==========================================
# 5. KEMBALIKAN MENU SESUAI JABATAN
# ==========================================
if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    t1, t2, t3, t4 = st.tabs(["🎥 MONITOR LIVE", "📁 LAPORAN MASUK", "✍️ INSTRUKSI", "💰 KEUANGAN"])
    with t1:
        if st.session_state.live_monitor: st.table(pd.DataFrame(st.session_state.live_monitor)[::-1])
        else: st.write("Belum ada aktivitas hari ini.")
    with t2:
        for r in reversed(st.session_state.laporan_masuk):
            with st.expander(f"Lap: {r['Dari']} ({r['Jam']})"):
                st.write(r['Isi'])
                if 'Lampiran' in r and r['Lampiran']:
                    st.write("📎 Ada Lampiran File")
    with t3:
        target = st.multiselect("Pilih Target Staf:", [u for u in st.session_state.users.keys() if u != "Kepala Sekolah"])
        msg = st.text_area("Isi Instruksi:")
        if st.button("Kirim Instruksi"):
            for s in target: st.session_state.tugas_khusus.append({"Jam": waktu_wib, "Untuk": s, "Instruksi": msg})
            save_data(st.session_state.tugas_khusus, "database_tugas.csv"); st.success("Terkirim!")
    with t4:
        df_k = pd.DataFrame(st.session_state.data_kas)
        if not df_k.empty:
            st.subheader("DANA BOS"); st.dataframe(df_k[df_k['Kategori']=='DANA BOS'][::-1], use_container_width=True)
            st.subheader("DANA NON-BOS"); st.dataframe(df_k[df_k['Kategori']=='DANA NON-BOS'][::-1], use_container_width=True)

else:
    # MENU UNTUK STAF LAINNYA
    ts1, ts2, ts3 = st.tabs(["📝 INPUT KERJA", "🔔 INSTRUKSI", "📚 ARSIP SAYA"])
    with ts1:
        if "Bendahara" in st.session_state.user_role:
            with st.expander("💰 Input Kas Sekolah"):
                with st.form("f_kas"):
                    k = st.radio("Dana:", ["DANA BOS", "DANA NON-BOS"], horizontal=True)
                    t = st.selectbox("Jenis:", ["Masuk", "Keluar"])
                    n = st.number_input("Nominal:")
                    ket = st.text_input("Keterangan:")
                    if st.form_submit_button("Simpan Kas"):
                        st.session_state.data_kas.append({"Waktu": waktu_wib, "Kategori": k, "Masuk": n if t=="Masuk" else 0, "Keluar": n if t=="Keluar" else 0, "Keterangan": ket})
                        save_data(st.session_state.data_kas, "database_kas.csv"); st.rerun()

        st.write("### Laporan Aktivitas")
        act = st.text_area("Apa yang Anda kerjakan saat ini?")
        if st.button("Simpan Aktivitas"):
            st.session_state.live_monitor.append({"Jam": waktu_wib, "Staf": st.session_state.user_role, "Aktivitas": act})
            save_data(st.session_state.live_monitor, "database_monitor.csv"); st.success("Tersimpan!"); time.sleep(1); st.rerun()

    with ts2:
        st.write("### Instruksi Pimpinan")
        for t in reversed(st.session_state.tugas_khusus):
            if t['Untuk'] == st.session_state.user_role: st.warning(f"[{t['Jam']}] {t['Instruksi']}")
    
    with ts3:
        my = [a for a in st.session_state.live_monitor if a['Staf'] == st.session_state.user_role]
        if my: st.table(pd.DataFrame(my)[::-1])

st.markdown("<p style='text-align:center; color:grey; margin-top:50px;'>E-KENDALI SMK NASIONAL | HARDIANTO - RUAS STUDIO</p>", unsafe_allow_html=True)
time.sleep(1); st.rerun()
