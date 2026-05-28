import streamlit as st
import pandas as pd
import numpy as np
import re  # Untuk membersihkan teks/angka nyasar

# Set konfigurasi layout
st.set_page_config(page_title="NutrisiAnak", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
    .stButton>button { border-radius: 20px; transition: all 0.3s; }
    .stButton>button:hover { transform: scale(1.05); box-shadow: 0px 4px 10px rgba(0,0,0,0.1); }
    [data-testid="stMetricValue"] { color: #27ae60; font-weight: bold; }
    
    /* Style untuk kartu di Beranda */
    .feature-card {
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        background-color: #f9f9f9;
        margin-bottom: 20px;
        transition: 0.3s;
    }
    .feature-card:hover {
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        border-color: #27ae60;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================================
# 1. INITIALIZE DATASETS & STATE
# =========================================================================

@st.cache_data
def load_nutrition_standards():
    try:
        df = pd.read_csv("standard-nutrition.csv")
        # Membersihkan angka nyasar di awal nama nutrisi (misal "18 Phosphorus" jadi "Phosphorus")
        if 'Nutrisi' in df.columns:
            df['Nutrisi'] = df['Nutrisi'].astype(str).apply(lambda x: re.sub(r'^\d+\s*', '', x))
        return df
    except FileNotFoundError:
        st.error("File 'standard-nutrition.csv' tidak ditemukan.")
        return pd.DataFrame()

@st.cache_data
def load_food_data():
    try:
        df = pd.read_csv("foods.csv")
        # Rename kolom Menu ke Nama Makanan
        if "Menu" in df.columns:
            df.rename(columns={"Menu": "Nama Makanan"}, inplace=True)
            
        # Menghapus kolom "ID" atau "Unnamed: 0" agar tidak muncul di pilihan gizi
        kolom_sampah = [col for col in ["ID", "Unnamed: 0", "id"] if col in df.columns]
        if kolom_sampah:
            df.drop(columns=kolom_sampah, inplace=True)
            
        df.fillna(0, inplace=True)
        return df
    except FileNotFoundError:
        st.error("File 'foods.csv' tidak ditemukan.")
        return pd.DataFrame()

std_nutrition_df = load_nutrition_standards()
foods_data_df = load_food_data()

# Inisialisasi Session State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'cf_pakar_prediksi' not in st.session_state:
    st.session_state.cf_pakar_prediksi = 0.85  # Default bobot prediksi penyakit

if 'food_df' not in st.session_state:
    st.session_state.food_df = foods_data_df if not foods_data_df.empty else pd.DataFrame([{"Nama Makanan": "Kosong", "Energy (kJ)": 0, "Protein (g)": 0}])

# --- STATE BARU (Auto-Generate dari CSV untuk Dual Diagnosis) ---
if 'rules_symptoms_new' not in st.session_state:
    auto_rules = []
    rule_idx = 1
    if not std_nutrition_df.empty:
        for _, row in std_nutrition_df.iterrows():
            nutrisi = str(row['Nutrisi']).split(" (")[0]
            
            if pd.notna(row['Dampak Kekurangan']) and str(row['Dampak Kekurangan']).lower() != "nan":
                for g in str(row['Dampak Kekurangan']).split(','):
                    if g.strip():
                        auto_rules.append({"Kode": f"RN{rule_idx:03d}", "Gejala": g.strip().capitalize(), "Diagnosis": f"Kekurangan {nutrisi}", "Tipe": "Defisit", "CF_Pakar": 0.6})
                        rule_idx += 1
                        
            if pd.notna(row['Dampak Kelebihan']) and str(row['Dampak Kelebihan']).lower() != "nan":
                for g in str(row['Dampak Kelebihan']).split(','):
                    if g.strip():
                        auto_rules.append({"Kode": f"RN{rule_idx:03d}", "Gejala": g.strip().capitalize(), "Diagnosis": f"Kelebihan {nutrisi}", "Tipe": "Ekses", "CF_Pakar": 0.6})
                        rule_idx += 1
                        
        st.session_state.rules_symptoms_new = pd.DataFrame(auto_rules)
    else:
        st.session_state.rules_symptoms_new = pd.DataFrame(columns=["Kode", "Gejala", "Diagnosis", "Tipe", "CF_Pakar"])

# Setup Batasan Minimum dan Maksimum Harian
AKG_MIN = {}
AKG_MAX = {}
if not std_nutrition_df.empty:
    for index, row in std_nutrition_df.iterrows():
        nutrisi = row['Nutrisi']
        if pd.notna(row['Minimum']): AKG_MIN[nutrisi] = float(row['Minimum'])
        if pd.notna(row['Maximum']): AKG_MAX[nutrisi] = float(row['Maximum'])

# Fallback AKG jika file kosong
if not AKG_MIN:
    AKG_MIN = {"Protein (g)": 13.0, "Dietary Fiber (g)": 14.0, "Vitamin C (mg)": 15.0, "Iron (mg)": 7.0}

cf_options = {"Tidak Merasakan": 0.0, "Gejala Ringan": 0.4, "Gejala Sedang": 0.7, "Gejala Parah": 1.0}

# Ekstrak daftar nutrisi murni (hanya kolom angka)
available_nutrients = [col for col in st.session_state.food_df.columns if pd.api.types.is_numeric_dtype(st.session_state.food_df[col])]


# =========================================================================
# 2. SIDEBAR NAVIGATION
# =========================================================================
if 'menu_utama' not in st.session_state:
    st.session_state.menu_utama = "Beranda"

menu = st.sidebar.radio("", [
    "Beranda",
    "Ensiklopedia Gizi",
    "Rekomendasi Makanan",
    "Analisis Asupan Harian",
    "Pemulihan Gizi",
    "Dual-Diagnosis",
    "Prediksi Penyakit",
    "Panel Admin",
    "Tentang Aplikasi"
], key="menu_utama")

if st.session_state.menu_utama == "Beranda":
    st.title("Selamat Datang di NutrisiAnak")
    st.markdown("Sistem Pakar Gizi Berbasis *Certainty Factor* (CF)")
    st.write("NutrisiAnak adalah sistem cerdas yang membantu Anda menganalisis asupan gizi, merekomendasikan makanan, hingga mendiagnosa potensi masalah kesehatan akibat kekurangan atau kelebihan nutrisi.")
    st.divider()
    
    st.markdown("Jelajahi Fitur Kami:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3 style="text-align: center;">Ensiklopedia & Asupan</h3>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ensiklopedia Gizi", use_container_width=True, help="Cari tahu kandungan detail dari ratusan jenis bahan makanan."):
            st.session_state.menu_utama = "Ensiklopedia Gizi"
            st.rerun()
        if st.button("Analisis Asupan Harian", use_container_width=True, help="Masukkan makanan Anda hari ini dan lihat apakah sudah memenuhi standar AKG."):
            st.session_state.menu_utama = "Analisis Asupan Harian"
            st.rerun()

    with col2: 
        st.markdown("""
        <div class="feature-card">
            <h3 style="text-align: center;">Rekomendasi & Pemulihan</h3>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Rekomendasi Makanan", use_container_width=True, help="Temukan makanan terbaik untuk memenuhi target gizi tertentu."):
            st.session_state.menu_utama = "Rekomendasi Makanan"
            st.rerun()
        if st.button("Pemulihan Gizi (CF)", use_container_width=True, help="Hitung kepastian (persentase CF) suatu makanan dalam menutupi defisit gizi Anda."):
            st.session_state.menu_utama = "Pemulihan Gizi"
            st.rerun()

    with col3: 
        st.markdown("""
        <div class="feature-card">
            <h3 style="text-align: center;">Diagnosis Sistem Pakar</h3>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Dual-Diagnosis (CF)", use_container_width=True, help="Masukkan keluhan fisik Anda, dan sistem akan menebak kekurangan atau keracunan gizi."):
            st.session_state.menu_utama = "Dual-Diagnosis"
            st.rerun()
        if st.button("Prediksi Penyakit (CF)", use_container_width=True, help="AI memprediksi risiko penyakit esok hari berdasarkan asupan makanan Anda hari ini."):
            st.session_state.menu_utama = "Prediksi Penyakit"
            st.rerun()

# ----------------- HALAMAN 1: ENSIKLOPEDIA (LAMA) -----------------
elif menu == "Ensiklopedia Gizi":
    st.title("Ensiklopedia Data Kandungan Gizi")
    st.write(f"Database murni berisi **{len(st.session_state.food_df)} bahan pangan.**")
    selected_food = st.selectbox("Pilih Nama Makanan:", st.session_state.food_df["Nama Makanan"].unique())
    food_data = st.session_state.food_df[st.session_state.food_df["Nama Makanan"] == selected_food].iloc[0]
    
    col1, col2, col3 = st.columns(3)
    
    st.subheader("Kandungan Gizi Utama")
    col1.metric("Energi", f"{food_data.get('Energy (kJ)', 0)} kJ")
    col1.metric("Karbohidrat", f"{food_data.get('Carbohydrates (g)', 0)} g")
    col2.metric("Protein", f"{food_data.get('Protein (g)', 0)} g")
    col2.metric("Serat", f"{food_data.get('Dietary Fiber (g)', 0)} g")
    col3.metric("Vitamin C", f"{food_data.get('Vitamin C (mg)', 0)} mg")
    col3.metric("Zat Besi", f"{food_data.get('Iron (mg)', 0)} mg")
    st.dataframe(st.session_state.food_df, use_container_width=True)

# ----------------- HALAMAN 2: REKOMENDASI (LAMA) -----------------
elif menu == "Rekomendasi Makanan":
    st.title("Rekomendasi Makanan")
    
    if not available_nutrients:
        st.warning("Tidak ada data nutrisi yang tersedia.")
    else:
        gizi_pilihan = st.selectbox("Nutrisi yang ingin dipenuhi:", available_nutrients, index=0)
        target_akg = AKG_MIN.get(gizi_pilihan, 10.0)
        st.info(f"Target minimal harian untuk **{gizi_pilihan}** adalah **{target_akg}**.")

        if st.button("Hitung Rekomendasi"):
            recommendations = []
            for _, row in st.session_state.food_df.iterrows():
                nilai_gizi = float(row.get(gizi_pilihan, 0))
                if nilai_gizi > 0:
                    cf_score = min(nilai_gizi / target_akg, 1.0) 
                    if cf_score >= 0.1:
                        recommendations.append({
                            "Nama Makanan": row["Nama Makanan"],
                            f"Kandungan": nilai_gizi,
                            "Skor": cf_score,
                            "Keyakinan Sistem": f"{cf_score * 100:.2f} %"
                        })
            if recommendations:
                rec_df = pd.DataFrame(recommendations).sort_values(by="Skor", ascending=False).head(20)
                st.success(f"Ditemukan {len(recommendations)} makanan penunjang. Berikut Top 20 Makanan Terbaik:")
                st.dataframe(rec_df[["Nama Makanan", "Kandungan", "Keyakinan Sistem"]], use_container_width=True)
            else:
                st.warning("Tidak ada makanan yang memenuhi syarat.")

# ----------------- HALAMAN 4: ANALISIS ASUPAN (REVISI) -----------------
elif menu == "Analisis Asupan Harian":
    st.title("Evaluasi Asupan Harian")
    st.write("Sistem dengan indikator batas minimum dan maksimum gizi harian.")
    
    selected_items = st.multiselect("Pilih daftar menu makanan Anda hari ini:", st.session_state.food_df["Nama Makanan"].unique())
    if selected_items:
        summary_gizi = {nut: 0.0 for nut in available_nutrients}
        for item in selected_items:
            row = st.session_state.food_df[st.session_state.food_df["Nama Makanan"] == item].iloc[0]
            for key in summary_gizi.keys(): summary_gizi[key] += float(row.get(key, 0))
            
        st.divider()
        st.subheader("Indikator Batas Konsumsi Harian")
        nutrisi_utama = ["Energy (kJ)", "Protein (g)", "Dietary Fiber (g)", "Vitamin C (mg)", "Iron (mg)"]
        
        for nutrisi in nutrisi_utama:
            if nutrisi in summary_gizi:
                asupan = summary_gizi[nutrisi]
                batas_min = AKG_MIN.get(nutrisi, 1.0)
                batas_max = AKG_MAX.get(nutrisi, None)
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.write(f"**{nutrisi.split(' (')[0]}**")
                    st.write(f"Asupan: {asupan:.1f}")
                with col2:
                    if asupan < batas_min:
                        st.warning(f"Kekurangan (Minimal: {batas_min})")
                        st.progress(float(max(0.0, min(asupan/batas_min, 1.0))))
                    elif batas_max and asupan > batas_max:
                        st.error(f"Berlebih! (Maksimal: {batas_max})")
                        st.progress(1.0)
                    else:
                        st.success(f"Ideal (Sesuai Standar)")
                        st.progress(1.0)
                st.markdown("---")

# ----------------- HALAMAN 5: CF PEMULIHAN GIZI (BARU 1) -----------------
elif menu == "Pemulihan Gizi":
    st.title("Pemulihan Makanan")
    st.write("Menghitung kepastian suatu makanan mampu **menyembuhkan defisit gizi spesifik** Anda.")
    
    if not available_nutrients:
        st.warning("Tidak ada data nutrisi yang tersedia.")
    else:
        gizi_pilihan = st.selectbox("Saya sedang kekurangan gizi:", available_nutrients, index=0)
        target_akg = AKG_MIN.get(gizi_pilihan, 10.0)
        defisit_user = st.number_input(f"Berapa banyak defisit {gizi_pilihan} yang ingin ditutupi?", value=float(target_akg))

        if st.button("Cari Obat Alami"):
            recommendations = []
            for _, row in st.session_state.food_df.iterrows():
                nilai_gizi = float(row.get(gizi_pilihan, 0))
                if nilai_gizi > 0 and defisit_user > 0:
                    cf_score = min(nilai_gizi / defisit_user, 1.0) 
                    if cf_score >= 0.1:
                        recommendations.append({
                            "Nama Makanan": row["Nama Makanan"],
                            f"Kandungan Makanan": f"{nilai_gizi:.1f}",
                            "Kepastian Memulihkan": cf_score
                        })
            if recommendations:
                rec_df = pd.DataFrame(recommendations).sort_values(by="Kepastian Memulihkan", ascending=False).head(15)
                rec_df["Kepastian Memulihkan"] = rec_df["Kepastian Memulihkan"].apply(lambda x: f"{x * 100:.1f} %")
                st.success("Tabel Makanan Pemulih Terbaik:")
                st.dataframe(rec_df, use_container_width=True)

# ----------------- HALAMAN 6: DUAL DIAGNOSIS (BARU 2) -----------------
elif menu == "Dual-Diagnosis":
    st.title("Diagnosis Medis")
    st.write("Masukan gejala Anda untuk mendiagnosa apakah Anda mengalami **Kekurangan Gizi** atau **Keracunan (Kelebihan) Gizi**.")
    
    unique_symptoms = st.session_state.rules_symptoms_new["Gejala"].unique()
    selected_symptoms = st.multiselect("Pilih semua keluhan yang dialami:", options=unique_symptoms)
    
    if selected_symptoms:
        user_inputs = {}
        valid_cf_options = {k: v for k, v in cf_options.items() if v > 0.0}
        for symptom in selected_symptoms:
            user_inputs[symptom] = st.radio(f"Parahnya '{symptom}'?", list(valid_cf_options.keys()), key=symptom, horizontal=True)
            
        if st.button("Proses Dual Diagnosis"):
            active_inputs = {sym: valid_cf_options[val] for sym, val in user_inputs.items()}
            diagnoses = st.session_state.rules_symptoms_new["Diagnosis"].unique()
            final_results = {}
            for diag in diagnoses:
                diag_rules = st.session_state.rules_symptoms_new[st.session_state.rules_symptoms_new["Diagnosis"] == diag]
                cf_list = [active_inputs[r["Gejala"]] * r["CF_Pakar"] for _, r in diag_rules.iterrows() if r["Gejala"] in active_inputs]
                if cf_list:
                    cf_combine = cf_list[0]
                    for cf_next in cf_list[1:]:
                        cf_combine = cf_combine + cf_next * (1 - cf_combine)
                    if cf_combine > 0.0: final_results[diag] = cf_combine
            
            if final_results:
                st.divider()
                sorted_results = sorted(final_results.items(), key=lambda x: x[1], reverse=True)
                top_diag, top_score = sorted_results[0]
                st.error(f"**KESIMPULAN UTAMA:** Pasien mengalami **{top_diag}** (Kepastian: {top_score*100:.1f}%)")
                st.write("**Diagnosis Lainnya:**")
                for diag, score in sorted_results[1:5]:
                    st.write(f"• {diag} ({score*100:.1f}%)")

# ----------------- HALAMAN 7: PREDIKSI PENYAKIT (BARU 3) -----------------
elif menu == "Prediksi Penyakit":
    st.title("Prediksi Penyakit Spesifik")
    st.write("Sistem menghitung Peluang Anda terjangkit penyakit spesifik esok hari berdasarkan menu yang Anda makan hari ini.")
    
    selected_items = st.multiselect("Masukkan asupan makanan Anda hari ini:", st.session_state.food_df["Nama Makanan"].unique())
    if selected_items:
        summary_gizi = {nut: 0.0 for nut in available_nutrients}
        for item in selected_items:
            row = st.session_state.food_df[st.session_state.food_df["Nama Makanan"] == item].iloc[0]
            for key in summary_gizi.keys(): summary_gizi[key] += float(row.get(key, 0))
        
        risiko_list = []
        
        for _, row_std in std_nutrition_df.iterrows():
            nutrisi_full = row_std['Nutrisi']
            if pd.isna(nutrisi_full) or nutrisi_full not in summary_gizi: 
                continue
                
            nutrisi_name = str(nutrisi_full).split(' (')[0]
            asupan = summary_gizi[nutrisi_full]
            batas_min = AKG_MIN.get(nutrisi_full, 1.0)
            batas_max = AKG_MAX.get(nutrisi_full, None)
            
            penyakit_kurang = str(row_std['Dampak Kekurangan']).capitalize() if pd.notna(row_std['Dampak Kekurangan']) and str(row_std['Dampak Kekurangan']).lower() != 'nan' else f"Penyakit defisit {nutrisi_name}"
            penyakit_lebih = str(row_std['Dampak Kelebihan']).capitalize() if pd.notna(row_std['Dampak Kelebihan']) and str(row_std['Dampak Kelebihan']).lower() != 'nan' else f"Keracunan ekses {nutrisi_name}"
            
            # Menggunakan nilai cf_pakar_prediksi dari st.session_state (diatur Admin)
            cf_pakar = float(st.session_state.cf_pakar_prediksi)

            if asupan < batas_min:
                cf_risiko = min((batas_min - asupan) / batas_min, 1.0) * cf_pakar 
                if cf_risiko > 0.1: 
                    risiko_list.append((f"{penyakit_kurang} (Kekurangan {nutrisi_name})", cf_risiko))
            elif batas_max and asupan > batas_max:
                cf_risiko = min((asupan - batas_max) / batas_max, 1.0) * cf_pakar
                if cf_risiko > 0.1: 
                    risiko_list.append((f"{penyakit_lebih} (Kelebihan {nutrisi_name})", cf_risiko))
                    
        st.divider()
        if risiko_list:
            st.subheader("Top 10 Prediksi Risiko Klinis")
            top_10_risiko = sorted(risiko_list, key=lambda x: x[1], reverse=True)[:10]
            for risiko, cf_val in top_10_risiko:
                st.error(f"**Risiko Medis:** {risiko} | **Peluang Terjadi: {cf_val*100:.1f}%**")
        else:
            st.success("Hebat! Asupan Anda sangat seimbang. Risiko Penyakit = 0%")

# ----------------- HALAMAN 8: PANEL ADMIN -----------------
elif menu == "Panel Admin":
    st.title("🛠️ Panel Manajemen Pakar")
    if not st.session_state.logged_in:
        username = st.text_input("Username Admin:")
        password = st.text_input("Password Admin:", type="password")
        if st.button("Masuk Panel"):
            if username == "admin" and password == "pakar123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Kredensial salah!")
    else:
        st.success("Mode Pakar Terotorisasi")
        if st.button("Keluar (Logout)"):
            st.session_state.logged_in = False
            st.rerun()
        
        st.divider()
        st.subheader("A. Edit Aturan Diagnosis Lama")
        st.session_state.rules_symptoms_old = st.data_editor(st.session_state.rules_symptoms_old, num_rows="dynamic", key="edit_old")
        
        st.subheader("B. Edit Aturan Dual-Diagnosis Baru")
        st.write("Aturan ini di-generate otomatis dari CSV. Ubah bobot CF di sini.")
        st.session_state.rules_symptoms_new = st.data_editor(st.session_state.rules_symptoms_new, num_rows="dynamic", key="edit_new")
        
        st.subheader("C. Edit Sensitivitas Prediksi Penyakit")
        st.write("Atur seberapa 'Yakin' sistem (CF Pakar) dalam memprediksi penyakit berdasarkan asupan yang melenceng dari standar.")
        st.session_state.cf_pakar_prediksi = st.slider(
            "Bobot CF Pakar Prediksi Penyakit:", 
            min_value=0.1, max_value=1.0, 
            value=float(st.session_state.cf_pakar_prediksi), 
            step=0.05
        )
        
        if st.button("Simpan Semua Konfigurasi", type="primary"):
            st.success("Semua basis pengetahuan Certainty Factor berhasil diperbarui.")

# ----------------- HALAMAN 9: TENTANG APLIKASI -----------------
elif menu == "Tentang Aplikasi":
    st.title("Tentang Aplikasi")
    st.write("Informasi mengenai pengembangan, dataset, dan metode yang digunakan dalam aplikasi ini.")
    st.divider()
    
    st.subheader("Anggota kelompok")
    st.write("**Nama/NIM:** Ghulam Yahya Nashrillah (2313010654)")
    st.write("**Nama/NIM:** Mikhael Dava Putra Wibowo (2313010650)")
    
    st.write("")
    st.subheader("Metode Analisis: Certainty Factor (CF)")
    st.write("""
    Aplikasi ini menggunakan metode **Certainty Factor (CF)** dari cabang keilmuan Sistem Pakar (*Expert System*). 
    CF digunakan untuk membuktikan tingkat kepastian suatu fakta atau diagnosis berdasarkan perhitungan matematis dari bobot pakar dan input pengguna.
    
    Pada aplikasi ini, CF diimplementasikan ke dalam 3 kasus utama:
    1. **CF Pemulihan:** Mengukur persentase kepastian sebuah makanan dalam mencukupi defisit gizi.
    2. **CF Dual-Diagnosis:** Mengukur kepastian medis apakah pasien mengalami Kekurangan atau Kelebihan gizi berdasarkan gejalanya.
    3. **CF Prediksi Penyakit:** Mengukur probabilitas risiko penyakit di masa depan akibat asupan gizi yang tidak memenuhi standar (Minimum/Maksimum).
    """)
    
    st.write("")
    st.subheader("Dataset yang Digunakan")
    st.markdown("""
    Sistem ini dibangun di atas dua basis data utama:
    * **`standard-nutrition.csv`**: Dataset berisi standar Angka Kecukupan Gizi (AKG) beserta dampak medis jika terjadi kekurangan atau kelebihan.
    * **`foods.csv`**: Database komprehensif yang berisi profil ratusan jenis makanan beserta rincian gizi makro dan mikronya.
    """)
