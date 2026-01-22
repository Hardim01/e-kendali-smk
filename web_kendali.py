import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64

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

# Fungsi untuk memproses file upload menjadi link download
def process_file_upload(uploaded_file):
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        base64_file = base64.b64encode(file_bytes).decode()
        return {"name": uploaded_file.name, "data": base64_file, "type": uploaded_file.type}
    return None

def display_attachment(file_info):
    if file_info and isinstance(file_info, dict):
        file_name = file_info.get("name", "File")
        file_data = file_info.get("data", "")
        file_type = file_info.get("type", "")
        
        href = f'<a href="data:{file_type};base64,{file_data}" download="{file_name}">📥 Download Lampiran: {file_name}</a>'
        st.markdown(href, unsafe_allow_html=True)
        
        # Jika gambar, tampilkan preview
        if "image" in file_type:
            st.image(f"data:{file_type};base64,{file_data}", width=200)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .marquee-container { background-color: #002b5b; color: #ffffff; padding: 12px 0; font-weight: bold; border-bottom: 4px solid #ffc107; margin-bottom: 25px; overflow: hidden; white-space: nowrap; }
    .marquee-text { display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite; font-size: 1.2rem; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    .digital-clock-main { font-family: 'Courier New', monospace; color: #ffc107; background-color: #000; font-size: 3em; font-weight: bold; text-align: center; border: 3px solid #ffc107; border-radius: 15px; padding: 10px; }
    .welcome-text-gold { color: #ffc107; font-weight: bold; font-size: 1.8rem; text-align: center; text-shadow: 2px 2px 4px #000; }
    .school-text-gold { color: #ffc107; font-weight: bold; font-size: 1.6rem; text-align: center; text-shadow: 2px 2px 4px #000; }
    .dev-name { color: #000; font-weight: 900; text-align: center; }
    .ruas-text { color: #e60000; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATABASE SYSTEM
# ==========================================
USER_DB = {
    "ADMIN SISTEM": "admin789", "Kepala Sekolah": "kepsek123", "Ketua Tata Usaha": "ktu123", 
    "Bendahara Bos": "bos123", "Bendahara Sekolah": "bendahara123", "Staf bendahara Sekolah": "stafbend123",
    "Staf Publikasi": "publikasi123", "Kesiswaan": "kesiswaan123", "Pembina OSIS": "osis123",
    "Ketertiban": "tertib123", "Kepala LAB": "lab123", "Kepala Perpustakaan": "perpus123",
    "BK": "bk123", "Waka Kurikulum": "kurikulum123", "Waka Kesiswaan": "wakakes123",
    "Waka Hubin": "hubin123", "Waka Sarpras": "sarpras123"
}

DB_DIR = "database"
if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)

def save_data(data_list, filename):
    pd.DataFrame(data_list).to_csv(os.path.join(DB_DIR, filename), index=False)

def load_data(filename):
    path = os.path.join(DB_DIR, filename)
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            # Konversi kolom string JSON/Dict kembali ke objek jika perlu
            import ast
            for col in df.columns:
                df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('{') else x)
            return df.to_dict('records')
        except: return []
    return []

# ==========================================
# 3. SESSION INITIALIZATION
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False, "user_role": None,
        "data_kas": load_data("database_kas.csv"),
        "live_monitor": load_data("database_monitor.csv"),
        "laporan_masuk": load_data("database_laporan.csv"),
        "tugas_khusus": load_data("database_tugas.csv")
    })

current_time = datetime.now().strftime("%H:%M:%S")

# ==========================================
# 4. HALAMAN LOGIN
# ==========================================
if not st.session_state.logged_in:
    st.markdown('<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Pekerjaan memang penting tapi Sholat Yang Utama ✨</div></div>', unsafe_allow_html=True)
    st.markdown('<p class="welcome-text-gold">Selamat Datang di Aplikasi Kendali Sekolah</p>', unsafe_allow_html=True)
    logo_base64 = get_base64_image("logo_smk.png")
    if logo_base64:
        st.markdown(f'<div style="display: flex; justify-content: center; padding: 10px;"><img src="data:image/png;base64,{logo_base64}" width="120"></div>', unsafe_allow_html=True)
    st.markdown('<p class="school-text-gold">SMK Nasional Bandung</p>', unsafe_allow_html=True)
    _, col_form, _ = st.columns([1, 0.8, 1])
    with col_form:
        u = st.selectbox("Pilih Jabatan:", list(USER_DB.keys()))
        p = st.text_input("Password:", type="password")
        if st.button("MASUK SISTEM", use_container_width=True):
            if p == USER_DB[u]:
                st.session_state.logged_in = True; st.session_state.user_role = u; st.rerun()
            else: st.error("Password Salah!")
    st.stop()

# ==========================================
# 5. SIDEBAR
# ==========================================
with st.sidebar:
    if os.path.exists("logo_smk.png"): st.image("logo_smk.png")
    st.success(f"User: **{st.session_state.user_role}**")
    st.markdown(f"<h2 class='digital-clock-main'>{current_time}</h2>", unsafe_allow_html=True)
    st.divider()
    st.link_button("🗓️ Kalender Jabar", "https://disdik.jabarprov.go.id/akademik")
    st.link_button("🏫 PSMK", "https://psmk.kemdikbud.go.id/")
    st.divider()
    st.markdown("<p class='dev-name'>HARDIANTO</p><p class='ruas-text'>RUAS STUDIO © 2026</p>", unsafe_allow_html=True)
    if st.button("🚪 LOGOUT", use_container_width=True):
        st.session_state.logged_in = False; st.rerun()

# ==========================================
# 6. DASHBOARD UTAMA
# ==========================================
st.markdown('<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Pekerjaan memang penting tapi Sholat Yang Utama ✨</div></div>', unsafe_allow_html=True)

role = st.session_state.user_role
df_kas = pd.DataFrame(st.session_state.data_kas)

# --- ROLE: KEPALA SEKOLAH ---
if role == "Kepala Sekolah":
    t1, t2, t3, t4 = st.tabs(["🎥 MONITOR LIVE", "📁 LAPORAN STAF", "✍️ INSTRUKSI", "💰 KAS"])
    with t1: st.table(pd.DataFrame(st.session_state.live_monitor)[::-1])
    with t2:
        for r in reversed(st.session_state.laporan_masuk):
            with st.expander(f"Laporan {r['Dari']} ({r['Jam']})"): 
                st.write(r['Isi'])
                if 'Lampiran' in r: display_attachment(r['Lampiran'])
    with t3:
        target = st.multiselect("Pilih Staf:", [j for j in USER_DB.keys() if j != "Kepala Sekolah"])
        pesan = st.text_area("Isi Instruksi:")
        file_kepsek = st.file_uploader("Lampirkan Dokumen (Photo/PDF/Video/Word):", type=['png','jpg','jpeg','pdf','docx','mp4'])
        if st.button("KIRIM INSTRUKSI"):
            file_data = process_file_upload(file_kepsek)
            for s in target:
                st.session_state.tugas_khusus.append({"Jam": current_time, "Untuk": s, "Instruksi": pesan, "Lampiran": file_data})
            save_data(st.session_state.tugas_khusus, "database_tugas.csv"); st.success("Terkirim!"); st.rerun()
    with t4: st.dataframe(df_kas[::-1], use_container_width=True)

# --- ROLE: STAF (Termasuk Bendahara) ---
else:
    # Cek Instruksi Kepsek
    tasks = [t for t in st.session_state.tugas_khusus if t['Untuk'] == role]
    if tasks:
        with st.expander("🔔 INSTRUKSI KEPALA SEKOLAH", expanded=True):
            for t in reversed(tasks):
                st.warning(f"🕒 {t['Jam']}: {t['Instruksi']}")
                if 'Lampiran' in t: display_attachment(t['Lampiran'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Monitoring Live")
        ac = st.text_area("Aktivitas saat ini:")
        if st.button("Update Aktivitas"):
            st.session_state.live_monitor.append({"Jam": current_time, "Staf": role, "Aktivitas": ac})
            save_data(st.session_state.live_monitor, "database_monitor.csv"); st.success("Update!")
    with col2:
        st.subheader("Kirim Laporan Resmi")
        lp = st.text_area("Isi Laporan Detail:")
        file_staf = st.file_uploader("Lampirkan Bukti (Photo/PDF/Video/Word):", type=['png','jpg','jpeg','pdf','docx','mp4'], key="staf_up")
        if st.button("Kirim ke Kepsek"):
            file_data = process_file_upload(file_staf)
            st.session_state.laporan_masuk.append({"Jam": current_time, "Dari": role, "Isi": lp, "Lampiran": file_data})
            save_data(st.session_state.laporan_masuk, "database_laporan.csv"); st.success("Laporan Terkirim!"); st.rerun()
