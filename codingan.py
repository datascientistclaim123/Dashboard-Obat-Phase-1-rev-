import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

# Cache untuk membaca dataset
@st.cache_data
def load_data(file_path):
    return pd.read_excel(file_path)

# Load data dari file
df = load_data("Data Obat Input Billing Manual Revisi.xlsx")  # Ganti dengan path file Anda

# Pastikan kolom Qty dan Amount Bill adalah numerik
df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce').fillna(0)
df['Amount Bill'] = pd.to_numeric(df['Amount Bill'], errors='coerce').fillna(0)

# Sidebar untuk navigasi
st.sidebar.title("Navigasi")
selected_page = st.sidebar.radio(
    "Pilih Halaman:", 
    ["Distribusi Penggunaan Obat per Provider", "Distribusi Provider Berdasarkan Obat"]
)

# Fungsi untuk filter data dan menampilkan tabel
def display_table(
    filtered_df, 
    filter_columns, 
    group_by_column, 
    aggregation_map, 
    title
):
    st.subheader(title)

    # Buat filter dinamis berdasarkan kolom yang ditentukan
    for col in filter_columns:
        options = filtered_df[col].dropna().unique()
        selected_options = st.multiselect(
            f"Pilih {col}:",
            options=options,
            default=[],
            key=f"filter_{col}"
        )
        if selected_options:
            filtered_df = filtered_df[filtered_df[col].isin(selected_options)]
    
    if filtered_df.empty:
        st.warning("Tidak ada data yang sesuai dengan filter.")
        return

    # Agregasi data
    grouped_df = filtered_df.groupby(group_by_column).agg(aggregation_map).reset_index()

    # Ubah tipe data kolom hasil agregasi
    if 'Qty' in grouped_df.columns:
        grouped_df['Qty'] = grouped_df['Qty'].astype(int)
    if 'AmountBill' in grouped_df.columns:
        grouped_df['AmountBill'] = grouped_df['AmountBill'].astype(int)
    if 'HargaSatuan' in grouped_df.columns:
        grouped_df['HargaSatuan'] = grouped_df['HargaSatuan'].fillna(0).round(0).astype(int)

    # Tampilkan tabel
    st.dataframe(grouped_df, height=300)

    # Total Amount Bill
    if 'AmountBill' in grouped_df.columns:
        total_amount_bill = grouped_df['AmountBill'].sum()
        formatted_total = f"Rp {total_amount_bill:,.0f}".replace(",", ".")
        st.markdown(f"**Total Amount Bill: {formatted_total}**")
    else:
        st.warning("Kolom 'Amount Bill' tidak ditemukan di dataset.")

    # WordCloud
    st.subheader("WordCloud")
    wordcloud_text = " ".join(grouped_df[group_by_column].dropna().astype(str))

    # Daftar kata yang ingin dihapus
    excluded_words = [
        "FORTE", "PLUS", "TABLET", "MG", "ML", "KAPSUL", "SYRUP", 
        "INJECTION", "FORCE", "D", "S", "IV", "NS", "RL", "SODIUM"
    ]
    excluded_pattern = r'\b(?:' + '|'.join(map(re.escape, excluded_words)) + r')\b'
    wordcloud_text = re.sub(excluded_pattern, '', wordcloud_text, flags=re.IGNORECASE)

    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(wordcloud_text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

# Halaman 1: Distribusi Penggunaan Obat per Provider
if selected_page == "Distribusi Penggunaan Obat per Provider":
    st.title("Dashboard Sebaran Obat di Tiap Provider 💊")
    st.dataframe(df)  # Preview data
    display_table(
        filtered_df=df.copy(),
        filter_columns=['GroupProvider', 'TreatmentPlace', 'DoctorName', 'PrimaryDiagnosis', 'ProductType'],
        group_by_column="Nama Item Garda Medika",
        aggregation_map={
            "Qty": ('Qty', 'sum'),
            "AmountBill": ('Amount Bill', 'sum'),
            "HargaSatuan": ('Harga Satuan', 'median'),
            "Golongan": ('Golongan', 'first'),
            "Subgolongan": ('Subgolongan', 'first'),
            "KomposisiZatAktif": ('Komposisi Zat Aktif', 'first')
        },
        title="Tabel Sebaran Penggunaan Obat per Provider"
    )
