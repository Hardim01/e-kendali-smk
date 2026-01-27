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
    .digital-clock { 
        font-family: 'Courier New', monospace; color: #ffc107; background-color: #000; font-size: 3.2em; 
        font-weight: bold; text-align: center; border: 3px solid #ffc107; border-radius: 12px; 
        padding: 10px 25px; margin: 15px auto; display: inline-block; box-shadow: 0px 0px 15px #ffc107;
    }
    div[data-testid="stForm"] { margin: 0 auto !important; width: 450px !important; border: 2px solid #ffc107 !important; border-radius: 15px; }
    .footer-section { 
        display: flex; flex-direction: column; align-items: center; text-align: center;
        margin-top: 50px; padding-top: 20px; border-top: 1px solid #333; 
    }
    .dev-text { color: #888; font-size: 0.8rem; font-weight: bold; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATABASE ENGINE (FIX MATEMATIKA & KOLOM)
# ==========================================
DB_DIR = "database"
if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)

def load_db(name):
    p = os.path.join(DB_DIR, name)
    if os.path.exists(p):
        df = pd.read_csv(p)
        # Mapping kolom agar konsisten
        mapping = {'Jam': 'Time', 'Aktivitas': 'Activity', 'Staf': 'Staff', 'Sumber': 'Source', 'User': 'PIC'}
        df = df.rename(columns=mapping)
        if name == "kas.csv" and not df.empty:
            df['Masuk'] = pd.to_numeric(df['Masuk'], errors='coerce').fillna(0)
            df['Keluar'] = pd.to_numeric(df['Keluar'], errors='coerce').fillna(0)
            df['Source'] = df['Source'].replace(['None', '', 'nan'], 'SPP/Internal')
        return df
    return pd.DataFrame()

def save_db(df, name):
    df.to_csv(os.path.join(DB_DIR, name), index=False)

if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False, "user_role": None,
        "users": {
            "Kepala Sekolah": "kepsek123", "Waka Kurikulum": "kurikulum123", "Waka Kesiswaan": "kesiswaan123",
            "Bendahara Sekolah": "bendahara123", "Bendahara Bos": "bos123", "ADMIN SISTEM": "admin789"
        }
    })

waktu_wib = (datetime.now() + timedelta(hours=7)).strftime("%H:%M:%S")

# ==========================================
# 3. LOGIN PAGE
# ==========================================
if not st.session_state.logged_in:
    _, l_col, _ = st.columns([1, 0.4, 1])
    with l_col: st.image("logo_smk.png", use_container_width=True)
    st.markdown("<h3 style='text-align:center; color:#ffc107;'>E-KENDALI LOGIN</h3>", unsafe_allow_html=True)
    with st.form("f_login"):
        jab = st.selectbox("Position:", list(st.session_state.users.keys()))
        pw = st.text_input("Password:", type="password")
        if st.form_submit_button("LOGIN", use_container_width=True):
            if pw == st.session_state.users[jab]:
                st.session_state.logged_in = True; st.session_state.user_role = jab; st.rerun()
            else: st.error("Wrong Password!")
    st.stop()

# Header Jam
st.markdown(f'<div style="text-align:center;"><div class="digital-clock">{waktu_wib}</div></div>', unsafe_allow_html=True)

# ==========================================
# 4. MAIN CONTENT
# ==========================================
df_kas = load_db("kas.csv")

if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    t1, t2, t3 = st.tabs(["🎥 MONITOR LIVE", "✍️ INSTRUKSI", "💰 KEUANGAN"])
    with t3:
        if not df_kas.empty:
            s_spp = df_kas[df_kas['Source'] == 'SPP/Internal']
            saldo = s_spp['Masuk'].sum() - s_spp['Keluar'].sum()
            st.metric("SALDO BERSIH (NON-BOS)", f"Rp {saldo:,}")
            st.write("Jurnal Transaksi Lengkap:")
            st.dataframe(df_kas[::-1], use_container_width=True)
else:
    menu = ["📝 LAPOR KERJA", "🔔 INSTRUKSI"]
    if "Bendahara" in st.session_state.user_role: menu.insert(1, "💰 INPUT KAS")
    tabs = st.tabs(menu)
    
    with tabs[0]:
        akt = st.text_area("Laporan Kerja Hari Ini:")
        if st.button("Simpan Laporan"):
            df_mon = load_db("monitor.csv")
            save_db(pd.concat([df_mon, pd.DataFrame([{"Time": waktu_wib, "Staff": st.session_state.user_role, "Activity": akt}])], ignore_index=True), "monitor.csv")
            st.success("Tersimpan!")

    if "Bendahara" in st.session_state.user_role:
        with tabs[1]:
            with st.form("form_kas_final"):
                src = st.selectbox("Sumber Dana:", ["SPP/Internal", "BOS"])
                ket = st.text_input("Keterangan (Contoh: Beli ATK):")
                m = st.number_input("Masuk (Rp):", value=0)
                k = st.number_input("Keluar (Rp):", value=0)
                pic = st.text_input("Nama Penerima / PIC:") # KOLOM PIC KEMBALI!
                if st.form_submit_button("Update Kas & Hitung Saldo"):
                    df_kas = load_db("kas.csv")
                    new_entry = pd.DataFrame([{"Time": waktu_wib, "Staff": st.session_state.user_role, "Ket": ket, "Masuk": m, "Keluar": k, "Source": src, "PIC": pic}])
                    save_db(pd.concat([df_kas, new_entry], ignore_index=True), "kas.csv")
                    st.rerun()
            
            st.divider()
            df_v = load_db("kas.csv")
            if not df_v.empty:
                s_spp = df_v[df_v['Source'] == 'SPP/Internal']
                st.info(f"### 🧮 SALDO AKHIR SPP: Rp {s_spp['Masuk'].sum() - s_spp['Keluar'].sum():,}")
                st.dataframe(df_v[::-1], use_container_width=True)

# ==========================================
# 5. ACCOUNT ACTIONS (PASSWORD & LOGOUT)
# ==========================================
st.divider()
col_act1, col_act2 = st.columns(2)
with col_act1:
    if st.button("🚪 LOGOUT", use_container_width=True):
        st.session_state.logged_in = False; st.rerun()
with col_act2:
    with st.expander("🔑 GANTI PASSWORD"):
        pw_baru = st.text_input("Password Baru:", type="password")
        if st.button("Simpan Password Baru"):
            st.session_state.users[st.session_state.user_role] = pw_baru
            st.success("Berhasil diubah!")

# ==========================================
# 6. FOOTER
# ==========================================
st.markdown('<div class="footer-section">', unsafe_allow_html=True)
_, mid_logo, _ = st.columns([1, 0.12, 1])
with mid_logo: st.image("logo_ruas.png", use_container_width=True)
st.markdown('<p class="dev-text">Developed by Hardianto | Powered by RUAS STUDIO</p></div>', unsafe_allow_html=True)
