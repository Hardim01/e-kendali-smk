import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# ==========================================
# 1. CSS: TAMPILAN TETAP KEREN (TIDAK BERUBAH)
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
    .footer-section { display: flex; flex-direction: column; align-items: center; margin-top: 50px; padding-top: 20px; border-top: 1px solid #333; }
    .dev-text { color: #888; font-size: 0.75rem; letter-spacing: 1px; margin-top: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATABASE ENGINE (FIX ERROR KEYERROR)
# ==========================================
DB_DIR = "database"
if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)

def load_db(name):
    p = os.path.join(DB_DIR, name)
    if os.path.exists(p):
        df = pd.read_csv(p)
        # Menyelaraskan nama kolom agar tidak KeyError
        mapping = {'Jam': 'Time', 'Isi': 'Message', 'Aktivitas': 'Activity', 'Staf': 'Staff'}
        df = df.rename(columns=mapping)
        return df
    return pd.DataFrame()

def save_db(df, name):
    df.to_csv(os.path.join(DB_DIR, name), index=False)

if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False, "user_role": None,
        "users": {
            "Kepala Sekolah": "kepsek123", "Waka Kurikulum": "kurikulum123", "Waka Kesiswaan": "kesiswaan123",
            "Waka Hubin": "hubin123", "Waka Sarpras": "sarpras123", "Kepala Tata Usaha": "ktu123",
            "Bendahara Bos": "bos123", "Bendahara Sekolah": "bendahara123", "Staf Bendahara Sekolah": "stafbend123",
            "Pembina Osis": "osis123", "Ketertiban": "tertib123", "Kepala Lab": "lab123",
            "BK": "bk123", "Kepala Perpustakaan": "perpus123", "Dokumentasi dan Publikasi": "dokpub123",
            "ADMIN SISTEM": "admin789"
        }
    })

waktu_wib = (datetime.now() + timedelta(hours=7)).strftime("%H:%M:%S")

# ==========================================
# 3. LOGIN PAGE (TIDAK BERUBAH)
# ==========================================
if not st.session_state.logged_in:
    _, l_col, _ = st.columns([1, 0.4, 1])
    with l_col: st.image("logo_smk.png", use_container_width=True)
    st.markdown("<h3 style='text-align:center; color:#ffc107;'>E-KENDALI LOGIN</h3>", unsafe_allow_html=True)
    with st.form("f_login"):
        jab = st.selectbox("Position:", list(st.session_state.users.keys()))
        pw = st.text_input("Password:", type="password")
        if st.form_submit_button("LOGIN TO SYSTEM", use_container_width=True):
            if pw == st.session_state.users[jab]:
                st.session_state.logged_in = True; st.session_state.user_role = jab; st.rerun()
            else: st.error("Wrong Password!")
    st.stop()

# ==========================================
# 4. DASHBOARD HEADER (TETAP DI TENGAH)
# ==========================================
_, d_col, _ = st.columns([1, 0.3, 1])
with d_col: st.image("logo_smk.png", use_container_width=True)
st.markdown(f'<div style="text-align:center;"><div class="digital-clock">{waktu_wib}</div></div>', unsafe_allow_html=True)

# ==========================================
# 5. MAIN TABS (SAMA SEPERTI SEBELUMNYA)
# ==========================================
if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    t1, t2, t3, t4, t5 = st.tabs(["🎥 MONITOR LIVE", "✍️ INSTRUCTION", "💰 FINANCE", "📁 REPORT ARCHIVE", "📚 TASK ARCHIVE"])
    with t1:
        df_mon = load_db("monitor.csv")
        st.table(df_mon[::-1] if not df_mon.empty else pd.DataFrame(columns=["Time", "Staff", "Activity"]))
    with t2:
        target = st.multiselect("Select Staff:", list(st.session_state.users.keys()))
        msg = st.text_area("Task Detail:")
        if st.button("Send Now"):
            df_ins = load_db("instruksi.csv")
            new_ins = pd.DataFrame([{"Time": waktu_wib, "Target": str(target), "Message": msg}])
            save_db(pd.concat([df_ins, new_ins], ignore_index=True), "instruksi.csv")
            st.success("Instruction Sent!")
    with t3:
        df_kas = load_db("kas.csv")
        if not df_kas.empty:
            st.metric("Balance", f"Rp {df_kas['Masuk'].sum() - df_kas['Keluar'].sum():,}")
            st.dataframe(df_kas[::-1], use_container_width=True)
    with t4: st.dataframe(load_db("monitor.csv")[::-1], use_container_width=True)
    with t5: st.dataframe(load_db("instruksi.csv")[::-1], use_container_width=True)
else:
    # STAFF VIEW (KURIKULUM DLL)
    st1, st2, st3 = st.tabs(["📝 WORK REPORT", "🔔 INSTRUCTIONS", "📚 MY ARCHIVE"])
    with st1:
        akt = st.text_area("Progress Update:")
        if st.button("Submit Progress"):
            df_mon = load_db("monitor.csv")
            new_mon = pd.DataFrame([{"Time": waktu_wib, "Staff": st.session_state.user_role, "Activity": akt}])
            save_db(pd.concat([df_mon, new_mon], ignore_index=True), "monitor.csv")
            st.success("Archived!")
    with st2:
        df_ins = load_db("instruksi.csv")
        if not df_ins.empty:
            for _, r in df_ins.iterrows():
                # Menggunakan r.get() untuk mencegah Error Kolom
                if st.session_state.user_role in str(r.get('Target', '')):
                    st.warning(f"**[{r.get('Time', 'N/A')}]** {r.get('Message', 'No Message')}")
    with st3:
        df_all = load_db("monitor.csv")
        if not df_all.empty:
            st.dataframe(df_all[df_all['Staff'] == st.session_state.user_role][::-1], use_container_width=True)

# ==========================================
# 6. PENGATURAN AKUN (LOGOUT & PW) - DI SINI!
# ==========================================
st.markdown("---")
col_log1, col_log2 = st.columns(2)
with col_log1:
    if st.button("🚪 LOGOUT FROM SYSTEM", use_container_width=True):
        st.session_state.logged_in = False; st.rerun()
with col_log2:
    with st.expander("🔑 Change Password"):
        n_pw = st.text_input("New Password:", type="password")
        if st.button("Save Password"):
            st.session_state.users[st.session_state.user_role] = n_pw
            st.success("Saved!")

# ==========================================
# 7. FOOTER (LOGO RUAS & ENGLISH CREDIT)
# ==========================================
st.markdown('<div class="footer-section">', unsafe_allow_html=True)
_, f_logo, _ = st.columns([1, 0.1, 1])
with f_logo:
    st.image("logo_ruas.png", use_container_width=True)
st.markdown('<p class="dev-text">Developed by Hardianto | Powered by RUAS STUDIO</p></div>', unsafe_allow_html=True)
