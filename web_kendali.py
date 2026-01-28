import streamlit as st
import pandas as pd
from datetime import datetime
import pytz 
import os

# ==========================================
# 1. KONFIGURASI & TAMPILAN
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
    .welcome-msg { text-align: center; font-size: 1.5em; font-weight: bold; color: #2e7d32; margin-top: 10px; }
    .ibadah-msg { text-align: center; color: #ffffff; background-color: #d32f2f; padding: 15px; border-radius: 10px; font-weight: bold; margin-bottom: 20px; border: 2px solid #ffc107; }
    .running-text { background-color: #ffc107; color: #000; padding: 10px; font-weight: bold; border-radius: 5px; margin: 20px 0; font-size: 1.1em; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. SINKRONISASI WAKTU
# ==========================================
tz_jkt = pytz.timezone('Asia/Jakarta')
waktu_sekarang = datetime.now(tz_jkt)
waktu_tabel = waktu_sekarang.strftime("%d/%m/%Y %H:%M:%S")
jam_digital = waktu_sekarang.strftime("%H:%M:%S")

# ==========================================
# 3. DATABASE ENGINE
# ==========================================
DB_DIR = "database"
UPLOAD_DIR = "uploads"
for d in [DB_DIR, UPLOAD_DIR]:
    if not os.path.exists(d): os.makedirs(d)

def load_db(name, cols):
    p = os.path.join(DB_DIR, name)
    if os.path.exists(p):
        df = pd.read_csv(p)
        for c in cols:
            if c not in df.columns: df[c] = "-"
        return df
    return pd.DataFrame(columns=cols)

def save_db(df, name):
    df.to_csv(os.path.join(DB_DIR, name), index=False)

COL_MONITOR = ["Jam", "Staf", "Aktivitas", "Lampiran_File"]
COL_KAS = ["Jam", "Staf", "Sumber_Dana", "Peruntukan", "PJ_Pengguna", "Keterangan", "Masuk", "Keluar"]
COL_INS = ["Jam", "Target", "Pesan", "File_Instruksi", "Status"]
COL_RESPON = ["Jam", "Staf", "Hasil", "Lampiran_Hasil"]
COL_PROFIL = ["Jabatan", "Nama", "NUPTK", "Foto_Path"]

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

# ==========================================
# 4. LOGIN SYSTEM
# ==========================================
st.markdown('<h1 class="headline">SISTEM KENDALI SMK NASIONAL BANDUNG</h1>', unsafe_allow_html=True)
if not st.session_state.logged_in:
    st.markdown('<div class="ibadah-msg">"Awali setiap pekerjaan dengan selalu berniat untuk Ibadah kepada Allah SWT agar setiap langkah menjadi berkah."</div>', unsafe_allow_html=True)
    _, mid_logo, _ = st.columns([1, 0.3, 1])
    with mid_logo: st.image("logo_smk.png", use_container_width=True)
    _, l_col, _ = st.columns([1, 0.4, 1])
    with l_col:
        with st.form("login"):
            u = st.selectbox("Jabatan", list(st.session_state.users.keys()))
            p = st.text_input("Password", type="password")
            if st.form_submit_button("LOGIN"):
                if p == st.session_state.users[u]: 
                    st.session_state.logged_in = True
                    st.session_state.user_role = u
                    st.rerun()
                else: st.error("Akses Ditolak!")
    st.stop()

st.markdown(f"""<div class="running-text"><marquee scrollamount="10">Kieu Bisa, Kitu Bisa, Sagala Bisa... Pekerjaan Memang Penting Tapi Sholat Yang Utama!</marquee></div>""", unsafe_allow_html=True)
st.markdown(f'<div style="text-align:center;"><div class="digital-clock">{jam_digital}</div></div>', unsafe_allow_html=True)
st.markdown(f'<div class="welcome-msg">Selamat Datang, {st.session_state.user_role} SMK NASIONAL</div>', unsafe_allow_html=True)

# ==========================================
# 5. DASHBOARD KEPALA SEKOLAH
# ==========================================
if st.session_state.user_role in ["Kepala Sekolah", "ADMIN UTAMA"]:
    t1, t2, t3, t4, t5, t6, t7 = st.tabs(["🎥 MONITORING", "✍️ INSTRUKSI", "📋 DAFTAR INSTRUKSI", "📂 ARSIP JAWABAN", "💰 CASHFLOW", "📚 RIWAYAT", "⚙️ AKUN"])
    
    with t1: st.dataframe(load_db("monitor.csv", COL_MONITOR)[::-1], use_container_width=True)
    with t2:
        with st.form("ins"):
            target = st.multiselect("Tujukan Ke:", list(st.session_state.users.keys()))
            msg = st.text_area("Isi Instruksi")
            f = st.file_uploader("File")
            if st.form_submit_button("Kirim"):
                fn = f.name if f else "-"
                if f:
                    with open(os.path.join(UPLOAD_DIR, f.name), "wb") as file: file.write(f.getbuffer())
                save_db(pd.concat([load_db("instruksi.csv", COL_INS), pd.DataFrame([{"Jam": waktu_tabel, "Target": str(target), "Pesan": msg, "File_Instruksi": fn, "Status": "Terkirim"}])], ignore_index=True), "instruksi.csv")
                st.success("Terkirim!")
    with t3: st.dataframe(load_db("instruksi.csv", COL_INS)[::-1], use_container_width=True)
    with t4: st.dataframe(load_db("respon.csv", COL_RESPON)[::-1], use_container_width=True)
    with t5:
        df_s = load_db("kas_sekolah.csv", COL_KAS); df_b = load_db("kas_bos.csv", COL_KAS)
        st.write("### Rekap Kas Sekolah"); st.dataframe(df_s[::-1], use_container_width=True)
        st.write("### Rekap Kas BOS"); st.dataframe(df_b[::-1], use_container_width=True)
    with t6: st.dataframe(load_db("monitor.csv", COL_MONITOR)[::-1], use_container_width=True)
    with t7:
        # Bagian Update Profil Kepala Sekolah (Nama, NUPTK, Foto, Pwd)
        df_p = load_db("profil.csv", COL_PROFIL); me = df_p[df_p["Jabatan"] == st.session_state.user_role]
        with st.form("up_adm"):
            n = st.text_input("Nama", value=me.iloc[0]["Nama"] if not me.empty else "")
            nu = st.text_input("NUPTK/NIK", value=me.iloc[0]["NUPTK"] if not me.empty else "")
            fo = st.file_uploader("Foto"); pw = st.text_input("Sandi Baru", type="password")
            if st.form_submit_button("Simpan Profil"):
                if pw: st.session_state.users[st.session_state.user_role] = pw
                fn_f = f"foto_{st.session_state.user_role}.jpg" if fo else (me.iloc[0]["Foto_Path"] if not me.empty else "-")
                if fo:
                    with open(os.path.join(UPLOAD_DIR, fn_f), "wb") as f: f.write(fo.getbuffer())
                df_p = df_p[df_p["Jabatan"] != st.session_state.user_role]
                save_db(pd.concat([df_p, pd.DataFrame([{"Jabatan": st.session_state.user_role, "Nama": n, "NUPTK": nu, "Foto_Path": fn_f}])], ignore_index=True), "profil.csv")
                st.rerun()

# ==========================================
# 6. DASHBOARD STAF
# ==========================================
else:
    is_bendahara = "Bendahara" in st.session_state.user_role
    t_labels = ["📝 CATATAN HARIAN", "🔔 INSTRUKSI KEPSEK", "📂 ARSIP SAYA", "⚙️ AKUN"]
    if is_bendahara: t_labels.insert(0, "💰 INPUT KAS")
    tabs = st.tabs(t_labels)

    # KHUSUS BENDAHARA (FITUR BARU SESUAI PERMINTAAN)
    if is_bendahara:
        with tabs[0]:
            db_f = "kas_bos.csv" if "BOS" in st.session_state.user_role else "kas_sekolah.csv"
            df_k = load_db(db_f, COL_KAS)
            st.metric("SALDO", f"Rp {pd.to_numeric(df_k['Masuk'], errors='coerce').sum() - pd.to_numeric(df_k['Keluar'], errors='coerce').sum():,.0f}")
            with st.form("kas_form"):
                c1, c2 = st.columns(2)
                src = c1.text_input("Sumber Dana (Dari Mana?)")
                unt = c1.text_input("Peruntukan (Untuk Apa?)")
                pj = c2.text_input("Penanggung Jawab / Pengguna Anggaran")
                ket = c2.text_area("Keterangan Tambahan")
                m = c1.number_input("Uang Masuk (Rp)", min_value=0)
                k = c2.number_input("Uang Keluar (Rp)", min_value=0)
                if st.form_submit_button("SIMPAN TRANSAKSI KAS"):
                    new_kas = pd.DataFrame([{"Jam": waktu_tabel, "Staf": st.session_state.user_role, "Sumber_Dana": src, "Peruntukan": unt, "PJ_Pengguna": pj, "Keterangan": ket, "Masuk": m, "Keluar": k}])
                    save_db(pd.concat([df_k, new_kas], ignore_index=True), db_f)
                    st.success("Data Berhasil Dicatat!"); st.rerun()
            st.dataframe(df_k[::-1], use_container_width=True)

    with tabs[t_labels.index("📝 CATATAN HARIAN")]:
        with st.form("h"):
            akt = st.text_area("Aktivitas:"); f_h = st.file_uploader("Bukti")
            if st.form_submit_button("Simpan"):
                fn_h = f_h.name if f_h else "-"
                if f_h:
                    with open(os.path.join(UPLOAD_DIR, f_h.name), "wb") as fl: fl.write(f_h.getbuffer())
                save_db(pd.concat([load_db("monitor.csv", COL_MONITOR), pd.DataFrame([{"Jam": waktu_tabel, "Staf": st.session_state.user_role, "Aktivitas": akt, "Lampiran_File": fn_h}])], ignore_index=True), "monitor.csv")
                st.rerun()
        st.dataframe(load_db("monitor.csv", COL_MONITOR)[load_db("monitor.csv", COL_MONITOR)['Staf'] == st.session_state.user_role][::-1], use_container_width=True)

    with tabs[t_labels.index("🔔 INSTRUKSI KEPSEK")]:
        df_i = load_db("instruksi.csv", COL_INS); my_i = df_i[df_i['Target'].str.contains(st.session_state.user_role)]
        for i, r in my_i[::-1].iterrows():
            with st.expander(f"Tugas {r['Jam']}"):
                st.warning(r['Pesan'])
                with st.form(f"res_{i}"):
                    res = st.text_area("Hasil:"); f_res = st.file_uploader("Upload Bukti", key=f"f_{i}")
                    if st.form_submit_button("Kirim Laporan"):
                        fn_res = f_res.name if f_res else "-"
                        if f_res:
                            with open(os.path.join(UPLOAD_DIR, f_res.name), "wb") as fl: fl.write(f_res.getbuffer())
                        save_db(pd.concat([load_db("respon.csv", COL_RESPON), pd.DataFrame([{"Jam": waktu_tabel, "Staf": st.session_state.user_role, "Hasil": res, "Lampiran_Hasil": fn_res}])], ignore_index=True), "respon.csv")
                        st.success("Terkirim!"); st.rerun()

    with tabs[t_labels.index("📂 ARSIP SAYA")]:
        st.dataframe(load_db("respon.csv", COL_RESPON)[load_db("respon.csv", COL_RESPON)['Staf'] == st.session_state.user_role][::-1], use_container_width=True)

    with tabs[t_labels.index("⚙️ AKUN")]:
        df_p = load_db("profil.csv", COL_PROFIL); me = df_p[df_p["Jabatan"] == st.session_state.user_role]
        if not me.empty:
            c1, c2 = st.columns([0.2, 0.8])
            if me.iloc[0]["Foto_Path"] != "-": c1.image(os.path.join(UPLOAD_DIR, me.iloc[0]["Foto_Path"]), width=150)
            c2.write(f"**Nama:** {me.iloc[0]['Nama']}\n**NUPTK/NIK:** {me.iloc[0]['NUPTK']}")
        with st.form("up_stf"):
            n = st.text_input("Nama Lengkap", value=me.iloc[0]["Nama"] if not me.empty else "")
            nu = st.text_input("NUPTK/NIK", value=me.iloc[0]["NUPTK"] if not me.empty else "")
            fo = st.file_uploader("Foto"); pw = st.text_input("Password Baru", type="password")
            if st.form_submit_button("Update Akun"):
                if pw: st.session_state.users[st.session_state.user_role] = pw
                fn_f = f"foto_{st.session_state.user_role}.jpg" if fo else (me.iloc[0]["Foto_Path"] if not me.empty else "-")
                if fo:
                    with open(os.path.join(UPLOAD_DIR, fn_f), "wb") as f: f.write(fo.getbuffer())
                df_p = df_p[df_p["Jabatan"] != st.session_state.user_role]
                save_db(pd.concat([df_p, pd.DataFrame([{"Jabatan": st.session_state.user_role, "Nama": n, "NUPTK": nu, "Foto_Path": fn_f}])], ignore_index=True), "profil.csv")
                st.rerun()

if st.button("🚪 LOGOUT", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()
