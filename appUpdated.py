import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit.components.v1 import html
import plotly.graph_objects as go

# cd to the directory where the app is : cd "C:\Users\angel\OneDrive\Desktop\stat research skills"
# Command to run the app: 
# streamlit run appUpdated.py

# Load the necessary datasets
monthly_data = pd.read_csv("/Users/angel/OneDrive/Desktop/stat research skills/averagesDataMonthlyMinus.csv")
annual_data = pd.read_csv("/Users/angel/OneDrive/Desktop/stat research skills/averagesDataAnnualFinal.csv")
meanImputedData = pd.read_csv("/Users/angel/OneDrive/Desktop/masterThesis/meanImputedData.csv") 
annual_pollutants = pd.read_csv("/Users/angel/OneDrive/Desktop/stat research skills/annualPollutants.csv")
monthly_pollutants = pd.read_csv("/Users/angel/OneDrive/Desktop/stat research skills/monthlyPollutants.csv")

st.title("Environmental Data Visualization")

# Sidebar
report_type = st.sidebar.radio("", ["📊 Datasets Info", "📈 General Trends", "📅 Monthly Report", "📅 Annual Report", "📂 Download Data"])
city_options = meanImputedData["city"].unique()
selected_city = st.sidebar.selectbox("Select City for General Trends or Monthly Reports", options=city_options)

# DATASETS INFO OPTION
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
    - Average air temperature in Celsius degrees (tavg)
    - Minimum air temperature (tmin)
    - Maximum air temperature (tmax)
    - Precipitation in mm (prcp) 
    - Snow depth in mm
    - Wind direction in degrees (wdir)
    - Average wind speed in km/h (wspd)
    - Peak wind gust in km/h (wpgt)
    
    Only a particular subset of the features were used for this purpose.
    """)
    st.subheader("Link to the edited datasets")
    st.markdown("[Link to my Github Repository](https://github.com/angelamladenovska/streamlitApp)")
    data = {
        "AQI Values": ["0 to 50", "51 to 100", "101 to 150", "151 to 200", "201 to 300", "301 to 500"],
        "Levels of Health Concern": ["Good", "Moderate", "Unhealthy for Sensitive Groups", "Unhealthy", "Very Unhealthy", "Hazardous"],
        "Colors": ["Green", "Orange", "Red", "Darkred", "Purple", "Maroon"]
    }
    st.subheader("Definition of Air Quality Index")
    df = pd.DataFrame(data)
    st.table(df)

# GENERAL TRENDS OPTION
elif report_type == "📈 General Trends":
    st.subheader("📈 General Trends for AQI and Pollutants")

    city_report_type = st.radio("Select the Report Type", ["City Trends", "City Map with AQI", "Radar Chart"])

    if city_report_type == "City Trends":
        filtered_data = meanImputedData[
            (meanImputedData["city"] == selected_city) & 
            (meanImputedData["Date"].between("2023-01-01", "2023-12-31"))
        ]

        fig_aqi_trend = px.line(
            filtered_data,
            x="Date",
            y="Overall AQI Value",
            title=f"AQI Trend for 2023 in {selected_city}",
            markers=True
        )
        st.plotly_chart(fig_aqi_trend)

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
                'CO': 'saddlebrown',
                'PM10': 'darkorange',
                'NO2': 'purple'
            },
            title=f"Pollutant Trend for {selected_city}",
            labels={"count": "Occurrences", "Month-Year": "Month", "Main Pollutant": "Pollutant"},
            barmode="stack"
        )
        st.plotly_chart(fig_pollutant_trend)

    elif city_report_type == "City Map with AQI":
        st.header("Map of Cities with AQI Levels")
        aqi_representation = st.radio("Select AQI Representation", ["Monthly Average AQI", "Annual Average AQI"])
        city_map = folium.Map(location=[39.8283, -98.5795], zoom_start=3)

        if aqi_representation == "Monthly Average AQI":
            data_to_use = monthly_data
            aqi_column = "averageAQIMonthly"
        else:
            data_to_use = annual_data
            aqi_column = "averageAQIAnnual"

        for idx, row in data_to_use.iterrows():
            city = row['city']
            lat = row['lat']
            lon = row['lon']
            aqi = float(row[aqi_column])

            if aqi <= 50:
                color = 'green'
            elif aqi <= 100:
                color = 'orange'
            elif aqi <= 150:
                color = 'red'
            elif aqi <= 200:
                color = 'darkred'
            elif aqi <= 300:
                color = 'purple'
            else:
                color = 'maroon'

            folium.Marker(
                [lat, lon],
                popup=f"{city} - {aqi_representation}: {aqi}",
                icon=folium.Icon(color=color)
            ).add_to(city_map)

        map_html = city_map._repr_html_()
        html(map_html, height=500)

    elif city_report_type == "Radar Chart":
        radar_type = st.radio("Select Data Type", ["Annual Pollutants", "Monthly Pollutants"])
        title_extra = ""
        # For monthly radar chart, let the user select a month by name
        if radar_type == "Monthly Pollutants":
            # Dictionary mapping month names to numeric values
            month_dict = {
                "January": 1,
                "February": 2,
                "March": 3,
                "April": 4,
                "May": 5,
                "June": 6,
                "July": 7,
                "August": 8,
                "September": 9,
                "October": 10,
                "November": 11,
                "December": 12
            }
            selected_month_str = st.selectbox("Select Month", options=list(month_dict.keys()))
            selected_month_num = month_dict[selected_month_str]
            title_extra = f" in {selected_month_str}"
        cities_selected = st.multiselect("Select one or more cities for the Radar Chart", options=city_options, default=[selected_city])
        
        if not cities_selected:
            st.warning("Please select at least one city.")
        else:
            fig = go.Figure()
            for city in cities_selected:
                if radar_type == "Annual Pollutants":
                    filtered_data = annual_pollutants[annual_pollutants["city"] == city]
                else:
                    filtered_data = monthly_pollutants[(monthly_pollutants["city"] == city) & (monthly_pollutants["Month"] == selected_month_num)]
                    
                if not filtered_data.empty:
                    pollutants = ["Ozone", "PM25", "CO", "PM10", "NO2"]
                    values = filtered_data.iloc[0][pollutants].tolist()
                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=pollutants,
                        fill='toself',
                        name=city
                    ))
                else:
                    st.warning(f"No data available for {city}.")
                    
            title = f"{radar_type} Radar Chart for {', '.join(cities_selected)}{title_extra}"
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True)
                ),
                title=title
            )
            st.plotly_chart(fig)

# MONTHLY REPORT OPTION
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
            'CO': 'saddlebrown',
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

# ANNUAL REPORT OPTION
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
            'CO': 'saddlebrown',
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

# DOWNLOAD DATA OPTION
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

    filter_city = st.checkbox("Filter by city")
    if filter_city:
        selected_city_download = st.selectbox("Select City (Optional)", options=city_options)
        filtered_data = meanImputedData[
            (pd.to_datetime(meanImputedData["Date"]) >= start_date) & 
            (pd.to_datetime(meanImputedData["Date"]) <= end_date) & 
            (meanImputedData["city"] == selected_city_download)
        ]
    else:
        filtered_data = meanImputedData[
            (pd.to_datetime(meanImputedData["Date"]) >= start_date) & 
            (pd.to_datetime(meanImputedData["Date"]) <= end_date)
        ]

    st.subheader(f"📅 Data Overview from {start_date.date()} to {end_date.date()}")
    st.dataframe(filtered_data, hide_index=True)

    csv = filtered_data.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv,
        file_name=f"filtered_data_{start_date.date()}_{end_date.date()}.csv",
        mime="text/csv"
    )
