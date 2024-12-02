import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

# Cache untuk membaca dataset
@st.cache_data
def load_data(file_path):
    return pd.read_excel(file_path)

# Load data dari file baru
df = load_data("Data Obat Input Billing Manual Revisi.xlsx")  # Ganti dengan path file yang diunggah

# Pastikan kolom Qty dan Amount Bill adalah numerik
df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce').fillna(0)
df['Amount Bill'] = pd.to_numeric(df['Amount Bill'], errors='coerce').fillna(0)

# Sidebar untuk navigasi
st.sidebar.title("Navigasi")
selected_page = st.sidebar.radio("Pilih Halaman:", ["Page 1", "Page 2"])

# Page 1
if selected_page == "Page 1":
    st.title("Dashboard Sebaran Obat di Tiap Rumah Sakit 💊")

    # Tambahkan teks kecil untuk "Created by"
    st.markdown("<small>Created by: Dexcel Oswald Otniel</small>", unsafe_allow_html=True)

    # Menampilkan preview data
    st.subheader("Preview Data")
    st.dataframe(df)

    # Container untuk mengelola tabel dinamis
    tabel_container = st.container()

    # State untuk menyimpan jumlah tabel yang ditampilkan
    if "table_count" not in st.session_state:
        st.session_state.table_count = 1  # Mulai dengan 1 tabel

    # Fungsi untuk menampilkan tabel berdasarkan filter
    def display_table(index):
        st.subheader(f"Tabel {index}")
        # (Isi fungsi sama seperti sebelumnya)
        # ...

    # Menampilkan tabel dinamis berdasarkan jumlah tabel di session state
    for i in range(1, st.session_state.table_count + 1):
        with tabel_container:
            display_table(i)

    # Tombol untuk menambah tabel baru
    if st.button("Insert Tabel Baru"):
        st.session_state.table_count += 1

# Page 2
elif selected_page == "Page 2":
    st.title("Page 2: Analisis Tambahan")
    st.write("Ini adalah halaman kedua dalam aplikasi Streamlit Anda.")

    st.subheader("Fitur Analisis Baru")
    st.write("Tambahkan konten atau fitur yang sesuai untuk page 2.")
