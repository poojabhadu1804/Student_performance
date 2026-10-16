
import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import urlparse

st.set_page_config(
    page_title="Analyse Your Own Data",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Analyse Your Own Student Data")
st.caption(
    "Upload a dataset or import an external CSV "
    "to analyse student performance."
)

# ---------- CHOOSE DATA SOURCE ----------
source = st.radio(
    "Choose your data source",
    ["Upload File", "External CSV URL"],
    horizontal=True
)

uploaded_df = None

if source == "Upload File":
    uploaded_file = st.file_uploader(
        "Upload student data",
        type=["csv", "xlsx"]
    )

    if uploaded_file is not None:
        try:
            if uploaded_file.name.lower().endswith(".xlsx"):
                uploaded_df = pd.read_excel(uploaded_file)
            else:
                uploaded_df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"Unable to read file: {e}")

else:
    csv_url = st.text_input(
        "Paste a direct CSV URL",
        placeholder="https://example.com/students.csv"
    )

    if csv_url.strip():
        parsed = urlparse(csv_url.strip())

        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            st.error("Enter a valid HTTP or HTTPS URL.")
        else:
            try:
                uploaded_df = pd.read_csv(
                    csv_url.strip(),
                    nrows=10000,
                    on_bad_lines="error"
                )
            except Exception:
                st.error(
                    "Could not read this URL as a CSV. "
                    "Check the link, access permissions "
                    "and internet connection."
                )

# ---------- PREVIEW & CONFIGURE ----------
if uploaded_df is not None:
    if uploaded_df.empty:
        st.error("The uploaded dataset is empty.")
        st.stop()

    # Clean column names
    uploaded_df.columns = (
        uploaded_df.columns.astype(str).str.strip()
    )

    if uploaded_df.columns.duplicated().any():
        st.error(
            "Your file contains duplicate column names. "
            "Rename them and upload again."
        )
        st.stop()

    st.subheader("1. Preview Your Dataset")
    st.write(
        f"Rows: {len(uploaded_df)} | "
        f"Columns: {len(uploaded_df.columns)}"
    )
    st.dataframe(
        uploaded_df.head(10),
        use_container_width=True,
        hide_index=True
    )

    columns = uploaded_df.columns.tolist()

    # Find numeric columns for suggested subjects
    numeric_cols = [
        c for c in columns
        if pd.api.types.is_numeric_dtype(uploaded_df[c])
    ]

    st.subheader("2. Configure Your Analysis")

    name_options = ["None"] + columns
    default_name_index = next(
        (i for i, c in enumerate(name_options)
         if c.lower() in ["name", "student", "student name",
                          "student_name", "student id", "id"]),
        0
    )

    name_col = st.selectbox(
        "Student name or ID column",
        name_options,
        index=default_name_index
    )

    suggested_subjects = [
        c for c in numeric_cols
        if c != name_col
        and any(word in c.lower() for word in
                ["python", "math", "english", "science",
                 "computer", "physics", "chemistry", "mark",
                 "score", "subject"])
    ]

    if not suggested_subjects:
        suggested_subjects = [
            c for c in numeric_cols if c != name_col
        ]

    subject_cols = st.multiselect(
        "Select columns containing marks (0–100)",
        [c for c in columns if c != name_col],
        default=suggested_subjects
    )

    if st.button("Analyse Dataset", type="primary"):
        if not subject_cols:
            st.error("Select at least one subject marks column.")
            st.stop()

        data = uploaded_df.copy()

        for col in subject_cols:
            data[col] = pd.to_numeric(
                data[col], errors="coerce"
            )

        if data[subject_cols].isna().any().any():
            st.error(
                "Selected marks columns contain blank or "
                "non-numeric values. Please correct the data."
            )
            st.stop()

        if not data[subject_cols].apply(
            lambda col: col.between(0, 100).all()
        ).all():
            st.error("All marks must be between 0 and 100.")
            st.stop()

        data["Total"] = data[subject_cols].sum(axis=1)
        data["Percentage"] = (
            data["Total"] / len(subject_cols)
        )
        data["Result"] = (
            data[subject_cols].ge(35).all(axis=1)
            .map({True: "Pass", False: "Fail"})
        )

        if name_col == "None":
            data.insert(
                0, "Student",
                [f"Student {i + 1}" for i in range(len(data))]
            )
            display_name = "Student"
        else:
            display_name = name_col

        st.session_state["analysed_student_data"] = data
        st.session_state["analysed_subject_cols"] = subject_cols
        st.session_state["analysed_name_col"] = display_name

# ---------- SHOW ANALYSIS ----------
if "analysed_student_data" in st.session_state:
    data = st.session_state["analysed_student_data"]
    subjects = st.session_state["analysed_subject_cols"]
    display_name = st.session_state["analysed_name_col"]

    st.divider()
    st.subheader("3. Performance Overview")

    total_students = len(data)
    passed = int((data["Result"] == "Pass").sum())
    failed = total_students - passed
    avg_percentage = data["Percentage"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Students", total_students)
    c2.metric("Passed", passed)
    c3.metric("Failed", failed)
    c4.metric("Average Percentage", f"{avg_percentage:.2f}%")

    st.subheader("4. Subject-Wise Average Marks")
    averages = data[subjects].mean().rename_axis(
        "Subject"
    ).reset_index(name="Average Marks")

    fig1 = px.bar(
        averages,
        x="Subject",
        y="Average Marks",
        color="Average Marks",
        range_y=[0, 100],
        title="Average Marks by Subject"
    )
    st.plotly_chart(fig1, use_container_width=True)

    left, right = st.columns(2)

    with left:
        st.subheader("Pass vs Fail")
        result_counts = (
            data["Result"].value_counts()
            .rename_axis("Result")
            .reset_index(name="Students")
        )
        fig2 = px.pie(
            result_counts,
            names="Result",
            values="Students",
            hole=0.5
        )
        st.plotly_chart(fig2, use_container_width=True)

    with right:
        st.subheader("Student Percentages")
        fig3 = px.bar(
            data,
            x=display_name,
            y="Percentage",
            color="Result",
            title="Student Performance",
            range_y=[0, 100]
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("5. Student Results")
    ranking = data.sort_values(
        "Percentage", ascending=False
    ).reset_index(drop=True)
    ranking.insert(0, "Rank", range(1, len(ranking) + 1))

    st.dataframe(
        ranking,
        use_container_width=True,
        hide_index=True
    )

    csv_data = ranking.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Analysed Results",
        data=csv_data,
        file_name="analysed_student_results.csv",
        mime="text/csv"
    )
else:
    st.info(
        "Upload a dataset or enter an external CSV URL "
        "to begin your analysis."
    )
