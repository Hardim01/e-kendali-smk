import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# ==========================================
# 1. CSS: FOOTER SESUAI GAMBAR TERBARU
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
    
    .footer-container {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 20px;
        margin-top: 50px;
        padding: 20px;
        border-top: 1px solid #333;
    }
    .dev-text-v2 { color: #888; font-size: 0.9rem; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATABASE ENGINE: LOGIKA MATEMATIKA FIX
# ==========================================
DB_DIR = "database"
if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)

def load_db(name):
    p = os.path.join(DB_DIR, name)
    if os.path.exists(p):
        df = pd.read_csv(p)
        df.columns = df.columns.str.strip()
        # Penyelarasan Nama Kolom
        mapping = {'Jam': 'Time', 'Aktivitas': 'Activity', 'Staf': 'Staff', 'Sumber': 'Source'}
        df = df.rename(columns=mapping)
        
        if name == "kas.csv" and not df.empty:
            # Paksa jadi angka, hilangkan 'None' atau teks aneh
            df['Masuk'] = pd.to_numeric(df['Masuk'], errors='coerce').fillna(0)
            df['Keluar'] = pd.to_numeric(df['Keluar'], errors='coerce').fillna(0)
            # Fix Source yang kosong agar terhitung ke saldo internal
            df['Source'] = df['Source'].replace(['None', '', 'nan'], 'SPP/Internal')
        return df
    return pd.DataFrame()

def save_db(df, name):
    df.to_csv(os.path.join(DB_DIR, name), index=False)

# Session State & Login Logic (Tetap Sama)
if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "user_role": None, "users": {"Kepala Sekolah": "kepsek123", "Bendahara Sekolah": "bendahara123", "ADMIN SISTEM": "admin789"}})

waktu_wib = (datetime.now() + timedelta(hours=7)).strftime("%H:%M:%S")

if not st.session_state.logged_in:
    st.markdown("<h3 style='text-align:center;'>E-KENDALI LOGIN</h3>", unsafe_allow_html=True)
    with st.form("login"):
        u = st.selectbox("Role", list(st.session_state.users.keys())); p = st.text_input("PW", type="password")
        if st.form_submit_button("MASUK"):
            if p == st.session_state.users[u]: st.session_state.logged_in = True; st.session_state.user_role = u; st.rerun()
    st.stop()

# Header Jam
st.markdown(f'<div style="text-align:center;"><div class="digital-clock">{waktu_wib}</div></div>', unsafe_allow_html=True)

# ==========================================
# 3. KONTEN UTAMA: HITUNG SALDO BERSIH
# ==========================================
df_kas = load_db("kas.csv")

if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    t1, t2 = st.tabs(["🎥 MONITORING", "💰 KEUANGAN"])
    with t2:
        if not df_kas.empty:
            total_spp = df_kas[df_kas['Source'] == 'SPP/Internal']['Masuk'].sum() - df_kas[df_kas['Source'] == 'SPP/Internal']['Keluar'].sum()
            st.metric("SALDO AKHIR (NON-BOS)", f"Rp {total_spp:,}")
            st.dataframe(df_kas[::-1], use_container_width=True)

else:
    t1, t2 = st.tabs(["📝 LAPORAN", "💰 KAS SEKOLAH"])
    with t2:
        with st.form("input_kas"):
            src = st.selectbox("Pos Dana", ["SPP/Internal", "BOS"])
            ket = st.text_input("Keperluan (Contoh: Beli ATK)")
            m = st.number_input("Uang Masuk", value=0); k = st.number_input("Uang Keluar", value=0)
            if st.form_submit_button("SIMPAN & UPDATE SALDO"):
                new = pd.DataFrame([{"Time": waktu_wib, "Staff": st.session_state.user_role, "Ket": ket, "Masuk": m, "Keluar": k, "Source": src}])
                save_db(pd.concat([df_kas, new], ignore_index=True), "kas.csv")
                st.rerun()
        
        # DISPLAY SALDO YANG SUDAH DI-FIX MATEMATIKANYA
        st.divider()
        df_fresh = load_db("kas.csv")
        if not df_fresh.empty:
            # Hitung Saldo SPP: Semua Masuk SPP dikurangi Semua Keluar SPP (Termasuk yang tadi None)
            s_spp = df_fresh[df_fresh['Source'] == 'SPP/Internal']
            saldo_asli = s_spp['Masuk'].sum() - s_spp['Keluar'].sum()
            
            st.warning(f"### 🧮 SALDO SPP SAAT INI: Rp {saldo_asli:,}")
            st.write("**Riwayat Transaksi:**")
            st.dataframe(df_fresh[::-1], use_container_width=True)

# ==========================================
# 4. FOOTER (SESUAI GAMBAR MAS HARDIANTO)
# ==========================================
st.markdown("---")
if st.button("🚪 KELUAR SISTEM"): st.session_state.logged_in = False; st.rerun()

st.markdown(f"""
    <div class="footer-container">
        <div class="dev-text-v2">Developed by Hardianto | Powered by RUAS STUDIO</div>
        <img src="https://raw.githubusercontent.com/hardianto-id/e-kendali-smk/main/logo_ruas.png" width="40">
    </div>
    """, unsafe_allow_html=True)
