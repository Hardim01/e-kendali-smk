import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import base64
import ast
import time 

# ==========================================
# 1. CSS: TATA LETAK PROFESIONAL (MULTIMEDIA GRADE)
# ==========================================
st.set_page_config(page_title="SMK NASIONAL - E-KENDALI", layout="wide", page_icon="🏛️")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Marquee Styling */
    .marquee-container { background-color: #002b5b; color: #ffffff; padding: 12px 0; font-weight: bold; border-bottom: 4px solid #ffc107; margin-bottom: 25px; overflow: hidden; white-space: nowrap; }
    .marquee-text { display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite; font-size: 1.2rem; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    
    /* Login & Header Centering */
    .login-box { display: flex; flex-direction: column; align-items: center; justify-content: center; }
    .stForm { margin: 0 auto; max-width: 500px !important; border: 2px solid #ffc107 !important; border-radius: 15px; padding: 30px; background: #0e1117; }
    
    /* Clock Styling */
    .digital-clock { 
        font-family: 'Courier New', monospace; color: #ffc107; background-color: #000; font-size: 3.5em; 
        font-weight: bold; text-align: center; border: 3px solid #ffc107; border-radius: 15px; 
        padding: 15px; margin: 15px auto; display: block; width: fit-content; box-shadow: 0px 0px 15px #ffc107;
    }
    .welcome-text { color: #ffc107; font-weight: bold; font-size: 1.8rem; text-align: center; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATABASE & SESSION
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
        "users": {"Kepala Sekolah": "kepsek123", "Ketua Tata Usaha": "ktu123", "Bendahara": "bendahara123", "Waka Kurikulum": "kurikulum123", "Waka Kesiswaan": "wakakes123", "ADMIN SISTEM": "admin789"},
        "data_kas": load_data("database_kas.csv"),
        "live_monitor": load_data("database_monitor.csv"),
        "laporan_masuk": load_data("database_laporan.csv"),
        "tugas_khusus": load_data("database_tugas.csv")
    })

# JAM SINKRON KOMPUTER (WIB)
waktu_wib = (datetime.now() + timedelta(hours=7)).strftime("%H:%M:%S")

# ==========================================
# 3. HALAMAN LOGIN (SIMETRIS & CENTER)
# ==========================================
if not st.session_state.logged_in:
    st.markdown('<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Sholat Yang Utama ✨</div></div>', unsafe_allow_html=True)
    
    # Menempatkan logo tepat di tengah kalimat login
    _, col_mid, _ = st.columns([1, 0.4, 1])
    with col_mid:
        try: st.image("logo_smk.png", use_container_width=True)
        except: st.markdown("<h1 style='text-align:center;'>🏛️</h1>", unsafe_allow_html=True)
    
    with st.form("form_login"):
        st.markdown("<p class='welcome-text'>E-KENDALI LOGIN</p>", unsafe_allow_html=True)
        jab = st.selectbox("Jabatan:", list(st.session_state.users.keys()))
        pw = st.text_input("Password:", type="password")
        if st.form_submit_button("MASUK SISTEM", use_container_width=True):
            if pw == st.session_state.users[jab]:
                st.session_state.logged_in = True; st.session_state.user_role = jab; st.rerun()
            else: st.error("Password Salah!")
    st.stop()

# ==========================================
# 4. HEADER DASHBOARD (SIMETRIS)
# ==========================================
st.markdown('<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Sholat Yang Utama ✨</div></div>', unsafe_allow_html=True)

h1, h2, h3 = st.columns([1, 2, 1])
with h1:
    st.info(f"👤 {st.session_state.user_role}")
with h2:
    st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
    try: st.image("logo_smk.png", width=90)
    except: st.write("🏛️")
    st.markdown(f'<div class="digital-clock">{waktu_wib}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
with h3:
    if st.button("🚪 KELUAR", use_container_width=True):
        st.session_state.logged_in = False; st.rerun()
    st.markdown("<p style='text-align:right; font-weight:bold; color:#ffc107;'>HARDIANTO<br>RUAS STUDIO</p>", unsafe_allow_html=True)

st.divider()

# ==========================================
# 5. MENU LENGKAP (MONITOR, LAPORAN, INSTRUKSI, KAS)
# ==========================================
if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    t1, t2, t3, t4 = st.tabs(["🎥 MONITOR LIVE", "📁 ARSIP LAPORAN", "✍️ INSTRUKSI", "💰 KEUANGAN"])
    
    with t1: # Monitor Live
        if st.session_state.live_monitor: st.table(pd.DataFrame(st.session_state.live_monitor)[::-1])
        else: st.info("Belum ada aktivitas.")
        
    with t2: # Laporan & Lampiran
        for r in reversed(st.session_state.laporan_masuk):
            with st.expander(f"Lap: {r['Dari']} ({r['Jam']})"):
                st.write(r['Isi'])
                if 'Lampiran' in r and r['Lampiran']:
                    try:
                        f = ast.literal_eval(r['Lampiran'])
                        st.markdown(f'<a href="data:{f["type"]};base64,{f["data"]}" download="{f["name"]}">📥 Download: {f["name"]}</a>', unsafe_allow_html=True)
                    except: pass
                    
    with t3: # Instruksi
        st.subheader("Kirim Instruksi Ke Staf")
        target = st.multiselect("Pilih Staf:", [u for u in st.session_state.users.keys() if u != "Kepala Sekolah"])
        msg = st.text_area("Isi Instruksi:")
        if st.button("Kirim Sekarang"):
            for s in target: st.session_state.tugas_khusus.append({"Jam": waktu_wib, "Untuk": s, "Instruksi": msg})
            save_data(st.session_state.tugas_khusus, "database_tugas.csv"); st.success("Terkirim!")

    with t4: # Keuangan
        df_k = pd.DataFrame(st.session_state.data_kas)
        if not df_k.empty:
            st.subheader("DANA BOS"); st.dataframe(df_k[df_k['Kategori']=='DANA BOS'][::-1], use_container_width=True)
            st.subheader("DANA NON-BOS"); st.dataframe(df_k[df_k['Kategori']=='DANA NON-BOS'][::-1], use_container_width=True)

else:
    # --- TAMPILAN STAF (TIDAK BERKURANG) ---
    ts1, ts2, ts3 = st.tabs(["📝 UPDATE KERJA", "🔔 INSTRUKSI", "📚 ARSIP SAYA"])
    with ts1:
        if "Bendahara" in st.session_state.user_role:
            with st.form("f_kas"):
                k, t, n = st.radio("Dana:", ["DANA BOS", "DANA NON-BOS"], horizontal=True), st.selectbox("Jenis:", ["Masuk", "Keluar"]), st.number_input("Nominal:")
                ket = st.text_input("Keterangan:")
                if st.form_submit_button("Simpan Keuangan"):
                    st.session_state.data_kas.append({"Waktu": waktu_wib, "Kategori": k, "Masuk": n if t=="Masuk" else 0, "Keluar": n if t=="Keluar" else 0, "Keterangan": ket})
                    save_data(st.session_state.data_kas, "database_kas.csv"); st.rerun()
        
        c_a, c_b = st.columns(2)
        with c_a:
            act = st.text_area("Aktivitas Anda:")
            if st.button("Simpan Aktivitas"):
                st.session_state.live_monitor.append({"Jam": waktu_wib, "Staf": st.session_state.user_role, "Aktivitas": act})
                save_data(st.session_state.live_monitor, "database_monitor.csv"); st.rerun()
        with c_b:
            lap, fil = st.text_area("Laporan Khusus:"), st.file_uploader("Upload Lampiran:")
            if st.button("Kirim Laporan"):
                f_d = str({"name": fil.name, "type": fil.type, "data": base64.b64encode(fil.getvalue()).decode()}) if fil else None
                st.session_state.laporan_masuk.append({"Jam": waktu_wib, "Dari": st.session_state.user_role, "Isi": lap, "Lampiran": f_d})
                save_data(st.session_state.laporan_masuk, "database_laporan.csv"); st.success("Laporan Terkirim!")
    with ts2:
        for t in reversed(st.session_state.tugas_khusus):
            if t['Untuk'] == st.session_state.user_role: st.info(f"[{t['Jam']}] {t['Instruksi']}")
    with ts3:
        my = [a for a in st.session_state.live_monitor if a['Staf'] == st.session_state.user_role]
        if my: st.table(pd.DataFrame(my)[::-1])

st.markdown("<p style='text-align:center; color:grey; margin-top:50px;'>E-KENDALI SMK NASIONAL | MULTIMEDIA DESIGN OK</p>", unsafe_allow_html=True)
time.sleep(1); st.rerun()
