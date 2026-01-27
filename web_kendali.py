import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64
import ast

# ==========================================
# 1. PAGE & CSS CONFIG
# ==========================================
st.set_page_config(page_title="SMK NASIONAL - E-KENDALI", layout="wide", page_icon="🏛️")

def get_base64_image(image_path):
    if os.path.exists(image_path):
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except: return None
    return None

def process_file_upload(uploaded_file):
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        base64_file = base64.b64encode(file_bytes).decode()
        return {"name": uploaded_file.name, "data": base64_file, "type": uploaded_file.type}
    return None

def display_attachment(file_info):
    try:
        if file_info and isinstance(file_info, str):
            file_info = ast.literal_eval(file_info)
        if file_info and isinstance(file_info, dict):
            file_name = file_info.get("name", "File")
            file_data = file_info.get("data", "")
            file_type = file_info.get("type", "")
            href = f'<a href="data:{file_type};base64,{file_data}" download="{file_name}">📥 Download Lampiran: {file_name}</a>'
            st.markdown(href, unsafe_allow_html=True)
            if "image" in file_type:
                st.image(f"data:{file_type};base64,{file_data}", width=250)
    except: pass

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
# 2. DATABASE SYSTEM
# ==========================================
DB_DIR = "database"
if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)

DEFAULT_USERS = {
    "ADMIN SISTEM": "admin789", "Kepala Sekolah": "kepsek123", "Ketua Tata Usaha": "ktu123", 
    "Bendahara Bos": "bos123", "Bendahara Sekolah": "bendahara123", "Staf bendahara Sekolah": "stafbend123",
    "Staf Publikasi": "publikasi123", "Kesiswaan": "kesiswaan123", "Pembina OSIS": "osis123",
    "Ketertiban": "tertib123", "Kepala LAB": "lab123", "Kepala Perpustakaan": "perpus123",
    "BK": "bk123", "Waka Kurikulum": "kurikulum123", "Waka Kesiswaan": "wakakes123",
    "Waka Hubin": "hubin123", "Waka Sarpras": "sarpras123"
}

def load_users():
    path = os.path.join(DB_DIR, "database_users.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        return dict(zip(df.Role, df.Password))
    return DEFAULT_USERS

def save_users(users_dict):
    df = pd.DataFrame(list(users_dict.items()), columns=['Role', 'Password'])
    df.to_csv(os.path.join(DB_DIR, "database_users.csv"), index=False)

def save_data(data_list, filename):
    pd.DataFrame(data_list).to_csv(os.path.join(DB_DIR, filename), index=False)

def load_data(filename):
    path = os.path.join(DB_DIR, filename)
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            return df.to_dict('records')
        except: return []
    return []

# ==========================================
# 3. SESSION INITIALIZATION
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False, "user_role": None,
        "users": load_users(),
        "data_kas": load_data("database_kas.csv"),
        "live_monitor": load_data("database_monitor.csv"),
        "laporan_masuk": load_data("database_laporan.csv"),
        "tugas_khusus": load_data("database_tugas.csv")
    })

current_time = datetime.now().strftime("%H:%M:%S")

# ==========================================
# 4. LOGIN INTERFACE
# ==========================================
if not st.session_state.logged_in:
    st.markdown('<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Pekerjaan memang penting tapi Sholat Yang Utama ✨</div></div>', unsafe_allow_html=True)
    st.markdown('<p class="welcome-text-gold">Selamat Datang di Aplikasi Kendali Sekolah</p>', unsafe_allow_html=True)
    logo_smk_b64 = get_base64_image("logo_smk.png")
    if logo_smk_b64:
        st.markdown(f'<div style="display: flex; justify-content: center; padding: 10px;"><img src="data:image/png;base64,{logo_smk_b64}" width="120"></div>', unsafe_allow_html=True)
    st.markdown('<p class="school-text-gold">SMK Nasional Bandung</p>', unsafe_allow_html=True)
    _, col_login, _ = st.columns([1, 0.8, 1])
    with col_login:
        u = st.selectbox("Pilih Jabatan:", list(st.session_state.users.keys()))
        p = st.text_input("Password:", type="password")
        if st.button("MASUK SISTEM", use_container_width=True):
            if p == st.session_state.users[u]:
                st.session_state.logged_in = True; st.session_state.user_role = u; st.rerun()
            else: st.error("Password Salah!")
    st.stop()

# ==========================================
# 5. SIDEBAR
# ==========================================
with st.sidebar:
    logo_sidebar = get_base64_image("logo_smk.png")
    if logo_sidebar:
        st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo_sidebar}" width="80"></div>', unsafe_allow_html=True)
    st.success(f"Login: **{st.session_state.user_role}**")
    st.markdown(f"<h2 class='digital-clock-main'>{current_time}</h2>", unsafe_allow_html=True)
    
    # MENU MANDIRI: GANTI PASSWORD SENDIRI
    with st.expander("🔑 Ganti Password Saya"):
        new_pw = st.text_input("Password Baru:", type="password", key="self_pw")
        if st.button("Update Password Saya"):
            if new_pw:
                st.session_state.users[st.session_state.user_role] = new_pw
                save_users(st.session_state.users)
                st.success("Berhasil Diganti!")
            else: st.warning("Isi password!")

    # MENU ADMIN: RESET PASSWORD STAF (Hanya Muncul Jika Login Admin Sistem)
    if st.session_state.user_role == "ADMIN SISTEM":
        st.divider()
        with st.expander("🛠️ PANEL RESET PASSWORD (ADMIN)", expanded=True):
            user_to_reset = st.selectbox("Pilih Staf:", list(st.session_state.users.keys()))
            reset_pw = st.text_input("Password Baru Staf:", type="password", key="admin_pw")
            if st.button("RESET PASSWORD STAF"):
                if reset_pw:
                    st.session_state.users[user_to_reset] = reset_pw
                    save_users(st.session_state.users)
                    st.success(f"Password {user_to_reset} Berhasil Direset!")
                else: st.warning("Isi password reset!")
            
    st.divider()
    logo_ruas_b64 = get_base64_image("logo_ruas.png")
    if logo_ruas_b64:
        st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo_ruas_b64}" width="50"></div>', unsafe_allow_html=True)
    st.markdown("<p class='dev-name'>HARDIANTO</p><p class='ruas-text'>RUAS STUDIO © 2026</p>", unsafe_allow_html=True)
    if st.button("🚪 LOGOUT", use_container_width=True):
        st.session_state.logged_in = False; st.rerun()

# ==========================================
# 6. HITUNG SALDO KAS
# ==========================================
df_kas = pd.DataFrame(st.session_state.data_kas)
if not df_kas.empty:
    m = pd.to_numeric(df_kas['Masuk'], errors='coerce').fillna(0)
    k = pd.to_numeric(df_kas['Keluar'], errors='coerce').fillna(0)
    total_saldo = m.sum() - k.sum()
else:
    total_saldo = 0

# ==========================================
# 7. MAIN DASHBOARD
# ==========================================
st.markdown('<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Pekerjaan memang penting tapi Sholat Yang Utama ✨</div></div>', unsafe_allow_html=True)

role = st.session_state.user_role

# --- KEPALA SEKOLAH & ADMIN ---
if role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    st.info(f"💰 **TOTAL SALDO KAS SAAT INI: Rp {total_saldo:,.0f}**")
    t1, t2, t3, t4 = st.tabs(["🎥 MONITOR LIVE", "📁 LAPORAN STAF", "✍️ INSTRUKSI", "💰 KEUANGAN"])
    with t1: 
        if st.session_state.live_monitor: st.table(pd.DataFrame(st.session_state.live_monitor)[::-1])
    with t2:
        for r in reversed(st.session_state.laporan_masuk):
            with st.expander(f"Laporan {r['Dari']} ({r['Jam']})"): 
                st.write(r['Isi'])
                if 'Lampiran' in r: display_attachment(r['Lampiran'])
    with t3:
        target = st.multiselect("Pilih Staf:", [j for j in st.session_state.users.keys() if j not in ["Kepala Sekolah", "ADMIN SISTEM"]])
        pes_k = st.text_area("Pesan:")
        f_k = st.file_uploader("Lampiran:")
        if st.button("KIRIM"):
            if target:
                f_data = process_file_upload(f_k)
                for s in target:
                    st.session_state.tugas_khusus.append({"Jam": current_time, "Untuk": s, "Instruksi": pes_k, "Lampiran": f_data})
                save_data(st.session_state.tugas_khusus, "database_tugas.csv"); st.rerun()
        if st.session_state.tugas_khusus: st.dataframe(pd.DataFrame(st.session_state.tugas_khusus)[::-1], use_container_width=True)
    with t4: st.dataframe(df_kas[::-1], use_container_width=True)

# --- BENDAHARA / STAF ---
else:
    tasks = [t for t in st.session_state.tugas_khusus if t['Untuk'] == role]
    if tasks:
        for t in reversed(tasks):
            with st.expander(f"🔔 INSTRUKSI KEPSEK ({t['Jam']})", expanded=True):
                st.write(t['Instruksi'])
                if 'Lampiran' in t: display_attachment(t['Lampiran'])
    
    if "Bendahara" in role:
        st.info(f"💰 **TOTAL SALDO KAS: Rp {total_saldo:,.0f}**")
        c1, c2 = st.columns([1, 2])
        with c1:
            with st.form("kas"):
                tp = st.selectbox("Jenis", ["Masuk", "Keluar"])
                nm = st.number_input("Nominal", min_value=0)
                pa = st.selectbox("Unit:", ["Sarpras", "Kurikulum", "Kesiswaan", "Hubin", "TU", "Lainnya"])
                kt = st.text_input("Ket:")
                if st.form_submit_button("Simpan"):
                    st.session_state.data_kas.append({"Waktu": current_time, "Masuk": nm if tp=="Masuk" else 0, "Keluar": nm if tp=="Keluar" else 0, "Pengguna": pa, "Keterangan": kt})
                    save_data(st.session_state.data_kas, "database_kas.csv"); st.rerun()
        with c2: st.dataframe(df_kas[::-1].head(10), use_container_width=True)
        st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        ac = st.text_area("Aktivitas Anda:")
        if st.button("Update Aktivitas"):
            st.session_state.live_monitor.append({"Jam": current_time, "Staf": role, "Aktivitas": ac})
            save_data(st.session_state.live_monitor, "database_monitor.csv"); st.success("Update!")
    with col_b:
        lp = st.text_area("Laporan ke Kepsek:")
        f_st = st.file_uploader("Lampiran:", key="up_s")
        if st.button("Kirim Laporan"):
            fd = process_file_upload(f_st)
            st.session_state.laporan_masuk.append({"Jam": current_time, "Dari": role, "Isi": lp, "Lampiran": fd})
            save_data(st.session_state.laporan_masuk, "database_laporan.csv"); st.rerun()

if st.session_state.logged_in:
    st.divider()
    if os.path.exists("kalender_akademik.png"): st.image("kalender_akademik.png", use_container_width=True)

