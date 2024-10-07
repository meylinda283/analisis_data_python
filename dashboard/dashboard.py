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
def create_monthly_rentals_df(df):
    # Mengelompokkan data berdasarkan tanggal dan menghitung total penyewaan
    monthly_rentals_df = df.resample(rule='D', on="dteday").agg({
        "cnt": "sum",  # Menghitung total penyewaan
        "casual": "sum",  # Menghitung total penyewaan kasual
        "registered": "sum"  # Menghitung total penyewaan terdaftar
    })
    
    # Mengatur ulang index dan mengganti nama kolom
    monthly_rentals_df = monthly_rentals_df.reset_index()
    monthly_rentals_df.rename(columns={
        "dteday": "month",
        "cnt": "total_rentals",  
        "casual": "casual_rentals",  
        "registered": "registered_rentals"
    }, inplace=True)
    
    return monthly_rentals_df

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
monthly_rentals_df = create_monthly_rentals_df(filtered_df)

st.subheader('Penyewaan Sepeda Bulanan Berdasarkan Rentang Waktu')

# Membuat figure dengan ukuran yang sesuai
plt.figure(figsize=(10, 6))

# Plot penyewaan total bulanan
plt.plot(monthly_rentals_df['month'], monthly_rentals_df['total_rentals'], marker='o', label='Total Rentals', color='#72BCD4')

# Plot penyewaan kasual bulanan
plt.plot(monthly_rentals_df['month'], monthly_rentals_df['casual_rentals'], marker='o', label='Casual Rentals', color='#FFA07A')

# Plot penyewaan terdaftar bulanan
plt.plot(monthly_rentals_df['month'], monthly_rentals_df['registered_rentals'], marker='o', label='Registered Rentals', color='#FF7F50')

# Menambahkan judul dan label sumbu
plt.title('Penyewaan Sepeda Bulanan (2011-2012)', fontsize=16)
plt.xlabel('Bulan', fontsize=14)
plt.ylabel('Jumlah Penyewaan', fontsize=14)

# Menampilkan legenda
plt.legend()

# Mengatur rotasi label x-axis
plt.xticks(rotation=45)

# Menyesuaikan layout agar tidak terpotong
plt.tight_layout()

# Menampilkan plot di Streamlit
st.pyplot(plt)






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

























