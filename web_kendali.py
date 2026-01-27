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
    .custom-footer { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-top: 50px; padding: 20px 0; border-top: 1px solid #333; }
    .dev-text { color: #888; font-size: 0.8rem; font-weight: bold; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATABASE ENGINE DENGAN LOGIKA SALDO
# ==========================================
DB_DIR = "database"
if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)

def load_db(name):
    p = os.path.join(DB_DIR, name)
    if os.path.exists(p):
        df = pd.read_csv(p)
        mapping = {'Jam': 'Time', 'Isi': 'Message', 'Aktivitas': 'Activity', 'Staf': 'Staff', 'Sumber': 'Source'}
        df = df.rename(columns=mapping)
        # LOGIKA HITUNG SALDO OTOMATIS
        if name == "kas.csv" and not df.empty:
            df = df.sort_values(by='Time') # Urutkan biar hitungannya benar
            df['Balance'] = df['Masuk'].fillna(0) - df['Keluar'].fillna(0)
            df['Running_Total'] = df['Balance'].cumsum()
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
            else: st.error("Password Salah!")
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
    t1, t2, t3, t4 = st.tabs(["🎥 MONITOR LIVE", "✍️ INSTRUKSI", "💰 KEUANGAN (REALTIME)", "📚 ARSIP"])
    with t1:
        df_mon = load_db("monitor.csv")
        st.table(df_mon[::-1] if not df_mon.empty else pd.DataFrame(columns=["Time", "Staff", "Activity"]))
    with t2:
        target = st.multiselect("Pilih Staf:", list(st.session_state.users.keys()))
        msg = st.text_area("Detail Tugas:")
        if st.button("Kirim Sekarang"):
            df_ins = load_db("instruksi.csv")
            save_db(pd.concat([df_ins, pd.DataFrame([{"Time": waktu_wib, "Target": str(target), "Message": msg}])], ignore_index=True), "instruksi.csv")
            st.success("Terkirim!")
    with t3:
        df_kas = load_db("kas.csv")
        if not df_kas.empty:
            b_val = df_kas[df_kas['Source'] == 'BOS']
            s_val = df_kas[df_kas['Source'] == 'SPP/Internal']
            
            # METRIC YANG DINAMIS
            m1, m2 = st.columns(2)
            m1.metric("SALDO BOS (NET)", f"Rp {b_val['Masuk'].sum() - b_val['Keluar'].sum():,}")
            m2.metric("SALDO SPP (NET)", f"Rp {s_val['Masuk'].sum() - s_val['Keluar'].sum():,}")
            
            st.divider()
            st.write("Log Transaksi (Saldo Berjalan):")
            st.dataframe(df_kas[::-1], use_container_width=True)

else:
    # VIEW UNTUK BENDAHARA & STAF
    menu = ["📝 LAPOR KERJA", "🔔 INSTRUKSI"]
    if "Bendahara" in st.session_state.user_role:
        menu.insert(1, "💰 INPUT KAS & SALDO")
    
    tabs = st.tabs(menu)
    
    with tabs[0]:
        akt = st.text_area("Laporan Hari Ini:")
        if st.button("Kirim Laporan"):
            df_mon = load_db("monitor.csv")
            save_db(pd.concat([df_mon, pd.DataFrame([{"Time": waktu_wib, "Staff": st.session_state.user_role, "Activity": akt}])], ignore_index=True), "monitor.csv")
            st.success("Laporan Terkirim!")

    if "Bendahara" in st.session_state.user_role:
        with tabs[1]:
            with st.form("kas_final"):
                src = st.selectbox("Pilih Pos Dana:", ["BOS", "SPP/Internal"])
                desc = st.text_input("Keterangan (Contoh: Beli ATK):")
                m = st.number_input("Uang Masuk (Rp):", value=0)
                k = st.number_input("Uang Keluar (Rp):", value=0)
                u = st.text_input("PIC/Penerima:")
                if st.form_submit_button("Update Kas"):
                    df_kas = load_db("kas.csv")
                    # Simpan data mentah
                    new_entry = pd.DataFrame([{"Time": waktu_wib, "Staff": st.session_state.user_role, "Source": src, "Ket": desc, "Masuk": m, "Keluar": k, "User": u}])
                    save_db(pd.concat([df_kas, new_entry], ignore_index=True), "kas.csv")
                    st.success("Kas Berhasil Diupdate!")
            
            st.divider()
            # TAMPILAN SALDO AKTUAL SETELAH PENGURANGAN
            df_v = load_db("kas.csv")
            if not df_v.empty:
                v_bos = df_v[df_v['Source'] == 'BOS']
                v_spp = df_v[df_v['Source'] == 'SPP/Internal']
                
                # BOX INFO SALDO AKHIR
                st.info(f"💰 **SALDO BOS AKHIR:** Rp {v_bos['Masuk'].sum() - v_bos['Keluar'].sum():,}")
                st.success(f"💰 **SALDO SPP AKHIR:** Rp {v_spp['Masuk'].sum() - v_spp['Keluar'].sum():,}")
                
                st.write("Riwayat Pengeluaran/Pemasukan:")
                st.dataframe(df_v[::-1], use_container_width=True)

    with tabs[-1]:
        df_ins = load_db("instruksi.csv")
        if not df_ins.empty:
            for _, r in df_ins.iterrows():
                if st.session_state.user_role in str(r.get('Target', '')):
                    st.warning(f"**[{r.get('Time', 'N/A')}]** {r.get('Message', 'No Message')}")

# ==========================================
# 6. LOGOUT & FOOTER
# ==========================================
st.divider()
clout1, clout2 = st.columns(2)
with clout1:
    if st.button("🚪 LOGOUT", use_container_width=True):
        st.session_state.logged_in = False; st.rerun()
with clout2:
    with st.expander("🔑 Password"):
        p_new = st.text_input("New:", type="password")
        if st.button("Update"):
            st.session_state.users[st.session_state.user_role] = p_new
            st.success("OK")

st.markdown('<div class="custom-footer">', unsafe_allow_html=True)
_, mid_logo, _ = st.columns([1, 0.12, 1])
with mid_logo: st.image("logo_ruas.png", use_container_width=True)
st.markdown('<p class="dev-text">Developed by Hardianto | Powered by RUAS STUDIO</p></div>', unsafe_allow_html=True)
