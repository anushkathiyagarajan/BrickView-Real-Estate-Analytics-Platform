import pandas as pd
import json


# LOAD DATA
listings = pd.read_json("data/listings_final_expanded.json")
attributes = pd.read_json("data/property_attributes_final_expanded.json")
agents = pd.read_json("data/agents_cleaned.json")
sales = pd.read_csv("data/sales_cleaned.csv")
buyers = pd.read_json("data/buyers_cleaned.json")

# STANDARDIZE DATA TYPES
# Date Columns
listings['Date_Listed'] = pd.to_datetime(listings['Date_Listed'], errors='coerce')
print(listings.info())
sales['Date_Sold'] = pd.to_datetime(sales['Date_Sold'], errors='coerce')
print(sales.info())
# Numeric Columns
listings['Price'] = listings['Price'].astype(float)
listings['Sqft'] = listings['Sqft'].astype(float)
sales['Sale_Price'] = sales['Sale_Price'].astype(float)
sales['Days_on_Market'] = sales['Days_on_Market'].astype(int)
# Boolean Mapping
attributes['parking_available'] = attributes['parking_available'].map({'Yes': True, 'No': False})
attributes['power_backup'] = attributes['power_backup'].map({'Yes': True, 'No': False})
attributes['is_rented'] = attributes['is_rented'].map({'Yes': True, 'No': False})


# HANDLE MISSING VALUES
# Listings
listings['Price'] = listings['Price'].fillna(listings['Price'].mean())
listings['Sqft'] = listings['Sqft'].fillna(listings['Sqft'].mean())
listings['Property_Type'] = listings['Property_Type'].fillna(listings['Property_Type'].mode()[0])
# Sales
sales['Sale_Price'] = sales['Sale_Price'].fillna(sales['Sale_Price'].mean())
sales['Days_on_Market'] = sales['Days_on_Market'].fillna(sales['Days_on_Market'].median())
# Attributes
attributes = attributes.fillna(0).infer_objects(copy=False)
# Ensure data format and price/area are consistent
listings['Price'] = (listings['Price'] .astype(str).str.replace(',', '', regex=False).str.replace('$', '', regex=False) .str.replace('₹', '', regex=False))
# Convert to float
listings['Price'] = pd.to_numeric( listings['Price'],  errors='coerce')
print(listings['Price'].dtype)
listings['Sqft'] = (listings['Sqft'].astype(str).str.replace(',', '', regex=False).str.replace('sqft', '', regex=False).str.replace('sq.ft', '', regex=False))
listings['Sqft'] = pd.to_numeric(listings['Sqft'], errors='coerce')
print(listings['Sqft'].dtype)

#to check flatten is required or not
print(listings.applymap(lambda x: isinstance(x, dict)).any())
print(sales.applymap(lambda x: isinstance(x, dict)).any())
print(attributes.applymap(lambda x: isinstance(x, dict)).any())
print(buyers.applymap(lambda x: isinstance(x, dict)).any())
print(agents.applymap(lambda x: isinstance(x, dict)).any())

# SAVE CLEANED FILES
listings.to_csv("clean_listings.csv", index=False)
attributes.to_csv("clean_attributes.csv", index=False)
agents.to_csv("clean_agents.csv", index=False)
sales.to_csv("clean_sales.csv", index=False)
buyers.to_csv("clean_buyers.csv", index=False)
print(" Data Cleaning Completed Successfully")