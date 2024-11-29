import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Cache untuk membaca dataset baru
@st.cache_data
def load_data(file_path):
    return pd.read_excel(file_path)

# Load data dari file baru
df = load_data("/mnt/data/data test.xlsx")  # Ganti dengan path file yang diunggah

# Streamlit App Title
st.title("Dashboard Sebaran Obat di Tiap Rumah Sakit 💊")

# Filter Utama
st.header("Pilih Filter untuk Membandingkan Data")

# Menampilkan semua kolom yang tersedia di dataset
st.subheader("Preview Data")
st.write(f"Dataset berisi {df.shape[0]} baris dan {df.shape[1]} kolom.")
st.dataframe(df)

# Filter untuk Group Provider
if 'GroupProvider' in df.columns:
    selected_group_providers = st.multiselect(
        "Pilih Group Provider:",
        options=df['GroupProvider'].dropna().unique(),
        default=df['GroupProvider'].dropna().unique()[:1]
    )
else:
    selected_group_providers = []
    st.warning("Kolom 'GroupProvider' tidak ditemukan di dataset.")

# Filter untuk Treatment Place
if 'TreatmentPlace' in df.columns:
    selected_treatment_places = st.multiselect(
        "Pilih Treatment Place:",
        options=df['TreatmentPlace'].dropna().unique(),
        default=df['TreatmentPlace'].dropna().unique()[:1]
    )
else:
    selected_treatment_places = []
    st.warning("Kolom 'TreatmentPlace' tidak ditemukan di dataset.")

# Proses Data Filter
@st.cache_data
def filter_data(df, selected_treatment_places, selected_group_providers):
    filtered = df
    if selected_treatment_places:
        filtered = filtered[filtered['TreatmentPlace'].isin(selected_treatment_places)]
    if selected_group_providers:
        filtered = filtered[filtered['GroupProvider'].isin(selected_group_providers)]
    return filtered

filtered_df = filter_data(df, selected_treatment_places, selected_group_providers)

if filtered_df.empty:
    st.warning("Tidak ada data untuk filter yang dipilih.")
else:
    # Tabs untuk perbandingan
    st.header("Perbandingan Data")
    tabs = st.tabs([f"Tab {i+1}" for i in range(len(selected_treatment_places))])

    for i, tab in enumerate(tabs):
        with tab:
            treatment = selected_treatment_places[i] if selected_treatment_places else "Semua Treatment"
            subset = filtered_df[filtered_df['TreatmentPlace'] == treatment] if selected_treatment_places else filtered_df

            st.subheader(f"Tabel Data untuk {treatment}")
            st.dataframe(subset, height=300)  # Menampilkan semua kolom

            if 'Amount Bill' in subset.columns:
                total_amount_bill = subset['Amount Bill'].sum()
                formatted_total_amount_bill = f"Rp {total_amount_bill:,.0f}".replace(",", ".")
                st.text(f"Total Amount Bill: {formatted_total_amount_bill}")
            else:
                st.warning("Kolom 'Amount Bill' tidak ditemukan di dataset.")

            if 'Nama Item Garda Medika' in subset.columns:
                # WordCloud
                st.subheader("WordCloud")
                wordcloud_text = " ".join(subset['Nama Item Garda Medika'].dropna().astype(str))
                wordcloud = WordCloud(width=800, height=400, background_color="white").generate(wordcloud_text)
                
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig)
            else:
                st.warning("Kolom 'Nama Item Garda Medika' tidak ditemukan di dataset.")
