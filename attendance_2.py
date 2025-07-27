from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---- Page Config ----
st.set_page_config(page_title="Attendance Dashboard", layout="wide")

# ---- Styling ----
# Enrolment Summary Table Styling
st.markdown("""
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
        width: 35%;
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
st.markdown("### 🧭 Instructions")
st.info("""
1. Select **Year**, **Term**, and **Education Level** from the sidebar to display enrolment data.
2. Once enrolment data is shown, scroll down to view Attendance data.
3. Use Attendance filters to explore weekly and gender-based trends.
""")
# --- Sidebar Logo at Top ---
with st.sidebar:
    logo_path = "assets/fca_logo1.png"
    if Path(logo_path).exists():
        logo = Image.open(logo_path)
        st.image(logo, use_container_width=True)

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
st.sidebar.markdown("## 👣 Start Here")
st.sidebar.info("Begin by selecting filters below to view **Enrolment Data**. Once done, proceed to Attendance filters.")
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

    # Prepare the data
    multi_school_df = enrol_summary[enrol_summary["School_Name"] != "TOTAL"].copy()

    gender_bar_df = pd.melt(
        multi_school_df,
        id_vars="School_Name",
        value_vars=["Boys", "Girls"],
        var_name="Gender",
        value_name="Count"
    )

    # Create an enhanced grouped bar chart
    fig_multi = px.bar(
        gender_bar_df,
        x="School_Name",
        y="Count",
        color="Gender",
        barmode="group",
        text="Count",
        title="👨‍👩‍👧‍👦 Enrolment by Gender per School",
        color_discrete_map={"Boys": "#1f77b4", "Girls": "#e377c2"},  # custom colors
    )

    # Improve layout and readability
    fig_multi.update_layout(
        yaxis_title="Enrolled Learners",
        xaxis_title="School",
        title_font_size=20,
        height=600,
        bargap=0.2,
        bargroupgap=0.1,
        xaxis_tickangle=-30,
        legend=dict(
            title="Gender",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    # Refine trace styling
    fig_multi.update_traces(
    texttemplate="%{text:,}",
    textposition="outside",
    width=0.3
    )

    # Show the chart in Streamlit
    st.plotly_chart(fig_multi, use_container_width=True)


    # ---- Merge Attendance Data ----
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
        weeks = merged_df[
            (merged_df["Year"] == int(selected_year)) &
            (merged_df["Term"] == selected_term)
        ]["Attendance_Week"].dropna().unique()

    # ✅ NEW DROPDOWN — Education Level filter for Attendance Table
    attendance_levels = list(school_order.keys())
    selected_attendance_level = st.sidebar.selectbox(
        "Education Level (Attendance Table)",
        ["Select Level", "ALL LEVELS"] + attendance_levels
    )

    # Extract numeric part, sort descending, then rebuild full week label
    weeks_sorted = sorted(weeks, key=lambda w: int(w.split()[-1]), reverse=True)
    selected_week = st.sidebar.selectbox("Select Week", ["Select Week"] + weeks_sorted)

    trend_weeks = merged_df["Attendance_Week"].dropna().unique()
    trend_weeks_sorted = sorted(trend_weeks, key=lambda w: int(w.split()[-1]), reverse=True)

    selected_trend_weeks = st.sidebar.multiselect(
        "Compare Trend Weeks",
        trend_weeks_sorted,
        default=trend_weeks_sorted[:2]  # Select 2 most recent by default
    )

    # ✅ Optional: sort again here in *ascending* order for stacking logic (bottom = oldest)
    selected_trend_weeks = sorted(selected_trend_weeks, key=lambda w: int(w.split()[-1]))

    if selected_term == "Select Term" or selected_week == "Select Week":
        st.warning("📌 To view attendance summaries and charts, please select both a valid **term** and **week** from the attendance filters.")
        st.stop()

    filtered_df = merged_df[(merged_df["Term"] == selected_term) & (merged_df["Attendance_Week"] == selected_week)]

    # ---- Display Attendance Summary Table Before Charts ----
    if selected_attendance_level != "Select Level":
        st.subheader(f"🧾 Attendance Summary Table — {selected_attendance_level}")

        if selected_attendance_level == "ALL LEVELS":
            df_level_attendance = filtered_df[filtered_df["Education_Level"].isin(school_order.keys())].copy()
        else:
            df_level_attendance = filtered_df[filtered_df["Education_Level"] == selected_attendance_level].copy()

        # Maintain school order as in enrolment section
        if selected_attendance_level == "ALL LEVELS":
            seen = set()
            ordered_schools = []
            for level in ["ECDE", "Primary", "Junior", "Secondary"]:
                for school in school_order.get(level, []):
                    if school not in seen:
                        ordered_schools.append(school)
                        seen.add(school)
        else:
            ordered_schools = school_order[selected_attendance_level]

        schools_df = pd.DataFrame(ordered_schools, columns=["School_Name"])
        df_level_attendance = schools_df.merge(df_level_attendance, on="School_Name", how="left")

        # Fill NaNs
        for col in ["Boys_Attendance", "Girls_Attendance", "Total_Attendance",
                    "Boys_Enrolment", "Girls_Enrolment", "Total_Enrolment"]:
            df_level_attendance[col] = df_level_attendance[col].fillna(0)

        # Group and summarize attendance by school
        attendance_summary = df_level_attendance.groupby("School_Name").agg({
            "Boys_Attendance": "sum",
            "Girls_Attendance": "sum",
            "Total_Attendance": "sum",
            "Boys_Enrolment": "sum",
            "Girls_Enrolment": "sum",
            "Total_Enrolment": "sum"
        }).reset_index()

        # Calculate rates
        attendance_summary["Attendance Rate (%)"] = (
            attendance_summary["Total_Attendance"] /
            attendance_summary["Total_Enrolment"].replace(0, pd.NA)
        ) * 100
        attendance_summary["Attendance Rate (%)"] = attendance_summary["Attendance Rate (%)"].round(1)

        # Add TOTAL row
        total_row = {
            "School_Name": "TOTAL",
            "Boys_Attendance": attendance_summary["Boys_Attendance"].sum(),
            "Girls_Attendance": attendance_summary["Girls_Attendance"].sum(),
            "Total_Attendance": attendance_summary["Total_Attendance"].sum(),
            "Boys_Enrolment": attendance_summary["Boys_Enrolment"].sum(),
            "Girls_Enrolment": attendance_summary["Girls_Enrolment"].sum(),
            "Total_Enrolment": attendance_summary["Total_Enrolment"].sum()
        }
        total_row["Attendance Rate (%)"] = (
            total_row["Total_Attendance"] / total_row["Total_Enrolment"]
        ) * 100 if total_row["Total_Enrolment"] else 0
        total_row["Attendance Rate (%)"] = round(total_row["Attendance Rate (%)"], 1)
        attendance_summary = pd.concat(
            [attendance_summary, pd.DataFrame([total_row])],
            ignore_index=True
        )

        # Format numbers for display
        # Format numeric columns
        for col in ["Boys_Attendance", "Girls_Attendance", "Total_Attendance",
                    "Boys_Enrolment", "Girls_Enrolment", "Total_Enrolment"]:
            attendance_summary[col] = attendance_summary[col].apply(lambda x: f"{int(x):,}")

        attendance_summary["Attendance Rate (%)"] = (
        attendance_summary["Attendance Rate (%)"]
        .fillna(0)
        .round(0)
        .astype(int)
        .astype(str) + "%")

        # Styled HTML Table
        st.markdown("""
            <style>
            .attendance-table {
                border-collapse: collapse;
                width: 100%;
                font-family: 'Segoe UI', sans-serif;
                font-size: 15px;
                margin-top: 1rem;
                margin-bottom: 1rem;
                table-layout: auto;
            }

            .attendance-table th {
                background-color: #004c6d;
                color: white;
                font-weight: bold;
                padding: 10px;
                text-align: center;
                border: 1px solid #ddd;
            }

            .attendance-table td {
                padding: 10px;
                border: 1px solid #ddd;
                vertical-align: middle;
                font-weight: 500;
            }

            .attendance-table td:first-child {
                text-align: left;
                width: 35%;
            }

            .attendance-table td:nth-child(n+2) {
                text-align: right;
            }

            .attendance-table tr:nth-child(even):not(:last-child) {
                background-color: #f9f9f9;
            }

            .attendance-table tr:hover:not(:last-child) {
                background-color: #e8f4fa;
            }

            .attendance-table tr:last-child {
                background-color: #e0f7e9;
                font-weight: bold;
                border-top: 2px solid #006c4e;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown(
        attendance_summary[[
            "School_Name",
            "Boys_Attendance",
            "Girls_Attendance",
            "Total_Attendance",
            "Total_Enrolment",
            "Attendance Rate (%)"
        ]].to_html(index=False, classes="attendance-table", escape=False, border=0),
        unsafe_allow_html=True
    )

    else:
        st.info("Please select an education level to view attendance summary table.")
        # Optionally, you can add more logic here if needed.
    if selected_attendance_level != "Select Level" and 'attendance_summary' in locals():
        st.subheader(f"📊 Attendance Rate Chart — {selected_attendance_level}")

        # Convert numeric columns back to integers for plotting
        attendance_summary_numeric = attendance_summary.copy()
        for col in ["Boys_Attendance", "Girls_Attendance", "Total_Attendance", "Total_Enrolment"]:
            attendance_summary_numeric[col] = attendance_summary_numeric[col].replace(",", "", regex=True).replace("TOTAL", 0).astype(str).str.replace(",", "").astype(int)

        # Remove TOTAL row for plotting
        attendance_summary_plot = attendance_summary_numeric[attendance_summary_numeric["School_Name"] != "TOTAL"].copy()

        # Convert Attendance Rate (%) to numeric for plotting
        attendance_summary_plot["Attendance Rate (%)"] = attendance_summary_plot["Attendance Rate (%)"].str.replace("%", "").astype(float)

        # Assign a unique color to each school using Plotly's qualitative palette
        color_palette = px.colors.qualitative.Plotly
        school_names = attendance_summary_plot["School_Name"].tolist()
        color_map = {school: color_palette[i % len(color_palette)] for i, school in enumerate(school_names)}
        attendance_summary_plot["Color"] = attendance_summary_plot["School_Name"].map(color_map)

        # Assign a unique color to each school using Plotly's qualitative palette
        color_palette = px.colors.qualitative.Plotly
        school_names = attendance_summary_plot["School_Name"].tolist()
        color_map = {school: color_palette[i % len(color_palette)] for i, school in enumerate(school_names)}
        attendance_summary_plot["Color"] = attendance_summary_plot["School_Name"].map(color_map)

        fig = px.bar(
            attendance_summary_plot,
            x="School_Name",
            y="Attendance Rate (%)",
            text=attendance_summary_plot["Attendance Rate (%)"].round(0).astype(int).astype(str) + "%",
            title="📊 Attendance Rate per School",
            height=600,
            width=1800,  # ✅ Manually increase width
            color_discrete_sequence=["#1f77b4"]  # ✅ Single color to avoid splitting bars
        )

        fig.update_traces(
            textposition='outside',
            marker_line_width=1,
            marker_line_color='black'
        )

        fig.update_layout(
            xaxis_title="School",
            yaxis_title="Attendance Rate (%)",
            xaxis_tickangle=45,
            bargap=0.02,  # ✅ Small gap = thicker bars
            showlegend=False,
            margin=dict(l=40, r=40, t=60, b=150),
            xaxis=dict(categoryorder="total descending")  # ✅ Sorts for clarity
        )

        # 🚫 DO NOT use use_container_width
        st.plotly_chart(fig)

    # ---- Attendance Charts ----
    for level, schools in school_order.items():
        st.markdown(f"---\n### 📊 {level} Attendance Charts — Term {selected_term}, {selected_week}")

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

        # Sort trend weeks from newest to oldest (for stacking: top=latest)
        ordered_weeks = sorted(selected_trend_weeks, key=lambda w: int(w.split()[-1]), reverse=True)

        # Step 1: Force category order for weeks (newest to oldest for stacking: top=latest)
        trend_df["Attendance_Week"] = pd.Categorical(
            trend_df["Attendance_Week"],
            categories=ordered_weeks,
            ordered=True
        )

        # Step 2: Sort data to match stacking order: School > Grade > Week
        trend_df = trend_df.sort_values(["School_Name", "Grade_Level", "Attendance_Week"])

        # Grouping after proper ordering
        trend_df = trend_df.groupby(["School_Name", "Grade_Level", "Attendance_Week"]).agg(
            Attendance_Rate=('Attendance Rate (%)', 'mean')
        ).reset_index()

        trend_df["Label"] = trend_df["Attendance_Rate"].round(0).astype(int).astype(str) + "%"

        # Get unique school facets
        school_facets = trend_df["School_Name"].unique()
        n_cols = 2
        n_rows = -(-len(school_facets) // n_cols)  # Ceiling division

        # Create subplot layout
        fig_trend = make_subplots(
            rows=n_rows,
            cols=n_cols,
            subplot_titles=school_facets,
            shared_yaxes=True,
            shared_xaxes=False,
        )

        # Mapping from school name to subplot row/col
        school_positions = {
            school: divmod(idx, n_cols) for idx, school in enumerate(school_facets)
        }

        colors = px.colors.qualitative.Plotly  # Consistent color palette

        # For each school, plot stacked bars for each grade, with each week as a segment
        for school in school_facets:
            row, col = school_positions[school]
            row += 1
            col += 1

            grades = trend_df[trend_df["School_Name"] == school]["Grade_Level"].unique()
            grades = sorted(grades)

            # For each week (newest to oldest, so top=latest), collect y-values for each grade
            for week_index, week in enumerate(ordered_weeks):
                color = colors[week_index % len(colors)]
                week_data = trend_df[
                    (trend_df["School_Name"] == school) &
                    (trend_df["Attendance_Week"] == week)
                ]
                # Ensure all grades are present (fill missing with 0)
                week_y = []
                week_labels = []
                for grade in grades:
                    row_data = week_data[week_data["Grade_Level"] == grade]
                    if not row_data.empty:
                        week_y.append(row_data["Attendance_Rate"].values[0])
                        week_labels.append(row_data["Label"].values[0])
                    else:
                        week_y.append(0)
                        week_labels.append("0%")

                fig_trend.add_trace(
                    go.Bar(
                        x=grades,
                        y=week_y,
                        name=week,
                        marker_color=color,
                        text=week_labels,
                        textposition="inside",
                        showlegend=(row == 1 and col == 1)
                    ),
                    row=row, col=col
                )

        fig_trend.update_layout(
            height=800,
            barmode="stack",
            title_text=f"📊 Weekly Attendance Trends per Grade — {level}",
            legend_title="Attendance Week",
            yaxis_title="Attendance Rate (%)",
            xaxis_title="Grade Level"
        )

        # Reverse legend order so newest week is at the top
        fig_trend.update_layout(legend_traceorder="reversed")

        fig_trend.update_traces(texttemplate="%{text}", textposition="inside")
        st.plotly_chart(fig_trend, use_container_width=True)

    # ---- 📈 Attendance Trend Line (After Comparative Stacked Bars) ----
    st.markdown("### Weekly Attendance Trend Line by School")

    # Prepare trend data
    trend_df = merged_df.copy()

    # Filter by selected education level
    if selected_attendance_level != "ALL LEVELS":
        trend_df = trend_df[trend_df["Education_Level"] == selected_attendance_level]

    # Group by Week and School
    weekly_attendance = (
        trend_df.groupby(["Attendance_Week", "School_Name"])["Total_Attendance"]
        .sum()
        .reset_index()
    )

    # Ensure weeks are sorted chronologically
    week_order = sorted(weekly_attendance['Attendance_Week'].unique(), reverse=False)
    weekly_attendance["Attendance_Week"] = pd.Categorical(
        weekly_attendance["Attendance_Week"], categories=week_order, ordered=True
    )

    # Line chart using Plotly
    fig = px.line(
        weekly_attendance,
        x="Attendance_Week",
        y="Total_Attendance",
        color="School_Name",
        markers=True,
        labels={"Attendance_Week": "Week", "Total_Attendance": "Attendance"},
        title="Attendance Trend Over Time"
    )

    fig.update_layout(
        xaxis_title="Week",
        yaxis_title="Total Attendance",
        plot_bgcolor='white',
        hovermode='x unified',
        legend_title_text="School"
    )

    st.plotly_chart(fig, use_container_width=True)

