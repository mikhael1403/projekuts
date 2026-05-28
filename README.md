# NutrisiAnak - Sistem Pakar Gizi Berbasis Certainty Factor

Sistem pakar berbasis web ini dirancang untuk membantu melakukan analisis gizi, merekomendasikan makanan, hingga mendiagnosa awal potensi masalah kesehatan akibat kekurangan atau kelebihan nutrisi pada anak. Sistem ini mengimplementasikan metode Certainty Factor (CF) untuk mengatasi ketidakpastian pada gejala medis dan asupan harian, sehingga menghasilkan perhitungan tingkat keyakinan dalam bentuk persentase.

---

## Fitur Utama

Sistem ini terdiri dari berbagai modul utama yang dapat diakses melalui menu navigasi:

1. **Beranda**
   Halaman utama yang menyajikan pintasan navigasi cepat ke seluruh fitur yang tersedia di dalam aplikasi.
2. **Ensiklopedia Gizi**
   Eksplorasi daftar lengkap profil kandungan nutrisi (makro dan mikro) dari ratusan jenis bahan makanan.
3. **Rekomendasi Makanan**
   Fitur pencarian pintar untuk menemukan 100 saran makanan terbaik berdasarkan target gizi spesifik yang sedang dibutuhkan.
4. **Analisis Asupan Harian**
   Modul evaluasi untuk mencatat total konsumsi makanan harian dan memastikan apakah pemenuhannya sudah sesuai dengan standar Angka Kecukupan Gizi (AKG).
5. **Pemulihan Gizi**
   Modul perhitungan Certainty Factor yang mencari rekomendasi makanan penyembuh beserta persentase kepastian kemampuannya dalam menutupi defisit gizi spesifik.
6. **Dual-Diagnosis**
   Modul sistem pakar inti tempat pengguna memilih gejala yang dialami untuk dianalisis guna menentukan apakah pasien mengalami kondisi kekurangan atau keracunan (kelebihan) gizi.
7. **Prediksi Penyakit**
   Menu visualisasi AI yang memproyeksikan probabilitas risiko penyakit klinis di masa depan berdasarkan asupan gizi harian yang melenceng dari standar batas toleransi.
8. **Panel Admin**
   Menu berpelindung otentikasi (login) khusus bagi pakar/dokter untuk memodifikasi basis aturan medis (Rule Base) dan mengatur sensitivitas sistem prediksi secara langsung.
9. **Tentang Aplikasi**
   Berisi informasi mengenai pengembang, metodologi yang digunakan, serta rincian dataset yang menopang sistem.

---

## Teknologi yang Digunakan

* **Python** (Bahasa pemrograman utama)
* **Streamlit** (Framework untuk antarmuka web yang interaktif)
* **Pandas** (Eksplorasi, pembersihan, dan manipulasi dataset langsung dari file CSV)
* **Numpy** (Komputasi dan kalkulasi numerik)

---

## Cara Penggunaan Website

Berikut adalah panduan langkah demi langkah untuk menggunakan modul-modul utama dalam sistem pakar ini:

### Langkah 1: Mengevaluasi Asupan Harian
* Masuk ke menu **Analisis Asupan Harian**.
* Pilih atau ketik menu makanan apa saja yang dikonsumsi hari ini pada kolom yang tersedia.
* Sistem akan memunculkan indikator status kelayakan (Aman, Kurang, atau Berlebih) berdasarkan standar gizi.

### Langkah 2: Proses Diagnosa Medis (Dual-Diagnosis)
* Buka menu **Dual-Diagnosis**.
* Pada kolom pilihan, masukkan satu atau beberapa gejala fisik yang sedang dirasakan oleh pasien.
* Tentukan tingkat keparahan untuk masing-masing gejala tersebut (Misalnya: Gejala Ringan, Sedang, atau Parah).
* Klik tombol **Proses Dual Diagnosis**. Sistem akan memproses bobot gejala menggunakan kalkulasi Certainty Factor dan memunculkan hasil persentase kepastian penyakit pasien.

### Langkah 3: Mencari Pemulihan Gizi
* Jika terdiagnosis kekurangan nutrisi tertentu, masuk ke menu **Pemulihan Gizi**.
* Pilih jenis nutrisi yang kurang dan ketikkan angka defisitnya.
* Klik tombol **Cari Obat Alami**. Sistem akan menampilkan daftar makanan yang direkomendasikan beserta nilai keyakinan (CF) seberapa kuat makanan tersebut mampu menyembuhkan kondisi pasien.

### Langkah 4: Memprediksi Risiko Penyakit
* Masuk ke menu **Prediksi Penyakit**.
* Masukkan riwayat makanan yang dikonsumsi hari ini.
* Sistem akan memproses data tersebut dan menampilkan tabel Top 10 Prediksi Risiko Penyakit klinis di masa depan lengkap dengan persentase probabilitasnya jika asupan melenceng dari standar.

### Langkah 5: Otentikasi dan Manajemen Pakar (Login)
* Buka menu **Panel Admin**.
* Masukkan kredensial sistem (Username: **admin**, Password: **pakar123**) untuk membuka akses konfigurasi pakar.
* Di dalam panel ini, admin atau pakar gizi dapat mengubah tabel basis aturan (Rule Base) secara manual atau mengatur *slider* sensitivitas prediksi sistem, lalu menyimpan perubahannya ke dalam memori aplikasi.
