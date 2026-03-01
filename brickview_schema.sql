
#database created
CREATE database brickview;
use brickview;
#table creation
#structure of a table
CREATE TABLE agents (
    Agent_ID VARCHAR(20) PRIMARY KEY,
    Name VARCHAR(150),
    Phone VARCHAR(50),
    Email VARCHAR(150),
    commission_rate DECIMAL(5,2),
    deals_closed INT,
    rating FLOAT,
    experience_years INT,
    avg_closing_days INT
);
CREATE TABLE listings (
    Listing_ID VARCHAR(20) PRIMARY KEY,
    City VARCHAR(100),
    Property_Type VARCHAR(100),
    Price DECIMAL(15,2),
    Sqft FLOAT,
    Date_Listed DATE,
    Agent_ID VARCHAR(20),
    Latitude DOUBLE,
    Longitude DOUBLE
);
CREATE TABLE sales (
    Sale_ID INT AUTO_INCREMENT PRIMARY KEY,
    Listing_ID VARCHAR(20),
    Sale_Price DECIMAL(15,2),
    Date_Sold DATE,
    Days_on_Market INT,
    FOREIGN KEY (Listing_ID) REFERENCES listings(Listing_ID)
);
CREATE TABLE buyers (
    Buyer_ID VARCHAR(20) PRIMARY KEY,
    Sale_ID INT,
    Buyer_Type VARCHAR(50),
    Payment_Mode VARCHAR(50),
    Loan_Taken BOOLEAN,
    Loan_Provider VARCHAR(100),
    Loan_Amount DECIMAL(15,2),
    FOREIGN KEY (Sale_ID) REFERENCES sales(Sale_ID)
);
CREATE TABLE property_attributes (
    attribute_id INT PRIMARY KEY,
    listing_id VARCHAR(20),
    bedrooms INT,
    bathrooms INT,
    floor_number INT,
    total_floors INT,
    year_built INT,
    is_rented BOOLEAN,
    tenant_count INT,
    furnishing_status VARCHAR(50),
    metro_distance_km FLOAT,
    parking_available BOOLEAN,
    power_backup BOOLEAN,
    FOREIGN KEY (listing_id) REFERENCES listings(Listing_ID)
);
DROP TABLE agents;
DROP TABLE listings;
DROP TABLE sales;
DROP TABLE buyers;
DROP TABLE property_attributes;
#referal integrity

#shows the table which are imported
select count(*) from clean_agents;
select count(*) from clean_listings;
select * from clean_sales LIMIT 5;
select count(*) from clean_attributes;
#Normalization
#unsold property
CREATE VIEW property_summary AS
SELECT 
    l.Listing_ID,
    l.City,
    l.Property_Type,
    l.Price,
    a.Name AS Agent_Name,
    s.Sale_Price,
    s.Days_on_Market
FROM clean_listings l
JOIN clean_agents a ON l.Agent_ID = a.Agent_ID
LEFT JOIN clean_sales s ON l.Listing_ID = s.Listing_ID;

CREATE VIEW agent_performance AS
SELECT 
    a.Agent_ID,
    a.Name,
    COUNT(*) AS Total_Sales,
    SUM(s.Sale_Price) AS Total_Revenue,
    AVG(s.Days_on_Market) AS Avg_Closing_Time
FROM clean_agents a
LEFT JOIN clean_listings l ON a.Agent_ID = l.Agent_ID
LEFT JOIN clean_sales s ON l.Listing_ID = s.Listing_ID
GROUP BY a.Agent_ID, a.Name;
select * from agent_performance;
select * from property_summary;
#sold property
SELECT 
    l.Listing_ID,
    l.City,
    l.Property_Type,
    l.Price,
    a.Name AS Agent_Name,
    s.Sale_Price,
    s.Days_on_Market
FROM clean_listings l
JOIN clean_agents a ON l.Agent_ID = a.Agent_ID
JOIN clean_sales s ON l.Listing_ID = s.Listing_ID;
use brickview;
ALTER TABLE clean_listings MODIFY Agent_ID VARCHAR(50);
ALTER TABLE clean_listings MODIFY Listing_ID VARCHAR(50);
ALTER TABLE clean_sales MODIFY Listing_ID VARCHAR(50);
ALTER TABLE clean_attributes MODIFY listing_id VARCHAR(50);
ALTER TABLE clean_buyers MODIFY sale_id VARCHAR(50);
ALTER TABLE clean_buyers MODIFY buyer_id int;
ALTER TABLE clean_attributes MODIFY attribute_id int;
use brickview;

#create indexing
CREATE INDEX in_agent
ON clean_agents (rating);
CREATE INDEX idx_listings_agents_new
ON clean_listings (Agent_ID);
CREATE INDEX idx_sales_listings_neww
ON clean_sales (Listing_ID);
CREATE INDEX idx_buyers_sale
ON clean_buyers (sale_id);
CREATE INDEX idx_attributes_listing
ON clean_attributes (listing_id);

show index from clean_listings;
show index from clean_agents;
show index from clean_attributes;
show index from clean_buyers;
show index from clean_sales;

#Property & Pricing Analysis
#What is the average listing price by city?
SELECT City, AVG(Price) AS Avg_Price
FROM clean_listings
GROUP BY City
ORDER BY Avg_Price DESC;

#What is the average price per square foot by property type?
SELECT Property_Type,
       AVG(Price / Sqft) AS Avg_Price_per_Sqft
FROM clean_listings
GROUP BY Property_Type;

#How does furnishing status impact property prices?
SELECT pa.furnishing_status,
       AVG(l.Price) AS Avg_Price
FROM clean_listings l
JOIN clean_attributes pa
ON l.Listing_ID = pa.listing_id
GROUP BY pa.furnishing_status;

#Do properties closer to metro stations command higher prices?
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

#Are rented properties priced differently from non-rented ones?
SELECT pa.is_rented,
       AVG(l.Price) AS Avg_Price
FROM clean_listings l
JOIN clean_attributes pa
ON l.Listing_ID = pa.listing_id
GROUP BY pa.is_rented;

#How Do Bedrooms and Bathrooms Affect Pricing?
SELECT 
    pa.bedrooms,
    pa.bathrooms,
    AVG(l.Price) AS Avg_Price
FROM clean_listings l
JOIN clean_attributes pa
ON l.Listing_ID = pa.listing_id
GROUP BY pa.bedrooms, pa.bathrooms
ORDER BY pa.bedrooms, pa.bathrooms;

#Do Properties with Parking & Power Backup Sell at Higher Prices?
SELECT 
    pa.parking_available,
    pa.power_backup,
    AVG(l.Price) AS Avg_Price
FROM clean_listings l
JOIN clean_attributes pa
ON l.Listing_ID = pa.listing_id
GROUP BY pa.parking_available, pa.power_backup;

#How Does Year Built Influence Listing Price?
SELECT 
    pa.year_built,
    AVG(l.Price) AS Avg_Price
FROM clean_listings l
JOIN clean_attributes pa
ON l.Listing_ID = pa.listing_id
GROUP BY pa.year_built
ORDER BY pa.year_built DESC;

#Which Cities Have the Highest Median Property Prices?
SELECT City, AVG(Price) AS Avg_Price
FROM clean_listings
GROUP BY City
ORDER BY Avg_Price DESC;

#How Are Properties Distributed Across Price Buckets?
SELECT 
    CASE 
        WHEN Price < 5000000 THEN 'Low'
        WHEN Price BETWEEN 5000000 AND 10000000 THEN 'Medium'
        ELSE 'High'
    END AS Price_Category,
    COUNT(*) AS Property_Count
FROM clean_listings
GROUP BY Price_Category;

#Sales & Market Performance
#What is the average days on market by city?
SELECT 
    l.City,
    AVG(s.Days_on_Market) AS Avg_Days_On_Market
FROM clean_sales s
JOIN clean_listings l 
ON s.Listing_ID = l.Listing_ID
GROUP BY l.City
ORDER BY Avg_Days_On_Market DESC;

#Which property types sell the fastest?
SELECT 
    l.Property_Type,
    AVG(s.Days_on_Market) AS Avg_Days
FROM clean_sales s
JOIN clean_listings l 
ON s.Listing_ID = l.Listing_ID
GROUP BY l.Property_Type
ORDER BY Avg_Days ASC;

#What percentage of properties are sold above listing price?
SELECT 
    (COUNT(CASE WHEN s.Sale_Price > l.Price THEN 1 END) * 100.0 
     / COUNT(*)) AS Percentage_Above_List
FROM clean_sales s
JOIN clean_listings l 
ON s.Listing_ID = l.Listing_ID;

#What is the sale-to-list price ratio by city?
SELECT 
    l.City,
    AVG(s.Sale_Price / l.Price) AS Price_Ratio
FROM clean_sales s
JOIN clean_listings l 
ON s.Listing_ID = l.Listing_ID
GROUP BY l.City
ORDER BY Price_Ratio DESC;

#Which listings took more than 90 days to sell?
SELECT 
    l.Listing_ID,
    l.City,
    s.Days_on_Market
FROM clean_sales s
JOIN clean_listings l 
ON s.Listing_ID = l.Listing_ID
WHERE s.Days_on_Market > 90;

#How does metro distance affect time on market?
SELECT 
    l.Listing_ID,
    l.City,
    s.Days_on_Market
FROM clean_sales s
JOIN clean_listings l 
ON s.Listing_ID = l.Listing_ID
WHERE s.Days_on_Market > 90;

#What is the monthly sales trend?
SELECT 
    DATE_FORMAT(Date_Sold, '%Y-%m') AS Sale_Month,
    COUNT(*) AS Total_Sales
FROM clean_sales
GROUP BY Sale_Month
ORDER BY Sale_Month;

#Which properties are currently unsold?
SELECT 
    l.Listing_ID,
    l.City,
    l.Price
FROM clean_listings l
LEFT JOIN clean_sales s
ON l.Listing_ID = s.Listing_ID
WHERE s.Listing_ID IS NULL;

#Agent Performance
#Which agents have closed the most sales?
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

#Who are the top agents by total sales revenue?
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

#Which agents close deals fastest?
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

#Does experience correlate with deals closed?
SELECT 
    experience_years,
    deals_closed
FROM clean_agents
ORDER BY experience_years;

#Do agents with higher ratings close deals faster?
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

#What is the average commission earned by each agent?
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

#Which agents currently have the most active listings?
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

#Buyer & Financing Behavior
#What percentage of buyers are investors vs end users?
SELECT 
    buyer_type,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM clean_buyers) AS percentage
FROM clean_buyers
GROUP BY buyer_type;

#Which cities have the highest loan uptake rate?
SELECT 
    l.City,
    COUNT(CASE WHEN b.loan_taken = 'True' THEN 1 END) * 100.0 / COUNT(*) 
        AS loan_uptake_rate
FROM clean_buyers b
JOIN clean_sales s 
    ON b.Listing_ID = s.Listing_ID
JOIN clean_listings l 
    ON s.Listing_ID = l.Listing_ID
GROUP BY l.City
ORDER BY loan_uptake_rate DESC;

#What is the average loan amount by buyer type?
SELECT 
    buyer_type,
    AVG(loan_amount) AS avg_loan_amount
FROM clean_buyers
WHERE loan_taken = 'True'
GROUP BY buyer_type;
SELECT * FROM clean_buyers WHERE loan_taken = 'True' AND loan_amount IS NULL;
#Which payment mode is most commonly used?
SELECT 
    payment_mode,
    COUNT(*) AS count
FROM clean_buyers
GROUP BY payment_mode
ORDER BY count DESC
LIMIT 1;

#Do loan-backed purchases take longer to close?
SELECT 
    b.loan_taken,
    AVG(s.Days_on_Market) AS avg_days_to_close
FROM clean_buyers b
JOIN clean_sales s 
ON b.sale_id = s.sale_id
GROUP BY b.loan_taken;
select 1;

show databases;

'''select count(*) from clean_sales;
select * from clean_sales LIMIT 15;
SELECT COUNT(*) FROM clean_buyers WHERE sale_id IS NULL;
SELECT MIN(sale_id), MAX(sale_id) FROM clean_buyers;
SELECT MIN(sale_id), MAX(sale_id) FROM clean_sales;
describe clean_buyers;
describe clean_sales;
SELECT * FROM clean_buyers WHERE loan_taken = TRUE LIMIT 5;
SELECT COUNT(*) FROM clean_buyers WHERE loan_amount IS NOT NULL;'''