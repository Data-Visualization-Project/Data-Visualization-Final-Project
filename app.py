import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import os

# ---------------------------------------------------------------------------
# DATA LOAD
# ---------------------------------------------------------------------------

@st.cache_data
def load_data():
    return pd.read_csv("update_temperature.csv")

df = load_data()


# ---------------------------------------------------------------------------
# FILTER SIDEBAR UI
# ---------------------------------------------------------------------------

st.sidebar.header("Interactive Controls")

st.sidebar.markdown("### Filter Data")

# Year Filter
year_min = int(df["Year"].min())
year_max = int(df["Year"].max())
year_range = st.sidebar.slider(
    "Year Range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
    step=1,
)

# Country Filter
countries = sorted(df["Country"].unique())
country_select = st.sidebar.multiselect(
    "Select Countries", ["All Countries"] + countries, default=["All Countries"]
)

# Temperature filter
temp_range = st.sidebar.slider(
    "Temperature (°C)",
    float(df["Avg_Temperature_degC"].min()),
    float(df["Avg_Temperature_degC"].max()),
    (
        float(df["Avg_Temperature_degC"].min()),
        float(df["Avg_Temperature_degC"].max()),
    ),
)

# CO2 filter
co2_range = st.sidebar.slider(
    "CO2 (tons/capita)",
    float(df["CO2_Emissions_tons_per_capita"].min()),
    float(df["CO2_Emissions_tons_per_capita"].max()),
    (
        float(df["CO2_Emissions_tons_per_capita"].min()),
        float(df["CO2_Emissions_tons_per_capita"].max()),
    ),
)

# Renewable filter
renew_range = st.sidebar.slider(
    "Renewable Energy (%)",
    float(df["Renewable_Energy_pct"].min()),
    float(df["Renewable_Energy_pct"].max()),
    (
        float(df["Renewable_Energy_pct"].min()),
        float(df["Renewable_Energy_pct"].max()),
    ),
)

# ---------------------------------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------------------------------

filtered_df = df[
    (df["Year"] >= year_range[0])
    & (df["Year"] <= year_range[1])
    & (df["Avg_Temperature_degC"] >= temp_range[0])
    & (df["Avg_Temperature_degC"] <= temp_range[1])
    & (df["CO2_Emissions_tons_per_capita"] >= co2_range[0])
    & (df["CO2_Emissions_tons_per_capita"] <= co2_range[1])
    & (df["Renewable_Energy_pct"] >= renew_range[0])
    & (df["Renewable_Energy_pct"] <= renew_range[1])
]

# Country filter
if "All Countries" not in country_select:
    filtered_df = filtered_df[filtered_df["Country"].isin(country_select)]


# ---------------------------------------------------------------------------
# DOWNLOAD FILTERED DATA BUTTON (working)
# ---------------------------------------------------------------------------

csv_buffer = io.StringIO()
filtered_df.to_csv(csv_buffer, index=False)

st.sidebar.download_button(
    label="Export Filtered Data",
    data=csv_buffer.getvalue(),
    file_name=f"filtered_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv",
)


# ---------------------------------------------------------------------------
# UI TITLE & SUMMARY
# ---------------------------------------------------------------------------

st.title("Climate Change Analysis Dashboard")

st.markdown("### Data Summary")

st.write(
    f"""
**Records Shown:** {len(filtered_df):,}  
**Countries in View:** {len(filtered_df['Country'].unique())}  
**Years Covered:** {filtered_df['Year'].min()} to {filtered_df['Year'].max()}  
"""
)

# ---------------------------------------------------------------------------
# ANALYSIS MODE SELECTOR
# ---------------------------------------------------------------------------

analysis_mode = st.selectbox(
    "Select Analysis Mode",
    ["Overview", "Trends", "Correlation", "Temperature", "Renewable"],
)


# ---------------------------------------------------------------------------
# VISUALIZATION FUNCTIONS
# ---------------------------------------------------------------------------

def show_treemap():
    treemap_data = filtered_df.groupby('Country').agg({
        'CO2_Emissions_tons_per_capita': 'mean',
        'Avg_Temperature_degC': 'mean',
        'Extreme_Weather_Events': 'mean',
        'Population': 'mean'
    }).reset_index()

    fig = px.treemap(
        treemap_data,
        path=['Country'],
        values='Population',
        color='Avg_Temperature_degC',
        color_continuous_scale='RdYlBu_r',
        title='Country Climate Impact Distribution'
    )
    st.plotly_chart(fig, use_container_width=True)


def show_trend_panels():
    yearly = filtered_df.groupby('Year').agg({
        'Avg_Temperature_degC': 'mean',
        'CO2_Emissions_tons_per_capita': 'mean',
        'Renewable_Energy_pct': 'mean',
        'Extreme_Weather_Events': 'mean'
    }).reset_index()

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Temperature", "CO₂ Emissions", "Renewable Energy", "Extreme Events")
    )

    fig.add_trace(
        go.Scatter(x=yearly['Year'], y=yearly['Avg_Temperature_degC'], mode="lines+markers", name="Temp"),
        1, 1
    )
    fig.add_trace(
        go.Scatter(x=yearly['Year'], y=yearly['CO2_Emissions_tons_per_capita'], mode="lines+markers", name="CO2"),
        1, 2
    )
    fig.add_trace(
        go.Scatter(x=yearly['Year'], y=yearly['Renewable_Energy_pct'], mode="lines+markers", name="Renewable"),
        2, 1
    )
    fig.add_trace(
        go.Scatter(x=yearly['Year'], y=yearly['Extreme_Weather_Events'], mode="lines+markers", name="Events"),
        2, 2
    )

    fig.update_layout(height=600, title="Climate Trends", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)


def show_correlation():
    latest_year = filtered_df['Year'].max()
    latest = filtered_df[filtered_df['Year'] == latest_year]

    fig = px.scatter(
        latest,
        x="CO2_Emissions_tons_per_capita",
        y="Avg_Temperature_degC",
        size="Population",
        color="Country",
        title=f"CO2 vs Temperature ({latest_year})"
    )
    st.plotly_chart(fig, use_container_width=True)


def show_temperature_heatmap():
    heatmap_data = filtered_df.groupby(['Country', 'Year'])['Avg_Temperature_degC'].mean().reset_index()
    pivot = heatmap_data.pivot(index="Country", columns="Year", values="Avg_Temperature_degC")

    fig = px.imshow(pivot, color_continuous_scale="RdBu_r", aspect="auto")
    fig.update_layout(title="Temperature Heatmap")
    st.plotly_chart(fig, use_container_width=True)


def show_renewable_analysis():
    show_trend_panels()


# ---------------------------------------------------------------------------
# DISPLAY BASED ON MODE
# ---------------------------------------------------------------------------

if len(filtered_df) == 0:
    st.warning("No data available for selected filters")
else:
    if analysis_mode == "Overview":
        show_treemap()
        show_trend_panels()

    elif analysis_mode == "Trends":
        show_trend_panels()

    elif analysis_mode == "Correlation":
        show_correlation()

    elif analysis_mode == "Temperature":
        show_temperature_heatmap()

    elif analysis_mode == "Renewable":
        show_renewable_analysis()
