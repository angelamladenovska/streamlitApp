import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit.components.v1 import html

#cd to the directory where the app is : cd "C:\Users\angel\OneDrive\Desktop\stat research skills"
# Command to run the app: 
# streamlit run sidebarMenuApp.py

# Load the necessary datasets
monthly_data = pd.read_csv("/Users/angel/OneDrive/Desktop/stat research skills/averagesDataMonthly.csv")
annual_data = pd.read_csv("/Users/angel/OneDrive/Desktop/stat research skills/averagesDataAnnualFinal.csv")
meanImputedData = pd.read_csv("/Users/angel/OneDrive/Desktop/masterThesis/meanImputedData.csv")  # Your meanImputedData dataset

st.title("Environmental Data Visualization")

# Creating a sidebar for selecting a report type
report_type = st.sidebar.radio("", ["📊 Datasets Info", "📈 General Trends", "📅 Monthly Report", "📅 Annual Report", "📂 Download Data"])

# City selection 
city_options = meanImputedData["city"].unique()
selected_city = st.sidebar.selectbox("Select City for General Trends or Monthly Reports", options=city_options)
if report_type == "📊 Datasets Info":
    st.header("Basic Information about the datasets")
    st.subheader("Links to the source datasets")
    st.markdown("[Air Quality Dataset](https://www.kaggle.com/datasets/nikkiperry/2023-air-quality-data-for-cbsas)")
    st.markdown("[Weather Dataset](https://www.kaggle.com/datasets/marslandis/largest-50-us-cities-weather-data-2020-to-2023)")
    st.markdown("Additional weather data was scraped with Meteostat library that uses the Meteostat API")
    st.subheader("Air Quality Dataset Features")
    st.markdown("""
    - Date the measure was taken
    - Overall AQI value
    - Main Pollutant
    - Name of site where the AQI value was measured
    - ID of site where the AQI value was measured
    - Source of overall AQI value
    - Ozone level
    - PM25 level
    - CO level
    - PM10 level
    - NO2 level
    - AQI category (good, moderate, unhealthy, etc.)
    - City name
    - State name

    """)
    st.subheader("Weather Dataset Features")    
    st.markdown("""
    - City
    - Date
    - Average temperature (tavg)
    - Minimum temperature (tmin)
    - Maximum temperature (tmax)
    - Precipitation (prcp) 
    - Snow depth
    - Wind direction (wdir)
    - Average wind speed (wspd)
    - Peak wind gust (wpgt)
    
    Only a particular subset of the features were used for this purpose.
    """
    )
    st.subheader("Link to the edited datasets")
    st.markdown("[Link to my Github Repository](https://github.com/angelamladenovska/streamlitApp)")
    
# Download csv data for a particular city and range of dates
if report_type == "📂 Download Data":
    st.header("Download Filtered Data")

    start_date, end_date = st.date_input(
        "Select date range",
        value=(pd.to_datetime("2023-01-01"), pd.to_datetime("2023-12-31")),
        min_value=pd.to_datetime("2000-01-01"),
        max_value=pd.to_datetime("2025-12-31")
    )

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Optional city filtering
    filter_city = st.checkbox("Filter by city")
    if filter_city:
        selected_city = st.selectbox("Select City (Optional)", options=city_options)
        filtered_data = meanImputedData[
            (pd.to_datetime(meanImputedData["Date"]) >= start_date) & 
            (pd.to_datetime(meanImputedData["Date"]) <= end_date) & 
            (meanImputedData["city"] == selected_city)
        ]
    else:
        filtered_data = meanImputedData[
            (pd.to_datetime(meanImputedData["Date"]) >= start_date) & 
            (pd.to_datetime(meanImputedData["Date"]) <= end_date)
        ]

    # Display filtered data
    st.subheader(f"📅 Data Overview from {start_date.date()} to {end_date.date()}")
    st.dataframe(filtered_data, hide_index=True)

    # CSV Download Button
    csv = filtered_data.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv,
        file_name=f"filtered_data_{start_date.date()}_{end_date.date()}.csv",
        mime="text/csv"
    )

# GENERAL TRENDS SECTION
elif report_type == "📈 General Trends":
    st.subheader("📈 General Trends for AQI and Pollutants")

    # Filter data by selected city and date range for trends
    filtered_data = meanImputedData[
        (meanImputedData["city"] == selected_city) & 
        (meanImputedData["Date"].between("2023-01-01", "2023-12-31"))
    ]

    # AQI Trend for 2023
    fig_aqi_trend = px.line(
        filtered_data,
        x="Date",
        y="Overall AQI Value",
        title=f"AQI Trend for 2023 in {selected_city}",
        markers=True
    )
    st.plotly_chart(fig_aqi_trend)

    # Main Pollutant Trend (Stacked Bar Chart)
    filtered_data["Date"] = pd.to_datetime(filtered_data["Date"])
    filtered_data["Month-Year"] = filtered_data["Date"].dt.to_period("M").astype(str)

    pollutant_trend = filtered_data.groupby(["Month-Year", "Main Pollutant"]).size().reset_index(name="count")

    fig_pollutant_trend = px.bar(
        pollutant_trend,
        x="Month-Year",
        y="count",
        color="Main Pollutant",
        color_discrete_map={
        'Ozone': 'lightblue',
        'PM2.5': 'darkred',
        'CO': 'darkbrown',
        'PM10': 'darkorange',
        'NO2': 'purple'
    },
        title=f"Pollutant Trend for {selected_city}",
        labels={"count": "Occurrences", "Month-Year": "Month", "Main Pollutant": "Pollutant"},
        barmode="stack"
    )
    st.plotly_chart(fig_pollutant_trend)

# MONTHLY REPORT SECTION
elif report_type == "📅 Monthly Report":
    st.subheader("📅 Monthly Report")

    # Filter data by selected city
    filtered_monthly = monthly_data[monthly_data["city"] == selected_city]

    # Monthly Average Temperature by City
    fig_temp_month = px.bar(filtered_monthly, 
                            x="month", 
                            y="averageTempMonthly", 
                            title=f"Monthly Average Temperature for {selected_city}")
    st.plotly_chart(fig_temp_month)

    # Average Monthly AQI by City
    fig_aqi_month = px.bar(filtered_monthly, 
                           x="month", 
                           y="averageAQIMonthly", 
                           title=f"Average Monthly AQI for {selected_city}")
    st.plotly_chart(fig_aqi_month)

    # Main Pollutant by Month (Pie Chart)
    fig_pollutant_month = px.pie(
        filtered_monthly,
        names="mainPollutantMonthly",  
        title=f"Main Pollutant by Month for {selected_city}",
        color="mainPollutantMonthly",  
        color_discrete_map={  
        'Ozone': 'lightblue',
        'PM2.5': 'darkred',
        'CO': 'darkbrown',
        'PM10': 'darkorange',
        'NO2': 'purple'
        },
        labels={"mainPollutantMonthly": "Pollutant"} 
    )
    st.plotly_chart(fig_pollutant_month)


    # Main AQI Category by Month (Pie Chart)
    fig_aqi_category_month = px.pie(
        filtered_monthly,
        names="AQI category",  
        title=f"Main AQI Category by Month for {selected_city}",
        color="AQI category",  
        color_discrete_map={  
        'Good': 'green',
        'Moderate': 'yellow',
        'Unhealthy for Sensitive Groups': 'orange',
        'Unhealthy': 'red',
        'Very Unhealthy': 'purple',
        'Hazardous': 'brown'
        },
        labels={"AQI category": "AQI Category"} 
    )
    st.plotly_chart(fig_aqi_category_month)


    # Average Precipitation by Month for Selected City
    fig_precipitation = px.bar(filtered_monthly, 
                               x="month", 
                               y="averagePrecipitationMonthly", 
                               title=f"Average Precipitation by Month for {selected_city}")
    st.plotly_chart(fig_precipitation)

    # Average Wind Speed by Month for Selected City
    fig_wind_speed = px.bar(filtered_monthly, 
                            x="month", 
                            y="averageWindSpeedMonthly", 
                            title=f"Average Wind Speed by Month for {selected_city}")
    st.plotly_chart(fig_wind_speed)

    # Render Map of Selected City
    st.header(f"Map of {selected_city}")
    city_lat = filtered_monthly["lat"].values[0]
    city_lon = filtered_monthly["lon"].values[0]
    city_map = folium.Map(location=[city_lat, city_lon], zoom_start=10)
    folium.Marker([city_lat, city_lon], popup=f"{selected_city}").add_to(city_map)

    map_html = city_map._repr_html_()
    html(map_html, height=500)

# ANNUAL REPORT SECTION
elif report_type == "📅 Annual Report":
    st.header("Annual Report for All Cities")

    # Average Annual AQI across all cities
    fig_aqi_ann = px.bar(
        annual_data,
        x="city",
        y="averageAQIAnnual",
        title="Annual Average AQI for All Cities",
    )
    st.plotly_chart(fig_aqi_ann)

    # Main Pollutant Distribution for All Cities
    fig_pollutant_ann = px.pie(
        annual_data,
        names="mainPollutantAnnual",
        title="Main Pollutants Annualy",
        color="mainPollutantAnnual",
        color_discrete_map={
        'Ozone': 'lightblue',
        'PM2.5': 'darkred',
        'CO': 'darkbrown',
        'PM10': 'darkorange',
        'NO2': 'purple'
    }
        
    )
    st.plotly_chart(fig_pollutant_ann)

   # Main AQI Category by City (Annual) - Pie Chart
    fig_aqi_category_ann = px.pie(
        annual_data,
        names="mainAQICategoryAnnual",  
        title="Main AQI Categories Annually",
        color="mainAQICategoryAnnual",  
        color_discrete_map={  
            'Good': 'green',
            'Moderate': 'yellow',
            'Unhealthy for Sensitive Groups': 'orange',
            'Unhealthy': 'red',
            'Very Unhealthy': 'purple',
            'Hazardous': 'brown'
        },
        labels={"mainAQICategoryAnnual": "AQI Category"} 
    )
    st.plotly_chart(fig_aqi_category_ann)


    # Average Precipitation for All Cities
    fig_precipitation_ann = px.bar(
        annual_data,
        x="city",
        y="averagePrecipitationAnnual",
        title="Annual Average Precipitation by City"
    )
    st.plotly_chart(fig_precipitation_ann)

    # Average Annual Temperature for All Cities
    fig_temp_ann = px.bar(
        annual_data,
        x="city",
        y="averageTempAnnual",
        title="Annual Average Temperature for All Cities",
        labels={"averageTemperatureAnnual": "Average Temperature (°C)", "city": "City"}
    )
    st.plotly_chart(fig_temp_ann)




