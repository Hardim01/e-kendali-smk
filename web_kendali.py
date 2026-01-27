import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64
import ast
import time 

# ==========================================
# 1. PAGE CONFIG & UI STYLE
# ==========================================
st.set_page_config(page_title="SMK NASIONAL - E-KENDALI", layout="wide", page_icon="🏛️")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
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
# 2. FUNGSI UTAMA (DATABASE & FILE)
# ==========================================
DB_DIR = "database"
if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

def save_data(data_list, filename):
    pd.DataFrame(data_list).to_csv(os.path.join(DB_DIR, filename), index=False)

def load_data(filename):
    path = os.path.join(DB_DIR, filename)
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            if filename == "database_kas.csv" and 'Kategori' not in df.columns:
                df['Kategori'] = 'DANA NON-BOS'
            return df.to_dict('records')
        except: return []
    return []

def process_file_upload(uploaded_file):
    if uploaded_file:
        return {"name": uploaded_file.name, "data": base64.b64encode(uploaded_file.getvalue()).decode(), "type": uploaded_file.type}
    return None

def display_attachment(file_info):
    try:
        if isinstance(file_info, str): file_info = ast.literal_eval(file_info)
        if file_info and isinstance(file_info, dict):
            href = f'<a href="data:{file_info["type"]};base64,{file_info["data"]}" download="{file_info["name"]}">📥 Download: {file_info["name"]}</a>'
            st.markdown(href, unsafe_allow_html=True)
            if "image" in file_info["type"]: st.image(f"data:{file_info['type']};base64,{file_info['data']}", width=250)
    except: pass

# ==========================================
# 3. SESSION & LOGIN LOGIC
# ==========================================
USERS = {
    "Kepala Sekolah": "kepsek123", "Ketua Tata Usaha": "ktu123", "Bendahara Bos": "bos123", 
    "Bendahara Sekolah": "bendahara123", "Waka Kurikulum": "kurikulum123", "ADMIN SISTEM": "admin789"
}

if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False, "user_role": None,
        "data_kas": load_data("database_kas.csv"),
        "live_monitor": load_data("database_monitor.csv"),
        "laporan_masuk": load_data("database_laporan.csv"),
        "tugas_khusus": load_data("database_tugas.csv")
    })

waktu_skrg = datetime.now().strftime("%H:%M:%S")

# --- INTERFACE LOGIN ---
if not st.session_state.logged_in:
    st.markdown('<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Pekerjaan memang penting tapi Sholat Yang Utama ✨</div></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        logo = get_base64_image("logo_smk.png")
        if logo: st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo}" width="150"></div>', unsafe_allow_html=True)
        st.markdown('<p class="welcome-text-gold">E-KENDALI SEKOLAH</p>', unsafe_allow_html=True)
        
        jabatan = st.selectbox("Pilih Jabatan:", ["--- Pilih ---"] + list(USERS.keys()))
        sandi = st.text_input("Kode Akses:", type="password")
        
        if st.button("MASUK SISTEM", use_container_width=True):
            if jabatan in USERS and sandi == USERS[jabatan]:
                st.session_state.logged_in = True
                st.session_state.user_role = jabatan
                st.rerun()
            else:
                st.error("Akses Ditolak!")
    st.stop() # Mencegah dashboard muncul sebelum login

# ==========================================
# 4. DASHBOARD (SETELAH LOGIN)
# ==========================================
# Hitung Saldo
df_kas = pd.DataFrame(st.session_state.data_kas)
s_bos = 0; s_non = 0
if not df_kas.empty:
    b = df_kas[df_kas['Kategori'] == 'DANA BOS']
    s_bos = pd.to_numeric(b['Masuk']).sum() - pd.to_numeric(b['Keluar']).sum()
    n = df_kas[df_kas['Kategori'] == 'DANA NON-BOS']
    s_non = pd.to_numeric(n['Masuk']).sum() - pd.to_numeric(n['Keluar']).sum()

# Sidebar
with st.sidebar:
    st.markdown(f"<h2 class='digital-clock-main'>{waktu_skrg}</h2>", unsafe_allow_html=True)
    st.success(f"User: {st.session_state.user_role}")
    if st.button("🚪 LOGOUT"):
        st.session_state.logged_in = False; st.rerun()
    st.divider()
    st.markdown("<p class='dev-name'>HARDIANTO</p><p class='ruas-text'>RUAS STUDIO</p>", unsafe_allow_html=True)

st.markdown('<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Sholat Yang Utama ✨</div></div>', unsafe_allow_html=True)

# Tampilan Kepsek vs Staf
if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    c1, c2 = st.columns(2)
    c1.metric("💰 SALDO BOS", f"Rp {s_bos:,.0f}")
    c2.metric("💵 SALDO NON-BOS", f"Rp {s_non:,.0f}")
    
    t1, t2, t3, t4 = st.tabs(["🎥 LIVE MONITOR", "📁 LAPORAN", "✍️ INSTRUKSI", "💰 KEUANGAN"])
    with t1: st.table(pd.DataFrame(st.session_state.live_monitor)[::-1])
    with t2:
        for r in reversed(st.session_state.laporan_masuk):
            with st.expander(f"Laporan {r['Dari']} ({r['Jam']})"):
                st.write(r['Isi'])
                if 'Lampiran' in r: display_attachment(r['Lampiran'])
    with t3:
        tgt = st.multiselect("Pilih Staf:", [u for u in USERS.keys() if u != "Kepala Sekolah"])
        msg = st.text_area("Pesan:")
        if st.button("Kirim Instruksi"):
            for s in tgt:
                st.session_state.tugas_khusus.append({"Jam": waktu_skrg, "Untuk": s, "Instruksi": msg})
            save_data(st.session_state.tugas_khusus, "database_tugas.csv"); st.rerun()
    with t4:
        st.subheader("Jurnal BOS"); st.dataframe(df_kas[df_kas['Kategori']=='DANA BOS'][::-1], use_container_width=True)
        st.subheader("Jurnal Non-BOS"); st.dataframe(df_kas[df_kas['Kategori']=='DANA NON-BOS'][::-1], use_container_width=True)

else:
    # Dashboard Staf
    t_staf1, t_staf2, t_staf3 = st.tabs(["📝 INPUT KERJA", "🔔 INSTRUKSI", "📚 ARSIP SAYA"])
    with t_staf1:
        if "Bendahara" in st.session_state.user_role:
            with st.form("keuangan"):
                kat = st.radio("Sumber:", ["DANA BOS", "DANA NON-BOS"], horizontal=True)
                tipe = st.selectbox("Jenis:", ["Masuk", "Keluar"])
                nom = st.number_input("Nominal:", min_value=0)
                ket = st.text_input("Ket:")
                if st.form_submit_button("Simpan"):
                    st.session_state.data_kas.append({"Waktu": waktu_skrg, "Kategori": kat, "Masuk": nom if tipe=="Masuk" else 0, "Keluar": nom if tipe=="Keluar" else 0, "Keterangan": ket})
                    save_data(st.session_state.data_kas, "database_kas.csv"); st.rerun()
        
        ca, cb = st.columns(2)
        with ca:
            act = st.text_area("Aktivitas Anda:")
            if st.button("Kirim Aktivitas"):
                st.session_state.live_monitor.append({"Jam": waktu_skrg, "Staf": st.session_state.user_role, "Aktivitas": act})
                save_data(st.session_state.live_monitor, "database_monitor.csv"); st.rerun()
        with cb:
            lap = st.text_area("Laporan ke Kepsek:")
            if st.button("Kirim Laporan"):
                st.session_state.laporan_masuk.append({"Jam": waktu_skrg, "Dari": st.session_state.user_role, "Isi": lap})
                save_data(st.session_state.laporan_masuk, "database_laporan.csv"); st.rerun()

    with t_staf2:
        my_tasks = [t for t in st.session_state.tugas_khusus if t['Untuk'] == st.session_state.user_role]
        for t in reversed(my_tasks):
            st.info(f"[{t['Jam']}] {t['Instruksi']}")

    with t_staf3:
        st.subheader("Riwayat Kerja Anda")
        my_history = [a for a in st.session_state.live_monitor if a['Staf'] == st.session_state.user_role]
        st.table(pd.DataFrame(my_history)[::-1])

time.sleep(1)
st.rerun()
