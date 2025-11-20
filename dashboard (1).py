import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Proyek Analisis Sepeda", page_icon="🚲")

# --- Style ---
sns.set(style='whitegrid')

# --- Fungsi Load Data ---
@st.cache_data
def load_data():
    file_path = "day_cleaned.csv"
    if not os.path.exists(file_path):
        st.error("File 'day_cleaned.csv' tidak ditemukan!")
        return None
    
    data = pd.read_csv(file_path)
    data['tanggal'] = pd.to_datetime(data['tanggal'])
    return data

# --- Main Program ---
df = load_data()

if df is not None:
    
    # ====================================================================
    # --- FIX BUG: Membuat kolom 'tipe_hari' secara manual di sini ---
    # Karena kolom ini mungkin belum ada di CSV hasil cleaning
    # ====================================================================
    if 'tipe_hari' not in df.columns:
        df['tipe_hari'] = df['hari_kerja_efektif'].apply(
            lambda x: 'Hari Kerja' if x == 1 else 'Hari Libur/Akhir Pekan'
        )

    # --- Sidebar ---
    st.sidebar.image("https://raw.githubusercontent.com/dicodingacademy/assets/main/logo.png", width=150)
    st.sidebar.title("Filter Data 🚲")
    
    min_date = df["tanggal"].min()
    max_date = df["tanggal"].max()

    start_date, end_date = st.sidebar.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    # Filter data
    main_df = df[(df["tanggal"] >= str(start_date)) & 
                 (df["tanggal"] <= str(end_date))]

    # Judul Utama
    st.title('Dashboard Analisis Peminjaman Sepeda')
    st.markdown("---")

    # Metrik
    col1, col2 = st.columns(2)
    with col1:
        total_rides = main_df['total_peminjaman'].sum()
        st.metric("Total Peminjaman", value=f"{total_rides:,.0f}")
    with col2:
        avg_rides = main_df['total_peminjaman'].mean()
        st.metric("Rata-rata Harian", value=f"{avg_rides:,.0f}")

    st.markdown("---")

    # Chart 1: Musim & Cuaca
    st.header('1. Pengaruh Musim & Cuaca')
    
    # Cek agar tidak error saat data kosong karena filter
    if not main_df.empty:
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        sns.barplot(x='musim', y='total_peminjaman', hue='kondisi_cuaca', data=main_df, palette='viridis', ax=ax1)
        ax1.set_title('Peminjaman Berdasarkan Musim dan Cuaca')
        st.pyplot(fig1)
    else:
        st.warning("Data tidak tersedia untuk rentang tanggal yang dipilih.")

    # Chart 2: Pola Pengguna
    st.header('2. Pola Pengguna (Kasual vs Terdaftar)')
    
    if not main_df.empty:
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        
        # Persiapan data untuk chart 2
        plot2_data = main_df.groupby('tipe_hari')[['pengguna_kasual', 'pengguna_terdaftar']].mean().reset_index()
        plot2_melted = plot2_data.melt('tipe_hari', var_name='Tipe Pengguna', value_name='Jumlah')
        
        sns.barplot(x='tipe_hari', y='Jumlah', hue='Tipe Pengguna', data=plot2_melted, palette='muted', ax=ax2)
        ax2.set_title('Perbandingan Pengguna berdasarkan Hari')
        st.pyplot(fig2)

    st.caption('Copyright (c) 2025')
