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
    .custom-footer { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-top: 50px; padding: 20px 0; border-top: 1px solid #333; }
    .dev-text { color: #888; font-size: 0.8rem; font-weight: bold; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATABASE ENGINE DENGAN KALKULASI FIX
# ==========================================
DB_DIR = "database"
if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)

def load_db(name):
    p = os.path.join(DB_DIR, name)
    if os.path.exists(p):
        df = pd.read_csv(p)
        mapping = {'Jam': 'Time', 'Isi': 'Message', 'Aktivitas': 'Activity', 'Staf': 'Staff', 'Sumber': 'Source'}
        df = df.rename(columns=mapping)
        # Pastikan kolom angka adalah numeric agar bisa dihitung
        if name == "kas.csv" and not df.empty:
            df['Masuk'] = pd.to_numeric(df['Masuk'], errors='coerce').fillna(0)
            df['Keluar'] = pd.to_numeric(df['Keluar'], errors='coerce').fillna(0)
        return df
    return pd.DataFrame()

def save_db(df, name):
    df.to_csv(os.path.join(DB_DIR, name), index=False)

if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False, "user_role": None,
        "users": {
            "Kepala Sekolah": "kepsek123", "Waka Kurikulum": "kurikulum123", "ADMIN SISTEM": "admin789",
            "Bendahara Bos": "bos123", "Bendahara Sekolah": "bendahara123", "Staf Bendahara Sekolah": "stafbend123"
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
        if st.form_submit_button("LOGIN"):
            if pw == st.session_state.users[jab]:
                st.session_state.logged_in = True; st.session_state.user_role = jab; st.rerun()
            else: st.error("Salah Password!")
    st.stop()

# ==========================================
# 4. DASHBOARD HEADER
# ==========================================
_, d_col, _ = st.columns([1, 0.3, 1])
with d_col: st.image("logo_smk.png", use_container_width=True)
st.markdown(f'<div style="text-align:center;"><div class="digital-clock">{waktu_wib}</div></div>', unsafe_allow_html=True)

# ==========================================
# 5. MAIN CONTENT
# ==========================================
if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    t1, t2, t3 = st.tabs(["🎥 MONITOR LIVE", "✍️ INSTRUKSI", "💰 KEUANGAN (UPDATE)"])
    with t1:
        df_mon = load_db("monitor.csv")
        st.table(df_mon[::-1] if not df_mon.empty else pd.DataFrame())
    with t2:
        target = st.multiselect("Pilih Staf:", list(st.session_state.users.keys()))
        msg = st.text_area("Tugas:")
        if st.button("Kirim"):
            df_ins = load_db("instruksi.csv")
            save_db(pd.concat([df_ins, pd.DataFrame([{"Time": waktu_wib, "Target": str(target), "Message": msg}])], ignore_index=True), "instruksi.csv")
            st.success("Sent!")
    with t3:
        df_kas = load_db("kas.csv")
        if not df_kas.empty:
            # KALKULASI MATEMATIKA YANG BENAR
            total_masuk = df_kas[df_kas['Source'] == 'SPP/Internal']['Masuk'].sum()
            total_keluar = df_kas[df_kas['Source'] == 'SPP/Internal']['Keluar'].sum()
            saldo_akhir = total_masuk - total_keluar
            
            st.metric("SALDO NON-BOS (SPP)", f"Rp {saldo_akhir:,}", delta=f"- Rp {total_keluar:,}")
            st.divider()
            st.dataframe(df_kas[::-1], use_container_width=True)

else:
    menu = ["📝 LAPOR KERJA", "🔔 INSTRUKSI"]
    if "Bendahara" in st.session_state.user_role: menu.insert(1, "💰 INPUT KAS")
    tabs = st.tabs(menu)
    
    with tabs[0]:
        akt = st.text_area("Laporan:")
        if st.button("Submit"):
            df_mon = load_db("monitor.csv")
            save_db(pd.concat([df_mon, pd.DataFrame([{"Time": waktu_wib, "Staff": st.session_state.user_role, "Activity": akt}])], ignore_index=True), "monitor.csv")
            st.success("Saved!")

    if "Bendahara" in st.session_state.user_role:
        with tabs[1]:
            with st.form("kas_v3"):
                src = st.selectbox("Sumber:", ["BOS", "SPP/Internal"])
                desc = st.text_input("Keterangan (Beli ATK, dll):")
                m = st.number_input("Masuk (Rp):", value=0)
                k = st.number_input("Keluar (Rp):", value=0)
                if st.form_submit_button("Simpan & Hitung Saldo"):
                    df_kas = load_db("kas.csv")
                    new_entry = pd.DataFrame([{"Time": waktu_wib, "Source": src, "Ket": desc, "Masuk": m, "Keluar": k, "Staff": st.session_state.user_role}])
                    save_db(pd.concat([df_kas, new_entry], ignore_index=True), "kas.csv")
                    st.rerun()
            
            df_v = load_db("kas.csv")
            if not df_v.empty:
                # LOGIKA PENGURANGAN REAL-TIME
                s_spp = df_v[df_v['Source'] == 'SPP/Internal']
                saldo_skrg = s_spp['Masuk'].sum() - s_spp['Keluar'].sum()
                st.info(f"### 🧮 Saldo SPP Saat Ini: Rp {saldo_skrg:,}")
                st.dataframe(df_v[::-1], use_container_width=True)

# ==========================================
# 6. FOOTER & ACTIONS
# ==========================================
st.divider()
if st.button("🚪 LOGOUT", use_container_width=True):
    st.session_state.logged_in = False; st.rerun()

st.markdown('<div class="custom-footer">', unsafe_allow_html=True)
_, mid_logo, _ = st.columns([1, 0.12, 1])
with mid_logo: st.image("logo_ruas.png", use_container_width=True)
st.markdown('<p class="dev-text">Developed by Hardianto | Powered by RUAS STUDIO</p></div>', unsafe_allow_html=True)
