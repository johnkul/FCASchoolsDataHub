from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# ---- Page Config ----
st.set_page_config(page_title="Attendance Dashboard", layout="wide")

# ---- Styling ----
st.markdown("""
    <style>
        body, .stApp {
            background-color: #f9f9f9;
            color: #222222;
            font-family: 'Segoe UI', sans-serif;
        }
        section[data-testid="stSidebar"] {
            background-color: #004c6d;
            color: white;
        }
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] label,
        .stSelectbox label {
            color: white !important;
            font-weight: 600;
        }
        .stSelectbox div[role="button"] {
            color: black !important;
        }
        .stSelectbox div[data-baseweb="select"] {
            background-color: white !important;
            color: black !important;
        }
        .stSelectbox span {
            color: black !important;
        }
        /* Fix selectbox label color in main area */
        .stSelectbox label {
            color: #222222 !important;
            font-weight: 600;
        }
        <style>
        .enrolment-table {
            border-collapse: collapse;
            width: 100%;
            font-family: 'Segoe UI', sans-serif;
            font-size: 15px;
            margin-top: 1rem;
            margin-bottom: 1rem;
            table-layout: auto;
        }

        .enrolment-table th {
            background-color: #004c6d;
            color: white;
            font-weight: bold;
            padding: 10px;
            text-align: center;
            border: 1px solid #ddd;
        }

        .enrolment-table td {
            padding: 10px;
            border: 1px solid #ddd;
            vertical-align: middle;
            font-weight: 500;
        }

        .enrolment-table td:first-child {
            text-align: left;
            width: 40%;
        }

        .enrolment-table td:nth-child(n+2) {
            text-align: right;
        }

        .enrolment-table tr:nth-child(even):not(:last-child) {
            background-color: #f9f9f9;
        }

        .enrolment-table tr:hover:not(:last-child) {
            background-color: #e8f4fa;
        }

        .enrolment-table tr:last-child {
            background-color: #e0f7e9;
            font-weight: bold;
            border-top: 2px solid #006c4e;
        }
    </style>
""", unsafe_allow_html=True)

# ---- Title ----
st.title("FCA Schools Data Dashboard")

# ---- Logo ----
logo_path = "assets/fca_logo1.png"
if Path(logo_path).exists():
    logo = Image.open(logo_path)
    st.sidebar.image(logo, use_column_width=True)

# ---- Load File ----
data_path = Path("School Enrolment&Attendance/Enrolment Data vs Attendance Report.xlsx")
if not data_path.exists():
    st.error(f"⚠️ File not found: '{data_path}' — make sure the file is in the app directory.")
    st.stop()

xls = pd.ExcelFile(data_path)
enrol_df = xls.parse("Enrolment Data")
attend_df = xls.parse("Attendance Report")

for df in [enrol_df, attend_df]:
    for col in ["Boys", "Girls", "Total"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# ---- Enrolment Filter Section ----
st.sidebar.header("📋 Filter Enrolment Data")
enrol_years = sorted(enrol_df["Year"].dropna().unique())
selected_enrol_year = st.sidebar.selectbox("Year (Enrolment)", ["Select Year"] + [str(y) for y in enrol_years])

enrol_terms = sorted(enrol_df["Term"].dropna().unique())
selected_enrol_term = st.sidebar.selectbox("Term (Enrolment)", ["Select Term"] + enrol_terms)

edu_levels = sorted(enrol_df["Education_Level"].dropna().unique())
selected_edu_level = st.sidebar.selectbox("Education Level", ["Select Education Level", "ALL LEVELS"] + edu_levels)

grades = sorted(enrol_df["Grade_Level"].dropna().unique())

# Logic to populate or disable Grade Level selectbox
if selected_edu_level == "Select Education Level":
    selected_grade_level = st.sidebar.selectbox("Grade Level", ["Select Grade Level"])
elif selected_edu_level == "ALL LEVELS":
    st.sidebar.selectbox("Grade Level", ["All Levels Combined"], disabled=True)
    selected_grade_level = "All Levels Combined"
else:
    grade_choices = sorted(enrol_df[enrol_df["Education_Level"] == selected_edu_level]["Grade_Level"].dropna().unique())
    selected_grade_level = st.sidebar.selectbox("Grade Level", ["Select Grade Level"] + grade_choices)

# ---- Filter and Display Enrolment Table ----
school_order = {
    "ECDE": ["Kalobeyei Morning Star Sch", "Kalobeyei Settlement Sch", "Kalobeyei Friends Sch", "Joy Sch", "Future Sch", "Bright Sch", "Nationokar Sch", "Esikiriat Sch"],
    "Primary": ["Kalobeyei Morning Star Sch", "Kalobeyei Settlement Sch", "Kalobeyei Friends Sch", "Joy Sch", "Future Sch", "Bright Sch", "Nationokar Sch", "Esikiriat Sch"],
    "Junior": ["Kalobeyei Morning Star Sch", "Kalobeyei Settlement Sch", "Kalobeyei Friends Sch", "Joy Sch", "Future Sch", "Bright Sch", "Nationokar Sch", "Esikiriat Sch"],
    "Secondary": ["Kalobeyei Settlement Secondary", "Brightstar Integrated Secondary", "The Big Heart Foundation Girls"]
}

if (
    selected_enrol_year != "Select Year" and
    selected_enrol_term != "Select Term" and
    selected_edu_level != "Select Education Level"
):
    # Filter by Year and Term first
    enrol_filtered = enrol_df[
        (enrol_df["Year"] == int(selected_enrol_year)) &
        (enrol_df["Term"] == selected_enrol_term)
    ]

    # Filter by education level (if not ALL)
    if selected_edu_level != "ALL LEVELS":
        enrol_filtered = enrol_filtered[enrol_filtered["Education_Level"] == selected_edu_level]

    # Filter by grade (only if not ALL LEVELS)
    if selected_edu_level != "ALL LEVELS" and selected_grade_level != "Select Grade Level":
        enrol_filtered = enrol_filtered[enrol_filtered["Grade_Level"] == selected_grade_level]
        enrol_summary = enrol_filtered[["School_Name", "Boys", "Girls", "Total"]]
    else:
        enrol_summary = enrol_filtered.groupby("School_Name")[["Boys", "Girls", "Total"]].sum().reset_index()

    # Generate school list depending on level
    if selected_edu_level == "ALL LEVELS":
        school_list = list(set(sum(school_order.values(), [])))  # Flatten & remove duplicates
    else:
        school_list = school_order[selected_edu_level]

    school_df = pd.DataFrame(school_list, columns=["School_Name"])
    enrol_summary = school_df.merge(enrol_summary, on="School_Name", how="left").fillna(0)

        # Reorder enrol_summary to match custom order
    if selected_edu_level == "ALL LEVELS":
        custom_order = list(set(sum(school_order.values(), [])))  # Flattened unique list
        # Optional: Maintain order exactly as in ECDE → Secondary
        seen = set()
        ordered_all = []
        for level in ["ECDE", "Primary", "Junior", "Secondary"]:
            for school in school_order.get(level, []):
                if school not in seen:
                    ordered_all.append(school)
                    seen.add(school)
        custom_order = ordered_all
    else:
        custom_order = school_order[selected_edu_level]

    enrol_summary["School_Name"] = pd.Categorical(enrol_summary["School_Name"], categories=custom_order + ["TOTAL"], ordered=True)
    enrol_summary = enrol_summary.sort_values("School_Name").reset_index(drop=True)


    total_row = pd.DataFrame({
        "School_Name": ["TOTAL"],
        "Boys": [enrol_summary["Boys"].sum()],
        "Girls": [enrol_summary["Girls"].sum()],
        "Total": [enrol_summary["Total"].sum()]
    })

    enrol_summary = pd.concat([enrol_summary, total_row], ignore_index=True)


    if not enrol_summary.empty:
        st.markdown(f"### 🏫 Enrolment Summary Table — {selected_edu_level}")

        # Format numbers with commas for display
        formatted_df = enrol_summary.copy()
        for col in ["Boys", "Girls", "Total"]:
            formatted_df[col] = formatted_df[col].apply(lambda x: f"{int(x):,}")

        # Display as styled HTML table without index
        st.markdown(
            formatted_df[["School_Name", "Boys", "Girls", "Total"]].to_html(
                index=False,
                classes="enrolment-table",
                escape=False,
                border=0
            ),
            unsafe_allow_html=True
        )

        # Dropdown for selecting school, excluding TOTAL
        # Add "ALL SCHOOLS" option to dropdown
        select_options = enrol_summary[enrol_summary["School_Name"] != "TOTAL"]["School_Name"].tolist()
        select_options.insert(0, "ALL SCHOOLS")

        selected_school = st.selectbox("📍 Select a school to view its enrolment details:", select_options)

        if selected_school:
            if selected_school == "ALL SCHOOLS":
                total_row = enrol_summary[enrol_summary["School_Name"] == "TOTAL"].iloc[0]
            st.success(
                f"**Total Enrolment Across All Schools**  \n"
                f"👦 Boys: {int(total_row['Boys']):,}  \n"
                f"👧 Girls: {int(total_row['Girls']):,}  \n"
                f"👥 Total: {int(total_row['Total']):,}"
            )
        else:
            selected_row = enrol_summary[enrol_summary["School_Name"] == selected_school].iloc[0]
            st.success(
                f"**{selected_school} Enrolment**  \n"
                f"👦 Boys: {int(selected_row['Boys']):,}  \n"
                f"👧 Girls: {int(selected_row['Girls']):,}  \n"
                f"👥 Total: {int(selected_row['Total']):,}"
            )

        # Show grouped bar chart for all schools: Boys vs Girls
        multi_school_df = enrol_summary[enrol_summary["School_Name"] != "TOTAL"].copy()

        gender_bar_df = pd.melt(
            multi_school_df,
            id_vars="School_Name",
            value_vars=["Boys", "Girls"],
            var_name="Gender",
            value_name="Count"
        )

        fig_multi = px.bar(
            gender_bar_df,
            x="School_Name",
            y="Count",
            color="Gender",
            barmode="group",
            text="Count",
            title="👨‍👩‍👧‍👦 Enrolment by Gender per School",
        )

        fig_multi.update_layout(
            yaxis_title="Enrolled Learners",
            xaxis_title="School",
            height=600,
            xaxis_tickangle=-45,
            bargap=0.25,
            bargroupgap=0.15,
            uniformtext_minsize=8,
            uniformtext_mode='show'
        )

        fig_multi.update_traces(
            texttemplate="%{text:,}",
            textposition="auto",  # Automatically choose best position
            marker_line_width=1,
            marker_line_color='black',
            width=0.3
        )

        st.plotly_chart(fig_multi, use_container_width=True)


# ---- Merge Attendance Data ----
st.header("FCA Schools Attendance Data Visuals")
common_cols = ["School_Name", "Grade_Level", "Education_Level", "Term", "Year"]
merged_df = pd.merge(attend_df, enrol_df, on=common_cols, suffixes=('_Attendance', '_Enrolment'))

merged_df["Attendance Rate (%)"] = (merged_df["Total_Attendance"] / merged_df["Total_Enrolment"]) * 100
merged_df["Attendance Rate (%)"] = merged_df["Attendance Rate (%)"].fillna(0)
merged_df["Rate_Label"] = merged_df["Attendance Rate (%)"].round(0).astype(int).astype(str) + "%"

# ---- Attendance Filters ----
st.sidebar.header("📅 Filter Attendance Data")
years = sorted(merged_df["Year"].dropna().unique())
selected_year = st.sidebar.selectbox("Select Year", ["Select Year"] + [str(y) for y in years])

terms = sorted(merged_df["Term"].dropna().unique())
selected_term = st.sidebar.selectbox("Select Term", ["Select Term"] + terms)

weeks = []
if selected_year != "Select Year" and selected_term != "Select Term":
    weeks = merged_df[(merged_df["Year"] == int(selected_year)) & (merged_df["Term"] == selected_term)]["Attendance_Week"].dropna().unique()
selected_week = st.sidebar.selectbox("Select Week", ["Select Week"] + sorted(weeks))

trend_weeks = sorted(merged_df["Attendance_Week"].dropna().unique())
selected_trend_weeks = st.sidebar.multiselect("Compare Trend Weeks", trend_weeks, default=trend_weeks[-2:])

if selected_term == "Select Term" or selected_week == "Select Week":
    st.warning("Please select both a term and a week to display the charts.")
    st.stop()

filtered_df = merged_df[(merged_df["Term"] == selected_term) & (merged_df["Attendance_Week"] == selected_week)]

# ---- Attendance Charts ----
for level, schools in school_order.items():
    st.header(f"{level} Level — Term {selected_term}, Week {selected_week}")

    df_level = filtered_df[filtered_df["Education_Level"] == level].copy()
    schools_df = pd.DataFrame(schools, columns=["School_Name"])
    df_level = schools_df.merge(df_level, on="School_Name", how="left")

    for col in ["Attendance Rate (%)", "Total_Attendance", "Total_Enrolment", "Grade_Level"]:
        df_level[col] = df_level[col].fillna(0 if col != "Grade_Level" else "N/A")
    df_level["Rate_Label"] = df_level["Attendance Rate (%)"].round(0).astype(int).astype(str) + "%"

    fig1 = px.bar(
        df_level,
        x="School_Name",
        y="Attendance Rate (%)",
        color="Grade_Level",
        barmode="group",
        text="Rate_Label",
        title=f"Attendance Rate per Grade and School — {level}",
        hover_data=["Education_Level", "Grade_Level", "Total_Enrolment", "Total_Attendance"]
    )
    fig1.update_layout(xaxis_tickangle=-45, height=500)
    st.plotly_chart(fig1, use_container_width=True)

    for col in ["Boys_Attendance", "Girls_Attendance", "Boys_Enrolment", "Girls_Enrolment"]:
        df_level[col] = df_level[col].fillna(0)

    def summarize_gender(df, gender):
        grouped = df.groupby("School_Name")[[f"{gender}_Attendance", f"{gender}_Enrolment"]].sum().reset_index()
        grouped["Gender"] = gender
        grouped["Rate"] = (grouped[f"{gender}_Attendance"] / grouped[f"{gender}_Enrolment"].replace(0, pd.NA)) * 100
        return grouped.rename(columns={f"{gender}_Attendance": "Attendance", f"{gender}_Enrolment": "Enrolment"})

    boys = summarize_gender(df_level, "Boys")
    girls = summarize_gender(df_level, "Girls")
    total = df_level.groupby("School_Name")[["Total_Attendance", "Total_Enrolment"]].sum().reset_index()
    total["Gender"] = "Average"
    total["Rate"] = (total["Total_Attendance"] / total["Total_Enrolment"].replace(0, pd.NA)) * 100
    total = total.rename(columns={"Total_Attendance": "Attendance", "Total_Enrolment": "Enrolment"})

    combined = pd.concat([boys, girls, total])[["School_Name", "Gender", "Attendance", "Enrolment", "Rate"]]
    combined["Rate"] = combined["Rate"].fillna(0)
    combined["Label"] = combined["Rate"].round(0).astype(int).astype(str) + "%"

    fig2 = px.bar(
        combined,
        x="School_Name",
        y="Rate",
        color="Gender",
        text="Label",
        barmode="group",
        title=f"Attendance Rate by Gender — {level}",
        hover_data=["Attendance", "Enrolment"]
    )
    fig2.update_layout(xaxis_tickangle=-45, height=500)
    st.plotly_chart(fig2, use_container_width=True)

# ---- Weekly Trends ----
st.markdown("---")
st.header("📈 Comparative Attendance Trends by Grade and Week")

for level in school_order.keys():
    trend_df = merged_df[
        (merged_df["Education_Level"] == level) &
        (merged_df["Attendance_Week"].isin(selected_trend_weeks))
    ].copy()

    if trend_df.empty:
        st.info(f"No data for {level} in the selected trend weeks.")
        continue

    trend_df = trend_df.groupby(["School_Name", "Grade_Level", "Attendance_Week"]).agg(
        Attendance_Rate=('Attendance Rate (%)', 'mean')
    ).reset_index()
    trend_df["Label"] = trend_df["Attendance_Rate"].round(0).astype(int).astype(str) + "%"

    fig_trend = px.bar(
        trend_df,
        x="Grade_Level",
        y="Attendance_Rate",
        color="Attendance_Week",
        barmode="stack",
        text="Label",
        facet_col="School_Name",
        facet_col_wrap=2,
        title=f"📊 Weekly Attendance Trends per Grade — {level}",
        labels={"Attendance_Rate": "Attendance Rate (%)"}
    )
    fig_trend.update_traces(texttemplate="%{text}", textposition="inside")
    fig_trend.update_layout(
        height=800,
        legend_title="Attendance Week",
        yaxis_title="Attendance Rate (%)",
        xaxis_title="Grade Level"
    )
    st.plotly_chart(fig_trend, use_container_width=True)
