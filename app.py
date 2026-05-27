import streamlit as st
import pandas as pd

# Set konfigurasi layout halaman utama web
st.set_page_config(page_title="NutriExpert CF System", layout="wide", initial_sidebar_state="expanded")

# =========================================================================
# 1. INITIALIZE DATASET & STATE (Disimpan di memori agar bisa diubah Admin)
# =========================================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Dataset Utama Gizi Makanan (Untuk Halaman 1, 2, dan 4)
if 'food_df' not in st.session_state:
    st.session_state.food_df = pd.DataFrame([
        {"Nama Makanan": "Nasi Putih", "Kalori (kcal)": 130, "Karbohidrat (g)": 28.0, "Protein (g)": 2.7, "Serat (g)": 0.4, "Vitamin C (mg)": 0.0, "Zat Besi (mg)": 1.2},
        {"Nama Makanan": "Dada Ayam", "Kalori (kcal)": 165, "Karbohidrat (g)": 0.0, "Protein (g)": 31.0, "Serat (g)": 0.0, "Vitamin C (mg)": 0.0, "Zat Besi (mg)": 1.0},
        {"Nama Makanan": "Tempe Goreng", "Kalori (kcal)": 193, "Karbohidrat (g)": 9.0, "Protein (g)": 19.0, "Serat (g)": 1.4, "Vitamin C (mg)": 0.0, "Zat Besi (mg)": 2.7},
        {"Nama Makanan": "Telur Rebus", "Kalori (kcal)": 155, "Karbohidrat (g)": 1.1, "Protein (g)": 13.0, "Serat (g)": 0.0, "Vitamin C (mg)": 0.0, "Zat Besi (mg)": 1.2},
        {"Nama Makanan": "Bayam Rebus", "Kalori (kcal)": 23, "Karbohidrat (g)": 4.0, "Protein (g)": 3.0, "Serat (g)": 2.4, "Vitamin C (mg)": 10.0, "Zat Besi (mg)": 3.5},
        {"Nama Makanan": "Jeruk", "Kalori (kcal)": 47, "Karbohidrat (g)": 12.0, "Protein (g)": 0.9, "Serat (g)": 2.4, "Vitamin C (mg)": 53.2, "Zat Besi (mg)": 0.1},
        {"Nama Makanan": "Susu Sapi", "Kalori (kcal)": 42, "Karbohidrat (g)": 5.0, "Protein (g)": 3.4, "Serat (g)": 0.0, "Vitamin C (mg)": 0.0, "Zat Besi (mg)": 0.1}
    ])

# Aturan Pakar (Rule Base) Berdasarkan Gejala Klinis (Untuk Halaman 3)
if 'rules_symptoms' not in st.session_state:
    st.session_state.rules_symptoms = pd.DataFrame([
        {"Kode": "R001", "Gejala": "Gusi Berdarah", "Diagnosis": "Kekurangan Vitamin C", "CF_Pakar": 0.8},
        {"Kode": "R002", "Gejala": "Sariawan Berulang", "Diagnosis": "Kekurangan Vitamin C", "CF_Pakar": 0.7},
        {"Kode": "R003", "Gejala": "Mudah Memar", "Diagnosis": "Kekurangan Vitamin C", "CF_Pakar": 0.5},
        {"Kode": "R004", "Gejala": "Gusi Berdarah", "Diagnosis": "Kekurangan Vitamin K", "CF_Pakar": 0.4},
        {"Kode": "R005", "Gejala": "Mata Kabur di Malam Hari", "Diagnosis": "Kekurangan Vitamin A", "CF_Pakar": 0.9},
        {"Kode": "R006", "Gejala": "Kulit Kering Bersisik", "Diagnosis": "Kekurangan Vitamin A", "CF_Pakar": 0.5},
        {"Kode": "R007", "Gejala": "Sering Pusing & Lemas", "Diagnosis": "Kekurangan Zat Besi (Anemia)", "CF_Pakar": 0.8},
        {"Kode": "R008", "Gejala": "Pucat di Kuku/Mata", "Diagnosis": "Kekurangan Zat Besi (Anemia)", "CF_Pakar": 0.75},
        {"Kode": "R009", "Gejala": "Rambut Rontok Parah", "Diagnosis": "Kekurangan Protein", "CF_Pakar": 0.6},
        {"Kode": "R010", "Gejala": "Otot Menyusut / Lemah", "Diagnosis": "Kekurangan Protein", "CF_Pakar": 0.7}
    ])

# Aturan Pakar untuk Analisis Defisit Asupan Harian (Untuk Halaman 4)
if 'rules_intake' not in st.session_state:
    st.session_state.rules_intake = pd.DataFrame([
        {"Defisit": "Kekurangan Serat > 50%", "Prediksi_Dampak": "Sembelit & Gangguan Pencernaan", "CF_Pakar": 0.85},
        {"Defisit": "Kekurangan Protein > 40%", "Prediksi_Dampak": "Katabolisme Otot & Imunitas Turun", "CF_Pakar": 0.75},
        {"Defisit": "Kekurangan Vitamin C > 50%", "Prediksi_Dampak": "Penurunan Imunitas & Sariawan", "CF_Pakar": 0.70},
        {"Defisit": "Kekurangan Zat Besi > 30%", "Prediksi_Dampak": "Mudah Lelah & Kurang Konsentrasi", "CF_Pakar": 0.65}
    ])

# Acuan Angka Kecukupan Gizi (AKG) standar harian sehat harian
AKG = {"Kalori (kcal)": 2000, "Karbohidrat (g)": 300, "Protein (g)": 60, "Serat (g)": 30, "Vitamin C (mg)": 90, "Zat Besi (mg)": 15}

# Pilihan Skala Keyakinan Gejala oleh Pengguna (CF User)
cf_options = {
    "Tidak Tahu / Tidak Merasakan": 0.0,
    "Sedikit Merasakan / Gejala Ringan": 0.4,
    "Cukup Merasakan / Gejala Sedang": 0.7,
    "Sangat Merasakan / Gejala Berat": 1.0
}

# =========================================================================
# 2. SIDEBAR NAVIGATION CONTROLLER
# =========================================================================
st.sidebar.title("🥑 NutriExpert CF")
st.sidebar.markdown("Sistem Pakar Gizi - *Certainty Factor Engine*")

menu = st.sidebar.radio("Pilih Halaman Aplikasi:", [
    "1. Ensiklopedia Gizi",
    "2. Filter Rekomendasi Makanan",
    "3. Diagnosis Gejala (CF)",
    "4. Analisis Menu Harian (CF)",
    "5. Kamus Penyakit Malnutrisi",
    "6. Panel Manajemen Pakar (Admin)"
])

# ----------------- HALAMAN 1: ENSIKLOPEDIA GIZI -----------------
if menu == "1. Ensiklopedia Gizi":
    st.title("📖 1. Ensiklopedia Data Kandungan Gizi Makanan")
    st.write("Gunakan fitur ini untuk mencari kandungan nutrisi suatu bahan pangan secara instan.")
    
    selected_food = st.selectbox("Pilih atau Ketik Nama Makanan:", st.session_state.food_df["Nama Makanan"].unique())
    food_data = st.session_state.food_df[st.session_state.food_df["Nama Makanan"] == selected_food].iloc[0]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔥 Kalori", f"{food_data['Kalori (kcal)']} kcal")
        st.metric("🍞 Karbohidrat", f"{food_data['Karbohidrat (g)']} g")
    with col2:
        st.metric("💪 Protein", f"{food_data['Protein (g)']} g")
        st.metric("🥦 Serat", f"{food_data['Serat (g)']} g")
    with col3:
        st.metric("🍊 Vitamin C", f"{food_data['Vitamin C (mg)']} mg")
        st.metric("🩸 Zat Besi", f"{food_data['Zat Besi (mg)']} mg")

    st.subheader("📋 Seluruh Tabel Dataset Gizi")
    st.dataframe(st.session_state.food_df, use_container_width=True)

# ----------------- HALAMAN 2: FILTER REKOMENDASI -----------------
elif menu == "2. Filter Rekomendasi Makanan":
    st.title("🔍 2. Rekomendasi Balik: Cari Makanan Berdasarkan Kebutuhan Nutrisi")
    st.write("Masukkan target zat gizi tertentu untuk menampilkan jenis makanan penunjang terbaik.")
    
    gizi_pilihan = st.selectbox("Saya membutuhkan makanan yang tinggi:", ["Protein (g)", "Karbohidrat (g)", "Serat (g)", "Vitamin C (mg)", "Zat Besi (mg)"])
    min_val = st.slider("Batas Minimal Kandungan Gizi per porsi:", 0.0, 60.0, 5.0)
    
    filtered_df = st.session_state.food_df[st.session_state.food_df[gizi_pilihan] >= min_val].sort_values(by=gizi_pilihan, ascending=False)
    
    if not filtered_df.empty:
        st.success(f"Berhasil menemukan {len(filtered_df)} opsi makanan yang cocok!")
        st.dataframe(filtered_df[["Nama Makanan", gizi_pilihan, "Kalori (kcal)"]], use_container_width=True)
    else:
        st.warning("Data belum ditemukan. Coba geser batas minimal kandungan gizi ke arah kiri.")

# ----------------- HALAMAN 3: DIAGNOSIS GEJALA (CF ENGINE) -----------------
elif menu == "3. Diagnosis Gejala (CF)":
    st.title("🩺 3. Sistem Pakar Diagnosa Malnutrisi Berdasarkan Gejala Tubuh")
    st.write("Centang kondisi fisik Anda dan tentukan tingkat keyakinannya untuk dihitung oleh rumus Certainty Factor.")
    
    unique_symptoms = st.session_state.rules_symptoms["Gejala"].unique()
    user_inputs = {}
    
    st.subheader("Input Kondisi Fisik")
    for symptom in unique_symptoms:
        user_inputs[symptom] = st.selectbox(f"Seberapa yakin Anda mengalami '{symptom}'?", list(cf_options.keys()), key=symptom)
        
    if st.button("Proses Diagnosa Certainty Factor", type="primary"):
        active_inputs = {sym: cf_options[val] for sym, val in user_inputs.items() if cf_options[val] > 0}
        
        if not active_inputs:
            st.warning("Mohon pilih minimal satu gejala fisik yang Anda rasakan.")
        else:
            diagnoses = st.session_state.rules_symptoms["Diagnosis"].unique()
            final_results = {}
            
            for diag in diagnoses:
                diag_rules = st.session_state.rules_symptoms[st.session_state.rules_symptoms["Diagnosis"] == diag]
                cf_list = []
                
                for _, rule in diag_rules.iterrows():
                    s_name = rule["Gejala"]
                    if s_name in active_inputs:
                        cf_user = active_inputs[s_name]
                        cf_pakar = rule["CF_Pakar"]
                        # Rumus CF Tunggal: CF[H,E] = CF[E] * CF[Pakar]
                        cf_list.append(cf_user * cf_pakar)
                
                if cf_list:
                    # Rumus Kombinasi Paralel CF Combine
                    cf_combine = cf_list[0]
                    for cf_next in cf_list[1:]:
                        if cf_combine >= 0 and cf_next >= 0:
                            cf_combine = cf_combine + cf_next * (1 - cf_combine)
                    final_results[diag] = cf_combine
            
            if final_results:
                st.subheader("📊 Hasil Kalkulasi Keyakinan Sistem Pakar")
                sorted_results = sorted(final_results.items(), key=lambda x: x[1], reverse=True)
                for diag, score in sorted_results:
                    percentage = score * 100
                    st.info(f"**{diag}** | Persentase Keyakinan: **{percentage:.2f}%**")
                    st.progress(float(max(0.0, min(score, 1.0))))
            else:
                st.info("Kombinasi gejala Anda belum mengarah ke riwayat penyakit gizi di database.")

# ----------------- HALAMAN 4: ANALISIS MENU HARIAN (CF ENGINE) -----------------
elif menu == "4. Analisis Menu Harian (CF)":
    st.title("🍽️ 4. Evaluasi & Prediksi Risiko Menu Konsumsi Harian")
    st.write("Masukkan daftar makanan yang Anda konsumsi hari ini untuk mengukur potensi defisit kritis.")
    
    selected_items = st.multiselect("Pilih seluruh menu makanan Anda sejak pagi:", st.session_state.food_df["Nama Makanan"].unique())
    
    if selected_items:
        summary_gizi = {"Kalori (kcal)": 0.0, "Karbohidrat (g)": 0.0, "Protein (g)": 0.0, "Serat (g)": 0.0, "Vitamin C (mg)": 0.0, "Zat Besi (mg)": 0.0}
        
        for item in selected_items:
            row = st.session_state.food_df[st.session_state.food_df["Nama Makanan"] == item].iloc[0]
            for key in summary_gizi.keys():
                summary_gizi[key] += row[key]
                
        st.subheader("Total Asupan Nutrisi Masuk")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔥 Kalori", f"{summary_gizi['Kalori (kcal)']:.1f} / {AKG['Kalori (kcal)']} kcal")
            st.metric("🍞 Karbohidrat", f"{summary_gizi['Karbohidrat (g)']:.1f} / {AKG['Karbohidrat (g)']} g")
        with col2:
            st.metric("💪 Protein", f"{summary_gizi['Protein (g)']:.1f} / {AKG['Protein (g)']} g")
            st.metric("🥦 Serat", f"{summary_gizi['Serat (g)']:.1f} / {AKG['Serat (g)']} g")
        with col3:
            st.metric("🍊 Vitamin C", f"{summary_gizi['Vitamin C (mg)']:.1f} / {AKG['Vitamin C (mg)']} mg")
            st.metric("🩸 Zat Besi", f"{summary_gizi['Zat Besi (mg)']:.1f} / {AKG['Zat Besi (mg)']} mg")
            
        # Mengonversi besaran nilai defisit menjadi CF User (Skala 0 sampai 1)
        cf_user_deficits = {}
        
        pct_serat = summary_gizi["Serat (g)"] / AKG["Serat (g)"]
        if pct_serat < 0.5:
            cf_user_deficits["Kekurangan Serat > 50%"] = 1.0 - pct_serat
            
        pct_protein = summary_gizi["Protein (g)"] / AKG["Protein (g)"]
        if pct_protein < 0.6:
            cf_user_deficits["Kekurangan Protein > 40%"] = 1.0 - pct_protein
            
        pct_vit_c = summary_gizi["Vitamin C (mg)"] / AKG["Vitamin C (mg)"]
        if pct_vit_c < 0.5:
            cf_user_deficits["Kekurangan Vitamin C > 50%"] = 1.0 - pct_vit_c
            
        pct_iron = summary_gizi["Zat Besi (mg)"] / AKG["Zat Besi (mg)"]
        if pct_iron < 0.7:
            cf_user_deficits["Kekurangan Zat Besi > 30%"] = 1.0 - pct_iron
            
        st.subheader("🔮 Prediksi Dampak Kesehatan Masa Depan")
        if not cf_user_deficits:
            st.success("Sempurna! Asupan makanan hari ini aman dan memenuhi ambang batas aman gizi.")
        else:
            predictions = []
            for _, rule in st.session_state.rules_intake.iterrows():
                def_cond = rule["Defisit"]
                if def_cond in cf_user_deficits:
                    cf_u = cf_user_deficits[def_cond]
                    cf_p = rule["CF_Pakar"]
                    predictions.append((rule["Prediksi_Dampak"], cf_u * cf_p))
                    
            for dampak, score in sorted(predictions, key=lambda x: x[1], reverse=True):
                st.warning(f"Risiko {dampak} | Kemungkinan Terjadi: {score*100:.2f}%")

# ----------------- HALAMAN 5: KAMUS PENYAKIT MALNUTRISI (DARURAT) -----------------
elif menu == "5. Kamus Penyakit Malnutrisi":
    st.title("📚 5. Kamus Penyakit Akibat Malnutrisi (Katalog Edukasi)")
    st.write("Daftar katalog medis komprehensif jika pengguna membutuhkan informasi penyakit akibat kekurangan gizi harian secara instan.")
    
    kamus_data = [
        {"Penyakit": "Skorbut (Scurvy)", "Penyebab": "Defisit Vitamin C Kronis dalam jangka panjang", "Gejala Umum": "Gusi berdarah parah, memar spontan, penyembuhan luka sangat lambat.", "Pencegahan Makanan": "Buah jeruk, jambu biji, stroberi, paprika harian."},
        {"Penyakit": "Anemia Defisiensi Besi", "Penyebab": "Kekurangan Zat Besi pengikat hemoglobin darah", "Gejala Umum": "Letih berkepanjangan, wajah pucat, konsentrasi menurun drastic.", "Pencegahan Makanan": "Daging merah, hati sapi/ayam, sayur bayam, kacang merah."},
        {"Penyakit": "Xerophthalmia", "Penyebab": "Defisit akut Vitamin A hewani/nabati", "Gejala Umum": "Rabun ayam saat petang hari, mata kering ekstrem, bercak bitot kornea.", "Pencegahan Makanan": "Wortel, ubi jalar jepang, minyak hati ikan kod, kuning telur."},
        {"Penyakit": "Kwashiorkor & Marasmus", "Penyebab": "Kekurangan asupan Protein makro dan Kalori ekstrem", "Gejala Umum": "Otot atrofi (habis), penumpukan cairan perut busung, rambut memerah rapuh.", "Pencegahan Makanan": "Dada ayam filat, susu sapi murni, ikan kembung, tahu tempe telur."},
        {"Penyakit": "Konstipasi Kronis", "Penyebab": "Kekurangan serat selulosa tumbuhan dan air", "Gejala Umum": "Sakit perut bagian bawah, buang air besar keras kurang dari 3x seminggu.", "Pencegahan Makanan": "Buah pepaya masak, oatmeal gandum utuh, biji chia, sayur hijau."}
    ]
    
    for penyakit in kamus_data:
        with st.expander(f"🔴 {penyakit['Penyakit']} (Akibat {penyakit['Penyebab']})"):
            st.write(f"Gejala Utama Fisik: {penyakit['Gejala Umum']}")
            st.write(f"Bahan Pangan Pemulihan: {penyakit['Pencegahan Makanan']}")

# ----------------- HALAMAN 6: PANEL ADMIN (MANAJEMEN PAKAR) -----------------
elif menu == "6. Panel Manajemen Pakar (Admin)":
    st.title("🛠️ 6. Panel Manajemen Aturan Pakar (Autentikasi Admin)")
    
    if not st.session_state.logged_in:
        st.subheader("Silakan Login Terlebih Dahulu")
        username = st.text_input("Username Admin:")
        password = st.text_input("Password Admin:", type="password")
        
        if st.button("Masuk Ke Panel Kendali"):
            # Kredensial default aman akun admin
            if username == "admin" and password == "pakar123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Kombinasi Username atau Password salah!")
    else:
        st.success("🔓 Anda berhasil masuk sebagai Pakar/Admin Sistem!")
        if st.button("Keluar / Logout Admin"):
            st.session_state.logged_in = False
            st.rerun()
            
        st.divider()
        st.subheader("✏️ Ubah Bobot Persentase CF Pakar (Modul Gejala - Halaman 3)")
        st.caption("Double klik pada kolom 'CF_Pakar' untuk mengubah angka keyakinan medis (rentang 0.0 s.d 1.0).")
        
        # Fitur st.data_editor membuat dataset DataFrame dapat diedit langsung layaknya excel spreadsheet
        edited_symptoms = st.data_editor(st.session_state.rules_symptoms, num_rows="dynamic", key="editor_sym")
        
        st.subheader("✏️ Ubah Bobot Persentase CF Pakar (Modul Defisit Makan - Halaman 4)")
        edited_intake = st.data_editor(st.session_state.rules_intake, num_rows="dynamic", key="editor_int")
        
        if st.button("Simpan Perubahan Aturan Pakar ke Sistem", type="primary"):
            st.session_state.rules_symptoms = edited_symptoms
            st.session_state.rules_intake = edited_intake
            st.success("✅ Sukses! Seluruh basis aturan pakar berhasil di-update ke dalam memori aplikasi.")
