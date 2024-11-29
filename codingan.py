import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Fungsi untuk menghitung median berbobot berdasarkan kolom Qty
def weighted_median(group):

    group["Harga Satuan"] = group["Harga Satuan"].fillna(0)
    
    # Urutkan data berdasarkan Harga Satuan
    group = group.sort_values("Harga Satuan").reset_index()
    # Hitung jumlah kumulatif Qty
    group["CumulativeQty"] = group["Qty"].cumsum()
    # Cari total median pada kolom Qty
    median_qty = group["Qty"].sum() / 2
    # Cari baris di mana cumulative Qty melewati median
    median_row = group[group["CumulativeQty"] >= median_qty].iloc[0]
    return median_row["Harga Satuan"]

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

    # Filter data sementara berdasarkan Group Provider
    if selected_group_providers:
        filtered_temp = df[df['GroupProvider'].isin(selected_group_providers)]
    else:
        filtered_temp = df.copy()

    # Filter untuk Treatment Place
    selected_treatment_places = st.multiselect(
        f"[Tabel {index}] Pilih Treatment Place:",
        options=filtered_temp['TreatmentPlace'].dropna().unique() if 'TreatmentPlace' in filtered_temp.columns else [],
        default=[],
        key=f"treatment_place_{index}"
    )

    # Filter untuk Doctor Name, tergantung pada pilihan Treatment Place
    if selected_treatment_places:
        filtered_doctors = filtered_temp[filtered_temp['TreatmentPlace'].isin(selected_treatment_places)]['DoctorName'].dropna().unique()
    else:
        filtered_doctors = filtered_temp['DoctorName'].dropna().unique()

    selected_doctors = st.multiselect(
        f"[Tabel {index}] Pilih Doctor Name:",
        options=filtered_doctors,
        default=[],
        key=f"doctor_name_{index}"
    )

    # Filter untuk Primary Diagnosis, tergantung pada pilihan sebelumnya (Doctor Name dan Treatment Place)
    if selected_doctors:
        filtered_diagnosis = filtered_temp[filtered_temp['DoctorName'].isin(selected_doctors)]['PrimaryDiagnosis'].dropna().unique()
    else:
        filtered_diagnosis = filtered_temp['PrimaryDiagnosis'].dropna().unique()

    selected_diagnosis = st.multiselect(
        f"[Tabel {index}] Pilih Primary Diagnosis:",
        options=filtered_diagnosis,
        default=[],
        key=f"primary_diagnosis_{index}"
    )

    # Filter untuk Product Type, tergantung pada pilihan sebelumnya
    selected_product_types = st.multiselect(
        f"[Tabel {index}] Pilih Product Type:",
        options=filtered_temp['ProductType'].dropna().unique() if 'ProductType' in filtered_temp.columns else [],
        default=[],
        key=f"product_type_{index}"
    )

    # Filter data akhir berdasarkan semua filter
    filtered_df = filtered_temp.copy()
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
            HargaSatuan=('Harga Satuan', weighted_median),  # Gunakan median berbobot
            Golongan=('Golongan', 'first'),  # Mengambil nilai pertama untuk kolom lain yang relevan
            Subgolongan=('Subgolongan', 'first'),
            KomposisiZatAktif=('Komposisi Zat Aktif', 'first')
        ).reset_index()

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
            wordcloud_text = " ".join(grouped_df['Nama Item Garda Medika'].dropna().astype(str))
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
