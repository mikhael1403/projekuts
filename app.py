import streamlit as st
import pandas as pd
import numpy as np

# Set konfigurasi layout
st.set_page_config(page_title="NutriExpert CF System", layout="wide", initial_sidebar_state="expanded")
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

# ----------------- AUTO-GENERATE RULES (DUAL DIAGNOSIS: KURANG & LEBIH) -----------------
if 'rules_symptoms' not in st.session_state:
    auto_rules = []
    rule_idx = 1
    if not std_nutrition_df.empty:
        for _, row in std_nutrition_df.iterrows():
            nutrisi = str(row['Nutrisi']).split(" (")[0]
            
            # 1. Rules Dampak Kekurangan
            if pd.notna(row['Dampak Kekurangan']):
                gejala_kurang = str(row['Dampak Kekurangan']).split(',')
                for g in gejala_kurang:
                    g_clean = g.strip().capitalize()
                    if g_clean and g_clean.lower() != "nan":
                        auto_rules.append({"Kode": f"R{rule_idx:03d}", "Gejala": g_clean, "Diagnosis": f"Kekurangan {nutrisi}", "Tipe": "Defisit", "CF_Pakar": 0.6})
                        rule_idx += 1
                        
            # 2. Rules Dampak Kelebihan
            if pd.notna(row['Dampak Kelebihan']):
                gejala_lebih = str(row['Dampak Kelebihan']).split(',')
                for g in gejala_lebih:
                    g_clean = g.strip().capitalize()
                    if g_clean and g_clean.lower() != "nan":
                        auto_rules.append({"Kode": f"R{rule_idx:03d}", "Gejala": g_clean, "Diagnosis": f"Kelebihan/Keracunan {nutrisi}", "Tipe": "Ekses", "CF_Pakar": 0.6})
                        rule_idx += 1
                        
        st.session_state.rules_symptoms = pd.DataFrame(auto_rules)
    else:
        st.session_state.rules_symptoms = pd.DataFrame(columns=["Kode", "Gejala", "Diagnosis", "Tipe", "CF_Pakar"])

# Setup Batasan Minimum dan Maksimum Harian
AKG_MIN = {}
AKG_MAX = {}
if not std_nutrition_df.empty:
    for index, row in std_nutrition_df.iterrows():
        nutrisi = row['Nutrisi']
        if pd.notna(row['Minimum']): AKG_MIN[nutrisi] = float(row['Minimum'])
        if pd.notna(row['Maximum']): AKG_MAX[nutrisi] = float(row['Maximum'])

cf_options = {"Tidak Merasakan": 0.0, "Gejala Ringan": 0.4, "Gejala Sedang": 0.7, "Gejala Parah": 1.0}
available_nutrients = [col for col in st.session_state.food_df.columns if col not in ["Unnamed: 0", "Nama Makanan"] and pd.api.types.is_numeric_dtype(st.session_state.food_df[col])]

# =========================================================================
# 2. SIDEBAR NAVIGATION
# =========================================================================
st.sidebar.title("Sistem Pakar Gizi (CF)")
menu = st.sidebar.radio("Navigasi:", [
    "1. Ensiklopedia Gizi",
    "2. CF Pemulihan Makanan",
    "3. Diagnosis Medis Gizi",
    "4. Analisis Asupan Harian",
    "5. Panel Pakar (Admin)"
])

# ----------------- HALAMAN 1: ENSIKLOPEDIA -----------------
if menu == "1. Ensiklopedia Gizi":
    st.title("📖 1. Ensiklopedia Data Kandungan Gizi")
    st.write("Jelajahi kandungan makro dan mikro dari database.")
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

# ----------------- HALAMAN 2: REKOMENDASI (CF KAPASITAS MAKANAN) -----------------
elif menu == "2. CF Pemulihan Makanan":
    st.title("🎯 2. Rekomendasi Pemulihan Gizi")
    st.write("Hitung Certainty Factor (Kepastian) suatu makanan mampu menyembuhkan defisit gizi Anda.")
    
    gizi_pilihan = st.selectbox("Saya sedang kekurangan:", available_nutrients, index=0)
    target_akg = AKG_MIN.get(gizi_pilihan, 10.0)
    defisit_user = st.number_input(f"Berapa jumlah {gizi_pilihan} yang ingin dicapai?", value=float(target_akg))

    if st.button("Cari Obat Alami (Makanan)"):
        recommendations = []
        for _, row in st.session_state.food_df.iterrows():
            nilai_gizi = float(row.get(gizi_pilihan, 0))
            if nilai_gizi > 0:
                # CF Makanan: Kapasitas makanan memenuhi defisit dalam 1 porsi
                cf_score = min(nilai_gizi / defisit_user, 1.0) 
                if cf_score >= 0.1: # Minimal bisa memenuhi 10% defisit
                    recommendations.append({
                        "Nama Makanan": row["Nama Makanan"],
                        f"Kandungan {gizi_pilihan}": f"{nilai_gizi:.1f}",
                        "Kepastian Memulihkan": cf_score
                    })
        if recommendations:
            rec_df = pd.DataFrame(recommendations).sort_values(by="Kepastian Memulihkan", ascending=False).head(15)
            # Format UI CF
            rec_df["Kepastian Memulihkan"] = rec_df["Kepastian Memulihkan"].apply(lambda x: f"{x * 100:.1f} %")
            st.success(f"Ditemukan {len(recommendations)} makanan. Berikut Top 15:")
            st.dataframe(rec_df, use_container_width=True)
            st.caption("Catatan: Kepastian 100% artinya 1 porsi makanan tersebut langsung melunasi target gizi Anda.")

# ----------------- HALAMAN 3: DIAGNOSIS GEJALA (DUAL CF) -----------------
elif menu == "3. Diagnosis Medis Gizi":
    st.title("🩺 3. Diagnosis Kekurangan & Kelebihan Gizi")
    st.write("Sistem pakar akan menganalisis apakah gejala Anda merujuk pada **Kekurangan** gizi atau justru **Keracunan (Kelebihan)** gizi.")
    
    unique_symptoms = st.session_state.rules_symptoms["Gejala"].unique()
    selected_symptoms = st.multiselect("Pilih Gejala Fisik yang Dirasakan:", options=unique_symptoms)
    
    if selected_symptoms:
        st.divider()
        user_inputs = {}
        valid_cf_options = {k: v for k, v in cf_options.items() if v > 0.0}
        
        for symptom in selected_symptoms:
            user_inputs[symptom] = st.radio(f"Parahnya '{symptom}'?", list(valid_cf_options.keys()), key=symptom, horizontal=True)
            
        if st.button("Diagnosis CF", type="primary"):
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
                st.subheader("📊 Hasil Kepastian Diagnosis")
                sorted_results = sorted(final_results.items(), key=lambda x: x[1], reverse=True)
                top_diag, top_score = sorted_results[0]
                st.error(f"🚨 **DIAGNOSIS UTAMA:** Pasien mengalami **{top_diag}** (CF: {top_score*100:.1f}%)")
                
                st.write("**Kemungkinan Lainnya:**")
                for diag, score in sorted_results[1:]:
                    st.write(f"• **{diag}** (Keyakinan: {score*100:.1f}%)")

# ----------------- HALAMAN 4: ANALISIS HARIAN & INDIKATOR -----------------
elif menu == "4. Analisis Asupan Harian":
    st.title("🍽️ 4. CF Risiko Asupan Harian")
    st.write("Masukkan makanan hari ini. Sistem akan mencocokkan dengan Batas Minimum (AKG) dan Maksimum (Toleransi).")
    
    selected_items = st.multiselect("Daftar Menu Konsumsi Anda:", st.session_state.food_df["Nama Makanan"].unique())
    if selected_items:
        summary_gizi = {nut: 0.0 for nut in available_nutrients}
        for item in selected_items:
            row = st.session_state.food_df[st.session_state.food_df["Nama Makanan"] == item].iloc[0]
            for key in summary_gizi.keys(): 
                summary_gizi[key] += float(row.get(key, 0))
        
        st.divider()
        st.subheader("Indikator Batas Harian (Minimum & Maksimum)")
        
        # Analisis CF Risiko
        risiko_list = []
        
        # Menampilkan beberapa nutrisi penting sebagai indikator
        nutrisi_penting = ["Energy (kJ)", "Protein (g)", "Dietary Fiber (g)", "Iron (mg)", "Vitamin C (mg)"]
        
        for nutrisi in nutrisi_penting:
            if nutrisi in summary_gizi:
                asupan = summary_gizi[nutrisi]
                batas_min = AKG_MIN.get(nutrisi, 1.0) # Hindari div by 0
                batas_max = AKG_MAX.get(nutrisi, None)
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.write(f"**{nutrisi.split(' (')[0]}**")
                    st.write(f"{asupan:.1f}")
                with col2:
                    # UI Indikator Progress
                    if asupan < batas_min:
                        st.warning(f"⚠️ Kurang (Min: {batas_min})")
                        # Hitung CF Kekurangan (Semakin jauh dari minimum, semakin yakin berisiko)
                        cf_risiko = min((batas_min - asupan) / batas_min, 1.0) * 0.8 # Bobot pakar 0.8
                        if cf_risiko > 0.1: risiko_list.append((f"Risiko Sakit Akibat Defisit {nutrisi.split(' (')[0]}", cf_risiko))
                    elif batas_max and asupan > batas_max:
                        st.error(f"🚨 Berlebih! (Max: {batas_max})")
                        # Hitung CF Kelebihan (Semakin jauh di atas maksimum, semakin yakin berisiko)
                        cf_risiko = min((asupan - batas_max) / batas_max, 1.0) * 0.8
                        if cf_risiko > 0.1: risiko_list.append((f"Risiko Keracunan/Penyakit Akibat Ekses {nutrisi.split(' (')[0]}", cf_risiko))
                    else:
                        st.success(f"✅ Aman (Min: {batas_min} {f'| Max: {batas_max}' if batas_max else ''})")
                st.markdown("---")
        
        if risiko_list:
            st.subheader("🔮 Prediksi CF Dampak Penyakit Esok Hari")
            for risiko, cf_val in sorted(risiko_list, key=lambda x: x[1], reverse=True):
                st.error(f"{risiko} | **CF Kepastian: {cf_val*100:.1f}%**")

# ----------------- HALAMAN 5: PANEL ADMIN -----------------
elif menu == "5. Panel Pakar (Admin)":
    st.title("🛠️ 5. Panel Pakar (Manajemen Rule CF)")
    if not st.session_state.logged_in:
        username = st.text_input("Username Admin:")
        password = st.text_input("Password Admin:", type="password")
        if st.button("Masuk"):
            if username == "admin" and password == "pakar123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Kombinasi salah!")
    else:
        st.success("🔓 Mode Admin Aktif")
        if st.button("Keluar"):
            st.session_state.logged_in = False
            st.rerun()
        st.divider()
        st.write("Ubah bobot kepastian medis (CF Pakar) untuk aturan diagnosis (Halaman 3).")
        edited_symptoms = st.data_editor(st.session_state.rules_symptoms, num_rows="dynamic")
        if st.button("Simpan Aturan"):
            st.session_state.rules_symptoms = edited_symptoms
            st.success("Tersimpan.")
