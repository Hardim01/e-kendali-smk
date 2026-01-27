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
    .headline {
        text-align: center; color: #ffc107; font-size: 2.5em; font-weight: bold;
        margin-bottom: 0px; text-shadow: 2px 2px #000;
    }
    .digital-clock { 
        font-family: 'Courier New', monospace; color: #ffc107; background-color: #000; font-size: 3.2em; 
        font-weight: bold; text-align: center; border: 3px solid #ffc107; border-radius: 12px; 
        padding: 10px 25px; margin: 10px auto; display: inline-block; box-shadow: 0px 0px 15px #ffc107;
    }
    .running-text {
        background-color: #ffc107; color: #000; padding: 10px; font-weight: bold;
        border-radius: 5px; margin: 20px 0; font-size: 1.1em;
    }
    div[data-testid="stForm"] { margin: 0 auto !important; width: 450px !important; border: 2px solid #ffc107 !important; border-radius: 15px; }
    
    /* Footer Tengah & Logo Ruas */
    .footer-container {
        text-align: center;
        margin-top: 60px;
        padding: 20px;
        border-top: 1px solid #333;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .dev-text { color: #888; font-size: 0.9rem; font-weight: bold; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATABASE & UPLOAD ENGINE
# ==========================================
DB_DIR = "database"
UPLOAD_DIR = "uploads"
for d in [DB_DIR, UPLOAD_DIR]:
    if not os.path.exists(d): os.makedirs(d)

def load_db(name):
    p = os.path.join(DB_DIR, name)
    if os.path.exists(p):
        df = pd.read_csv(p)
        mapping = {'Jam': 'Time', 'Aktivitas': 'Activity', 'Staf': 'Staff', 'Sumber': 'Source', 'User': 'PIC', 'Isi': 'Message', 'Lampiran': 'Attachment'}
        df = df.rename(columns=mapping)
        if name == "kas.csv" and not df.empty:
            df['Masuk'] = pd.to_numeric(df['Masuk'], errors='coerce').fillna(0)
            df['Keluar'] = pd.to_numeric(df['Keluar'], errors='coerce').fillna(0)
        return df
    return pd.DataFrame()

def save_db(df, name):
    df.to_csv(os.path.join(DB_DIR, name), index=False)

# --- LOGIN SESSION ---
if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False, "user_role": None, 
        "users": {
            "Kepala Sekolah": "kepsek123", "Waka Kurikulum": "kurikulum123", "Waka Kesiswaan": "kesiswaan123",
            "Bendahara Sekolah": "bendahara123", "Bendahara Bos": "bos123", "ADMIN SISTEM": "admin789"
        }
    })

waktu_wib = (datetime.now() + timedelta(hours=7)).strftime("%H:%M:%S")

# Header Headline & Logo SMK Tengah
st.markdown('<h1 class="headline">SISTEM KENDALI SMK NASIONAL BANDUNG</h1>', unsafe_allow_html=True)
_, mid_logo_smk, _ = st.columns([1, 0.3, 1])
with mid_logo_smk: st.image("logo_smk.png", use_container_width=True)

# Running Text
st.markdown(f"""<div class="running-text"><marquee scrollamount="10">Kieu Bisa, Kitu Bisa, Sagala Bisa... Pekerjaan Memang Penting Tapi Sholat Yang Utama!</marquee></div>""", unsafe_allow_html=True)

if not st.session_state.logged_in:
    with st.form("login"):
        u = st.selectbox("Pilih Posisi", list(st.session_state.users.keys()))
        p = st.text_input("Password", type="password")
        if st.form_submit_button("MASUK SISTEM"):
            if p == st.session_state.users[u]: 
                st.session_state.logged_in = True; st.session_state.user_role = u; st.rerun()
            else: st.error("Akses Ditolak!")
    st.stop()

st.markdown(f'<div style="text-align:center;"><div class="digital-clock">{waktu_wib}</div></div>', unsafe_allow_html=True)

# ==========================================
# 3. KONTEN DASHBOARD
# ==========================================
list_sumber = ["BOS", "SPP", "PIP", "RMP", "Sumbangan", "Lain-lain"]

if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    t1, t2, t3 = st.tabs(["🎥 MONITOR LIVE", "✍️ INSTRUKSI KEPSEK", "💰 KEUANGAN"])
    with t1:
        st.dataframe(load_db("monitor.csv")[::-1], use_container_width=True)
    with t2:
        target = st.multiselect("Target Staf:", list(st.session_state.users.keys()))
        msg = st.text_area("Instruksi:")
        f_ins = st.file_uploader("Lampiran (PDF/Word/JPG/Video):", type=['pdf','docx','jpg','png','mp4'], key="ins")
        if st.button("Kirim Instruksi"):
            fn = f_ins.name if f_ins else "-"
            if f_ins:
                with open(os.path.join(UPLOAD_DIR, f_ins.name), "wb") as f: f.write(f_ins.getbuffer())
            df_i = load_db("instruksi.csv")
            save_db(pd.concat([df_i, pd.DataFrame([{"Time": waktu_wib, "Target": str(target), "Message": msg, "Attachment": fn}])], ignore_index=True), "instruksi.csv"); st.rerun()
        st.dataframe(load_db("instruksi.csv")[::-1], use_container_width=True)
    with t3:
        df_k = load_db("kas.csv")
        if not df_k.empty:
            m_cols = st.columns(3)
            for i, s in enumerate(list_sumber):
                ds = df_k[df_k['Source'] == s]
                saldo = ds['Masuk'].sum() - ds['Keluar'].sum()
                m_cols[i % 3].metric(f"Saldo {s}", f"Rp {saldo:,}")
            st.dataframe(df_k[::-1], use_container_width=True)

else:
    menu = ["📝 LAPOR KERJA", "🔔 INSTRUKSI"]
    if "Bendahara" in st.session_state.user_role: menu.insert(1, "💰 INPUT KAS")
    tabs = st.tabs(menu)
    with tabs[0]:
        akt = st.text_area("Laporan Kerja:")
        f_lapor = st.file_uploader("Lampirkan Bukti (Gambar/Doc/Video):", type=['pdf','docx','jpg','png','mp4'], key="lapor")
        if st.button("Simpan Laporan"):
            fn = f_lapor.name if f_lapor else "-"
            if f_lapor:
                with open(os.path.join(UPLOAD_DIR, f_lapor.name), "wb") as f: f.write(f_lapor.getbuffer())
            df_m = load_db("monitor.csv")
            save_db(pd.concat([df_m, pd.DataFrame([{"Time": waktu_wib, "Staff": st.session_state.user_role, "Activity": akt, "Attachment": fn}])], ignore_index=True), "monitor.csv"); st.rerun()
        st.divider(); st.dataframe(load_db("monitor.csv")[load_db("monitor.csv")['Staff'] == st.session_state.user_role][::-1], use_container_width=True)

    if "Bendahara" in st.session_state.user_role:
        with tabs[1]:
            with st.form("kas"):
                src = st.selectbox("Sumber:", list_sumber); ket = st.text_input("Ket"); m = st.number_input("Masuk", value=0); k = st.number_input("Keluar", value=0); pic = st.text_input("PIC"); sub = st.form_submit_button("Simpan")
                if sub:
                    df_kas = load_db("kas.csv")
                    save_db(pd.concat([df_kas, pd.DataFrame([{"Time": waktu_wib, "Staff": st.session_state.user_role, "Source": src, "Ket": ket, "Masuk": m, "Keluar": k, "PIC": pic}])], ignore_index=True), "kas.csv"); st.rerun()
            df_v = load_db("kas.csv")
            if not df_v.empty:
                v_cols = st.columns(3)
                for j, smb in enumerate(list_sumber):
                    val = df_v[df_v['Source'] == smb]
                    v_cols[j % 3].info(f"**{smb}:** Rp {val['Masuk'].sum() - val['Keluar'].sum():,}")
                st.dataframe(df_v[::-1], use_container_width=True)

    with tabs[-1]:
        df_ins = load_db("instruksi.csv")
        if not df_ins.empty:
            for _, r in df_ins.iterrows():
                if st.session_state.user_role in str(r.get('Target', '')):
                    st.warning(f"**[{r.get('Time', 'N/A')}]** {r.get('Message', 'No Message')} \n\n 📎 Lampiran: {r.get('Attachment', '-')}")

# ==========================================
# 4. PASSWORD & FOOTER (LOGO RUAS CENTERED)
# ==========================================
st.divider()
c1, c2 = st.columns(2)
with c1:
    if st.button("🚪 LOGOUT", use_container_width=True): st.session_state.logged_in = False; st.rerun()
with c2:
    with st.expander("🔑 GANTI PASSWORD"):
        new_pw = st.text_input("Baru:", type="password")
        if st.button("Update"): st.session_state.users[st.session_state.user_role] = new_pw; st.success("OK")

# FOOTER DENGAN LOGO RUAS DI TENGAH
st.markdown("---")
_, mid_footer, _ = st.columns([1, 0.4, 1])
with mid_footer:
    st.image("logo_ruas.png", use_container_width=True) # Pastikan file logo_ruas.png ada di folder aplikasi
    st.markdown('<p style="text-align:center; color:#888; font-weight:bold; font-size:0.9rem;">Developed by Hardianto | Powered by RUAS STUDIO</p>', unsafe_allow_html=True)
