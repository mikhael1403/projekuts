import streamlit as st
import pandas as pd
import numpy as np

# Set konfigurasi layout
st.set_page_config(page_title="NutriExpert Super CF", layout="wide", initial_sidebar_state="expanded")
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
    st.session_state.food_df = foods_data_df if not foods_data_df.empty else pd.DataFrame([{"Nama Makanan": "Kosong", "Energy (kJ)": 0, "Protein (g)": 0}])

# --- STATE LAMA (Manual) ---
if 'rules_symptoms_old' not in st.session_state:
    st.session_state.rules_symptoms_old = pd.DataFrame([
        {"Kode": "R001", "Gejala": "Gusi Berdarah", "Diagnosis": "Kekurangan Vitamin C", "CF_Pakar": 0.8},
        {"Kode": "R002", "Gejala": "Sariawan Berulang", "Diagnosis": "Kekurangan Vitamin C", "CF_Pakar": 0.7},
        {"Kode": "R003", "Gejala": "Mudah Memar", "Diagnosis": "Kekurangan Vitamin C", "CF_Pakar": 0.5},
        {"Kode": "R007", "Gejala": "Sering Pusing & Lemas", "Diagnosis": "Kekurangan Zat Besi (Anemia)", "CF_Pakar": 0.8},
        {"Kode": "R008", "Gejala": "Pucat di Kuku/Mata", "Diagnosis": "Kekurangan Zat Besi (Anemia)", "CF_Pakar": 0.75},
        {"Kode": "R009", "Gejala": "Rambut Rontok Parah", "Diagnosis": "Kekurangan Protein", "CF_Pakar": 0.6},
        {"Kode": "R010", "Gejala": "Otot Menyusut / Lemah", "Diagnosis": "Kekurangan Protein", "CF_Pakar": 0.7}
    ])

# --- STATE BARU (Auto-Generate dari CSV untuk Dual Diagnosis) ---
if 'rules_symptoms_new' not in st.session_state:
    auto_rules = []
    rule_idx = 1
    if not std_nutrition_df.empty:
        for _, row in std_nutrition_df.iterrows():
            nutrisi = str(row['Nutrisi']).split(" (")[0]
            if pd.notna(row['Dampak Kekurangan']):
                for g in str(row['Dampak Kekurangan']).split(','):
                    if g.strip() and g.strip().lower() != "nan":
                        auto_rules.append({"Kode": f"RN{rule_idx:03d}", "Gejala": g.strip().capitalize(), "Diagnosis": f"Kekurangan {nutrisi}", "Tipe": "Defisit", "CF_Pakar": 0.6})
                        rule_idx += 1
            if pd.notna(row['Dampak Kelebihan']):
                for g in str(row['Dampak Kelebihan']).split(','):
                    if g.strip() and g.strip().lower() != "nan":
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
available_nutrients = [col for col in st.session_state.food_df.columns if col not in ["Unnamed: 0", "Nama Makanan"] and pd.api.types.is_numeric_dtype(st.session_state.food_df[col])]

# =========================================================================
# 2. SIDEBAR NAVIGATION
# =========================================================================
st.sidebar.title("NutriExpert Master")
menu = st.sidebar.radio("Navigasi Aplikasi:", [
    "1. Ensiklopedia Gizi",
    "2. Rekomendasi CF (Lama)",
    "3. Diagnosis Gejala (Lama)",
    "4. Analisis Asupan (Revisi)",
    "5. CF Pemulihan Gizi (Baru)",
    "6. Dual-Diagnosis CF (Baru)",
    "7. Prediksi Penyakit (Baru)",
    "8. Panel Pakar (Admin)"
])

# ----------------- HALAMAN 1: ENSIKLOPEDIA (LAMA) -----------------
if menu == "1. Ensiklopedia Gizi":
    st.title("📖 1. Ensiklopedia Data Kandungan Gizi")
    st.write(f"Database murni berisi **{len(st.session_state.food_df)} bahan pangan**.")
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

# ----------------- HALAMAN 2: REKOMENDASI (LAMA) -----------------
elif menu == "2. Rekomendasi CF (Lama)":
    st.title("🎯 2. Rekomendasi Makanan (Versi Lama)")
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
                        "Skor CF": cf_score,
                        "Keyakinan Sistem": f"{cf_score * 100:.2f} %"
                    })
        if recommendations:
            rec_df = pd.DataFrame(recommendations).sort_values(by="Skor CF", ascending=False).head(20)
            st.success(f"Ditemukan {len(recommendations)} makanan penunjang. Berikut Top 20 Makanan Terbaik:")
            st.dataframe(rec_df[["Nama Makanan", "Kandungan", "Keyakinan Sistem"]], use_container_width=True)
        else:
            st.warning("Tidak ada makanan yang memenuhi syarat.")

# ----------------- HALAMAN 3: DIAGNOSIS (LAMA) -----------------
elif menu == "3. Diagnosis Gejala (Lama)":
    st.title("🩺 3. Sistem Pakar Diagnosa Malnutrisi (Versi Lama)")
    st.write("Versi lama menggunakan aturan medis yang diketik manual secara *hardcoded* (hanya 7 rules dasar).")
    
    unique_symptoms = st.session_state.rules_symptoms_old["Gejala"].unique()
    selected_symptoms = st.multiselect("Pilih Gejala Fisik:", options=unique_symptoms)
    
    if selected_symptoms:
        user_inputs = {}
        valid_cf_options = {k: v for k, v in cf_options.items() if v > 0.0}
        for symptom in selected_symptoms:
            user_inputs[symptom] = st.radio(f"Parahnya '{symptom}'?", list(valid_cf_options.keys()), key=symptom, horizontal=True)
            
        if st.button("Diagnosis", type="primary"):
            active_inputs = {sym: valid_cf_options[val] for sym, val in user_inputs.items()}
            diagnoses = st.session_state.rules_symptoms_old["Diagnosis"].unique()
            final_results = {}
            for diag in diagnoses:
                diag_rules = st.session_state.rules_symptoms_old[st.session_state.rules_symptoms_old["Diagnosis"] == diag]
                cf_list = [active_inputs[r["Gejala"]] * r["CF_Pakar"] for _, r in diag_rules.iterrows() if r["Gejala"] in active_inputs]
                if cf_list:
                    cf_combine = cf_list[0]
                    for cf_next in cf_list[1:]:
                        cf_combine = cf_combine + cf_next * (1 - cf_combine)
                    if cf_combine > 0.0: final_results[diag] = cf_combine
            if final_results:
                sorted_results = sorted(final_results.items(), key=lambda x: x[1], reverse=True)
                top_diag, top_score = sorted_results[0]
                st.success(f"🚨 **DIAGNOSIS UTAMA:** {top_diag} ({top_score*100:.2f}%)")

# ----------------- HALAMAN 4: ANALISIS ASUPAN (REVISI) -----------------
elif menu == "4. Analisis Asupan (Revisi)":
    st.title("🍽️ 4. Evaluasi Asupan Harian (Revisi)")
    st.write("Sistem yang telah direvisi dengan penambahan indikator Batas Minimum (AKG) dan Maksimum (Toleransi).")
    
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
                        st.warning(f"⚠️ Kekurangan (Minimal: {batas_min})")
                        st.progress(float(max(0.0, min(asupan/batas_min, 1.0))))
                    elif batas_max and asupan > batas_max:
                        st.error(f"🚨 Berlebih! (Maksimal: {batas_max})")
                        st.progress(1.0)
                    else:
                        st.success(f"✅ Ideal (Sesuai Standar)")
                        st.progress(1.0)
                st.markdown("---")

# ----------------- HALAMAN 5: CF PEMULIHAN GIZI (BARU 1) -----------------
elif menu == "5. CF Pemulihan Gizi (Baru)":
    st.title("🔋 5. CF Pemulihan Makanan")
    st.write("Konsep Baru 1: Hitung Certainty Factor (Kepastian) suatu makanan mampu **menyembuhkan defisit gizi spesifik** Anda.")
    
    gizi_pilihan = st.selectbox("Saya sedang kekurangan gizi:", available_nutrients, index=0)
    target_akg = AKG_MIN.get(gizi_pilihan, 10.0)
    defisit_user = st.number_input(f"Berapa banyak defisit {gizi_pilihan} yang ingin ditutupi?", value=float(target_akg))

    if st.button("Cari Obat Alami (Makanan)"):
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
elif menu == "6. Dual-Diagnosis CF (Baru)":
    st.title("⚖️ 6. Diagnosis Medis Dua Arah (Dual CF)")
    st.write("Konsep Baru 2: Sistem pakar CF sekarang otomatis mengekstrak CSV dan bisa membedakan apakah Anda mengalami **Kekurangan Gizi** atau **Keracunan (Kelebihan) Gizi**.")
    
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
                sorted_results = sorted(final_results.items(), key=lambda x: x[1], reverse=True)
                top_diag, top_score = sorted_results[0]
                st.error(f"🚨 **KESIMPULAN UTAMA:** Pasien mengalami **{top_diag}** (CF Kepastian: {top_score*100:.1f}%)")
                st.write("**Diagnosis Lainnya:**")
                for diag, score in sorted_results[1:5]:
                    st.write(f"• {diag} ({score*100:.1f}%)")

# ----------------- HALAMAN 7: PREDIKSI PENYAKIT (BARU 3) -----------------
elif menu == "7. Prediksi Penyakit (Baru)":
    st.title("🔮 7. CF Prediksi Penyakit Spesifik")
    st.write("Sistem menghitung **Certainty Factor (Risiko/Peluang)** Anda terjangkit penyakit spesifik esok hari berdasarkan menu yang Anda makan hari ini.")
    
    selected_items = st.multiselect("Masukkan asupan makanan Anda hari ini:", st.session_state.food_df["Nama Makanan"].unique())
    if selected_items:
        summary_gizi = {nut: 0.0 for nut in available_nutrients}
        for item in selected_items:
            row = st.session_state.food_df[st.session_state.food_df["Nama Makanan"] == item].iloc[0]
            for key in summary_gizi.keys(): summary_gizi[key] += float(row.get(key, 0))
        
        risiko_list = []
        
        # Mengecek semua nutrisi yang ada di tabel standar nutrisi
        for _, row_std in std_nutrition_df.iterrows():
            nutrisi_full = row_std['Nutrisi']
            if pd.isna(nutrisi_full) or nutrisi_full not in summary_gizi: 
                continue
                
            nutrisi_name = str(nutrisi_full).split(' (')[0]
            asupan = summary_gizi[nutrisi_full]
            batas_min = AKG_MIN.get(nutrisi_full, 1.0)
            batas_max = AKG_MAX.get(nutrisi_full, None)
            
            # Ekstrak nama penyakit/gejala dari CSV (Jika kosong, pakai teks default)
            penyakit_kurang = str(row_std['Dampak Kekurangan']).capitalize() if pd.notna(row_std['Dampak Kekurangan']) else f"Penyakit defisit {nutrisi_name}"
            penyakit_lebih = str(row_std['Dampak Kelebihan']).capitalize() if pd.notna(row_std['Dampak Kelebihan']) else f"Keracunan ekses {nutrisi_name}"
            
            # Hitung CF Kekurangan
            if asupan < batas_min:
                cf_risiko = min((batas_min - asupan) / batas_min, 1.0) * 0.85 # 0.85 adalah bobot CF Pakar
                if cf_risiko > 0.1: 
                    risiko_list.append((f"{penyakit_kurang} (Kekurangan {nutrisi_name})", cf_risiko))
                    
            # Hitung CF Kelebihan
            elif batas_max and asupan > batas_max:
                cf_risiko = min((asupan - batas_max) / batas_max, 1.0) * 0.85
                if cf_risiko > 0.1: 
                    risiko_list.append((f"{penyakit_lebih} (Kelebihan {nutrisi_name})", cf_risiko))
                    
        st.divider()
        if risiko_list:
            st.subheader("⚠️ Top 10 Prediksi Risiko Klinis")
            # Mengurutkan dari CF terbesar dan mengambil top 10 saja agar rapi
            top_10_risiko = sorted(risiko_list, key=lambda x: x[1], reverse=True)[:10]
            
            for risiko, cf_val in top_10_risiko:
                st.error(f"**Risiko Medis:** {risiko} | **CF Peluang Terjadi: {cf_val*100:.1f}%**")
        else:
            st.success("🎉 Hebat! Asupan Anda sangat seimbang. CF Risiko Penyakit = 0%")

# ----------------- HALAMAN 8: PANEL ADMIN -----------------
elif menu == "8. Panel Pakar (Admin)":
    st.title("🛠️ 8. Panel Manajemen Pakar")
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
        st.success("🔓 Mode Pakar Terotorisasi")
        if st.button("Keluar (Logout)"):
            st.session_state.logged_in = False
            st.rerun()
        
        st.divider()
        st.subheader("A. Edit Aturan Diagnosis Lama (Halaman 3)")
        st.session_state.rules_symptoms_old = st.data_editor(st.session_state.rules_symptoms_old, num_rows="dynamic", key="edit_old")
        
        st.subheader("B. Edit Aturan Dual-Diagnosis Baru (Halaman 6)")
        st.write("Aturan ini di-generate otomatis dari CSV. Ubah bobot CF di sini.")
        st.session_state.rules_symptoms_new = st.data_editor(st.session_state.rules_symptoms_new, num_rows="dynamic", key="edit_new")
        
        if st.button("Simpan Semua Konfigurasi", type="primary"):
            st.success("Semua basis pengetahuan Certainty Factor berhasil diperbarui.")
