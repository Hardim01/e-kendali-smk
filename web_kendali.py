import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import base64
import ast
import time 

# ==========================================
# 1. POSISI LOGO & LOGIN (FIXED SYMMETRIC)
# ==========================================
st.set_page_config(page_title="SMK NASIONAL - E-KENDALI", layout="wide", page_icon="🏛️")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Marquee Styling */
    .marquee-container { background-color: #002b5b; color: #ffffff; padding: 12px 0; font-weight: bold; border-bottom: 4px solid #ffc107; margin-bottom: 25px; overflow: hidden; white-space: nowrap; }
    .marquee-text { display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite; font-size: 1.2rem; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    
    /* Digital Clock */
    .digital-clock-main { font-family: 'Courier New', monospace; color: #ffc107; background-color: #000; font-size: 3em; font-weight: bold; text-align: center; border: 3px solid #ffc107; border-radius: 15px; padding: 10px; margin-bottom: 20px; }
    
    /* Logo Position Fix */
    .header-container { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding: 0 20px; }
    .logo-img { width: 80px; }
    
    /* Login Box Center Fix */
    .stForm { margin: 0 auto; max-width: 450px; padding: 30px; border: 1px solid #ffc107; border-radius: 15px; background: #0e1117; }
    .welcome-text-gold { color: #ffc107; font-weight: bold; font-size: 1.8rem; text-align: center; text-shadow: 2px 2px 4px #000; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATABASE & UTILS
# ==========================================
DB_DIR = "database"
if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)

def save_data(data_list, filename): pd.DataFrame(data_list).to_csv(os.path.join(DB_DIR, filename), index=False)
def load_data(filename):
    path = os.path.join(DB_DIR, filename)
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            if filename == "database_kas.csv" and 'Kategori' not in df.columns: df['Kategori'] = 'DANA NON-BOS'
            return df.to_dict('records')
        except: return []
    return []

# ==========================================
# 3. SESSION STATE
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False, "user_role": None,
        "users": {"Kepala Sekolah": "kepsek123", "Ketua Tata Usaha": "ktu123", "Bendahara Bos": "bos123", "Bendahara Sekolah": "bendahara123", "Staf bendahara Sekolah": "stafbend123", "Waka Kurikulum": "kurikulum123", "Waka Kesiswaan": "wakakes123", "Waka Hubin": "hubin123", "Waka Sarpras": "sarpras123", "ADMIN SISTEM": "admin789"},
        "data_kas": load_data("database_kas.csv"),
        "live_monitor": load_data("database_monitor.csv"),
        "laporan_masuk": load_data("database_laporan.csv"),
        "tugas_khusus": load_data("database_tugas.csv")
    })

waktu_skrg = (datetime.now() + timedelta(hours=7)).strftime("%H:%M:%S")

# ==========================================
# 4. HALAMAN LOGIN (DI TENGAH)
# ==========================================
if not st.session_state.logged_in:
    st.markdown('<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Sholat Yang Utama ✨</div></div>', unsafe_allow_html=True)
    
    # Header Login dengan Logo Kiri & Kanan
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l1:
        try: st.image("logo_smk.png", width=100)
        except: st.markdown("🏛️")
    with col_l3:
        try: st.image("logo_ruas.png", width=80)
        except: st.write("")
        
    st.markdown('<p class="welcome-text-gold">E-KENDALI SMK NASIONAL</p>', unsafe_allow_html=True)
    
    # Form Login Center
    with st.form("login_form"):
        jab = st.selectbox("Pilih Jabatan:", ["--- Pilih ---"] + list(st.session_state.users.keys()))
        pw = st.text_input("Password:", type="password")
        submit = st.form_submit_button("MASUK KE SISTEM", use_container_width=True)
        if submit:
            if jab in st.session_state.users and pw == st.session_state.users[jab]:
                st.session_state.logged_in = True
                st.session_state.user_role = jab
                st.rerun()
            else: st.error("Akses Ditolak!")
    st.stop()

# ==========================================
# 5. HEADER DASHBOARD (SIMETRIS)
# ==========================================
st.markdown('<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Sholat Yang Utama ✨</div></div>', unsafe_allow_html=True)

head_1, head_2, head_3 = st.columns([1, 2, 1])

with head_1:
    try: st.image("logo_smk.png", width=90)
    except: st.write("🏛️ **SMK NASIONAL**")
    st.info(f"User: {st.session_state.user_role}")

with head_2:
    st.markdown(f"<h2 class='digital-clock-main'>{waktu_skrg}</h2>", unsafe_allow_html=True)

with head_3:
    # Mengatur agar logo ruas di pojok kanan
    st.markdown('<div style="text-align: right;">', unsafe_allow_html=True)
    try: st.image("logo_ruas.png", width=80)
    except: st.write("🚀 **RUAS STUDIO**")
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("🚪 KELUAR", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

st.divider()

# ==========================================
# 6. KONTEN DASHBOARD (SAMA SEPERTI SEBELUMNYA)
# ==========================================
if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    t1, t2, t3, t4 = st.tabs(["🎥 MONITOR LIVE", "📁 ARSIP LAPORAN", "✍️ INSTRUKSI", "💰 KEUANGAN"])
    with t1:
        if st.session_state.live_monitor: st.table(pd.DataFrame(st.session_state.live_monitor)[::-1])
    with t2:
        for r in reversed(st.session_state.laporan_masuk):
            with st.expander(f"Lap: {r['Dari']} ({r['Jam']})"):
                st.write(r['Isi'])
                if r.get('Lampiran'):
                    try:
                        f = ast.literal_eval(r['Lampiran'])
                        st.markdown(f'<a href="data:{f["type"]};base64,{f["data"]}" download="{f["name"]}">📥 Download: {f["name"]}</a>', unsafe_allow_html=True)
                    except: pass
    with t3:
        target = st.multiselect("Target Staf:", [u for u in st.session_state.users.keys() if u != "Kepala Sekolah"])
        msg = st.text_area("Pesan:")
        if st.button("Kirim"):
            for s in target: st.session_state.tugas_khusus.append({"Jam": waktu_skrg, "Untuk": s, "Instruksi": msg})
            save_data(st.session_state.tugas_khusus, "database_tugas.csv"); st.success("Terkirim!")
    with t4:
        df_k = pd.DataFrame(st.session_state.data_kas)
        if not df_k.empty:
            st.subheader("BOS"); st.dataframe(df_k[df_k['Kategori']=='DANA BOS'][::-1], use_container_width=True)
            st.subheader("NON-BOS"); st.dataframe(df_k[df_k['Kategori']=='DANA NON-BOS'][::-1], use_container_width=True)

else:
    ts1, ts2, ts3 = st.tabs(["📝 INPUT KERJA", "🔔 INSTRUKSI", "📚 ARSIP"])
    with ts1:
        # Input Keuangan untuk Bendahara
        if "Bendahara" in st.session_state.user_role:
            with st.form("kas_form"):
                k, t, n, ket = st.radio("Dana:", ["DANA BOS", "DANA NON-BOS"], horizontal=True), st.selectbox("Jenis:", ["Masuk", "Keluar"]), st.number_input("Nominal:"), st.text_input("Ket:")
                if st.form_submit_button("Simpan"):
                    st.session_state.data_kas.append({"Waktu": waktu_skrg, "Kategori": k, "Masuk": n if t=="Masuk" else 0, "Keluar": n if t=="Keluar" else 0, "Keterangan": ket})
                    save_data(st.session_state.data_kas, "database_kas.csv"); st.rerun()
        
        ca, cb = st.columns(2)
        with ca:
            act = st.text_area("Aktivitas:")
            if st.button("Simpan Aktivitas"):
                st.session_state.live_monitor.append({"Jam": waktu_skrg, "Staf": st.session_state.user_role, "Aktivitas": act})
                save_data(st.session_state.live_monitor, "database_monitor.csv"); st.rerun()
        with cb:
            lap, fil = st.text_area("Laporan ke Kepsek:"), st.file_uploader("Lampiran:")
            if st.button("Kirim Laporan"):
                f_d = str({"name": fil.name, "type": fil.type, "data": base64.b64encode(fil.getvalue()).decode()}) if fil else None
                st.session_state.laporan_masuk.append({"Jam": waktu_skrg, "Dari": st.session_state.user_role, "Isi": lap, "Lampiran": f_d})
                save_data(st.session_state.laporan_masuk, "database_laporan.csv"); st.success("Terkirim!")

    with ts2:
        for t in reversed(st.session_state.tugas_khusus):
            if t['Untuk'] == st.session_state.user_role: st.info(f"[{t['Jam']}] {t['Instruksi']}")
    with ts3:
        my = [a for a in st.session_state.live_monitor if a['Staf'] == st.session_state.user_role]
        if my: st.table(pd.DataFrame(my)[::-1])

st.markdown("<p style='text-align:center; color:grey; margin-top:30px;'>E-KENDALI SMK NASIONAL | HARDIANTO - RUAS STUDIO</p>", unsafe_allow_html=True)
time.sleep(2); st.rerun()
