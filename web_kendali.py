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
    div[data-testid="stForm"] { border: 2px solid #ffc107 !important; border-radius: 15px; padding: 20px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATABASE ENGINE (FIX KEYERROR)
# ==========================================
DB_DIR = "database"
UPLOAD_DIR = "uploads"
for d in [DB_DIR, UPLOAD_DIR]:
    if not os.path.exists(d): os.makedirs(d)

def load_db(name):
    p = os.path.join(DB_DIR, name)
    if os.path.exists(p):
        df = pd.read_csv(p)
        # Standarisasi Nama Kolom agar tidak Error KeyError
        mapping = {
            'Time': 'Jam', 'Staff': 'Staf', 'Activity': 'Aktivitas', 
            'Attachment': 'File', 'Source': 'Sumber', 'PIC': 'PIC',
            'Message': 'Pesan', 'Target': 'Target'
        }
        df = df.rename(columns=mapping)
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
            "Kepala Sekolah": "kepsek123", "Waka Kurikulum": "kurikulum123", "Waka Kesiswaan": "kesiswaan123",
            "Bendahara Sekolah": "bendahara123", "Bendahara Bos": "bos123", "ADMIN SISTEM": "admin789"
        }
    })

waktu_wib = (datetime.now() + timedelta(hours=7)).strftime("%H:%M:%S")

# Header & Logo
st.markdown('<h1 class="headline">SISTEM KENDALI SMK NASIONAL BANDUNG</h1>', unsafe_allow_html=True)
_, mid_logo_smk, _ = st.columns([1, 0.3, 1])
with mid_logo_smk: st.image("logo_smk.png", use_container_width=True)

st.markdown(f"""<div class="running-text"><marquee scrollamount="10">Kieu Bisa, Kitu Bisa, Sagala Bisa... Pekerjaan Memang Penting Tapi Sholat Yang Utama!</marquee></div>""", unsafe_allow_html=True)

if not st.session_state.logged_in:
    _, l_col, _ = st.columns([1, 0.4, 1])
    with l_col:
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
# 3. DASHBOARD LOGIC
# ==========================================
list_sumber = ["BOS", "SPP", "PIP", "RMP", "Sumbangan", "Lain-lain"]

if st.session_state.user_role in ["Kepala Sekolah", "ADMIN SISTEM"]:
    t1, t2, t3 = st.tabs(["🎥 MONITOR REAL-TIME", "✍️ BERI INSTRUKSI", "💰 KEUANGAN"])
    
    with t1:
        st.subheader("📋 Laporan Kerja Harian Staf")
        st.dataframe(load_db("monitor.csv")[::-1], use_container_width=True)
        st.divider()
        st.subheader("✅ Pelaksanaan Instruksi (Progres)")
        st.dataframe(load_db("respon_instruksi.csv")[::-1], use_container_width=True)

    with t2:
        st.subheader("Kirim Instruksi Baru")
        target = st.multiselect("Target Staf:", list(st.session_state.users.keys()))
        msg = st.text_area("Isi Instruksi:")
        f_ins = st.file_uploader("Lampiran:", type=['pdf','docx','jpg','png','mp4'], key="ins_kepsek")
        if st.button("Kirim Sekarang"):
            fn = f_ins.name if f_ins else "-"
            if f_ins:
                with open(os.path.join(UPLOAD_DIR, f_ins.name), "wb") as f: f.write(f_ins.getbuffer())
            df_i = load_db("instruksi.csv")
            new_i = pd.DataFrame([{"Jam": waktu_wib, "Target": str(target), "Pesan": msg, "File": fn}])
            save_db(pd.concat([df_i, new_i], ignore_index=True), "instruksi.csv"); st.success("Instruksi Terkirim!"); st.rerun()
        st.dataframe(load_db("instruksi.csv")[::-1], use_container_width=True)

    with t3:
        df_k = load_db("kas.csv")
        if not df_k.empty:
            m_cols = st.columns(3)
            for i, s in enumerate(list_sumber):
                ds = df_k[df_k['Sumber'] == s] if 'Sumber' in df_k.columns else pd.DataFrame()
                saldo = ds['Masuk'].sum() - ds['Keluar'].sum() if not ds.empty else 0
                m_cols[i % 3].metric(f"Saldo {s}", f"Rp {saldo:,}")
            st.dataframe(df_k[::-1], use_container_width=True)

else:
    menu = ["📝 LAPOR KERJA HARIAN", "🔔 INSTRUKSI & PELAKSANAAN"]
    if "Bendahara" in st.session_state.user_role: menu.insert(1, "💰 INPUT KAS")
    tabs = st.tabs(menu)
    
    with tabs[0]:
        st.subheader("Catat Kerja Harian")
        akt = st.text_area("Aktivitas Anda?")
        f_l = st.file_uploader("Upload Bukti:", type=['pdf','docx','jpg','png','mp4'], key="lapor_staf")
        if st.button("Kirim Laporan"):
            fn = f_l.name if f_l else "-"
            if f_l:
                with open(os.path.join(UPLOAD_DIR, f_l.name), "wb") as f: f.write(f_l.getbuffer())
            df_m = load_db("monitor.csv")
            new_m = pd.DataFrame([{"Jam": waktu_wib, "Staf": st.session_state.user_role, "Aktivitas": akt, "File": fn}])
            save_db(pd.concat([df_m, new_m], ignore_index=True), "monitor.csv"); st.success("Terkirim!"); st.rerun()
        
        st.divider()
        df_my = load_db("monitor.csv")
        if not df_my.empty and 'Staf' in df_my.columns:
            st.write("Riwayat Laporan Saya:")
            st.dataframe(df_my[df_my['Staf'] == st.session_state.user_role][::-1], use_container_width=True)

    with tabs[-1]:
        st.subheader("🔔 Instruksi Bapak Kepsek")
        df_ins = load_db("instruksi.csv")
        if not df_ins.empty:
            for i, r in df_ins.iterrows():
                if st.session_state.user_role in str(r.get('Target', '')):
                    with st.expander(f"🔴 INSTRUKSI: {r.get('Jam','-')}"):
                        st.write(f"**Pesan:** {r.get('Pesan','-')}")
                        st.write(f"📎 **File:** {r.get('File','-')}")
                        st.divider()
                        with st.form(f"f_res_{i}"):
                            res_msg = st.text_area("Hasil Pelaksanaan:")
                            res_f = st.file_uploader("Bukti File:", type=['pdf','docx','jpg','png','mp4'])
                            if st.form_submit_button("Lapor Selesai"):
                                rf = res_f.name if res_f else "-"
                                if res_f:
                                    with open(os.path.join(UPLOAD_DIR, res_f.name), "wb") as f: f.write(res_f.getbuffer())
                                df_res = load_db("respon_instruksi.csv")
                                new_res = pd.DataFrame([{"Jam": waktu_wib, "Staf": st.session_state.user_role, "Hasil": res_msg, "File_Bukti": rf}])
                                save_db(pd.concat([df_res, new_res], ignore_index=True), "respon_instruksi.csv")
                                st.success("Berhasil Dilaporkan!"); st.rerun()

    if "Bendahara" in st.session_state.user_role:
        with tabs[1]:
            with st.form("kas"):
                src = st.selectbox("Sumber:", list_sumber); ket = st.text_input("Ket"); m = st.number_input("Masuk", 0); k = st.number_input("Keluar", 0); p_pic = st.text_input("PIC"); sub = st.form_submit_button("Simpan")
                if sub:
                    df_k = load_db("kas.csv")
                    new_k = pd.DataFrame([{"Jam": waktu_wib, "Staf": st.session_state.user_role, "Sumber": src, "Ket": ket, "Masuk": m, "Keluar": k, "PIC": p_pic}])
                    save_db(pd.concat([df_k, new_k], ignore_index=True), "kas.csv"); st.rerun()
            df_v = load_db("kas.csv")
            if not df_v.empty:
                v_cols = st.columns(3)
                for j, smb in enumerate(list_sumber):
                    val = df_v[df_v['Sumber'] == smb] if 'Sumber' in df_v.columns else pd.DataFrame()
                    saldo = val['Masuk'].sum() - val['Keluar'].sum() if not val.empty else 0
                    v_cols[j % 3].info(f"**{smb}:** Rp {saldo:,}")
                st.dataframe(df_v[::-1], use_container_width=True)

# ==========================================
# 4. FOOTER (TENGAH & LOGO RUAS)
# ==========================================
st.divider()
c1, c2 = st.columns(2)
with c1:
    if st.button("🚪 LOGOUT", use_container_width=True): st.session_state.logged_in = False; st.rerun()
with c2:
    with st.expander("🔑 GANTI PASSWORD"):
        new_pw = st.text_input("Baru:", type="password")
        if st.button("Update"): st.session_state.users[st.session_state.user_role] = new_pw; st.success("OK")

st.markdown("---")
_, mid_footer, _ = st.columns([1, 0.4, 1])
with mid_footer:
    st.image("logo_ruas.png", use_container_width=True)
    st.markdown('<p style="text-align:center; color:#888; font-weight:bold; font-size:0.9rem;">Developed by Hardianto | Powered by RUAS STUDIO</p>', unsafe_allow_html=True)
