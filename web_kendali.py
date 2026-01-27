import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# ==========================================
# 1. CSS & TAMPILAN (TETAP CAKEP)
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
# 2. DATABASE & HISTORY ENGINE (UNDO/REDO)
# ==========================================
DB_DIR = "database"
if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)

if "history" not in st.session_state:
    st.session_state.history = {"kas.csv": [], "monitor.csv": [], "instruksi.csv": []}
if "redo_stack" not in st.session_state:
    st.session_state.redo_stack = {"kas.csv": [], "monitor.csv": [], "instruksi.csv": []}

def load_db(name):
    p = os.path.join(DB_DIR, name)
    if os.path.exists(p):
        df = pd.read_csv(p)
        mapping = {'Jam': 'Time', 'Aktivitas': 'Activity', 'Staf': 'Staff', 'Sumber': 'Source', 'User': 'PIC', 'Isi': 'Message'}
        df = df.rename(columns=mapping)
        if name == "kas.csv" and not df.empty:
            df['Masuk'] = pd.to_numeric(df['Masuk'], errors='coerce').fillna(0)
            df['Keluar'] = pd.to_numeric(df['Keluar'], errors='coerce').fillna(0)
            df['Source'] = df['Source'].replace(['None', '', 'nan'], 'Lain-lain')
        return df
    return pd.DataFrame()

def save_db(df, name, record_history=True):
    if record_history:
        current_data = load_db(name)
        st.session_state.history[name].append(current_data)
        st.session_state.redo_stack[name] = []
    df.to_csv(os.path.join(DB_DIR, name), index=False)

def undo(name):
    if st.session_state.history[name]:
        st.session_state.redo_stack[name].append(load_db(name))
        save_db(st.session_state.history[name].pop(), name, record_history=False)
        st.rerun()

def redo(name):
    if st.session_state.redo_stack[name]:
        st.session_state.history[name].append(load_db(name))
        save_db(st.session_state.redo_stack[name].pop(), name, record_history=False)
        st.rerun()

# --- LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "user_role": None, "users": {"Kepala Sekolah": "kepsek123", "Bendahara Sekolah": "bendahara123", "ADMIN SISTEM": "admin789"}})

waktu_wib = (datetime.now() + timedelta(hours=7)).strftime("%H:%M:%S")

if not st.session_state.logged_in:
    st.markdown("<h3 style='text-align:center;'>E-KENDALI LOGIN</h3>", unsafe_allow_html=True)
    with st.form("login"):
        u = st.selectbox("Role", list(st.session_state.users.keys())); p = st.text_input("PW", type="password")
        if st.form_submit_button("LOGIN"):
            if p == st.session_state.users[u]: st.session_state.logged_in = True; st.session_state.user_role = u; st.rerun()
    st.stop()

st.markdown(f'<div style="text-align:center;"><div class="digital-clock">{waktu_wib}</div></div>', unsafe_allow_html=True)

# ==========================================
# 3. KONTEN UTAMA: REKAP SUMBER + UNDO/REDO
# ==========================================
list_sumber = ["BOS", "SPP", "PIP", "RMP", "Sumbangan", "Lain-lain"]

if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    t1, t2, t3 = st.tabs(["🎥 MONITOR LIVE", "✍️ INSTRUKSI", "💰 REKAP SUMBER DANA"])
    
    with t3:
        df_kas = load_db("kas.csv")
        if not df_kas.empty:
            st.subheader("📊 Ringkasan Saldo Sekolah")
            m_cols = st.columns(3)
            for i, s in enumerate(list_sumber):
                ds = df_kas[df_kas['Source'] == s]
                saldo = ds['Masuk'].sum() - ds['Keluar'].sum()
                m_cols[i % 3].metric(f"Total {s}", f"Rp {saldo:,}")
            st.divider()
            st.dataframe(df_kas[::-1], use_container_width=True)
            c1, c2 = st.columns(2)
            if c1.button("⏪ UNDO DATA KAS", use_container_width=True): undo("kas.csv")
            if c2.button("⏩ REDO DATA KAS", use_container_width=True): redo("kas.csv")

else:
    menu = ["📝 LAPOR KERJA", "💰 INPUT KAS"]
    tabs = st.tabs(menu)
    
    with tabs[1]:
        with st.form("kas_v_final"):
            src = st.selectbox("Sumber Dana:", list_sumber)
            ket = st.text_input("Keterangan:"); m = st.number_input("Masuk:", value=0)
            k = st.number_input("Keluar:", value=0); pic = st.text_input("PIC:"); sub = st.form_submit_button("Simpan")
            if sub:
                df_k = load_db("kas.csv")
                new = pd.DataFrame([{"Time": waktu_wib, "Staff": st.session_state.user_role, "Source": src, "Ket": ket, "Masuk": m, "Keluar": k, "PIC": pic}])
                save_db(pd.concat([df_k, new], ignore_index=True), "kas.csv"); st.rerun()
        
        st.divider()
        df_v = load_db("kas.csv")
        if not df_v.empty:
            st.subheader("💰 Saldo Per Kategori")
            v_cols = st.columns(3)
            for j, smb in enumerate(list_sumber):
                val = df_v[df_v['Source'] == smb]
                v_cols[j % 3].info(f"**{smb}:** Rp {val['Masuk'].sum() - val['Keluar'].sum():,}")
            st.dataframe(df_v[::-1], use_container_width=True)
            c1, c2 = st.columns(2)
            if c1.button("⏪ UNDO KAS", use_container_width=True): undo("kas.csv")
            if c2.button("⏩ REDO KAS", use_container_width=True): redo("kas.csv")

# ==========================================
# 4. FOOTER & ACTIONS
# ==========================================
st.divider()
if st.button("🚪 LOGOUT", use_container_width=True): st.session_state.logged_in = False; st.rerun()

st.markdown('<div class="footer-section">', unsafe_allow_html=True)
_, mid_logo, _ = st.columns([1, 0.12, 1])
with mid_logo: st.image("logo_ruas.png", use_container_width=True)
st.markdown('<p class="dev-text">Developed by Hardianto | Powered by RUAS STUDIO</p></div>', unsafe_allow_html=True)
