import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Mengatur style seaborn
sns.set(style='whitegrid')

# Fungsi untuk memuat data (dengan cache agar lebih cepat)
@st.cache_data
def load_data():
    # Path file
    file_path = "day_cleaned.csv"
    if not os.path.exists(file_path):
        st.error(f"File '{file_path}' tidak ditemukan. Pastikan file ada di folder yang sama dengan dashboard.py")
        return None
    
    data = pd.read_csv(file_path)
    data['tanggal'] = pd.to_datetime(data['tanggal'])
    return data

# Memuat data
df = load_data()

# Hanya jalankan jika data berhasil dimuat
if df is not None:

    # --- Judul Dashboard ---
    st.title('🚲 Dashboard Analisis Peminjaman Sepeda')

    # --- Sidebar untuk Filter ---
    st.sidebar.header("Filter Data")
    min_date = df["tanggal"].min()
    max_date = df["tanggal"].max()

    start_date, end_date = st.sidebar.date_input(
        label='Pilih Rentang Waktu:',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    # Filter dataframe utama berdasarkan tanggal
    main_df = df[(df["tanggal"] >= str(start_date)) & 
                 (df["tanggal"] <= str(end_date))]

    # --- Menampilkan Metrik Utama ---
    total_rides = main_df['total_peminjaman'].sum()
    st.metric("Total Peminjaman (sesuai filter)", value=f"{total_rides:,.0f}")

    st.markdown("---")

    # --- Visualisasi Pertanyaan 1 ---
    st.header('Pertanyaan 1: Pengaruh Musim dan Cuaca')
    
    plot1_data = main_df.groupby(['musim', 'kondisi_cuaca'], as_index=False)['total_peminjaman'].mean()

    fig1, ax1 = plt.subplots(figsize=(12, 7))
    sns.barplot(
        x='musim',
        y='total_peminjaman',
        hue='kondisi_cuaca',
        data=plot1_data,
        palette='viridis',
        ax=ax1
    )
    ax1.set_title('Rata-rata Peminjaman Berdasarkan Musim dan Cuaca', fontsize=16)
    ax1.set_xlabel('Musim')
    ax1.set_ylabel('Rata-rata Total Peminjaman')
    st.pyplot(fig1)

    # --- Visualisasi Pertanyaan 2 ---
    st.header('Pertanyaan 2: Pola Pengguna Kasual vs Terdaftar')
    
    # Agregasi data untuk plot 2
    plot2_data = main_df.groupby('tipe_hari')[['pengguna_kasual', 'pengguna_terdaftar']].mean()
    
    st.subheader('Rata-rata Peminjaman per Tipe Hari')
    st.bar_chart(plot2_data, color=["#FF6347", "#4682B4"]) # Memberi warna berbeda

    st.markdown("---")

    # --- Menampilkan Kesimpulan ---
    st.header('Kesimpulan dari Notebook')
    st.markdown("""
    * **Kesimpulan 1:** Peminjaman tertinggi terjadi pada **Musim Gugur** saat **Cuaca Cerah**. Hujan/Salju Ringan sangat menurunkan minat peminjaman.
    * **Kesimpulan 2:** **Pengguna Terdaftar** dominan di **Hari Kerja** (komuter), sementara **Pengguna Kasual** dominan di **Hari Libur/Akhir Pekan** (rekreasi).
    """)
