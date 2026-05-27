import streamlit as st
import pandas as pd

# Set konfigurasi layout halaman utama web
st.set_page_config(page_title="NutriExpert CF System", layout="wide", initial_sidebar_state="expanded")

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
    st.session_state.rules_symptoms = pd.DataFrame([
        {"Kode": "R001", "Gejala": "Gusi Berdarah", "Diagnosis": "Kekurangan Vitamin C", "CF_Pakar": 0.8},
        {"Kode": "R002", "Gejala": "Sariawan Berulang", "Diagnosis": "Kekurangan Vitamin C", "CF_Pakar": 0.7},
        {"Kode": "R003", "Gejala": "Mudah Memar", "Diagnosis": "Kekurangan Vitamin C", "CF_Pakar": 0.5},
        {"Kode": "R007", "Gejala": "Sering Pusing & Lemas", "Diagnosis": "Kekurangan Zat Besi (Anemia)", "CF_Pakar": 0.8},
        {"Kode": "R008", "Gejala": "Pucat di Kuku/Mata", "Diagnosis": "Kekurangan Zat Besi (Anemia)", "CF_Pakar": 0.75},
        {"Kode": "R009", "Gejala": "Rambut Rontok Parah", "Diagnosis": "Kekurangan Protein", "CF_Pakar": 0.6},
        {"Kode": "R010", "Gejala": "Otot Menyusut / Lemah", "Diagnosis": "Kekurangan Protein", "CF_Pakar": 0.7}
    ])

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

fallback_akg = {"Energy (kJ)": 4000.0, "Carbohydrates (g)": 130.0, "Protein (g)": 13.0, "Dietary Fiber (g)": 14.0, "Vitamin C (mg)": 15.0, "Iron (mg)": 7.0}
for k, v in fallback_akg.items():
    if k not in AKG:
        AKG[k] = v

cf_options = {"Tidak Tahu": 0.0, "Gejala Ringan": 0.4, "Gejala Sedang": 0.7, "Gejala Berat": 1.0}

# =========================================================================
# 2. SIDEBAR NAVIGATION
# =========================================================================
st.sidebar.title("NutriExpert CF")
menu = st.sidebar.radio("Pilih Halaman Aplikasi:", [
    "Ensiklopedia Gizi",
    "Rekomendasi Makanan",
    "Diagnosis Gejala",
    "Analisis Menu Harian",
    "Kamus Dampak Malnutrisi",
    "Panel Manajemen Pakar"
])

# ----------------- HALAMAN 1: ENSIKLOPEDIA GIZI -----------------
if menu == "Ensiklopedia Gizi":
    st.title("Ensiklopedia Data Kandungan Gizi Makanan")
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

# ----------------- HALAMAN 2: REKOMENDASI CF -----------------
elif menu == "Rekomendasi Makanan":
    st.title("Sistem Rekomendasi Makanan")
    st.write("Sistem akan menghitung tingkat keyakinan sebuah makanan dalam memenuhi kebutuhan nutrisi harian balita.")
    
    available_nutrients = [col for col in st.session_state.food_df.columns if col not in ["Unnamed: 0", "Nama Makanan"]]
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
            st.dataframe(
                rec_df[["Nama Makanan", f"Kandungan {gizi_pilihan}", "Keyakinan Sistem"]],
                use_container_width=True
            )
            st.caption("Catatan: Keyakinan 100% berarti 1 porsi makanan tersebut sudah cukup untuk memenuhi seluruh kebutuhan harian nutrisi yang dipilih.")
        else:
            st.warning("Tidak ada makanan yang signifikan mengandung nutrisi tersebut di dalam dataset.")

# ----------------- HALAMAN 3: DIAGNOSIS GEJALA (CF ENGINE) -----------------
elif menu == "Diagnosis Gejala":
    st.title("3. Sistem Pakar Diagnosa Malnutrisi Berdasarkan Gejala")
    unique_symptoms = st.session_state.rules_symptoms["Gejala"].unique()
    user_inputs = {}
    
    for symptom in unique_symptoms:
        user_inputs[symptom] = st.selectbox(f"Seberapa yakin Anda mengalami '{symptom}'?", list(cf_options.keys()), key=symptom)
        
    if st.button("Proses Diagnosa CF", type="primary"):
        active_inputs = {sym: cf_options[val] for sym, val in user_inputs.items() if cf_options[val] > 0}
        
        if not active_inputs:
            st.warning("Mohon pilih minimal satu gejala fisik.")
        else:
            diagnoses = st.session_state.rules_symptoms["Diagnosis"].unique()
            final_results = {}
            for diag in diagnoses:
                diag_rules = st.session_state.rules_symptoms[st.session_state.rules_symptoms["Diagnosis"] == diag]
                cf_list = [active_inputs[r["Gejala"]] * r["CF_Pakar"] for _, r in diag_rules.iterrows() if r["Gejala"] in active_inputs]
                
                if cf_list:
                    cf_combine = cf_list[0]
                    for cf_next in cf_list[1:]:
                        cf_combine = cf_combine + cf_next * (1 - cf_combine)
                    final_results[diag] = cf_combine
            
            if final_results:
                sorted_results = sorted(final_results.items(), key=lambda x: x[1], reverse=True)
                for diag, score in sorted_results:
                    st.info(f"**{diag}** | Persentase Keyakinan: **{score*100:.2f}%**")
                    st.progress(float(max(0.0, min(score, 1.0))))

# ----------------- HALAMAN 4: ANALISIS MENU HARIAN (CF ENGINE) -----------------
elif menu == "Analisis Menu Harian":
    st.title("Evaluasi Menu Konsumsi Harian")
    
    selected_items = st.multiselect("Pilih seluruh menu makanan Anda:", st.session_state.food_df["Nama Makanan"].unique())
    if selected_items:
        summary_gizi = {"Energy (kJ)": 0.0, "Protein (g)": 0.0, "Dietary Fiber (g)": 0.0, "Vitamin C (mg)": 0.0, "Iron (mg)": 0.0}
        
        for item in selected_items:
            row = st.session_state.food_df[st.session_state.food_df["Nama Makanan"] == item].iloc[0]
            for key in summary_gizi.keys():
                summary_gizi[key] += float(row.get(key, 0))
                
        col1, col2 = st.columns(2)
        col1.metric("Protein", f"{summary_gizi['Protein (g)']:.1f} / {AKG['Protein (g)']} g")
        col2.metric("Zat Besi", f"{summary_gizi['Iron (mg)']:.1f} / {AKG['Iron (mg)']} mg")
            
        cf_user_deficits = {}
        pct_protein = summary_gizi["Protein (g)"] / AKG["Protein (g)"] if AKG["Protein (g)"] > 0 else 1.0
        if pct_protein < 0.6: cf_user_deficits["Kekurangan Protein (g) > 40%"] = 1.0 - pct_protein
            
        pct_iron = summary_gizi["Iron (mg)"] / AKG["Iron (mg)"] if AKG["Iron (mg)"] > 0 else 1.0
        if pct_iron < 0.7: cf_user_deficits["Kekurangan Iron (mg) > 30%"] = 1.0 - pct_iron
            
        st.subheader("🔮 Prediksi CF Dampak Defisit Nutrisi")
        if not cf_user_deficits:
            st.success("Aman! Menu makanan memenuhi standar gizi.")
        else:
            predictions = []
            for _, rule in st.session_state.rules_intake.iterrows():
                if rule["Defisit"] in cf_user_deficits:
                    cf_u = cf_user_deficits[rule["Defisit"]]
                    predictions.append((rule["Prediksi_Dampak"], cf_u * rule["CF_Pakar"]))
            for dampak, score in sorted(predictions, key=lambda x: x[1], reverse=True):
                st.warning(f"Risiko {dampak} | CF Kemungkinan: {score*100:.2f}%")

# ----------------- HALAMAN 5: KAMUS DAMPAK MALNUTRISI -----------------
elif menu == "Kamus Dampak Malnutrisi":
    st.title("Kamus Dampak Malnutrisi")
    st.write("Daftar katalog medis komprehensif berdasarkan standar nutrisi.")
    
    if not std_nutrition_df.empty:
        for _, row in std_nutrition_df.iterrows():
            nutrisi = row['Nutrisi']
            dampak_kurang = row['Dampak Kekurangan']
            dampak_lebih = row['Dampak Kelebihan']
            fungsi = row['Fungsi Zat']
            
            with st.expander(f"{nutrisi}"):
                st.write(f"**Fungsi Zat:** {fungsi}")
                st.write(f"**Dampak Kekurangan:** {dampak_kurang}")
                st.write(f"**Dampak Kelebihan:** {dampak_lebih}")
    else:
        st.warning("Dataset standard-nutrition.csv belum dimuat.")

# ----------------- HALAMAN 6: PANEL ADMIN (MANAJEMEN PAKAR) -----------------
elif menu == "Panel Manajemen Pakar":
    st.title("Panel Manajemen Aturan Pakar")
    
    if not st.session_state.logged_in:
        st.subheader("Silakan Login Terlebih Dahulu")
        username = st.text_input("Username Admin:")
        password = st.text_input("Password Admin:", type="password")
        
        if st.button("Masuk Ke Panel Kendali"):
            if username == "admin" and password == "pakar123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Kombinasi Username atau Password salah!")
    else:
        st.success("Anda berhasil masuk sebagai Pakar/Admin Sistem!")
        if st.button("Keluar / Logout Admin"):
            st.session_state.logged_in = False
            st.rerun()
            
        st.divider()
        st.subheader("Ubah Bobot Persentase CF Pakar (Modul Gejala - Halaman 3)")
        st.caption("Double klik pada kolom 'CF_Pakar' untuk mengubah angka keyakinan medis (rentang 0.0 s.d 1.0).")
        
        edited_symptoms = st.data_editor(st.session_state.rules_symptoms, num_rows="dynamic", key="editor_sym")
        
        st.subheader("Ubah Bobot Persentase CF Pakar (Modul Defisit Makan - Halaman 4)")
        edited_intake = st.data_editor(st.session_state.rules_intake, num_rows="dynamic", key="editor_int")
        
        if st.button("Simpan Perubahan Aturan Pakar ke Sistem", type="primary"):
            st.session_state.rules_symptoms = edited_symptoms
            st.session_state.rules_intake = edited_intake
            st.success("✅ Sukses! Seluruh basis aturan pakar berhasil di-update ke dalam memori aplikasi.")
