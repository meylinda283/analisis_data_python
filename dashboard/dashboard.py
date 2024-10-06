import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Mengatur gaya visualisasi seaborn
sns.set(style='dark')

# Menampilkan header untuk dashboard
st.header('Bike Rent Dashboard :sparkles:')

# Fungsi untuk membuat DataFrame penyewaan harian
def create_daily_rentals_df(df):
    # Mengelompokkan data berdasarkan tanggal dan menghitung total penyewaan
    daily_rentals_df = df.resample(rule='D', on="dteday").agg({
        "cnt": "sum",  # Menghitung total penyewaan
        "casual": "sum",  # Menghitung total penyewaan kasual
        "registered": "sum"  # Menghitung total penyewaan terdaftar
    })
    
    # Mengatur ulang index dan mengganti nama kolom
    daily_rentals_df = daily_rentals_df.reset_index()
    daily_rentals_df.rename(columns={
        "dteday": "day",
        "cnt": "total_rentals",  
        "casual": "casual_rentals",  
        "registered": "registered_rentals"
    }, inplace=True)
    
    return daily_rentals_df

# Fungsi untuk membuat DataFrame penyewaan berdasarkan musim
def create_byseason_df(df):
    # Mengelompokkan data berdasarkan musim
    byseason_df = df.groupby(by='season')['cnt'].sum().reset_index()

    # Mengubah angka musim menjadi nama musim
    byseason_df['season'] = byseason_df['season'].map({
        1: 'Spring',
        2: 'Summer',
        3: 'Fall',
        4: 'Winter'
    })
    
    return byseason_df

# Fungsi untuk membuat DataFrame penyewaan berdasarkan kondisi cuaca
def create_byweather_df(df):
    # Mengelompokkan data berdasarkan kondisi cuaca
    byweather_df = df.groupby(by='weathersit')['cnt'].sum().reset_index()

    # Mengubah angka kondisi cuaca menjadi deskripsi
    byweather_df['weathersit'] = byweather_df['weathersit'].map({
        1: 'Clear',
        2: 'Mist',
        3: 'Light Rain/Snow',
        4: 'Heavy Rain/Snow'
    })
    
    return byweather_df

def create_byworkingday_df(df):
    byworkingday_df = df.groupby(by='workingday')['cnt'].sum().reset_index()

    byworkingday_df['workingday'] = byworkingday_df['workingday'].map({
        False: 'Not Working Day',
        True: 'Working Day'
    })
    
    return byworkingday_df
# Fungsi untuk membuat DataFrame RFM (Recency, Frequency, Monetary)
def create_rfm_df(df):
    max_date = df['dteday'].max()  # Mendapatkan tanggal maksimum dari dataset
    df['recency'] = (max_date - df['dteday']).dt.days  # Menghitung recency

    # Menghitung frekuensi penyewaan
    frequency_df = df.groupby('dteday').agg({'cnt': 'sum'}).reset_index()
    frequency_df.rename(columns={'cnt': 'frequency'}, inplace=True)

    # Menghitung monetary penyewaan
    monetary_df = df.groupby('dteday').agg({'cnt': 'sum'}).reset_index()
    monetary_df.rename(columns={'cnt': 'monetary'}, inplace=True)

    # Menggabungkan DataFrame frekuensi dan monetary dengan data recency
    rfm_df = frequency_df.merge(monetary_df, on='dteday').merge(days_df[['dteday', 'recency']], on='dteday')
    rfm_df = rfm_df.drop_duplicates(subset=['dteday'])  # Menghapus duplikasi

    # 4. RFM Scoring
    # Recency: Semakin kecil recency, semakin baik (skor tinggi untuk yang paling baru)
    bins_recency = [0, 30, 90, 180, 365, rfm_df['recency'].max()]
    labels_recency = [5, 4, 3, 2, 1]
    rfm_df['R_Score'] = pd.cut(rfm_df['recency'], bins=bins_recency, labels=labels_recency, right=False)

    # Frequency: Semakin sering penyewaan, semakin tinggi skornya
    bins_frequency = [0, 50, 100, 200, 500, rfm_df['frequency'].max()]
    labels_frequency = [1, 2, 3, 4, 5]
    rfm_df['F_Score'] = pd.cut(rfm_df['frequency'], bins=bins_frequency, labels=labels_frequency, right=False)

    # Monetary: Semakin besar penyewaan, semakin tinggi skornya
    bins_monetary = [0, 50, 100, 200, 500, rfm_df['monetary'].max()]
    labels_monetary = [1, 2, 3, 4, 5]
    rfm_df['M_Score'] = pd.cut(rfm_df['monetary'], bins=bins_monetary, labels=labels_monetary, right=False)

    # 5. Menggabungkan skor RFM menjadi satu kolom
    rfm_df['RFM_Score'] = rfm_df['R_Score'].astype(str) + rfm_df['F_Score'].astype(str) + rfm_df['M_Score'].astype(str)

    return rfm_df
    
# Membaca dataset hari dari file CSV
days_df = pd.read_csv("dashboard\days.csv")

# Mengkonversi kolom 'dteday' menjadi tipe datetime
days_df['dteday'] = pd.to_datetime(days_df['dteday'])
min_date = days_df["dteday"].min()  # Mendapatkan tanggal minimum
max_date = days_df["dteday"].max()  # Mendapatkan tanggal maksimum
 
# Sidebar untuk pengaturan filter
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("dashboard\sepeda.jpeg")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter data berdasarkan rentang tanggal yang dipilih
filtered_df = days_df[(days_df['dteday'] >= pd.to_datetime(start_date)) & (days_df['dteday'] <= pd.to_datetime(end_date))]

# Membuat DataFrame penyewaan harian setelah difilter
daily_rentals_df = create_daily_rentals_df(filtered_df)

# Membuat visualisasi penyewaan sepeda harian setelah difilter
st.subheader('Penyewaan Sepeda Harian Berdasarkan Rentang Waktu')
plt.figure(figsize=(10, 6))
sns.lineplot(x='day', y='total_rentals', data=daily_rentals_df, label='Total Rentals', color='blue')
sns.lineplot(x='day', y='casual_rentals', data=daily_rentals_df, label='Casual Rentals', color='green')
sns.lineplot(x='day', y='registered_rentals', data=daily_rentals_df, label='Registered Rentals', color='orange')
plt.title('Tren Penyewaan Sepeda Harian', fontsize=16)
plt.xlabel('Tanggal', fontsize=14)
plt.ylabel('Jumlah Penyewaan', fontsize=14)
plt.legend()
st.pyplot(plt)  # Menampilkan grafik ke Streamlit

# Membuat DataFrame penyewaan berdasarkan musim setelah difilter
byseason_df = create_byseason_df(filtered_df)

# Visualisasi penyewaan berdasarkan musim
st.subheader('Penyewaan Sepeda Berdasarkan Musim')
plt.figure(figsize=(8, 5))
sns.barplot(x='season', y='cnt', data=byseason_df, palette='coolwarm')
plt.title('Total Penyewaan Sepeda Berdasarkan Musim', fontsize=16)
plt.xlabel('Musim', fontsize=14)
plt.ylabel('Total Penyewaan', fontsize=14)
st.pyplot(plt)  # Menampilkan grafik ke Streamlit

# Menghitung total penyewaan berdasarkan kondisi cuaca
byweather_df = create_byweather_df(filtered_df)

# Membuat plot untuk visualisasi penyewaan berdasarkan cuaca
st.subheader("Total Penyewaan Berdasarkan Cuaca")
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x='weathersit', y='cnt', data=byweather_df, palette='coolwarm', ax=ax)
ax.set_title("Total Penyewaan Sepeda Berdasarkan Cuaca", fontsize=16)
ax.set_xlabel("Kondisi Cuaca", fontsize=14)
ax.set_ylabel("Total Penyewaan", fontsize=14)
st.pyplot(fig)  # Menampilkan grafik ke Streamlit

# Menghitung total penyewaan berdasarkan hari kerja
byworkingday_df = create_byworkingday_df(filtered_df)

# Membuat plot untuk visualisasi penyewaan berdasarkan hari kerja
st.subheader("Total Penyewaan Berdasarkan Hari Kerja")
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x='workingday', y='cnt', data=byworkingday_df, palette='coolwarm', ax=ax)
ax.set_title("Total Penyewaan Sepeda Berdasarkan Hari Kerja", fontsize=16)
ax.set_xlabel("Hari Kerja", fontsize=14)
ax.set_ylabel("Total Penyewaan", fontsize=14)
st.pyplot(fig)  # Menampilkan

# Menghitung RFM
rfm_df = create_rfm_df(filtered_df)

# Menampilkan distribusi frekuensi
st.subheader("Distribusi Frekuensi Penyewaan Sepeda")
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(rfm_df['frequency'], bins=30, kde=True, ax=ax)
ax.set_title("Distribusi Frekuensi Penyewaan Sepeda", fontsize=16)
ax.set_xlabel("Frekuensi Penyewaan", fontsize=14)
ax.set_ylabel("Jumlah Hari", fontsize=14)
st.pyplot(fig)

# Menampilkan distribusi recency
st.subheader("Distribusi Recency Penyewaan Sepeda")
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(rfm_df['recency'], bins=30, kde=True, ax=ax)
ax.set_title("Distribusi Recency Penyewaan Sepeda", fontsize=16)
ax.set_xlabel("Recency (Hari)", fontsize=14)
ax.set_ylabel("Jumlah Hari", fontsize=14)
st.pyplot(fig)

# Menampilkan distribusi monetary
st.subheader("Distribusi Monetary Penyewaan Sepeda")
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(rfm_df['monetary'], bins=30, kde=True, ax=ax)
ax.set_title("Distribusi Monetary Penyewaan Sepeda", fontsize=16)
ax.set_xlabel("Monetary (Jumlah Penyewaan)", fontsize=14)
ax.set_ylabel("Jumlah Hari", fontsize=14)
st.pyplot(fig)

# Menampilkan hasil RFM
st.subheader("Hasil RFM")
st.write(rfm_df[['dteday', 'recency', 'frequency', 'monetary', 'R_Score', 'F_Score', 'M_Score', 'RFM_Score']])

