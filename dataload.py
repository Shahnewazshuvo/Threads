import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Financial Executive Dashboard", layout="wide")
st.title("📊 Financial Executive Dashboard")
st.markdown("---")

# -------------------------------------------------
# LOAD GOOGLE SHEET
# -------------------------------------------------
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vST5ypw4O-nG04NnYeB-lZLBw9S3GUwlAXSjveGkS4SzPQAsV12oP0yvGhExO7otr5UGEu6tWrLqvJ_/pub?gid=1743156171&single=true&output=csv"
df = pd.read_csv(sheet_url)
df.columns = df.columns.str.strip()

# -------------------------------------------------
# CLEAN NUMERIC COLUMNS
# -------------------------------------------------
numeric_cols = [
    "Revised Budget","Expenditure",
    "Budgeted Revenue Generation","Actual Revenue Generation",
    "Cumulative Budget","Cumulative Expenditure"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = (
            df[col].astype(str)
            .str.replace(",", "")
            .str.strip()
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.fillna(0)

# Convert to Million USD
for col in numeric_cols:
    if col in df.columns:
        df[col] = df[col] / 1_000_000

# =================================================
st.header("1️⃣ Project-wise Revised Budget vs Expenditure (Million USD)")

proj_df = df[["Name of Project","Revised Budget","Expenditure"]].copy()

fig1 = go.Figure()

# Revised Budget
fig1.add_trace(go.Bar(
    y=proj_df["Name of Project"],
    x=proj_df["Revised Budget"],
    name="Revised Budget",
    orientation="h",
    marker=dict(color="#00CFFF"),
    text=[f"{v:.2f} M" for v in proj_df["Revised Budget"]],
    textposition="outside"
))

# Expenditure
fig1.add_trace(go.Bar(
    y=proj_df["Name of Project"],
    x=proj_df["Expenditure"],
    name="Expenditure",
    orientation="h",
    marker=dict(color="#FFD700"),
    text=[f"{v:.2f} M" for v in proj_df["Expenditure"]],
    textposition="outside"
))

fig1.update_layout(
    barmode="group",
    template="plotly_dark",
    title="Project-wise Budget vs Expenditure",
    xaxis_title="Million USD",
    yaxis_title="Project",
    legend=dict(
        orientation="v",
        x=1.02,
        y=1
    ),
    margin=dict(l=80, r=120, t=60, b=40)
)

st.plotly_chart(fig1, use_container_width=True)
st.markdown("---")

# 2️⃣ 3️⃣ 5️⃣ IN ONE ROW
# =================================================
col2, col3, col5 = st.columns(3)

# =================================================
# 2️⃣ Burn Rate Donut
# =================================================
with col2:
    st.subheader("2️⃣ Burn Rate (%)")

    burn_df = proj_df.copy()
    burn_df["Burn Rate"] = np.where(
        burn_df["Revised Budget"] != 0,
        (burn_df["Expenditure"] / burn_df["Revised Budget"]) * 100,
        0
    )

    fig2 = go.Figure(go.Pie(
        labels=burn_df["Name of Project"],
        values=burn_df["Burn Rate"],
        hole=0.6,
        text=burn_df["Burn Rate"].round(1).astype(str) + "%",
        textinfo="text",
        textposition="inside",
        marker=dict(colors=px.colors.qualitative.Set2)
    ))

    fig2.update_layout(template="plotly_white")
    st.plotly_chart(fig2, use_container_width=True)

# =================================================
# 3️⃣ Income Status
# =================================================
with col3:
    if "Budgeted Revenue Generation" in df.columns:

        st.subheader("3️⃣ Income Status")

        income_df = df[[
            "Name of Project_Income",
            "Budgeted Revenue Generation",
            "Actual Revenue Generation"
        ]].copy()

        for col in ["Budgeted Revenue Generation", "Actual Revenue Generation"]:
            income_df[col] = pd.to_numeric(income_df[col], errors="coerce").fillna(0)

        income_df["Revenue Achieved (%)"] = np.where(
            income_df["Budgeted Revenue Generation"] != 0,
            (income_df["Actual Revenue Generation"] /
             income_df["Budgeted Revenue Generation"]) * 100,
            0
        )

        fig3 = go.Figure()

        fig3.add_trace(go.Bar(
            x=income_df["Name of Project_Income"],
            y=income_df["Actual Revenue Generation"],
            name="Actual Revenue"
        ))

        fig3.add_trace(go.Bar(
            x=income_df["Name of Project_Income"],
            y=income_df["Revenue Achieved (%)"],
            name="Revenue Achieved %"
        ))

        fig3.add_trace(go.Scatter(
            x=income_df["Name of Project_Income"],
            y=income_df["Budgeted Revenue Generation"],
            name="Budgeted Revenue",
            mode="lines+markers",
            yaxis="y2"
        ))

        fig3.update_layout(
            template="plotly_white",
            barmode="group",
            yaxis2=dict(overlaying="y", side="right")
        )

        st.plotly_chart(fig3, use_container_width=True)

# =================================================
# 5️⃣ Donor-wise Budget vs Expenditure
# =================================================
with col5:
    if all(col in df.columns for col in ["Name of Project_2", "Revised Budget_D", "Expenditure_D"]):

        st.subheader("5️⃣ Donor Budget vs Expenditure")

        df["Name of Project_2"] = df["Name of Project_2"].astype(str).str.strip()

        for col in ["Revised Budget_D", "Expenditure_D"]:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace(" ", "", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        donor_df = (
            df.groupby("Name of Project_2", as_index=False)
            .agg({
                "Revised Budget_D": "sum",
                "Expenditure_D": "sum"
            })
        )

        fig5 = go.Figure()

        fig5.add_trace(go.Bar(
            x=donor_df["Name of Project_2"],
            y=donor_df["Revised Budget_D"],
            name="Revised Budget"
        ))

        fig5.add_trace(go.Bar(
            x=donor_df["Name of Project_2"],
            y=donor_df["Expenditure_D"],
            name="Expenditure"
        ))

        fig5.update_layout(
            barmode="group",
            template="plotly_white"
        )

        st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# =================================================
# 4️⃣ Cost Category Breakdown
# =================================================
if "Cost Category" in df.columns:

    st.header("4️⃣ Cost Category-wise Breakdown")

    df["Project_Name"] = df["Project_Name"].astype(str).str.strip()
    df["Cost Category"] = df["Cost Category"].astype(str).str.strip()

    for col in ["Cumulative Budget", "Cumulative Expenditure"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    col_filter, _ = st.columns([1, 4])
    with col_filter:
        project_selected = st.selectbox(
            "Select Project",
            sorted(df["Project_Name"].unique())
        )

    cost_df = (
        df[df["Project_Name"] == project_selected]
        .groupby("Cost Category", as_index=False)
        .agg({
            "Cumulative Budget": "sum",
            "Cumulative Expenditure": "sum"
        })
    )

    cost_df["Burn Rate"] = np.where(
        cost_df["Cumulative Budget"] != 0,
        (cost_df["Cumulative Expenditure"] /
         cost_df["Cumulative Budget"]) * 100,
        0
    )

    st.dataframe(cost_df, use_container_width=True)

st.markdown("---")
st.caption("Auto-updating Financial Dashboard | Streamlit + Google Sheets")
