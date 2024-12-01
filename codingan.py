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

if selected_page == "Page 1":
    # Page 1: Dashboard Sebaran Obat
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

        # Ambil filter dari session_state jika ada
        selected_group_providers = st.session_state.get(f"group_provider_{index}", [])
        selected_treatment_places = st.session_state.get(f"treatment_place_{index}", [])
        selected_doctors = st.session_state.get(f"doctor_name_{index}", [])
        selected_diagnosis = st.session_state.get(f"primary_diagnosis_{index}", [])
        selected_product_types = st.session_state.get(f"product_type_{index}", [])

        # Filter data berdasarkan semua pilihan saat ini
        filtered_df = df.copy()
        if selected_group_providers:
            filtered_df = filtered_df[filtered_df['GroupProvider'].isin(selected_group_providers)]
        if selected_treatment_places:
            filtered_df = filtered_df[filtered_df['TreatmentPlace'].isin(selected_treatment_places)]
        if selected_doctors:
            filtered_df = filtered_df[filtered_df['DoctorName'].isin(selected_doctors)]
        if selected_diagnosis:
            filtered_df = filtered_df[filtered_df['PrimaryDiagnosis'].isin(selected_diagnosis)]
        if selected_product_types:
            filtered_df = filtered_df[filtered_df['ProductType'].isin(selected_product_types)]

        # Pilihan untuk setiap filter berdasarkan data yang sudah difilter
        group_provider_options = filtered_df['GroupProvider'].dropna().unique()
        treatment_place_options = filtered_df['TreatmentPlace'].dropna().unique()
        doctor_options = filtered_df['DoctorName'].dropna().unique()
        diagnosis_options = filtered_df['PrimaryDiagnosis'].dropna().unique()
        product_type_options = filtered_df['ProductType'].dropna().unique()

        # Komponen filter
        selected_group_providers = st.multiselect(
            f"[Tabel {index}] Pilih Group Provider:",
            options=group_provider_options,
            default=selected_group_providers,
            key=f"group_provider_{index}"
        )
        selected_treatment_places = st.multiselect(
            f"[Tabel {index}] Pilih Treatment Place:",
            options=treatment_place_options,
            default=selected_treatment_places,
            key=f"treatment_place_{index}"
        )
        selected_doctors = st.multiselect(
            f"[Tabel {index}] Pilih Doctor Name:",
            options=doctor_options,
            default=selected_doctors,
            key=f"doctor_name_{index}"
        )
        selected_diagnosis = st.multiselect(
            f"[Tabel {index}] Pilih Primary Diagnosis:",
            options=diagnosis_options,
            default=selected_diagnosis,
            key=f"primary_diagnosis_{index}"
        )
        selected_product_types = st.multiselect(
            f"[Tabel {index}] Pilih Product Type:",
            options=product_type_options,
            default=selected_product_types,
            key=f"product_type_{index}"
        )

        # Filter ulang data berdasarkan input terbaru
        filtered_df = df.copy()
        if selected_group_providers:
            filtered_df = filtered_df[filtered_df['GroupProvider'].isin(selected_group_providers)]
        if selected_treatment_places:
            filtered_df = filtered_df[filtered_df['TreatmentPlace'].isin(selected_treatment_places)]
        if selected_doctors:
            filtered_df = filtered_df[filtered_df['DoctorName'].isin(selected_doctors)]
        if selected_diagnosis:
            filtered_df = filtered_df[filtered_df['PrimaryDiagnosis'].isin(selected_diagnosis)]
        if selected_product_types:
            filtered_df = filtered_df[filtered_df['ProductType'].isin(selected_product_types)]

        if filtered_df.empty:
            st.warning(f"Tidak ada data untuk filter di tabel {index}.")
        else:
            # Mengelompokkan berdasarkan "Nama Item Garda Medika"
            grouped_df = filtered_df.groupby("Nama Item Garda Medika").agg(
                Qty=('Qty', 'sum'),
                AmountBill=('Amount Bill', 'sum'),
                HargaSatuan=('Harga Satuan', 'median'),
                Golongan=('Golongan', 'first'),
                Subgolongan=('Subgolongan', 'first'),
                KomposisiZatAktif=('Komposisi Zat Aktif', 'first')
            ).reset_index()

            # Hilangkan desimal dengan pembulatan
            grouped_df['Qty'] = grouped_df['Qty'].astype(int)
            grouped_df['AmountBill'] = grouped_df['AmountBill'].astype(int)
            grouped_df['HargaSatuan'] = grouped_df['HargaSatuan'].fillna(0).round(0).astype(int)

            # Pindahkan kolom Qty, Amount Bill, dan Harga Satuan ke paling kanan
            column_order = [
                col for col in grouped_df.columns if col not in ['Qty', 'AmountBill', 'HargaSatuan']
            ] + ['Qty', 'AmountBill', 'HargaSatuan']
            grouped_df = grouped_df[column_order]

            # Menampilkan tabel yang sudah digabungkan
            st.dataframe(grouped_df, height=300)

            # Total Amount Bill
            total_amount_bill = grouped_df['AmountBill'].sum()
            formatted_total = f"Rp {total_amount_bill:,.0f}".replace(",", ".")
            st.markdown(f"**Total Amount Bill: {formatted_total}**")

            # WordCloud
            wordcloud_text = " ".join(grouped_df['Nama Item Garda Medika'].dropna().astype(str))
            wordcloud = WordCloud(width=800, height=400, background_color="white").generate(wordcloud_text)
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)

    # Menampilkan tabel dinamis
    for i in range(1, st.session_state.table_count + 1):
        with tabel_container:
            display_table(i)

    # Tombol untuk menambah tabel baru
    if st.button("Insert Tabel Baru"):
        st.session_state.table_count += 1

elif selected_page == "Page 2":
    # Page 2: Analisis Tambahan
    st.title("Page 2: Pencarian Data Berdasarkan Kriteria")

    # Tambahkan teks kecil untuk "Created by"
    st.markdown("<small>Created by: Dexcel Oswald Otniel</small>", unsafe_allow_html=True)

    # Inisialisasi data terfilter
    filtered_df = df.copy()

    # Pilihan filter berdasarkan kolom yang relevan
    selected_items = st.multiselect(
        "Cari di kolom 'Nama Item Garda Medika':",
        options=filtered_df['Nama Item Garda Medika'].dropna().unique(),
        default=[],
        key="filter_items"
    )
    if selected_items:
        filtered_df = filtered_df[filtered_df['Nama Item Garda Medika'].isin(selected_items)]

    selected_golongan = st.multiselect(
        "Cari di kolom 'Golongan':",
        options=filtered_df['Golongan'].dropna().unique(),
        default=[],
        key="filter_golongan"
    )
    if selected_golongan:
        filtered_df = filtered_df[filtered_df['Golongan'].isin(selected_golongan)]

    selected_subgolongan = st.multiselect(
        "Cari di kolom 'Subgolongan':",
        options=filtered_df['Subgolongan'].dropna().unique(),
        default=[],
        key="filter_subgolongan"
    )
    if selected_subgolongan:
        filtered_df = filtered_df[filtered_df['Subgolongan'].isin(selected_subgolongan)]

    selected_komposisi = st.multiselect(
        "Cari di kolom 'Komposisi Zat Aktif':",
        options=filtered_df['Komposisi Zat Aktif'].dropna().unique(),
        default=[],
        key="filter_komposisi"
    )
    if selected_komposisi:
        filtered_df = filtered_df[filtered_df['Komposisi Zat Aktif'].isin(selected_komposisi)]

    # Tampilkan hasil filter
    if filtered_df.empty:
        st.warning("Tidak ada data yang cocok dengan kriteria pencarian.")
    else:
        # Kolom yang akan ditampilkan di hasil pencarian
        display_columns = ['GroupProvider', 'TreatmentPlace', 'DoctorName']
        result_df = filtered_df[display_columns].drop_duplicates()

        st.subheader("Hasil Pencarian Berdasarkan Filter")
        st.dataframe(result_df)

        # Total jumlah entri yang ditampilkan
        total_entries = len(result_df)
        st.markdown(f"**Total hasil: {total_entries} entri.**")
