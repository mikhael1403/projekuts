import streamlit as st
import pandas as pd
import numpy as np

# Set konfigurasi layout halaman utama web
st.set_page_config(page_title="NutriExpert AI & CF System", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
    .stButton>button { border-radius: 20px; transition: all 0.3s; }
    .stButton>button:hover { transform: scale(1.05); box-shadow: 0px 4px 10px rgba(0,0,0,0.1); }
    [data-testid="stMetricValue"] { color: #27ae60; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# =========================================================================
# 1. INITIALIZE DATASETS & STATE
# =========================================================================

@st.cache_data
def load_nutrition_standards():
    try:
        return pd.read_csv("standard-nutrition.csv")
    except FileNotFoundError:
        st.error("File 'standard-nutrition.csv' tidak ditemukan.")
        return pd.DataFrame()

@st.cache_data
def load_food_data():
    try:
        df = pd.read_csv("foods.csv")
        if "Menu" in df.columns:
            df.rename(columns={"Menu": "Nama Makanan"}, inplace=True)
        df.fillna(0, inplace=True)
        return df
    except FileNotFoundError:
        st.error("File 'foods.csv' tidak ditemukan.")
        return pd.DataFrame()

std_nutrition_df = load_nutrition_standards()
foods_data_df = load_food_data()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'food_df' not in st.session_state:
    if not foods_data_df.empty:
        st.session_state.food_df = foods_data_df
    else:
        st.session_state.food_df = pd.DataFrame([{"Nama Makanan": "Data Kosong", "Energy (kJ)": 0, "Carbohydrates (g)": 0, "Protein (g)": 0, "Dietary Fiber (g)": 0, "Vitamin C (mg)": 0, "Iron (mg)": 0}])

if 'rules_symptoms' not in st.session_state:
    auto_rules = []
    rule_idx = 1
    if not std_nutrition_df.empty:
        for _, row in std_nutrition_df.dropna(subset=['Dampak Kekurangan']).iterrows():
            nutrisi = str(row['Nutrisi']).split(" (")[0]
            gejala_list = str(row['Dampak Kekurangan']).split(',')
            for g in gejala_list:
                g_clean = g.strip().capitalize()
                if g_clean and g_clean.lower() != "nan":
                    auto_rules.append({
                        "Kode": f"R{rule_idx:03d}",
                        "Gejala": g_clean,
                        "Diagnosis": f"Kekurangan {nutrisi}",
                        "CF_Pakar": 0.6 
                    })
                    rule_idx += 1
        st.session_state.rules_symptoms = pd.DataFrame(auto_rules)
    else:
        st.session_state.rules_symptoms = pd.DataFrame(columns=["Kode", "Gejala", "Diagnosis", "CF_Pakar"])

if 'rules_intake' not in st.session_state:
    st.session_state.rules_intake = pd.DataFrame([
        {"Defisit": "Kekurangan Dietary Fiber (g) > 50%", "Prediksi_Dampak": "Sembelit & Gangguan Pencernaan", "CF_Pakar": 0.85},
        {"Defisit": "Kekurangan Protein (g) > 40%", "Prediksi_Dampak": "Katabolisme Otot & Imunitas Turun", "CF_Pakar": 0.75},
        {"Defisit": "Kekurangan Vitamin C (mg) > 50%", "Prediksi_Dampak": "Penurunan Imunitas & Sariawan", "CF_Pakar": 0.70},
        {"Defisit": "Kekurangan Iron (mg) > 30%", "Prediksi_Dampak": "Mudah Lelah & Kurang Konsentrasi", "CF_Pakar": 0.65}
    ])

AKG = {}
if not std_nutrition_df.empty:
    for index, row in std_nutrition_df.dropna(subset=['Minimum']).iterrows():
        AKG[row['Nutrisi']] = float(row['Minimum'])

cf_options = {"Tidak Tahu": 0.0, "Gejala Ringan": 0.4, "Gejala Sedang": 0.7, "Gejala Berat": 1.0}

# =========================================================================
# 2. SIDEBAR NAVIGATION
# =========================================================================
st.sidebar.title("Nutrisi AI & SPK")
menu = st.sidebar.radio("Pilih Halaman Aplikasi:", [
    "1. Ensiklopedia Gizi",
    "2. Rekomendasi Makanan (CF)",
    "3. Diagnosis Gejala (CF)",
    "4. Analisis Menu Harian",
    "5. Analisis Kelayakan (Fuzzy Logic)",
    "6. Rekomendasi Pintar (TOPSIS)",
    "7. Panel Manajemen Pakar"
])

# Ambil list nutrisi numerik untuk pilihan filter
available_nutrients = [col for col in st.session_state.food_df.columns if col not in ["Unnamed: 0", "Nama Makanan"] and pd.api.types.is_numeric_dtype(st.session_state.food_df[col])]

# ----------------- HALAMAN 1 sampai 4 -----------------
if menu == "1. Ensiklopedia Gizi":
    st.title("📖 1. Ensiklopedia Data Kandungan Gizi Makanan")
    st.write(f"Dataset berisi **{len(st.session_state.food_df)} bahan pangan**.")
    
    selected_food = st.selectbox("Pilih Nama Makanan:", st.session_state.food_df["Nama Makanan"].unique())
    food_data = st.session_state.food_df[st.session_state.food_df["Nama Makanan"] == selected_food].iloc[0]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Energi", f"{food_data.get('Energy (kJ)', 0)} kJ")
    col1.metric("Karbohidrat", f"{food_data.get('Carbohydrates (g)', 0)} g")
    col2.metric("Protein", f"{food_data.get('Protein (g)', 0)} g")
    col2.metric("Serat", f"{food_data.get('Dietary Fiber (g)', 0)} g")
    col3.metric("Vitamin C", f"{food_data.get('Vitamin C (mg)', 0)} mg")
    col3.metric("Zat Besi", f"{food_data.get('Iron (mg)', 0)} mg")
    st.dataframe(st.session_state.food_df, use_container_width=True)

elif menu == "2. Rekomendasi Makanan (CF)":
    st.title("🎯 2. Sistem Rekomendasi Makanan (Certainty Factor)")
    gizi_pilihan = st.selectbox("Nutrisi yang ingin dipenuhi:", available_nutrients, index=available_nutrients.index("Iron (mg)") if "Iron (mg)" in available_nutrients else 0)
    target_akg = AKG.get(gizi_pilihan, 10.0)
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
                        f"Kandungan {gizi_pilihan}": nilai_gizi,
                        "Skor CF": cf_score,
                        "Keyakinan Sistem": f"{cf_score * 100:.2f} %"
                    })
        if recommendations:
            rec_df = pd.DataFrame(recommendations).sort_values(by="Skor CF", ascending=False).head(20)
            st.success(f"Ditemukan {len(recommendations)} makanan penunjang. Berikut Top 20 Makanan Terbaik:")
            st.dataframe(rec_df[["Nama Makanan", f"Kandungan {gizi_pilihan}", "Keyakinan Sistem"]], use_container_width=True)
        else:
            st.warning("Tidak ada makanan yang memenuhi syarat.")

elif menu == "3. Diagnosis Gejala (CF)":
    st.title("🩺 3. Sistem Pakar Diagnosa Malnutrisi (CF Engine)")
    unique_symptoms = st.session_state.rules_symptoms["Gejala"].unique()
    selected_symptoms = st.multiselect("1️⃣ Pilih Gejala Fisik:", options=unique_symptoms)
    
    if selected_symptoms:
        st.divider()
        st.subheader("2️⃣ Tentukan Tingkat Keparahan Gejala")
        user_inputs = {}
        valid_cf_options = {k: v for k, v in cf_options.items() if v > 0.0}
        
        for symptom in selected_symptoms:
            user_inputs[symptom] = st.radio(f"Seberapa parah '{symptom}'?", list(valid_cf_options.keys()), key=symptom, horizontal=True)
            
        if st.button("Proses Diagnosa Certainty Factor", type="primary"):
            active_inputs = {sym: valid_cf_options[val] for sym, val in user_inputs.items()}
            diagnoses = st.session_state.rules_symptoms["Diagnosis"].unique()
            final_results = {}
            for diag in diagnoses:
                diag_rules = st.session_state.rules_symptoms[st.session_state.rules_symptoms["Diagnosis"] == diag]
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
                st.success(f"🚨 **DIAGNOSIS UTAMA:** {top_diag} ({top_score*100:.2f}%)")
                for diag, score in sorted_results:
                    st.write(f"**{diag}** | {score*100:.2f}%")
                    st.progress(float(max(0.0, min(score, 1.0))))

elif menu == "4. Analisis Menu Harian":
    st.title("🍽️ 4. Evaluasi Menu Konsumsi Harian")
    selected_items = st.multiselect("Pilih seluruh menu makanan Anda:", st.session_state.food_df["Nama Makanan"].unique())
    if selected_items:
        summary_gizi = {"Energy (kJ)": 0.0, "Protein (g)": 0.0, "Dietary Fiber (g)": 0.0, "Vitamin C (mg)": 0.0, "Iron (mg)": 0.0}
        for item in selected_items:
            row = st.session_state.food_df[st.session_state.food_df["Nama Makanan"] == item].iloc[0]
            for key in summary_gizi.keys(): summary_gizi[key] += float(row.get(key, 0))
        st.write(f"**Total Protein:** {summary_gizi['Protein (g)']:.1f}g | **Total Zat Besi:** {summary_gizi['Iron (mg)']:.1f}mg")

# ----------------- HALAMAN 5: FUZZY LOGIC -----------------
elif menu == "5. Analisis Kelayakan (Fuzzy Logic)":
    st.title("🧠 5. Klasifikasi Kelayakan Makanan (Fuzzy Logic)")
    st.write("Sistem menggunakan fungsi keanggotaan Logika Fuzzy untuk menilai kelayakan kandungan makanan: **Rendah**, **Sedang**, atau **Tinggi**.")
    
    fuzzy_nutrisi = st.selectbox("Pilih Nutrisi untuk Dianalisis:", available_nutrients, index=available_nutrients.index("Protein (g)") if "Protein (g)" in available_nutrients else 0)
    target_akg = AKG.get(fuzzy_nutrisi, 10.0)
    st.info(f"Basis Himpunan Fuzzy menggunakan Standar AKG {fuzzy_nutrisi}: **{target_akg}**")

    if st.button("Proses Logika Fuzzy", type="primary"):
        fuzzy_results = []
        
        for _, row in st.session_state.food_df.iterrows():
            val = float(row.get(fuzzy_nutrisi, 0))
            
            # Rumus Keanggotaan Fuzzy (Mamdani sederhana)
            u_rendah, u_sedang, u_tinggi = 0.0, 0.0, 0.0
            
            # 1. Himpunan Rendah (0 s/d 40% AKG)
            if val <= 0.2 * target_akg: u_rendah = 1.0
            elif 0.2 * target_akg < val <= 0.4 * target_akg: 
                u_rendah = (0.4 * target_akg - val) / (0.2 * target_akg)
                
            # 2. Himpunan Sedang (20% s/d 80% AKG)
            if 0.2 * target_akg < val <= 0.5 * target_akg:
                u_sedang = (val - 0.2 * target_akg) / (0.3 * target_akg)
            elif 0.5 * target_akg < val <= 0.8 * target_akg:
                u_sedang = (0.8 * target_akg - val) / (0.3 * target_akg)
                
            # 3. Himpunan Tinggi (> 50% AKG)
            if 0.5 * target_akg < val <= 0.8 * target_akg:
                u_tinggi = (val - 0.5 * target_akg) / (0.3 * target_akg)
            elif val > 0.8 * target_akg: u_tinggi = 1.0

            # Defuzzifikasi sederhana (mencari derajat tertinggi)
            kategori_dominan = "Rendah"
            skor_dominan = u_rendah
            if u_sedang > skor_dominan:
                kategori_dominan = "Sedang"
                skor_dominan = u_sedang
            if u_tinggi > skor_dominan:
                kategori_dominan = "Tinggi"
                skor_dominan = u_tinggi
                
            # Filter hanya tampilkan yang Sedang dan Tinggi agar berguna bagi user
            if kategori_dominan in ["Sedang", "Tinggi"] and val > 0:
                fuzzy_results.append({
                    "Nama Makanan": row["Nama Makanan"],
                    f"Kandungan {fuzzy_nutrisi}": val,
                    "Kategori Fuzzy": kategori_dominan,
                    "Derajat Keanggotaan (μ)": f"{skor_dominan:.2f}"
                })
                
        if fuzzy_results:
            df_fuzzy = pd.DataFrame(fuzzy_results)
            # Urutkan berdasarkan yang 'Tinggi' dulu, lalu 'Sedang'
            df_fuzzy = df_fuzzy.sort_values(by=["Kategori Fuzzy", "Derajat Keanggotaan (μ)"], ascending=[False, False])
            st.success("Tabel Hasil Defuzzifikasi (Hanya menampilkan kategori Sedang & Tinggi):")
            st.dataframe(df_fuzzy, use_container_width=True)
        else:
            st.warning("Belum ada makanan dengan nilai gizi yang mencukupi untuk masuk ke himpunan fuzzy Sedang/Tinggi.")

# ----------------- HALAMAN 6: TOPSIS -----------------
elif menu == "6. Rekomendasi Pintar (TOPSIS)":
    st.title("⚖️ 6. Rekomendasi Multi-Kriteria (Metode TOPSIS)")
    st.write("Sistem akan merangking makanan terbaik jika Anda memiliki banyak kriteria yang bertentangan (misal: Ingin tinggi protein TAPI harus rendah lemak).")
    
    st.subheader("Tentukan Kriteria Pencarian")
    col1, col2 = st.columns(2)
    with col1:
        benefit_cols = st.multiselect("Kriteria Benefit (Makin tinggi makin bagus):", available_nutrients, default=["Protein (g)", "Iron (mg)"])
    with col2:
        cost_cols = st.multiselect("Kriteria Cost (Makin rendah makin bagus):", available_nutrients, default=["Fat (g)", "Sodium (mg)"])
    
    if st.button("Jalankan TOPSIS", type="primary"):
        # PERBAIKAN: Validasi Pengecekan Error Intersecting Kriteria
        overlap = set(benefit_cols).intersection(set(cost_cols))
        
        if overlap:
            # Jika ada nutrisi yang sama di benefit dan cost, sistem akan menolak
            overlap_str = ", ".join(overlap)
            st.error(f"⚠️ PERINGATAN LOGIKA: Kriteria '{overlap_str}' tidak boleh dipilih di Benefit sekaligus Cost. Silakan hapus salah satu!")
        elif not benefit_cols and not cost_cols:
            st.warning("Pilih minimal 1 kriteria!")
        else:
            all_criteria = benefit_cols + cost_cols
            # 1. Ambil dataset & bersihkan nilai kosong
            df_topsis = st.session_state.food_df[['Nama Makanan'] + all_criteria].copy()
            df_topsis = df_topsis.set_index("Nama Makanan").fillna(0)
            
            # Filter baris yang semua nilainya 0 (menghindari error pembagian 0)
            df_topsis = df_topsis.loc[(df_topsis != 0).any(axis=1)]
            
            # 2. Matriks Keputusan Ternormalisasi
            pembagi = np.sqrt((df_topsis**2).sum())
            pembagi = pembagi.replace(0, 1) # Cegah bagi 0
            df_norm = df_topsis / pembagi
            
            # 3. Solusi Ideal Positif (V+) & Negatif (V-)
            ideal_best = {}
            ideal_worst = {}
            for col in all_criteria:
                if col in benefit_cols:
                    ideal_best[col] = df_norm[col].max()
                    ideal_worst[col] = df_norm[col].min()
                else: # cost cols
                    ideal_best[col] = df_norm[col].min()
                    ideal_worst[col] = df_norm[col].max()
                    
            # 4. Jarak terhadap Ideal
            S_plus = np.sqrt(((df_norm - pd.Series(ideal_best))**2).sum(axis=1))
            S_min = np.sqrt(((df_norm - pd.Series(ideal_worst))**2).sum(axis=1))
            
            # 5. Skor Preferensi (Closeness Coefficient)
            skor_topsis = S_min / (S_plus + S_min)
            
            # Format output
            hasil_topsis = df_topsis.copy()
            hasil_topsis['Skor TOPSIS'] = skor_topsis
            hasil_topsis = hasil_topsis.sort_values(by="Skor TOPSIS", ascending=False).reset_index()
            
            st.success("Tabel Rekomendasi (Diurutkan dari yang terbaik berdasarkan rasio benefit & cost):")
            st.dataframe(hasil_topsis.head(25), use_container_width=True)
            st.caption("Skor TOPSIS mendekati 1.0 berarti makanan tersebut sangat ideal (tinggi di benefit, sangat rendah di cost).")

# ----------------- HALAMAN 7: PANEL ADMIN -----------------
elif menu == "7. Panel Manajemen Pakar":
    st.title("🛠️ 7. Panel Manajemen Aturan Pakar")
    if not st.session_state.logged_in:
        username = st.text_input("Username Admin:")
        password = st.text_input("Password Admin:", type="password")
        if st.button("Masuk"):
            if username == "admin" and password == "pakar123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Kombinasi Username atau Password salah!")
    else:
        st.success("🔓 Mode Admin Aktif")
        if st.button("Keluar"):
            st.session_state.logged_in = False
            st.rerun()
        st.divider()
        st.caption("Sesuaikan CF (Bobot Kepastian Pakar) untuk setiap diagnosis gejala dari dataset.")
        edited_symptoms = st.data_editor(st.session_state.rules_symptoms, num_rows="dynamic")
        if st.button("Simpan Aturan"):
            st.session_state.rules_symptoms = edited_symptoms
            st.success("Berhasil disimpan.")
