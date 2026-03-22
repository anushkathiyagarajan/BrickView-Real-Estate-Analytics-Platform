import streamlit as st
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
import plotly.express as px


# PAGE CONFIG
st.set_page_config(page_title="BrickView Dashboard", layout="wide")
st.title("🏠 BrickView Real Estate Dashboard")


# DATABASE CONNECTION

def get_connection():

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Anushka_21",  
        database="brickview"
    )

conn = get_connection()

# DATABASE CONNECTION
engine = create_engine("mysql+pymysql://root:Anushka_21@localhost/brickview")

st.title("📊 Real Estate SQL Query Dashboard")

# SQL QUERIES DICTIONARY

queries = {

"Average Listing Price by City": """
SELECT City, AVG(Price) AS Avg_Price
FROM clean_listings
GROUP BY City
ORDER BY Avg_Price DESC;
""",

"Average Price per Sqft by Property Type": """
SELECT Property_Type,
       AVG(Price / Sqft) AS Avg_Price_per_Sqft
FROM clean_listings
GROUP BY Property_Type;
""",

"Furnishing Status Impact on Price": """
SELECT pa.furnishing_status,
       AVG(l.Price) AS Avg_Price
FROM clean_listings l
JOIN clean_attributes pa
ON l.Listing_ID = pa.listing_id
GROUP BY pa.furnishing_status;
""",

"Metro Distance vs Price": """
SELECT 
    CASE 
        WHEN metro_distance_km <= 1 THEN 'Very Close'
        WHEN metro_distance_km <= 5 THEN 'Moderate'
        ELSE 'Far'
    END AS Metro_Category,
    AVG(l.Price) AS Avg_Price
FROM clean_listings l
JOIN clean_attributes pa
ON l.Listing_ID = pa.listing_id
GROUP BY Metro_Category;
""",

"Rented vs Non-Rented Pricing": """
SELECT pa.is_rented,
       AVG(l.Price) AS Avg_Price
FROM clean_listings l
JOIN clean_attributes pa
ON l.Listing_ID = pa.listing_id
GROUP BY pa.is_rented;
""",

"Bedrooms & Bathrooms vs Price": """
SELECT 
    pa.bedrooms,
    pa.bathrooms,
    AVG(l.Price) AS Avg_Price
FROM clean_listings l
JOIN clean_attributes pa
ON l.Listing_ID = pa.listing_id
GROUP BY pa.bedrooms, pa.bathrooms
ORDER BY pa.bedrooms, pa.bathrooms;
""",

"Parking & Power Backup Impact": """
SELECT 
    pa.parking_available,
    pa.power_backup,
    AVG(l.Price) AS Avg_Price
FROM clean_listings l
JOIN clean_attributes pa
ON l.Listing_ID = pa.listing_id
GROUP BY pa.parking_available, pa.power_backup;
""",

"Year Built Influence on Price": """
SELECT 
    pa.year_built,
    AVG(l.Price) AS Avg_Price
FROM clean_listings l
JOIN clean_attributes pa
ON l.Listing_ID = pa.listing_id
GROUP BY pa.year_built
ORDER BY pa.year_built DESC;
""",

"Highest Median Price Cities": """
SELECT City, AVG(Price) AS Avg_Price
FROM clean_listings
GROUP BY City
ORDER BY Avg_Price DESC;
""",

"Property Distribution by Price Bucket": """
SELECT 
    CASE 
        WHEN Price < 5000000 THEN 'Low'
        WHEN Price BETWEEN 5000000 AND 10000000 THEN 'Medium'
        ELSE 'High'
    END AS Price_Category,
    COUNT(*) AS Property_Count
FROM clean_listings
GROUP BY Price_Category;
""",

"Average Days on Market by City": """
SELECT 
    l.City,
    AVG(s.Days_on_Market) AS Avg_Days_On_Market
FROM clean_sales s
JOIN clean_listings l 
ON s.Listing_ID = l.Listing_ID
GROUP BY l.City
ORDER BY Avg_Days_On_Market DESC;
""",

"Fastest Selling Property Types": """
SELECT 
    l.Property_Type,
    AVG(s.Days_on_Market) AS Avg_Days
FROM clean_sales s
JOIN clean_listings l 
ON s.Listing_ID = l.Listing_ID
GROUP BY l.Property_Type
ORDER BY Avg_Days ASC;
""",

"Percentage Sold Above Listing Price": """
SELECT 
    (COUNT(CASE WHEN s.Sale_Price > l.Price THEN 1 END) * 100.0 
     / COUNT(*)) AS Percentage_Above_List
FROM clean_sales s
JOIN clean_listings l 
ON s.Listing_ID = l.Listing_ID;
""",

"Sale to List Price Ratio by City": """
SELECT 
    l.City,
    AVG(s.Sale_Price / l.Price) AS Price_Ratio
FROM clean_sales s
JOIN clean_listings l 
ON s.Listing_ID = l.Listing_ID
GROUP BY l.City
ORDER BY Price_Ratio DESC;
""",

"Metro Distance vs Time on Market": """
SELECT 
    CASE 
        WHEN pa.metro_distance_km <= 1 THEN 'Very Close'
        WHEN pa.metro_distance_km <= 5 THEN 'Moderate'
        ELSE 'Far'
    END AS Metro_Category,
    AVG(s.Days_on_Market) AS Avg_Days_On_Market
FROM clean_sales s
JOIN clean_listings l 
    ON s.Listing_ID = l.Listing_ID
JOIN clean_attributes pa
    ON l.Listing_ID = pa.listing_id
GROUP BY Metro_Category
ORDER BY Avg_Days_On_Market;
""",

"Listings Sold After 90 Days": """
SELECT 
    l.Listing_ID,
    l.City,
    s.Days_on_Market
FROM clean_sales s
JOIN clean_listings l 
ON s.Listing_ID = l.Listing_ID
WHERE s.Days_on_Market > 90;
""",

"Monthly Sales Trend": """
SELECT 
    DATE_FORMAT(Date_Sold, '%%Y-%%m-%%d') AS Sale_Month,
    COUNT(*) AS Total_Sales
FROM clean_sales
GROUP BY Sale_Month
ORDER BY Sale_Month;
""",

"Currently Unsold Properties": """
SELECT 
    l.Listing_ID,
    l.City,
    l.Price
FROM clean_listings l
LEFT JOIN clean_sales s
ON l.Listing_ID = s.Listing_ID
WHERE s.Listing_ID IS NULL;
""",

"Agents with Most Sales": """
SELECT 
    a.Agent_ID,
    a.Name,
    COUNT(*) AS Total_Sales_Closed
FROM clean_agents a
JOIN clean_listings l 
    ON a.Agent_ID = l.Agent_ID
JOIN clean_sales s 
    ON l.Listing_ID = s.Listing_ID
GROUP BY a.Agent_ID, a.Name
ORDER BY Total_Sales_Closed DESC;
""",

"Top Agents by Revenue": """
SELECT 
    a.Agent_ID,
    a.Name,
    SUM(s.Sale_Price) AS Total_Revenue
FROM clean_agents a
JOIN clean_listings l 
    ON a.Agent_ID = l.Agent_ID
JOIN clean_sales s 
    ON l.Listing_ID = s.Listing_ID
GROUP BY a.Agent_ID, a.Name
ORDER BY Total_Revenue DESC;
""",

"Agents Closing Deals Fastest": """
SELECT 
    a.Agent_ID,
    a.Name,
    AVG(s.Days_on_Market) AS Avg_Closing_Time
FROM clean_agents a
JOIN clean_listings l 
    ON a.Agent_ID = l.Agent_ID
JOIN clean_sales s 
    ON l.Listing_ID = s.Listing_ID
GROUP BY a.Agent_ID, a.Name
ORDER BY Avg_Closing_Time ASC;
""",

"Agent Experience vs Deals Closed": """
SELECT 
    experience_years,
    deals_closed
FROM clean_agents
ORDER BY experience_years;
""",

"Agent Ratings vs Closing Time": """
SELECT 
    a.rating,
    AVG(s.Days_on_Market) AS Avg_Closing_Time
FROM clean_agents a
JOIN clean_listings l 
    ON a.Agent_ID = l.Agent_ID
JOIN clean_sales s 
    ON l.Listing_ID = s.Listing_ID
GROUP BY a.rating
ORDER BY a.rating DESC;
""",

"Average Commission by Agent": """
SELECT 
    a.Agent_ID,
    a.Name,
    AVG(s.Sale_Price * a.commission_rate / 100) AS Avg_Commission
FROM clean_agents a
JOIN clean_listings l 
    ON a.Agent_ID = l.Agent_ID
JOIN clean_sales s 
    ON l.Listing_ID = s.Listing_ID
GROUP BY a.Agent_ID, a.Name
ORDER BY Avg_Commission DESC;
""",

"Agents with Most Active Listings": """
SELECT 
    a.Agent_ID,
    a.Name,
    COUNT(l.Listing_ID) AS Active_Listings
FROM clean_agents a
JOIN clean_listings l 
    ON a.Agent_ID = l.Agent_ID
LEFT JOIN clean_sales s 
    ON l.Listing_ID = s.Listing_ID
WHERE s.Listing_ID IS NULL
GROUP BY a.Agent_ID, a.Name
ORDER BY Active_Listings DESC;
""",

"Investor vs End User Percentage": """
SELECT 
    buyer_type,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM clean_buyers) AS percentage
FROM clean_buyers
GROUP BY buyer_type;
""",

"Loan Uptake Rate by City": """
SELECT l.City,
       COUNT(CASE WHEN b.loan_taken = 'True' THEN 1 END) * 100.0 / COUNT(*) AS loan_uptake_rate
FROM clean_buyers b
JOIN clean_sales s ON b.sale_id = s.Listing_ID
JOIN clean_listings l ON s.Listing_ID = l.Listing_ID
GROUP BY l.City
ORDER BY loan_uptake_rate DESC;
""",

"Average Loan Amount by Buyer Type": """
SELECT 
    buyer_type,
    AVG(loan_amount) AS avg_loan_amount
FROM clean_buyers
WHERE loan_taken = 'True'
GROUP BY buyer_type;
""",

"Most Common Payment Mode": """
SELECT 
    payment_mode,
    COUNT(*) AS count
FROM clean_buyers
GROUP BY payment_mode
ORDER BY count DESC
LIMIT 1;
""",

"Loan vs Non-Loan Closing Time": """
SELECT 
    b.loan_taken,
    AVG(s.Days_on_Market) AS avg_days_to_close
FROM clean_buyers b
JOIN clean_sales s 
ON b.sale_id = s.Listing_ID
GROUP BY b.loan_taken;
"""
}

# DROPDOWN SELECTION
selected_query = st.selectbox("Select a SQL Question", list(queries.keys()))

# SHOW SQL QUERY

st.subheader("📌 SQL Query")
st.code(queries[selected_query], language="sql")

# EXECUTE AND SHOW OUTPUT

if st.button("Run Query"):
    df = pd.read_sql(queries[selected_query], engine)
    st.subheader("📊 Output")
    st.dataframe(df)

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

st.subheader("📍 Property Locations")
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
