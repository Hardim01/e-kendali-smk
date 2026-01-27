import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# ==========================================
# 1. CSS & TAMPILAN
# ==========================================
st.set_page_config(page_title="SMK NASIONAL - E-KENDALI", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .headline { text-align: center; color: #ffc107; font-size: 2.5em; font-weight: bold; text-shadow: 2px 2px #000; }
    .digital-clock { 
        font-family: 'Courier New', monospace; color: #ffc107; background-color: #000; font-size: 3.2em; 
        font-weight: bold; text-align: center; border: 3px solid #ffc107; border-radius: 12px; 
        padding: 10px 25px; margin: 10px auto; display: inline-block; box-shadow: 0px 0px 15px #ffc107;
    }
    .running-text { background-color: #ffc107; color: #000; padding: 10px; font-weight: bold; border-radius: 5px; margin: 20px 0; font-size: 1.1em; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATABASE ENGINE (SISTEM ANTI-CRASH)
# ==========================================
DB_DIR = "database"
UPLOAD_DIR = "uploads"
for d in [DB_DIR, UPLOAD_DIR]:
    if not os.path.exists(d): os.makedirs(d)

def load_db(name):
    p = os.path.join(DB_DIR, name)
    if os.path.exists(p):
        try:
            df = pd.read_csv(p)
            # Normalisasi Kolom secara paksa agar tidak KeyError
            mapping = {
                'Time': 'Jam', 'Staff': 'Staf', 'Activity': 'Aktivitas', 
                'Attachment': 'File', 'Source': 'Sumber', 'Message': 'Pesan'
            }
            df = df.rename(columns=mapping)
            
            # Pastikan kolom Masuk & Keluar selalu angka
            if 'Masuk' in df.columns: df['Masuk'] = pd.to_numeric(df['Masuk'], errors='coerce').fillna(0)
            if 'Keluar' in df.columns: df['Keluar'] = pd.to_numeric(df['Keluar'], errors='coerce').fillna(0)
            return df
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def save_db(df, name):
    df.to_csv(os.path.join(DB_DIR, name), index=False)

# DAFTAR 16 STAF LENGKAP
if "users" not in st.session_state:
    st.session_state.users = {
        "Kepala Sekolah": "kepsek123", "Waka Kurikulum": "kurikulum123", "Waka Kesiswaan": "kesiswaan123",
        "Waka Hubin": "hubin123", "Waka Sarpras": "sarpras123", "Kepala Tata Usaha": "tu123",
        "Bendahara BOS": "bos123", "Bendahara Sekolah": "bendahara123", "Staf Bendahara Sekolah": "stafbend123",
        "Pembina OSIS": "osis123", "Ketertiban": "tertib123", "Kepala Lab": "lab123",
        "BK (Bimbingan Konseling)": "bk123", "Kepala Perpustakaan": "perpus123",
        "Dokumentasi & Publikasi": "dokpub123", "ADMIN UTAMA": "admin789"
    }

if "logged_in" not in st.session_state: st.session_state.logged_in = False

waktu_wib = (datetime.now() + timedelta(hours=7)).strftime("%H:%M:%S")

# Header & Logo
st.markdown('<h1 class="headline">SISTEM KENDALI SMK NASIONAL BANDUNG</h1>', unsafe_allow_html=True)
_, mid_logo_smk, _ = st.columns([1, 0.3, 1])
with mid_logo_smk: st.image("logo_smk.png", use_container_width=True)
st.markdown(f"""<div class="running-text"><marquee scrollamount="10">Kieu Bisa, Kitu Bisa, Sagala Bisa... Pekerjaan Memang Penting Tapi Sholat Yang Utama!</marquee></div>""", unsafe_allow_html=True)

# LOGIN
if not st.session_state.logged_in:
    _, l_col, _ = st.columns([1, 0.4, 1])
    with l_col:
        with st.form("login_form"):
            u = st.selectbox("Pilih Posisi", list(st.session_state.users.keys()))
            p = st.text_input("Password", type="password")
            if st.form_submit_button("MASUK SISTEM"):
                if p == st.session_state.users[u]: 
                    st.session_state.logged_in = True; st.session_state.user_role = u; st.rerun()
                else: st.error("Akses Ditolak")
    st.stop()

st.markdown(f'<div style="text-align:center;"><div class="digital-clock">{waktu_wib}</div></div>', unsafe_allow_html=True)

# ==========================================
# 3. KONTEN UTAMA
# ==========================================
list_sumber = ["BOS", "SPP", "PIP", "RMP", "Sumbangan", "Lain-lain"]

if st.session_state.user_role in ["Kepala Sekolah", "ADMIN UTAMA"]:
    t1, t2, t3 = st.tabs(["🎥 MONITOR STAF", "✍️ INSTRUKSI", "💰 CASHFLOW"])
    
    with t1:
        st.write("**Laporan Harian:**")
        st.dataframe(load_db("monitor.csv")[::-1], use_container_width=True)
        st.write("**Laporan Instruksi:**")
        st.dataframe(load_db("respon_instruksi.csv")[::-1], use_container_width=True)

    with t2:
        target = st.multiselect("Target Staf:", list(st.session_state.users.keys()))
        msg = st.text_area("Instruksi:")
        f_up = st.file_uploader("Lampiran (PDF/Video/Foto):", type=['pdf','jpg','png','mp4'])
        if st.button("Kirim Instruksi"):
            fn = f_up.name if f_up else "-"
            if f_up: 
                with open(os.path.join(UPLOAD_DIR, f_up.name), "wb") as f: f.write(f_up.getbuffer())
            df_i = load_db("instruksi.csv")
            save_db(pd.concat([df_i, pd.DataFrame([{"Jam": waktu_wib, "Target": str(target), "Pesan": msg, "File": fn}])], ignore_index=True), "instruksi.csv"); st.rerun()

    with t3:
        st.subheader("💰 Arus Kas Sekolah")
        df_k = load_db("kas.csv")
        if not df_k.empty:
            m_cols = st.columns(3)
            for i, s in enumerate(list_sumber):
                ds = df_k[df_k['Sumber'] == s] if 'Sumber' in df_k.columns else pd.DataFrame()
                saldo = ds['Masuk'].sum() - ds['Keluar'].sum() if not ds.empty else 0
                m_cols[i % 3].metric(f"Saldo {s}", f"Rp {saldo:,}")
            st.divider()
            st.dataframe(df_k[::-1], use_container_width=True)
        else: st.info("Data Cashflow Kosong")

else:
    # MODUL STAF (PRIVASI TOTAL)
    menu = ["📝 LAPOR KERJA", "🔔 INSTRUKSI"]
    if "Bendahara" in st.session_state.user_role: menu.insert(1, "💰 INPUT KAS")
    tabs = st.tabs(menu)
    
    with tabs[0]:
        akt = st.text_area("Aktivitas Anda:"); f_l = st.file_uploader("Bukti:", type=['pdf','jpg','png','mp4'])
        if st.button("Kirim Laporan"):
            fn = f_l.name if f_l else "-"
            if f_l: 
                with open(os.path.join(UPLOAD_DIR, f_l.name), "wb") as f: f.write(f_l.getbuffer())
            df_m = load_db("monitor.csv")
            save_db(pd.concat([df_m, pd.DataFrame([{"Jam": waktu_wib, "Staf": st.session_state.user_role, "Aktivitas": akt, "File": fn}])], ignore_index=True), "monitor.csv"); st.rerun()
        
        st.divider()
        df_v = load_db("monitor.csv")
        if not df_v.empty and 'Staf' in df_v.columns:
            # Proteksi: Hanya ambil baris milik user yang login
            my_data = df_v[df_v['Staf'] == st.session_state.user_role]
            st.dataframe(my_data[::-1], use_container_width=True)

    if "Bendahara" in st.session_state.user_role:
        with tabs[1]:
            with st.form("k_form"):
                src = st.selectbox("Sumber:", list_sumber); ket = st.text_input("Ket"); m = st.number_input("Masuk"); k = st.number_input("Keluar")
                if st.form_submit_button("Simpan Kas"):
                    df_kas = load_db("kas.csv")
                    save_db(pd.concat([df_kas, pd.DataFrame([{"Jam": waktu_wib, "Staf": st.session_state.user_role, "Sumber": src, "Ket": ket, "Masuk": m, "Keluar": k}])], ignore_index=True), "kas.csv"); st.rerun()
            df_k_v = load_db("kas.csv")
            if not df_k_v.empty and 'Staf' in df_k_v.columns:
                st.dataframe(df_k_v[df_k_v['Staf'] == st.session_state.user_role][::-1], use_container_width=True)

    with tabs[-1]:
        df_ins = load_db("instruksi.csv")
        if not df_ins.empty:
            for i, r in df_ins.iterrows():
                if st.session_state.user_role in str(r.get('Target', '')):
                    with st.expander(f"🔴 TUGAS: {r.get('Jam','-')}"):
                        st.write(r.get('Pesan','-')); st.write(f"File: {r.get('File','-')}")
                        with st.form(f"res_{i}"):
                            res_txt = st.text_area("Laporan:"); res_f = st.file_uploader("Upload Bukti:")
                            if st.form_submit_button("Lapor Selesai"):
                                rf_n = res_f.name if res_f else "-"
                                if res_f: 
                                    with open(os.path.join(UPLOAD_DIR, res_f.name), "wb") as f: f.write(res_f.getbuffer())
                                save_db(pd.concat([load_db("respon_instruksi.csv"), pd.DataFrame([{"Jam": waktu_wib, "Staf": st.session_state.user_role, "Hasil": res_txt, "File_Bukti": rf_n}])], ignore_index=True), "respon_instruksi.csv"); st.rerun()

# FOOTER
st.divider()
c1, c2 = st.columns(2)
with c1:
    if st.button("🚪 LOGOUT", use_container_width=True): st.session_state.logged_in = False; st.rerun()
with c2:
    with st.expander("🔑 GANTI PASSWORD"):
        new_p = st.text_input("Password Baru:", type="password")
        if st.button("Update"): st.session_state.users[st.session_state.user_role] = new_p; st.success("Ok")

st.markdown("---")
_, mid_f, _ = st.columns([1, 0.4, 1])
with mid_f:
    st.image("logo_ruas.png", use_container_width=True)
    st.markdown('<p style="text-align:center; color:#888; font-weight:bold; font-size:0.9rem;">Developed by Hardianto | Powered by RUAS STUDIO</p>', unsafe_allow_html=True)
