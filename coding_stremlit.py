import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Cache untuk membaca dataset
@st.cache_data
def load_data():
    return pd.read_excel('Data Obat Input Billing Manual.xlsx')

df = load_data()

# Streamlit App Title
st.title("Dashboard Sebaran Obat di Tiap Rumah Sakit 💊")

# Filter Utama
st.header("Pilih Filter untuk Membandingkan Data")

# Filter untuk Group Provider
selected_group_providers = st.multiselect(
    "Pilih Group Provider:",
    options=df['GroupProvider'].dropna().unique(),
    default=df['GroupProvider'].dropna().unique()[:1]
)

# Filter untuk Treatment Place
selected_treatment_places = st.multiselect(
    "Pilih Treatment Place:",
    options=df['TreatmentPlace'].dropna().unique(),
    default=df['TreatmentPlace'].dropna().unique()[:1]
)



# Proses Data Filter
@st.cache_data
def filter_data(selected_treatment_places, selected_group_providers):
    return df[
        (df['TreatmentPlace'].isin(selected_treatment_places)) &
        (df['GroupProvider'].isin(selected_group_providers))
    ]

filtered_df = filter_data(selected_treatment_places, selected_group_providers)

if filtered_df.empty:
    st.warning("Tidak ada data untuk filter yang dipilih.")
else:
    # Tabs untuk perbandingan
    st.header("Perbandingan Data")
    tabs = st.tabs([f"Tab {i+1}" for i in range(len(selected_treatment_places))])

    for i, tab in enumerate(tabs):
        with tab:
            treatment = selected_treatment_places[i]
            subset = filtered_df[filtered_df['TreatmentPlace'] == treatment]

            st.subheader(f"Tabel Data untuk {treatment}")
            st.dataframe(subset[['TreatmentPlace', 'GroupProvider', 'Nama Item Garda Medika', 'Qty', 'Amount Bill']], height=300)
            
            total_amount_bill = subset['Amount Bill'].sum()
            formatted_total_amount_bill = f"Rp {total_amount_bill:,.0f}".replace(",", ".")
            st.text(f"Total Amount Bill: {formatted_total_amount_bill}")

            # WordCloud
            st.subheader("WordCloud")
            wordcloud_text = " ".join(subset['Nama Item Garda Medika'].dropna().astype(str))
            wordcloud = WordCloud(width=800, height=400, background_color="white").generate(wordcloud_text)
            
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)
