import streamlit as st
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(page_title="NutriExpert AI", layout="wide")

# Inisialisasi Session State
if 'bobot_pakar' not in st.session_state:
    st.session_state['bobot_pakar'] = {'Protein': 30, 'Serat': 20, 'Gula': -20, 'Natrium': -20, 'Lemak': -10}
if 'is_admin' not in st.session_state:
    st.session_state['is_admin'] = False

# Fungsi Load Dataset
@st.cache_data
def load_data():
    df_makanan = pd.read_csv('nilai-gizi.csv').fillna(0)
    df_standar = pd.read_csv('standard-nutrition.csv')
    return df_makanan, df_standar

df_makanan, df_standar = load_data()

# ================= SIDEBAR NAVIGASI =================
menu = st.sidebar.radio("Navigasi", ["1. Beranda", "2. Data Makanan", "3. Analisis Pakar", "4. Info Gizi & Penyakit", "5. Bantuan", "6. Admin Panel"])

# ================= HALAMAN 1: BERANDA =================
if menu == "1. Beranda":
    st.title("🍏 NutriExpert AI")
    st.write("Sistem pakar untuk analisis gizi berbasis standar nutrisi kesehatan.")

# ================= HALAMAN 2: DATA MAKANAN =================
elif menu == "2. Data Makanan":
    st.title("📊 Dataset Makanan")
    st.dataframe(df_makanan.head(50))

# ================= HALAMAN 3: ANALISIS PAKAR =================
elif menu == "3. Analisis Pakar":
    st.title("🤖 Sistem Pakar Diagnosa Gizi")
    makanan_pilihan = st.selectbox("Pilih Makanan:", df_makanan['name'].unique())
    
    if st.button("Analisis"):
        data = df_makanan[df_makanan['name'] == makanan_pilihan].iloc[0]
        
        # Logika Pakar: Bandingkan dengan Standard Nutrition
        st.subheader(f"Hasil Analisis: {makanan_pilihan}")
        
        # Contoh cek Protein (Baris 1 di standard-nutrition.csv)
        prot_std = df_standar.iloc[1] # Baris Protein
        val_prot = data.get('protein_g', 0)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Protein (g)", val_prot)
            if val_prot < prot_std['Minimum']:
                st.warning(f"Status: Rendah. Risiko: {prot_std['Dampak Kekurangan']}")
            elif val_prot > prot_std['Maximum']:
                st.error(f"Status: Tinggi. Risiko: {prot_std['Dampak Kelebihan']}")
            else:
                st.success("Status: Normal (Sesuai Standar)")

        # Tambahkan lebih banyak logika di sini sesuai kolom di df_standar
        st.write(f"**Fungsi Utama Nutrisi:** {prot_std['Fungsi Zat']}")

# ================= HALAMAN 4: INFO GIZI & PENYAKIT =================
elif menu == "4. Info Gizi & Penyakit":
    st.title("🩺 Ensiklopedia Gizi")
    st.dataframe(df_standar[['Nutrisi', 'Dampak Kelebihan', 'Dampak Kekurangan', 'Fungsi Zat']])

# ================= HALAMAN 5: BANTUAN =================
elif menu == "5. Bantuan":
    st.write("Gunakan menu Analisis Pakar untuk membandingkan makanan dengan standar kesehatan.")

# ================= HALAMAN 6: ADMIN PANEL =================
elif menu == "6. Admin Panel":
    st.title("🔒 Admin Panel")
    if st.text_input("Password", type="password") == "admin123":
        st.session_state['is_admin'] = True
        st.write("Admin Mode Aktif. Silakan ubah bobot atau aturan di sini.")
        # Tambahkan form edit bobot di sini seperti sebelumnya
    else:
        st.error("Login Gagal")
