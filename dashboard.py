
import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Student Analytics | Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- CUSTOM DESIGN ----------
st.markdown("""
<style>
    .stApp {
        background-color: #F4F7FB;
    }

    h1, h2, h3 {
        color: #172554;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #E2E8F0;
        padding: 18px;
        border-radius: 14px;
        box-shadow: 0 3px 10px rgba(15, 23, 42, 0.04);
    }

    div[data-testid="stMetricLabel"] {
        color: #64748B;
    }

    div[data-testid="stMetricValue"] {
        color: #1D4ED8;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 10px;
    }

    section[data-testid="stSidebar"] {
        background-color: #EAF0FA;
    }

    .subtitle {
        color: #64748B;
        font-size: 16px;
    }

    .section-card {
        background: white;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# ---------- LOAD DATA ----------
@st.cache_data
def load_data():
    return pd.read_csv("student_results.csv")

try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "student_results.csv not found. "
        "Run Student_analysis.py first."
    )
    st.stop()

subjects = [
    "Python", "Maths", "English", "Science", "Computer"
]

required = ["Student"] + subjects
missing = [col for col in required if col not in df.columns]

if missing:
    st.error(f"Dataset is missing these columns: {missing}")
    st.stop()

# Recalculate metrics so dashboard stays consistent
df["Total"] = df[subjects].sum(axis=1)
df["Percentage"] = df["Total"] / len(subjects)
df["Result"] = df[subjects].ge(35).all(axis=1).map({
    True: "Pass",
    False: "Fail"
})

# ---------- HEADER ----------
st.title("📊 Student Performance Analytics")
st.markdown(
    '<p class="subtitle">Academic performance overview | '
    'Student Data Analysis Project</p>',
    unsafe_allow_html=True
)

st.divider()

# ---------- SIDEBAR FILTERS ----------
st.sidebar.title("🎛️ Dashboard Controls")
st.sidebar.caption("Filter the student records")

search = st.sidebar.text_input(
    "🔎 Search student",
    placeholder="Enter student name"
)

result_filter = st.sidebar.selectbox(
    "📌 Result status",
    ["All Students", "Pass", "Fail"]
)

min_percentage = st.sidebar.slider(
    "Minimum percentage",
    min_value=0,
    max_value=100,
    value=0
)

filtered = df.copy()

if search:
    filtered = filtered[
        filtered["Student"].str.contains(
            search, case=False, na=False
        )
    ]

if result_filter != "All Students":
    filtered = filtered[
        filtered["Result"] == result_filter
    ]

filtered = filtered[
    filtered["Percentage"] >= min_percentage
]

st.sidebar.divider()
st.sidebar.caption(f"Matching records: {len(filtered)}")

# ---------- KPI CARDS ----------
total_students = len(filtered)

if total_students > 0:
    average = filtered["Percentage"].mean()
    pass_count = (filtered["Result"] == "Pass").sum()
    pass_rate = pass_count / total_students * 100
    topper = filtered.loc[
        filtered["Percentage"].idxmax(), "Student"
    ]
else:
    average = 0
    pass_rate = 0
    topper = "N/A"

c1, c2, c3, c4 = st.columns(4)

c1.metric("👩‍🎓 Students", total_students)
c2.metric("📈 Average Score", f"{average:.1f}%")
c3.metric("✅ Pass Rate", f"{pass_rate:.1f}%")
c4.metric("🏆 Top Performer", topper)

st.write("")

# ---------- CHARTS ----------
if total_students > 0:
    left, right = st.columns(2)

    with left:
        st.subheader("📚 Subject Performance")

        subject_avg = (
            filtered[subjects]
            .mean()
            .rename_axis("Subject")
            .reset_index(name="Average Marks")
        )

        fig_subject = px.bar(
            subject_avg,
            x="Subject",
            y="Average Marks",
            color="Average Marks",
            color_continuous_scale="Blues",
            text_auto=".1f",
            title="Average Marks by Subject"
        )

        fig_subject.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis_range=[0, 100],
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=55, b=10)
        )

        st.plotly_chart(
            fig_subject, use_container_width=True
        )

    with right:
        st.subheader("🎯 Pass vs Fail")

        result_counts = (
            filtered["Result"]
            .value_counts()
            .reindex(["Pass", "Fail"], fill_value=0)
            .rename_axis("Result")
            .reset_index(name="Students")
        )

        fig_result = px.pie(
            result_counts,
            names="Result",
            values="Students",
            hole=0.55,
            color="Result",
            color_discrete_map={
                "Pass": "#16A34A",
                "Fail": "#EF4444"
            },
            title="Result Distribution"
        )

        fig_result.update_layout(
            paper_bgcolor="white",
            margin=dict(l=10, r=10, t=55, b=10)
        )

        st.plotly_chart(
            fig_result, use_container_width=True
        )

    st.subheader("📊 Student Percentage Comparison")

    fig_students = px.bar(
        filtered.sort_values("Percentage", ascending=False),
        x="Student",
        y="Percentage",
        color="Percentage",
        color_continuous_scale="Teal",
        hover_data=["Total", "Result"],
        title="Percentage by Student"
    )

    fig_students.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis_range=[0, 100],
        coloraxis_showscale=False,
        xaxis_tickangle=-45,
        margin=dict(l=10, r=10, t=55, b=10)
    )

    st.plotly_chart(
        fig_students, use_container_width=True
    )

    # ---------- DATA TABLE ----------
    st.divider()
    st.subheader("📋 Student Records")
    st.caption(
        "Search and filters above also apply to this table."
    )

    display_cols = (
        ["Student"] + subjects +
        ["Total", "Percentage", "Result"]
    )

    display_df = filtered[display_cols].copy()
    display_df["Percentage"] = (
        display_df["Percentage"].round(2)
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    csv_data = display_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download Filtered Results",
        data=csv_data,
        file_name="student_analysis_report.csv",
        mime="text/csv"
    )

else:
    st.warning(
        "No students match these filters. "
        "Please change your search or filters."
    )

# ---------- FOOTER ----------
st.divider()
st.caption(
    "Student Performance Analytics | "
    "Built with Python, Pandas, Streamlit and Plotly"
)
