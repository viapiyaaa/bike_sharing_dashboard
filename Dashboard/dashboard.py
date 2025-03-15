import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

day_df = pd.read_csv("day_data.csv")
hour_df = pd.read_csv("hour_data.csv")

def create_classify_day(row):
    if row["holiday"] == 1:
        return "Holiday"
    elif row["weekday"] in [0, 6]:
        return "Weekend"
    else:
        return "Workday"

day_df["day_type"] = day_df.apply(create_classify_day, axis=1)

def categorize_time(time_category, column="hr"):
    bins = [0, 6, 12, 16, 19, 24]
    labels = ["Dini Hari", "Pagi", "Siang", "Sore", "Malam"]
    hour_df["time_category"] = pd.cut(hour_df[column], bins=bins, labels=labels, right=False)
    return time_category

def get_category_count(day_df, column="day_type", value_column="cnt"):
    return day_df.groupby([column])[value_column].sum().reset_index()

def get_category_avg(day_df, column="day_type", value_column="cnt"):
    return day_df.groupby([column, "dteday"])[value_column].mean().reset_index()

def create_time_distribution(df, column="time_category", value_column="cnt"):
    return df.groupby(column)[value_column].sum().reset_index()


time_distribution = hour_df.groupby("time_category")["cnt"].sum().reset_index()
time_counts = hour_df["time_category"].value_counts().reset_index()
time_counts.columns = ["time_category", "count"]
time_analysis = time_distribution.merge(time_counts, on="time_category")
time_analysis["avg_peminjaman"] = time_analysis["cnt"] / time_analysis["count"]

# mengurutkan DataFrame berdasarkan order_date serta memastikan kedua kolom tersebut bertipe datetime
datetime_columns = ["dteday"]
day_df.sort_values(by="dteday", inplace=True)
day_df.reset_index(inplace=True)
 
for column in datetime_columns:
    day_df[column] = pd.to_datetime(day_df[column])
    
# Membuat Komponen Filter
min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

st.header('📊 Bicycle Distribution Dashboard')
with st.sidebar:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.jpg")
        
        # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# start_date dan end_date di atas akan digunakan untuk memfilter all_dfS
main_df = day_df[(day_df["dteday"] >= str(start_date)) & 
                (day_df["dteday"] <= str(end_date))]

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter dataset berdasarkan rentang tanggal yang dipilih
filtered_df = day_df[(day_df["dteday"] >= start_date) & (day_df["dteday"] <= end_date)]

st.subheader("📌 Loan Amount and Bike Rental Customers")
col1, col2, col3 = st.columns(3)
with col1:
    total_rentals = main_df["cnt"].sum()
    print(f"Total Peminjaman: {total_rentals}")
    st.metric("Total Peminjaman", f"{total_rentals:,.0f}")
with col2:
    total_customers_casual = main_df["casual"].sum () 
    print(f"Total Customers Casual: {total_customers_casual}")
    st.metric("Total Customers Casual", f"{total_customers_casual:,.0f}")
with col3:
    total_customers_registered = main_df["registered"].sum()
    print(f"Total Customers Registered: {total_customers_registered}")
    st.metric("Total Customers Registered", f"{total_customers_registered:,.0f}")

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(filtered_df["dteday"], filtered_df["cnt"], marker="o", linestyle="-", color="#90CAF9", label="Jumlah Peminjaman")

ax.set_xlabel("Tanggal")
ax.set_ylabel("Jumlah Peminjaman")
ax.set_title("Tren Peminjaman Berdasarkan Rentang Waktu")
plt.xticks(rotation=45)
ax.legend()

with st.container():
    st.pyplot(fig)
        
# Average Bike Rentals by Day Classification
st.subheader("📌 Average Bike Rentals by Day Classification")
category_avg = get_category_avg(filtered_df, column="day_type", value_column="cnt")
category_avg_summary = category_avg.groupby("day_type")["cnt"].mean().reset_index()

col1, col2, col3 = st.columns(3)
with col1:
    holiday_value = category_avg_summary.loc[category_avg_summary["day_type"] == "Holiday", "cnt"].values[0]
    st.metric("Holiday", f"{holiday_value:,.0f}")
with col2:
    weekend_value = category_avg_summary.loc[category_avg_summary["day_type"] == "Weekend", "cnt"].values[0]
    st.metric("Weekend", f"{weekend_value:,.0f}")
with col3:
    workday_value = category_avg_summary.loc[category_avg_summary["day_type"] == "Workday", "cnt"].values[0]
    st.metric("Workday", f"{workday_value:,.0f}")

filtered_category_avg = category_avg[
    (category_avg["dteday"] >= start_date) & (category_avg["dteday"] <= end_date)
]

fig, ax = plt.subplots(figsize=(7, 5)) 
sns.barplot(
    x="day_type", y="cnt", data=filtered_category_avg, color="#90CAF9", ax=ax, errorbar=None
)

st.pyplot(fig)

# Average Bike Rentals by Time Category
st.subheader("📌 Average Bike Rentals by Time Category")
hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])
filtered_hour_df = hour_df[(hour_df["dteday"] >= start_date) & (hour_df["dteday"] <= end_date)]

time_distribution = filtered_hour_df.groupby("time_category")["cnt"].mean().reset_index()

time_analysis = time_distribution.rename(columns={"cnt": "avg_peminjaman"})

labels = ["Dini Hari", "Pagi", "Siang", "Sore", "Malam"]

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    dini_hari_value = time_analysis[time_analysis["time_category"] == "Dini Hari"]["avg_peminjaman"].values
    st.metric("Dini Hari", f"{dini_hari_value[0]:,.0f}")
with col2:
    pagi_value = time_analysis[time_analysis["time_category"] == "Pagi"]["avg_peminjaman"].values
    st.metric("Pagi", f"{pagi_value[0]:,.0f}")
with col3:
    siang_value = time_analysis[time_analysis["time_category"] == "Siang"]["avg_peminjaman"].values
    st.metric("Siang", f"{siang_value[0]:,.0f}")
with col4:
    sore_value = time_analysis[time_analysis["time_category"] == "Sore"]["avg_peminjaman"].values
    st.metric("Sore", f"{sore_value[0]:,.0f}")
with col5:
    malam_value = time_analysis[time_analysis["time_category"] == "Malam"]["avg_peminjaman"].values
    st.metric("Malam", f"{malam_value[0]:,.0f}")

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x="time_category", y="avg_peminjaman", data=time_analysis, order=labels, color="#90CAF9", ax=ax)

st.pyplot(fig)