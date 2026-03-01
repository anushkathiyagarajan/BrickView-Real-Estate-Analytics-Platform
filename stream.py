import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px


# PAGE CONFIG
st.set_page_config(page_title="BrickView Dashboard", layout="wide")
st.title("🏠 BrickView Real Estate Dashboard")


# DATABASE CONNECTION

def get_connection():

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Anushka@21",  
        database="brickview"
    )

try:
    conn = get_connection()
    st.success("✅ Connected to MySQL!")
except mysql.connector.Error as e:
    st.error(f"❌ Connection failed: {e}")
conn = get_connection()

# SIDEBAR FILTERS
st.sidebar.header("🎛️ Filters")

# City filter
city_df = pd.read_sql("SELECT DISTINCT City FROM clean_listings", conn)
selected_cities = st.sidebar.multiselect("Select City", city_df["City"])

# Property Type
type_df = pd.read_sql("SELECT DISTINCT Property_Type FROM clean_listings", conn)
selected_type = st.sidebar.selectbox("Property Type", ["All"] + list(type_df["Property_Type"]))

# Price Range
price_df = pd.read_sql("SELECT MIN(Price) as min_price, MAX(Price) as max_price FROM clean_listings", conn)
min_price = int(price_df["min_price"][0])
max_price = int(price_df["max_price"][0])

price_range = st.sidebar.slider(
    "Price Range",
    min_price,
    max_price,
    (min_price, max_price)
)


# BUILD DYNAMIC QUERY
query = f"""
SELECT *
FROM clean_listings
WHERE Price BETWEEN {price_range[0]} AND {price_range[1]}
"""

if selected_cities:
    cities_str = ",".join([f"'{c}'" for c in selected_cities])
    query += f" AND City IN ({cities_str})"

if selected_type != "All":
    query += f" AND Property_Type = '{selected_type}'"

df = pd.read_sql(query, conn)


# KPI SECTION
col1, col2, col3 = st.columns(3)
col1.metric("Total Listings", len(df))
col2.metric("Average Price", f"₹ {int(df['Price'].mean()) if not df.empty else 0}")
col3.metric("Max Price", f"₹ {int(df['Price'].max()) if not df.empty else 0}")


#MAP VISUALIZATION
map_df = pd.read_sql("""
    SELECT Listing_ID, City, Price, Property_Type, Latitude, Longitude
    FROM clean_listings
""", conn)

# Convert to numeric
map_df["Latitude"] = pd.to_numeric(map_df["Latitude"], errors="coerce")
map_df["Longitude"] = pd.to_numeric(map_df["Longitude"], errors="coerce")

map_df = map_df.dropna(subset=["Latitude", "Longitude"])

st.write("Rows used for map:", len(map_df))

fig_map = px.scatter_map(
    map_df,
    lat="Latitude",
    lon="Longitude",
    hover_name="City",
    zoom=3,
    height=500,
)

fig_map.update_layout(map_style="open-street-map")

st.plotly_chart(fig_map, width="stretch")


# BAR CHART
if not df.empty:
    st.subheader("📊 Listings by City")

    city_count = df.groupby("City").size().reset_index(name="Count")
    fig_bar = px.bar(city_count, x="City", y="Count", text="Count")
    st.plotly_chart(fig_bar, use_container_width=True)


# PIE CHART
if not df.empty:
    st.subheader("🥧 Property Type Distribution")

    type_dist = df["Property_Type"].value_counts().reset_index()
    type_dist.columns = ["Property_Type", "Count"]

    fig_pie = px.pie(type_dist, names="Property_Type", values="Count")
    st.plotly_chart(fig_pie, use_container_width=True)


# MONTHLY SALES TREND
st.subheader("📈 Monthly Sales Trend")

sales_query = """
SELECT DATE_FORMAT(Date_Sold, '%Y-%m') AS Month,
COUNT(*) AS Total_Sales
FROM clean_sales
GROUP BY Month
ORDER BY Month
"""

sales_df = pd.read_sql(sales_query, conn)

if not sales_df.empty:
    fig_line = px.line(sales_df, x="Month", y="Total_Sales", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)


# DATA TABLE
st.subheader("📋 Filtered Listings Table")
st.dataframe(df, use_container_width=True)


# DOWNLOAD BUTTON
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇ Download Filtered Data",
    data=csv,
    file_name="filtered_listings.csv",
    mime="text/csv"
)