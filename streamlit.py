# -------------------------------------- Import Library ------------------------------
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import json
import streamlit as st 
import plotly.express as px

# ------------------------------ CONFIG ------------------------------
st.set_page_config(
    page_title="Dashboard Analisis Penjualan Supermarket",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------------------------- Read dataset and json file ------------------------------
# Dataset
df = pd.read_csv(r'data\nyc-rolling-sales_cleaned.csv')
# GeoJson of New York City's Boundries
with open(r'data\Borough Boundaries.geojson') as f:
    nyc_geojson = json.load(f)

# -------------------------------------- Side Bar --------------------------------------
with st.sidebar:
    # Logo dan BG
    st.write("Hello (〜￣▽￣)〜")
    st.image("asset\data-science.png")
    st.write("""
             Saya Prayogi Dwi Wibisono mempersembahkan Dashboard analisis data dari penjualan properti di 
             kota New York.
             Mari kita temukan hasil dan insight dari analisis yang saya buat.
            """)
    st.caption("Copyright © Prayogi Dwi Wibisono 2024")

# -------------------------------------- Row 1 --------------------------------------
st.write("# Dasboard Analisis of Property Sales in New York City, USA")

st.write("## Data Used for Analysis")
with st.expander("Buka Untuk Lihat Data Lengkap"):
    st.write("Data Penjualan Properti di NYC",df)

# -------------------------------------- Row 2 --------------------------------------
st.write("## Top and Bottom Property Density in New York City")

# Adding Name of each Borough in the dataset
borough_info = {
    1: {'name': 'Manhattan'},
    2: {'name': 'Bronx'},
    3: {'name': 'Brooklyn'},
    4: {'name': 'Queens'},
    5: {'name': 'Staten Island'}
}
df['BOROUGH NAME'] = df['BOROUGH'].map(lambda x: borough_info[x]['name'])

# Create a dropdown in Streamlit for selecting a borough
borough_selected = st.selectbox("Select a Borough", options=['Manhattan', 'Bronx', 'Brooklyn', 'Queens', 'Staten Island'])
borough = df[df['BOROUGH NAME']==borough_selected]

# Counting the sum value of each neighborhood
neighborhood_counts = borough['NEIGHBORHOOD'].value_counts()

# Get the top and bottom 5 neighborhoods
top_5_neighborhoods = neighborhood_counts.head(5)
bottom_5_neighborhoods = neighborhood_counts.tail(5)

# Set up the figure and axes for side-by-side bar charts
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Plot top 5 neighborhoods
axes[0].bar(top_5_neighborhoods.index, top_5_neighborhoods.values, color='skyblue')
axes[0].set_title('Top 5 Populated Neighborhoods in ' + borough['BOROUGH NAME'].iloc[0])
axes[0].set_xlabel('Neighborhood')
axes[0].set_ylabel('Buildings Count')
axes[0].tick_params(axis='x', rotation=45)

# Plot bottom 5 neighborhoods
axes[1].bar(bottom_5_neighborhoods.index, bottom_5_neighborhoods.values, color='salmon')
axes[1].set_title('Bottom 5 Populated Neighborhoods in ' + borough['BOROUGH NAME'].iloc[0])
axes[1].set_xlabel('Neighborhood')
axes[1].tick_params(axis='x', rotation=45)

# Adjust layout and display in Streamlit
plt.tight_layout()
st.pyplot(fig)

# -------------------------------------- Row 3 --------------------------------------

st.write("## Property Price Trend from 2016 to 2017 (10 Months)")

# Preparing Dataframe for Visualization
df_monthsales = df[['BOROUGH', 'BOROUGH NAME', 'SALE PRICE', 'SALE DATE']]
df_monthsales['SALE DATE'] = pd.to_datetime(df_monthsales['SALE DATE'])

# Extract month and year 
df_monthsales['SALE MONTH'] = df_monthsales['SALE DATE'].dt.to_period('M').astype(str)

# Group by SALE MONTH and sum SALE PRICE
df_monthsales = df_monthsales.groupby(['BOROUGH', 'BOROUGH NAME', 'SALE MONTH'])['SALE PRICE'].sum().reset_index()

df_monthsales = df_monthsales[df_monthsales['BOROUGH NAME']==borough_selected]

# Create a figure and axis object
fig, ax = plt.subplots(figsize=(14, 7))

# Plot the data on the axis
ax.plot(df_monthsales['SALE MONTH'], df_monthsales['SALE PRICE'], color='blue', marker='o')
ax.set_title('Monthly Sales Price Trend in ' + df_monthsales['BOROUGH NAME'].iloc[0])
ax.set_xlabel('Month-Year')
ax.set_ylabel('Sale Price')
ax.tick_params(axis='x', rotation=45)  # Rotate x-axis labels for readability

# Set y-axis formatting to display dollar amounts with commas
ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))

# Adjust layout to prevent overlap
fig.tight_layout()

# Display the plot in Streamlit
st.pyplot(fig)

# -------------------------------------- Row 4 --------------------------------------

st.write("## New York City's Sale Price Heatmap")

# Aggregate sale prices by borough
borough_sales = df[['BOROUGH', 'BOROUGH NAME', 'SALE PRICE', 'SALE DATE']]
borough_sales = borough_sales.groupby('BOROUGH').agg({
    'SALE PRICE': 'sum'
}).reset_index()

# Map borough codes to names to match the GeoJSON file
# (Update based on your specific GeoJSON structure and borough codes)
borough_mapping = {
    1: "Manhattan",
    2: "Bronx",
    3: "Brooklyn",
    4: "Queens",
    5: "Staten Island"
}
borough_sales['BOROUGH_NAME'] = borough_sales['BOROUGH'].map(borough_mapping)

# Create the choropleth map
fig = px.choropleth_mapbox(
    borough_sales,
    geojson=nyc_geojson,
    locations="BOROUGH_NAME",         # Match borough names with GeoJSON 'id' or 'name'
    featureidkey="properties.boro_name", # Key in the GeoJSON for borough name (update based on GeoJSON structure)
    color="SALE PRICE",               # Color by total sale price
    color_continuous_scale="YlOrRd",  # Yellow to Red scale, with red as the hottest
    range_color=(borough_sales["SALE PRICE"].min(), borough_sales["SALE PRICE"].max()), # Set color range
    hover_name="BOROUGH_NAME",        # Display borough name on hover
    hover_data={"SALE PRICE": ":,."}  # Format sale price for readability
)

# Customize map layout
fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=9,
    mapbox_center={"lat": 40.7128, "lon": -74.0060}, # Center around NYC
    title="Heat Map of Total Sale Price by Borough in New York City",
    margin={"r":0,"t":50,"l":0,"b":0}
)

st.plotly_chart(fig)