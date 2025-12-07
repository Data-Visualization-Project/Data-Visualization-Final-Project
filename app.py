import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =====================================================
# LOAD DATA
# =====================================================
df = pd.read_csv("update_temperature.csv")

st.set_page_config(page_title="Climate Dashboard", layout="wide")


# =====================================================
# SIDEBAR FILTERS
# =====================================================
st.sidebar.title("Interactive Filters")

years = st.sidebar.slider(
    "Year Range",
    int(df["Year"].min()),
    int(df["Year"].max()),
    (int(df["Year"].min()), int(df["Year"].max()))
)

countries = st.sidebar.multiselect(
    "Countries",
    options=["All Countries"] + sorted(df["Country"].unique()),
    default=["All Countries"]
)

temp_range = st.sidebar.slider(
    "Temperature (°C)",
    float(df["Avg_Temperature_degC"].min()),
    float(df["Avg_Temperature_degC"].max()),
    (float(df["Avg_Temperature_degC"].min()), float(df["Avg_Temperature_degC"].max()))
)

co2_range = st.sidebar.slider(
    "CO2 (tons/capita)",
    float(df["CO2_Emissions_tons_per_capita"].min()),
    float(df["CO2_Emissions_tons_per_capita"].max()),
    (float(df["CO2_Emissions_tons_per_capita"].min()), float(df["CO2_Emissions_tons_per_capita"].max()))
)

renew_range = st.sidebar.slider(
    "Renewable Energy (% of total)",
    float(df["Renewable_Energy_pct"].min()),
    float(df["Renewable_Energy_pct"].max()),
    (float(df["Renewable_Energy_pct"].min()), float(df["Renewable_Energy_pct"].max()))
)

st.sidebar.markdown("---")
export_request = st.sidebar.button("Export Filtered Data")


# =====================================================
# APPLY FILTERS
# =====================================================
filtered = df.copy()

filtered = filtered[
    (filtered["Year"] >= years[0]) &
    (filtered["Year"] <= years[1])
]

if "All Countries" not in countries:
    filtered = filtered[filtered["Country"].isin(countries)]

filtered = filtered[
    (filtered["Avg_Temperature_degC"] >= temp_range[0]) &
    (filtered["Avg_Temperature_degC"] <= temp_range[1]) &
    (filtered["CO2_Emissions_tons_per_capita"] >= co2_range[0]) &
    (filtered["CO2_Emissions_tons_per_capita"] <= co2_range[1]) &
    (filtered["Renewable_Energy_pct"] >= renew_range[0]) &
    (filtered["Renewable_Energy_pct"] <= renew_range[1])
]


# =====================================================
# ANALYSIS MODE TABS
# =====================================================
st.title("Climate Change Interactive Dashboard")

tabs = st.tabs(["Overview", "Trends", "Correlation", "Temperature", "Renewable Energy"])


# =====================================================
# SUMMARY PANEL
# =====================================================
st.subheader("Data Summary")

st.info(
    f"""
    • Showing **{len(filtered):,}** of {len(df):,} records  
    • Time period: **{filtered['Year'].min()} – {filtered['Year'].max()}**  
    • Countries: **{filtered['Country'].nunique()}** selected  
    • Temperature range: **{filtered['Avg_Temperature_degC'].min():.1f}°C – {filtered['Avg_Temperature_degC'].max():.1f}°C**
"""
)


# =====================================================
# QUICK INSIGHTS PANEL
# =====================================================

st.subheader("Quick Insights")

insights = []
if len(filtered) > 1:
    # temp trend
    temp_fit = np.polyfit(filtered["Year"], filtered["Avg_Temperature_degC"], 1)[0]*10
    insights.append(f"• Temperature warming rate: {temp_fit:.2f}°C per decade")

    renew_fit = np.polyfit(filtered["Year"], filtered["Renewable_Energy_pct"], 1)[0]
    insights.append(f"• Renewable energy growth: {renew_fit:.2f}% per year")

    co2_corr = np.corrcoef(filtered["CO2_Emissions_tons_per_capita"], filtered["Avg_Temperature_degC"])[0, 1]
    insights.append(f"• CO2 vs Temperature correlation: {co2_corr:.3f}")

    evt_fit = np.polyfit(filtered["Year"], filtered["Extreme_Weather_Events"], 1)[0]
    insights.append(f"• Extreme weather trend: {evt_fit:.2f} events per year")

    st.success("\n".join(insights))
else:
    st.warning("Not enough data for insights")


# =====================================================
# VIEW 1 — OVERVIEW TAB
# =====================================================
with tabs[0]:
    st.header("Overview Dashboard")

    if len(filtered) > 0:
        treemap_data = filtered.groupby("Country")[["Population", "Avg_Temperature_degC"]].mean().reset_index()

        fig = px.treemap(
            treemap_data,
            path=["Country"],
            values="Population",
            color="Avg_Temperature_degC",
            color_continuous_scale="RdYlBu_r"
        )
        st.plotly_chart(fig, use_container_width=True)

# =====================================================
# VIEW 2 — TRENDS TAB
# =====================================================
with tabs[1]:
    st.header("Climate Indicators")

    yearly = filtered.groupby("Year")[["Avg_Temperature_degC", "CO2_Emissions_tons_per_capita"]].mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=yearly.index, y=yearly["Avg_Temperature_degC"], mode="lines+markers", name="Temperature"))
    fig.add_trace(go.Scatter(x=yearly.index, y=yearly["CO2_Emissions_tons_per_capita"], mode="lines+markers", name="CO2"))

    st.plotly_chart(fig, use_container_width=True)


# =====================================================
# VIEW 3 — CORRELATION TAB
# =====================================================
with tabs[2]:
    st.header("CO2 & Temperature Relationship")

    yr = filtered["Year"].max()
    latest = filtered[filtered["Year"] == yr]

    fig = px.scatter(
        latest,
        x="CO2_Emissions_tons_per_capita",
        y="Avg_Temperature_degC",
        color="Country",
        size="Population"
    )
    st.plotly_chart(fig, use_container_width=True)


# =====================================================
# VIEW 4 — TEMPERATURE HEATMAP TAB
# =====================================================
with tabs[3]:
    st.header("Temperature Distribution")

    pivot = filtered.groupby(["Country", "Year"])["Avg_Temperature_degC"].mean().reset_index()
    heat = pivot.pivot(index="Country", columns="Year", values="Avg_Temperature_degC").fillna(0)

    fig = go.Figure(data=go.Heatmap(
        z=heat.values, x=heat.columns, y=heat.index, colorscale="RdYlBu_r"
    ))

    st.plotly_chart(fig, use_container_width=True)


# =====================================================
# VIEW 5 — RENEWABLE ENERGY TAB
# =====================================================
with tabs[4]:
    st.header("Renewable Energy Indicators")

    renewable = filtered.groupby("Year")["Renewable_Energy_pct"].mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=renewable.index, y=renewable.values, mode="lines+markers"))
    st.plotly_chart(fig, use_container_width=True)


# =====================================================
# DATA EXPORT FUNCTION
# =====================================================
if export_request:
    export_file = f"filtered_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filtered.to_csv(export_file, index=False)
    st.sidebar.success(f"Exported: {export_file}")
