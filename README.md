Beranda
Beranda merupakan halaman utama yang pertama kali ditampilkan saat aplikasi dibuka. Halaman ini berfungsi sebagai pusat navigasi yang menyediakan tombol-tombol pintasan cepat agar pengguna dapat langsung melompat ke berbagai fitur utama yang tersedia di dalam aplikasi.

Ensiklopedia Gizi
Fitur ini berguna untuk melihat detail profil gizi dari suatu bahan makanan. Pengguna dapat memilih atau mengetik nama makanan pada kotak pencarian, kemudian sistem akan langsung memunculkan kartu metrik dan tabel lengkap yang berisi angka kandungan gizi makanan tersebut, seperti energi, protein, serat, vitamin, dan mineral.

Rekomendasi Makanan
Fitur ini dirancang untuk mencari saran makanan terbaik ketika pengguna membutuhkan pemenuhan nutrisi spesifik. Pengguna cukup memilih jenis gizi yang sedang dibutuhkan, lalu sistem akan memproses dan menampilkan daftar 20 makanan teratas yang paling kaya akan nutrisi tersebut dalam basis data.

Analisis Asupan Harian
Fitur ini berfungsi untuk mengevaluasi apakah total konsumsi makanan harian sudah memenuhi standar angka kecukupan gizi atau belum. Pengguna memasukkan daftar makanan yang dimakan pada hari tersebut, lalu sistem akan menampilkan indikator kelayakan di mana warna hijau berarti aman, kuning berarti asupan kurang dari standar, dan merah menandakan asupan melewati batas maksimal.

Pemulihan Gizi
Fitur ini menggunakan perhitungan sistem pakar untuk mencari makanan penyembuh guna menutupi defisit gizi. Pengguna memilih nutrisi yang kurang beserta estimasi angka kekurangannya, kemudian sistem akan menghitung persentase keyakinan (Certainty Factor) mengenai seberapa kuat satu porsi dari suatu bahan makanan mampu menutupi kekurangan gizi tersebut.

Dual-Diagnosis
Menu ini digunakan untuk mendiagnosis potensi kondisi medis berdasarkan keluhan fisik yang dialami pengguna. Setelah pengguna memasukkan satu atau beberapa gejala beserta tingkat keparahannya, sistem pakar akan menganalisis dan menyimpulkan persentase kepastian apakah keluhan tersebut merupakan tanda kekurangan gizi atau justru gejala keracunan akibat kelebihan gizi.

Prediksi Penyakit
Fitur ini memproyeksikan risiko medis di masa depan berdasarkan menu makan hari ini. Jika asupan gizi harian yang dimasukkan pengguna sangat kurang atau sangat berlebih dari batas normal, kecerdasan buatan pada sistem akan secara otomatis memunculkan daftar 10 prediksi risiko penyakit spesifik lengkap dengan nilai probabilitas terjadinya penyakit tersebut.

Panel Admin
Ruang khusus ini diperuntukkan bagi pakar gizi atau dokter untuk mengatur logika dan sensitivitas perhitungan aplikasi. Dengan menggunakan kredensial default sistem (username: admin, password: pakar123), admin memiliki otoritas untuk menambah atau mengubah tabel basis aturan medis (rule base) serta menggeser slider tingkat kepekaan sistem dalam memprediksi penyakit.

Tentang Website
Aplikasi NutrisiAnak dikembangkan oleh Ghulam Yahya Nashrillah (NIM 2313010654) dan Mikhael Dava Putra Wibowo (NIM 2313010650). Sistem pakar ini menggunakan metode Certainty Factor (CF) untuk mengevaluasi asupan gizi, mendiagnosis masalah nutrisi (kekurangan atau kelebihan), dan memprediksi risiko penyakit melalui perhitungan kepastian matematis. Dalam pengoperasiannya, aplikasi ini mengandalkan dua basis data utama, yaitu standard-nutrition.csv yang berisi standar kecukupan gizi beserta dampak medisnya, serta foods.csv yang memuat informasi kandungan nutrisi dari ratusan jenis bahan makanan.
