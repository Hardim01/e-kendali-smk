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
# 2. DATABASE & HISTORY ENGINE
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
        return df
    return pd.DataFrame()

def save_db(df, name, record_history=True):
    if record_history:
        st.session_state.history[name].append(load_db(name))
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
    st.session_state.update({
        "logged_in": False, 
        "user_role": None, 
        "users": {
            "Kepala Sekolah": "kepsek123", "Waka Kurikulum": "kurikulum123", "Waka Kesiswaan": "kesiswaan123",
            "Bendahara Sekolah": "bendahara123", "Bendahara Bos": "bos123", "ADMIN SISTEM": "admin789"
        }
    })

waktu_wib = (datetime.now() + timedelta(hours=7)).strftime("%H:%M:%S")

if not st.session_state.logged_in:
    st.markdown("<h3 style='text-align:center;'>E-KENDALI LOGIN</h3>", unsafe_allow_html=True)
    with st.form("login"):
        u = st.selectbox("Position", list(st.session_state.users.keys()))
        p = st.text_input("Password", type="password")
        if st.form_submit_button("LOGIN"):
            if p == st.session_state.users[u]: 
                st.session_state.logged_in = True
                st.session_state.user_role = u
                st.rerun()
            else: st.error("Wrong Password!")
    st.stop()

st.markdown(f'<div style="text-align:center;"><div class="digital-clock">{waktu_wib}</div></div>', unsafe_allow_html=True)

# ==========================================
# 3. DASHBOARD LOGIC (PRIVACY DRIVEN)
# ==========================================
list_sumber = ["BOS", "SPP", "PIP", "RMP", "Sumbangan", "Lain-lain"]

if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    t1, t2, t3 = st.tabs(["🎥 MONITOR LIVE (ALL)", "✍️ INSTRUKSI", "💰 REKAP SUMBER DANA"])
    
    with t1: # Kepsek lihat semua
        df_all = load_db("monitor.csv")
        st.subheader("Semua Aktivitas Staf")
        st.dataframe(df_all[::-1], use_container_width=True)
        c1, c2 = st.columns(2); (c1.button("⏪ UNDO MON", on_click=undo, args=("monitor.csv",))); (c2.button("⏩ REDO MON", on_click=redo, args=("monitor.csv",)))

    with t2:
        target = st.multiselect("Pilih Staf:", list(st.session_state.users.keys()))
        msg = st.text_area("Pesan:")
        if st.button("Kirim"):
            df_ins = load_db("instruksi.csv")
            new_ins = pd.DataFrame([{"Time": waktu_wib, "Target": str(target), "Message": msg}])
            save_db(pd.concat([df_ins, new_ins], ignore_index=True), "instruksi.csv"); st.rerun()
        st.dataframe(load_db("instruksi.csv")[::-1], use_container_width=True)

    with t3:
        df_k = load_db("kas.csv")
        if not df_k.empty:
            m_cols = st.columns(3)
            for i, s in enumerate(list_sumber):
                ds = df_k[df_k['Source'] == s]
                saldo = ds['Masuk'].sum() - ds['Keluar'].sum()
                m_cols[i % 3].metric(f"Total {s}", f"Rp {saldo:,}")
            st.dataframe(df_k[::-1], use_container_width=True)

else:
    # --- PRIVASI STAF ---
    menu = ["📝 LAPOR KERJA", "🔔 INSTRUKSI"]
    if "Bendahara" in st.session_state.user_role: menu.insert(1, "💰 INPUT KAS")
    tabs = st.tabs(menu)
    
    with tabs[0]: # Staf hanya lihat miliknya sendiri
        akt = st.text_area("Laporan Kerja:")
        if st.button("Simpan Laporan"):
            df_mon = load_db("monitor.csv")
            new = pd.DataFrame([{"Time": waktu_wib, "Staff": st.session_state.user_role, "Activity": akt}])
            save_db(pd.concat([df_mon, new], ignore_index=True), "monitor.csv"); st.rerun()
        st.divider()
        st.subheader("Riwayat Laporan Saya")
        df_my = load_db("monitor.csv")
        if not df_my.empty:
            # FILTER HANYA DATA MILIK USER YANG LOGIN
            my_data = df_my[df_my['Staff'] == st.session_state.user_role]
            st.dataframe(my_data[::-1], use_container_width=True)

    if "Bendahara" in st.session_state.user_role:
        with tabs[1]:
            with st.form("kas_staff"):
                src = st.selectbox("Sumber Dana:", list_sumber)
                ket = st.text_input("Ket:"); m = st.number_input("Masuk:", value=0); k = st.number_input("Keluar:", value=0)
                pic = st.text_input("PIC:"); sub = st.form_submit_button("Simpan")
                if sub:
                    df_kas = load_db("kas.csv")
                    new_k = pd.DataFrame([{"Time": waktu_wib, "Staff": st.session_state.user_role, "Source": src, "Ket": ket, "Masuk": m, "Keluar": k, "PIC": pic}])
                    save_db(pd.concat([df_kas, new_k], ignore_index=True), "kas.csv"); st.rerun()
            
            st.subheader("Saldo Per Sumber")
            df_v = load_db("kas.csv")
            if not df_v.empty:
                v_cols = st.columns(3)
                for j, smb in enumerate(list_sumber):
                    val = df_v[df_v['Source'] == smb]
                    v_cols[j % 3].info(f"**{smb}:** Rp {val['Masuk'].sum() - val['Keluar'].sum():,}")
                st.dataframe(df_v[::-1], use_container_width=True)

    with tabs[-1]: # Instruksi dari Kepsek
        df_ins = load_db("instruksi.csv")
        if not df_ins.empty:
            for _, r in df_ins.iterrows():
                if st.session_state.user_role in str(r.get('Target', '')):
                    st.warning(f"**[{r.get('Time', 'N/A')}]** {r.get('Message', 'No Message')}")

# ==========================================
# 4. FOOTER & ACTIONS (GANTI PASSWORD BALIK!)
# ==========================================
st.divider()
act1, act2 = st.columns(2)
with act1:
    if st.button("🚪 LOGOUT", use_container_width=True): 
        st.session_state.logged_in = False; st.rerun()
with act2:
    with st.expander("🔑 GANTI PASSWORD"):
        new_pw = st.text_input("Password Baru:", type="password")
        if st.button("Simpan Perubahan"):
            st.session_state.users[st.session_state.user_role] = new_pw
            st.success("Password diperbarui!")

st.markdown('<div class="footer-section">', unsafe_allow_html=True)
_, mid_logo, _ = st.columns([1, 0.12, 1])
with mid_logo: st.image("logo_ruas.png", use_container_width=True)
st.markdown('<p class="dev-text">Developed by Hardianto | Powered by RUAS STUDIO</p></div>', unsafe_allow_html=True)
