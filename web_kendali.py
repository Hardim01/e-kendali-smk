import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import base64
import ast
import time 

# ==========================================
# 1. STYLE & KONFIGURASI
# ==========================================
st.set_page_config(page_title="SMK NASIONAL - E-KENDALI", layout="wide", page_icon="🏛️")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .marquee-container { background-color: #002b5b; color: #ffffff; padding: 12px 0; font-weight: bold; border-bottom: 4px solid #ffc107; margin-bottom: 25px; overflow: hidden; white-space: nowrap; }
    .marquee-text { display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite; font-size: 1.2rem; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    .digital-clock-main { font-family: 'Courier New', monospace; color: #ffc107; background-color: #000; font-size: 3em; font-weight: bold; text-align: center; border: 3px solid #ffc107; border-radius: 15px; padding: 10px; }
    .welcome-text-gold { color: #ffc107; font-weight: bold; font-size: 1.8rem; text-align: center; text-shadow: 2px 2px 4px #000; }
    .btn-download { background-color: #ffc107; color: black !important; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. SISTEM DATABASE
# ==========================================
DB_DIR = "database"
if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)

def save_data(data_list, filename):
    pd.DataFrame(data_list).to_csv(os.path.join(DB_DIR, filename), index=False)

def load_data(filename):
    path = os.path.join(DB_DIR, filename)
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            if filename == "database_kas.csv" and 'Kategori' not in df.columns: df['Kategori'] = 'DANA NON-BOS'
            return df.to_dict('records')
        except: return []
    return []

def get_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="btn-download">📥 DOWNLOAD DATA ({filename})</a>'

# ==========================================
# 3. AKSES & LOGIN (WAKTU WIB +7)
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

# SETTING WAKTU KE WIB (UTC+7)
waktu_skrg = (datetime.now() + timedelta(hours=7)).strftime("%H:%M:%S")

teks_marquee = '<div class="marquee-container"><div class="marquee-text">✨ SMK Nasional Bandung: Kieu Bisa, Kitu Bisa, Sagala Bisa. Sholat Yang Utama ✨</div></div>'

if not st.session_state.logged_in:
    st.markdown(teks_marquee, unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 1, 1])
    with col_log:
        st.markdown('<p class="welcome-text-gold">E-KENDALI SMK NASIONAL</p>', unsafe_allow_html=True)
        jab = st.selectbox("Pilih Jabatan:", ["--- Pilih ---"] + list(st.session_state.users.keys()))
        pw = st.text_input("Password:", type="password")
        if st.button("MASUK SISTEM", use_container_width=True):
            if jab in st.session_state.users and pw == st.session_state.users[jab]:
                st.session_state.logged_in = True; st.session_state.user_role = jab; st.rerun()
            else: st.error("Password Salah!")
    st.stop()

# ==========================================
# 4. HEADER (LOGO & JAM WIB)
# ==========================================
st.markdown(teks_marquee, unsafe_allow_html=True)
c1, c2, c3 = st.columns([1, 2, 1])
with c1:
    try: st.image("logo_smk.png", width=80)
    except: st.markdown("🏛️ **SMK NASIONAL**")
    st.info(f"User: {st.session_state.user_role}")
with c2:
    st.markdown(f"<h2 class='digital-clock-main'>{waktu_skrg}</h2>", unsafe_allow_html=True)
with c3:
    try: st.image("logo_ruas.png", width=60)
    except: st.markdown("🚀 **RUAS STUDIO**")
    if st.button("🚪 KELUAR", use_container_width=True):
        st.session_state.logged_in = False; st.rerun()
    with st.expander("🔑 Ganti PW"):
        npw = st.text_input("Password Baru:", type="password")
        if st.button("Update"):
            st.session_state.users[st.session_state.user_role] = npw; st.success("Ok!"); st.rerun()

st.divider()

# ==========================================
# 5. DASHBOARD UTAMA
# ==========================================
df_kas = pd.DataFrame(st.session_state.data_kas)

if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    t1, t2, t3, t4 = st.tabs(["🎥 MONITOR LIVE", "📁 ARSIP LAPORAN", "✍️ INSTRUKSI", "💰 KEUANGAN"])
    with t1:
        if st.session_state.live_monitor:
            df_m = pd.DataFrame(st.session_state.live_monitor)
            st.table(df_m[::-1])
            st.markdown(get_download_link(df_m, "arsip_aktivitas.csv"), unsafe_allow_html=True)
        else: st.info("Belum ada aktivitas.")
    with t2:
        if st.session_state.laporan_masuk:
            st.markdown(get_download_link(pd.DataFrame(st.session_state.laporan_masuk), "arsip_laporan.csv"), unsafe_allow_html=True)
            for r in reversed(st.session_state.laporan_masuk):
                with st.expander(f"Lap: {r['Dari']} ({r['Jam']})"):
                    st.write(r['Isi'])
                    if 'Lampiran' in r and r['Lampiran']:
                        try:
                            f = ast.literal_eval(r['Lampiran'])
                            st.markdown(f'<a href="data:{f["type"]};base64,{f["data"]}" download="{f["name"]}">📥 Download Lampiran: {f["name"]}</a>', unsafe_allow_html=True)
                        except: pass
    with t3:
        target = st.multiselect("Target Staf:", [u for u in st.session_state.users.keys() if u != "Kepala Sekolah"])
        msg = st.text_area("Instruksi:")
        if st.button("Kirim Instruksi"):
            for s in target: st.session_state.tugas_khusus.append({"Jam": waktu_skrg, "Untuk": s, "Instruksi": msg})
            save_data(st.session_state.tugas_khusus, "database_tugas.csv"); st.success("Terkirim!"); st.rerun()
    with t4:
        if not df_kas.empty:
            st.markdown(get_download_link(df_kas, "laporan_keuangan.csv"), unsafe_allow_html=True)
            st.subheader("Jurnal Dana BOS"); st.dataframe(df_kas[df_kas['Kategori']=='DANA BOS'][::-1], use_container_width=True)
            st.subheader("Jurnal Dana NON-BOS"); st.dataframe(df_kas[df_kas['Kategori']=='DANA NON-BOS'][::-1], use_container_width=True)

else:
    # --- VIEW STAF ---
    ts1, ts2, ts3 = st.tabs(["📝 INPUT KERJA", "🔔 INSTRUKSI", "📚 ARSIP SAYA"])
    with ts1:
        if "Bendahara" in st.session_state.user_role:
            with st.form("f_kas"):
                k, t, n, ket = st.radio("Dana:", ["DANA BOS", "DANA NON-BOS"], horizontal=True), st.selectbox("Jenis:", ["Masuk", "Keluar"]), st.number_input("Nominal:", min_value=0), st.text_input("Keterangan:")
                if st.form_submit_button("Simpan Transaksi"):
                    st.session_state.data_kas.append({"Waktu": waktu_skrg, "Kategori": k, "Masuk": n if t=="Masuk" else 0, "Keluar": n if t=="Keluar" else 0, "Keterangan": ket})
                    save_data(st.session_state.data_kas, "database_kas.csv"); st.rerun()
        c_a, c_b = st.columns(2)
        with c_a:
            act = st.text_area("Aktivitas Anda:")
            if st.button("Simpan Aktivitas"):
                st.session_state.live_monitor.append({"Jam": waktu_skrg, "Staf": st.session_state.user_role, "Aktivitas": act})
                save_data(st.session_state.live_monitor, "database_monitor.csv"); st.rerun()
        with c_b:
            lap, fil = st.text_area("Laporan Khusus:"), st.file_uploader("Upload Lampiran:")
            if st.button("Kirim Laporan"):
                f_d = None
                if fil:
                    f_d = str({"name": fil.name, "type": fil.type, "data": base64.b64encode(fil.getvalue()).decode()})
                st.session_state.laporan_masuk.append({"Jam": waktu_skrg, "Dari": st.session_state.user_role, "Isi": lap, "Lampiran": f_d})
                save_data(st.session_state.laporan_masuk, "database_laporan.csv"); st.success("Terkirim!"); st.rerun()
    with ts2:
        for t in reversed(st.session_state.tugas_khusus):
            if t['Untuk'] == st.session_state.user_role: st.info(f"[{t['Jam']}] {t['Instruksi']}")
    with ts3:
        my = [a for a in st.session_state.live_monitor if a['Staf'] == st.session_state.user_role]
        if my:
            df_my = pd.DataFrame(my)
            st.table(df_my[::-1])
            st.markdown(get_download_link(df_my, "arsip_pribadi.csv"), unsafe_allow_html=True)

st.markdown("<p style='text-align:center; color:grey; margin-top:30px;'>E-KENDALI SMK NASIONAL | HARDIANTO - RUAS STUDIO</p>", unsafe_allow_html=True)
time.sleep(1); st.rerun()
