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
        font-family: 'Courier New', monospace; color: #ffc107; background-color: #000; font-size: 2.5em; 
        font-weight: bold; text-align: center; border: 3px solid #ffc107; border-radius: 12px; 
        padding: 5px 20px; margin: 10px auto; display: inline-block; box-shadow: 0px 0px 15px #ffc107;
    }
    .welcome-msg { text-align: center; font-size: 1.5em; font-weight: bold; color: #2e7d32; margin-top: 10px; }
    .ibadah-msg { text-align: center; color: #ffffff; background-color: #d32f2f; padding: 15px; border-radius: 10px; font-weight: bold; margin-bottom: 20px; border: 2px solid #ffc107; }
    .running-text { background-color: #ffc107; color: #000; padding: 10px; font-weight: bold; border-radius: 5px; margin: 20px 0; font-size: 1.1em; }
    
    @keyframes blink {
        0% { background-color: #d32f2f; }
        50% { background-color: #ffc107; }
        100% { background-color: #d32f2f; }
    }
    .blink-box {
        padding: 15px; color: black; font-weight: bold; text-align: center; 
        border-radius: 10px; animation: blink 1.2s infinite; font-size: 1.3em; 
        margin-bottom: 20px; border: 2px solid #000;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. SINKRONISASI WAKTU WIB
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
        try:
            df = pd.read_csv(p)
            for c in cols:
                if c not in df.columns: df[c] = "-"
            return df
        except: return pd.DataFrame(columns=cols)
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
        "Dokumentasi & Publikasi": "dokpub123", "Operator Sekolah": "ops123", "ADMIN UTAMA": "admin789"
    }

if "logged_in" not in st.session_state: st.session_state.logged_in = False

# State untuk melacak notifikasi
if "last_seen_ins" not in st.session_state: 
    st.session_state.last_seen_ins = datetime.min.replace(tzinfo=tz_jkt)

# ==========================================
# 4. LOGIN SYSTEM
# ==========================================
st.markdown('<h1 class="headline">SISTEM KENDALI SMK NASIONAL BANDUNG</h1>', unsafe_allow_html=True)

if not st.session_state.logged_in:
    st.markdown('<div class="ibadah-msg">"Awali setiap pekerjaan dengan selalu berniat untuk Ibadah kepada Allah SWT agar setiap langkah menjadi berkah."</div>', unsafe_allow_html=True)
    _, mid_logo, _ = st.columns([1, 0.3, 1])
    with mid_logo:
        if os.path.exists("logo_smk.png"): st.image("logo_smk.png", use_container_width=True)
    
    _, l_col, _ = st.columns([1, 0.4, 1])
    with l_col:
        with st.form("login"):
            u = st.selectbox("Pilih Jabatan", list(st.session_state.users.keys()))
            p = st.text_input("Password", type="password")
            if st.form_submit_button("MASUK", use_container_width=True):
                if p == st.session_state.users[u]: 
                    st.session_state.logged_in = True
                    st.session_state.user_role = u
                    st.rerun()
                else: st.error("Akses Ditolak!")
    st.stop()

# Header Dashboard
st.markdown(f"""<div class="running-text"><marquee scrollamount="10">Pekerjaan Memang Penting Tapi Sholat Yang Utama!</marquee></div>""", unsafe_allow_html=True)
st.markdown(f'<div style="text-align:center;"><div class="digital-clock">{jam_digital}</div></div>', unsafe_allow_html=True)
st.markdown(f'<div class="welcome-msg">Selamat Datang, {st.session_state.user_role}</div>', unsafe_allow_html=True)

# ==========================================
# 5. DASHBOARD KEPSEK / ADMIN
# ==========================================
if st.session_state.user_role in ["Kepala Sekolah", "ADMIN UTAMA"]:
    t1, t2, t3, t4, t5, t6, t7 = st.tabs(["🎥 MONITORING", "✍️ INSTRUKSI", "📋 DAFTAR INSTRUKSI", "📂 ARSIP JAWABAN", "💰 CASHFLOW", "📚 RIWAYAT", "⚙️ PANEL ADMIN"])
    
    with t1: st.dataframe(load_db("monitor.csv", COL_MONITOR)[::-1], use_container_width=True)
    with t2:
        with st.form("ins"):
            target = st.multiselect("Tujukan Ke:", list(st.session_state.users.keys()))
            msg = st.text_area("Isi Instruksi")
            f = st.file_uploader("Lampiran File")
            if st.form_submit_button("KIRIM INSTRUKSI"):
                fn = f.name if f else "-"
                if f:
                    with open(os.path.join(UPLOAD_DIR, f.name), "wb") as fl: fl.write(f.getbuffer())
                save_db(pd.concat([load_db("instruksi.csv", COL_INS), pd.DataFrame([{"Jam": waktu_tabel, "Target": str(target), "Pesan": msg, "File_Instruksi": fn, "Status": "Terkirim"}])], ignore_index=True), "instruksi.csv")
                st.success("Instruksi Berhasil Disiarkan!")

    with t3: 
        st.dataframe(load_db("instruksi.csv", COL_INS)[::-1], use_container_width=True)
        if st.button("Hapus Riwayat Instruksi"):
            save_db(pd.DataFrame(columns=COL_INS), "instruksi.csv"); st.rerun()

    with t4: st.dataframe(load_db("respon.csv", COL_RESPON)[::-1], use_container_width=True)
    with t5:
        st.write("### Rekap Kas Sekolah"); st.dataframe(load_db("kas_sekolah.csv", COL_KAS)[::-1], use_container_width=True)
        st.write("### Rekap Kas BOS"); st.dataframe(load_db("kas_bos.csv", COL_KAS)[::-1], use_container_width=True)
    with t6: st.dataframe(load_db("monitor.csv", COL_MONITOR)[::-1], use_container_width=True)
    
    with t7:
        st.subheader("🛠️ Manajemen Akun & Profil")
        c_add, c_res = st.columns(2)
        with c_add:
            with st.container(border=True):
                st.write("➕ **Tambah Akun Baru**")
                n_j = st.text_input("Nama Jabatan")
                n_p = st.text_input("Password", type="password", key="new_p")
                if st.button("Daftarkan Akun"):
                    st.session_state.users[n_j] = n_p
                    st.success(f"Akun {n_j} Aktif!"); st.rerun()
        with c_res:
            with st.container(border=True):
                st.write("🔄 **Reset Password Staf**")
                u_sel = st.selectbox("Pilih Staf", list(st.session_state.users.keys()))
                p_new = st.text_input("Password Baru", type="password", key="res_p")
                if st.button("Update Password"):
                    st.session_state.users[u_sel] = p_new
                    st.success("Berhasil!"); st.rerun()
        
        st.write("---")
        df_p = load_db("profil.csv", COL_PROFIL); me = df_p[df_p["Jabatan"] == st.session_state.user_role]
        with st.form("up_adm"):
            st.write("👤 **Profil & Password Pribadi**")
            n = st.text_input("Nama", value=me.iloc[0]["Nama"] if not me.empty else "")
            nu = st.text_input("NUPTK/NIK", value=me.iloc[0]["NUPTK"] if not me.empty else "")
            fo = st.file_uploader("Ganti Foto")
            pw_pribadi = st.text_input("Ganti Password Saya", type="password")
            if st.form_submit_button("Simpan Perubahan"):
                if pw_pribadi: st.session_state.users[st.session_state.user_role] = pw_pribadi
                fn_f = f"foto_{st.session_state.user_role}.jpg" if fo else (me.iloc[0]["Foto_Path"] if not me.empty else "-")
                if fo:
                    with open(os.path.join(UPLOAD_DIR, fn_f), "wb") as f: f.write(fo.getbuffer())
                df_p = df_p[df_p["Jabatan"] != st.session_state.user_role]
                save_db(pd.concat([df_p, pd.DataFrame([{"Jabatan": st.session_state.user_role, "Nama": n, "NUPTK": nu, "Foto_Path": fn_f}])], ignore_index=True), "profil.csv")
                st.rerun()

# ==========================================
# 6. DASHBOARD STAF / OPERATOR / BENDAHARA
# ==========================================
else:
    df_i = load_db("instruksi.csv", COL_INS)
    mask = df_i['Target'].str.contains(st.session_state.user_role, na=False, case=False)
    my_instructions = df_i[mask].copy()

    # LOGIKA CEK PESAN BARU
    show_blink = False
    if not my_instructions.empty:
        my_instructions['dt'] = pd.to_datetime(my_instructions['Jam'], format="%d/%m/%Y %H:%M:%S").dt.tz_localize('Asia/Jakarta')
        waktu_terbaru = my_instructions['dt'].max()
        # Jika ada instruksi yang lebih baru dari waktu terakhir user "melihat" tab
        if waktu_terbaru > st.session_state.last_seen_ins:
            show_blink = True
    
    if show_blink:
        st.markdown(f'<div class="blink-box">⚠️ PERHATIAN: ADA INSTRUKSI BARU DARI KEPSEK!</div>', unsafe_allow_html=True)

    is_bendahara = "Bendahara" in st.session_state.user_role
    t_labels = ["📝 CATATAN HARIAN", "🔔 INSTRUKSI KEPSEK", "📂 ARSIP SAYA", "⚙️ AKUN & PRIVASI"]
    if is_bendahara: t_labels.insert(0, "💰 INPUT KAS")
    
    # Deteksi perubahan tab menggunakan session_state
    tabs = st.tabs(t_labels)

    if is_bendahara:
        with tabs[0]:
            db_f = "kas_bos.csv" if "BOS" in st.session_state.user_role else "kas_sekolah.csv"
            df_k = load_db(db_f, COL_KAS)
            st.metric("SALDO", f"Rp {pd.to_numeric(df_k['Masuk'], errors='coerce').sum() - pd.to_numeric(df_k['Keluar'], errors='coerce').sum():,.0f}")
            with st.form("kas"):
                c1, c2 = st.columns(2)
                src = c1.text_input("Sumber Dana"); unt = c1.text_input("Peruntukan")
                pj = c2.text_input("PJ"); ket = c2.text_area("Keterangan")
                m = c1.number_input("Masuk", min_value=0); k = c2.number_input("Keluar", min_value=0)
                if st.form_submit_button("SIMPAN"):
                    save_db(pd.concat([df_k, pd.DataFrame([{"Jam": waktu_tabel, "Staf": st.session_state.user_role, "Sumber_Dana": src, "Peruntukan": unt, "PJ_Pengguna": pj, "Keterangan": ket, "Masuk": m, "Keluar": k}])], ignore_index=True), db_f)
                    st.rerun()

    with tabs[t_labels.index("📝 CATATAN HARIAN")]:
        with st.form("h"):
            akt = st.text_area("Aktivitas Pekerjaan"); f_h = st.file_uploader("Bukti")
            if st.form_submit_button("Simpan Laporan"):
                fn_h = f_h.name if f_h else "-"
                if f_h:
                    with open(os.path.join(UPLOAD_DIR, f_h.name), "wb") as fl: fl.write(f_h.getbuffer())
                save_db(pd.concat([load_db("monitor.csv", COL_MONITOR), pd.DataFrame([{"Jam": waktu_tabel, "Staf": st.session_state.user_role, "Aktivitas": akt, "Lampiran_File": fn_h}])], ignore_index=True), "monitor.csv")
                st.success("Laporan Terkirim!"); st.rerun()

    with tabs[t_labels.index("🔔 INSTRUKSI KEPSEK")]:
        # UPDATE: Paksa update waktu 'last_seen' dan refresh jika sebelumnya statusnya 'show_blink'
        if show_blink:
            st.session_state.last_seen_ins = waktu_sekarang
            st.rerun() # Ini akan menghilangkan kotak merah seketika
        
        if my_instructions.empty:
            st.info("Belum ada instruksi baru.")
        else:
            for i, r in my_instructions[::-1].iterrows():
                with st.expander(f"📌 INSTRUKSI {r['Jam']}", expanded=True):
                    st.error(f"PESAN: {r['Pesan']}")
                    if r['File_Instruksi'] != "-": st.write(f"📁 File: {r['File_Instruksi']}")
                    with st.form(f"res_{i}"):
                        res = st.text_area("Hasil Pekerjaan"); f_res = st.file_uploader("Upload Hasil", key=f"f_{i}")
                        if st.form_submit_button("Kirim Jawaban"):
                            fn_res = f_res.name if f_res else "-"
                            if f_res:
                                with open(os.path.join(UPLOAD_DIR, f_res.name), "wb") as fl: fl.write(f_res.getbuffer())
                            save_db(pd.concat([load_db("respon.csv", COL_RESPON), pd.DataFrame([{"Jam": waktu_tabel, "Staf": st.session_state.user_role, "Hasil": res, "Lampiran_Hasil": fn_res}])], ignore_index=True), "respon.csv")
                            st.success("Terkirim!"); st.rerun()

    with tabs[t_labels.index("⚙️ AKUN & PRIVASI")]:
        df_p = load_db("profil.csv", COL_PROFIL); me = df_p[df_p["Jabatan"] == st.session_state.user_role]
        with st.form("up_stf"):
            st.write("🔒 **Ubah Profil & Password Login**")
            n = st.text_input("Nama", value=me.iloc[0]["Nama"] if not me.empty else "")
            nu = st.text_input("NUPTK/NIK", value=me.iloc[0]["NUPTK"] if not me.empty else "")
            fo = st.file_uploader("Foto"); pw = st.text_input("Ganti Password Login", type="password")
            if st.form_submit_button("Simpan Perubahan"):
                if pw: st.session_state.users[st.session_state.user_role] = pw
                fn_f = f"foto_{st.session_state.user_role}.jpg" if fo else (me.iloc[0]["Foto_Path"] if not me.empty else "-")
                if fo:
                    with open(os.path.join(UPLOAD_DIR, fn_f), "wb") as f: f.write(fo.getbuffer())
                df_p = df_p[df_p["Jabatan"] != st.session_state.user_role]
                save_db(pd.concat([df_p, pd.DataFrame([{"Jabatan": st.session_state.user_role, "Nama": n, "NUPTK": nu, "Foto_Path": fn_f}])], ignore_index=True), "profil.csv")
                st.success("Tersimpan!"); st.rerun()

if st.button("🚪 LOGOUT", use_container_width=True):
    st.session_state.logged_in = False; st.rerun()
