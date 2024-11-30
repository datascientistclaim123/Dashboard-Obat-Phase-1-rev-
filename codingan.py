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

# Streamlit App Title
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

        # Total Amount Bill (dalam hal kolom tersebut ada)
        if 'AmountBill' in grouped_df.columns:
            total_amount_bill = grouped_df['AmountBill'].sum()
            formatted_total = f"Rp {total_amount_bill:,.0f}".replace(",", ".")
            st.markdown(f"**Total Amount Bill: {formatted_total}**")
        else:
            st.warning("Kolom 'Amount Bill' tidak ditemukan di dataset.")

        # WordCloud (dalam hal kolom tersebut ada)
        if 'Nama Item Garda Medika' in grouped_df.columns:
            st.subheader("WordCloud")
            
            # Gabungkan semua teks dari kolom 'Nama Item Garda Medika'
            wordcloud_text = " ".join(grouped_df['Nama Item Garda Medika'].dropna().astype(str))
            
            # Daftar kata yang ingin dihapus
            excluded_words = ["FORTE", "PLUS","PLU", "INFLUAN", "INFUSAN", "INFUS", "OTSU", "SP", "D", "S", "XR", "PF", "FC", "FORCE", "B", "C", "P", "OTU", "IRPLU",
                              "N", "G", "ONE", "VIT", "O", "AY", "H","ETA", "WIA", "IV", "IR", "RING", "WATER", "SR", "RL", "PFS", "MR", "DP", "NS", "WIDA" , "E",
                              "Q", "TB", "TABLET", "GP", "MMR", "M", "WI", "Z", "NEO", "MIX", "GRANULE", "TT", "NA", "CL", "L", "FT", "MG", "KID", "HCL", "KIDS", "NEBULE",
                              "DUO", "NEW", "AQUA", "ECOSOL", "NEBULES", "ORAL", "NACL", "KA", "EN", "PAED", "RINGER", "JELLY", "MST", "NTG", "CPG", "AL"]
            
            # Gabungkan semua kata yang akan dihapus menjadi pola regex
            excluded_pattern = r'\b(?:' + '|'.join(map(re.escape, excluded_words)) + r')\b'

            # Hapus kata-kata dalam excluded_words tanpa menghapus bagian dari kata lain
            wordcloud_text = re.sub(excluded_pattern, '', wordcloud_text, flags=re.IGNORECASE)
            
            # Buat WordCloud
            wordcloud = WordCloud(width=800, height=400, background_color="white").generate(wordcloud_text)

            # Tampilkan WordCloud
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
