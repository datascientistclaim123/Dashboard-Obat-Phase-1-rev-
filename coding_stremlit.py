import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Cache untuk membaca dataset
@st.cache_data
def load_data(file_path):
    return pd.read_excel(file_path)

# Load data dari file baru
df = load_data("Data Obat Input Billing Manual.xlsx")  # Ganti dengan path file yang diunggah

# Streamlit App Title
st.title("Dashboard Sebaran Obat di Tiap Rumah Sakit 💊")

# Menampilkan preview data
st.subheader("Preview Data")
st.write(f"Dataset berisi {df.shape[0]} baris dan {df.shape[1]} kolom.")
st.dataframe(df)

# Container untuk mengelola tabel dinamis
tabel_container = st.container()

# State untuk menyimpan jumlah tabel yang ditampilkan
if "table_count" not in st.session_state:
    st.session_state.table_count = 1  # Mulai dengan 1 tabel

# Fungsi untuk menampilkan tabel berdasarkan filter
def display_table(index):
    st.subheader(f"Tabel {index}")
    
    # Filter untuk Group Provider
    selected_group_providers = st.multiselect(
        f"[Tabel {index}] Pilih Group Provider:",
        options=df['GroupProvider'].dropna().unique() if 'GroupProvider' in df.columns else [],
        default=[],
        key=f"group_provider_{index}"
    )

    # Filter untuk Treatment Place
    selected_treatment_places = st.multiselect(
        f"[Tabel {index}] Pilih Treatment Place:",
        options=df['TreatmentPlace'].dropna().unique() if 'TreatmentPlace' in df.columns else [],
        default=[],
        key=f"treatment_place_{index}"
    )

    # Filter data
    filtered_df = df.copy()
    if selected_group_providers:
        filtered_df = filtered_df[filtered_df['GroupProvider'].isin(selected_group_providers)]
    if selected_treatment_places:
        filtered_df = filtered_df[filtered_df['TreatmentPlace'].isin(selected_treatment_places)]

    if filtered_df.empty:
        st.warning(f"Tidak ada data untuk filter di tabel {index}.")
    else:
        # Menampilkan tabel
        st.dataframe(filtered_df, height=300)

        # Total Amount Bill
        if 'Amount Bill' in filtered_df.columns:
            filtered_df['Amount Bill'] = pd.to_numeric(filtered_df['Amount Bill'], errors='coerce').fillna(0)
            total_amount_bill = filtered_df['Amount Bill'].sum()
            formatted_total = f"Rp {total_amount_bill:,.0f}".replace(",", ".")
            st.text(f"Total Amount Bill: {formatted_total}")
        else:
            st.warning("Kolom 'Amount Bill' tidak ditemukan di dataset.")

        # WordCloud
        if 'Nama Item Garda Medika' in filtered_df.columns:
            st.subheader("WordCloud")
            wordcloud_text = " ".join(filtered_df['Nama Item Garda Medika'].dropna().astype(str))
            wordcloud = WordCloud(width=800, height=400, background_color="white").generate(wordcloud_text)

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.warning("Kolom 'Nama Item Garda Medika' tidak ditemukan di dataset.")

# Menampilkan tabel dinamis berdasarkan jumlah tabel di session state
for i in range(1, st.session_state.table_count + 1):
    with tabel_container:
        display_table(i)

# Tombol untuk menambah tabel baru
if st.button("Insert Tabel Baru"):
    st.session_state.table_count += 1