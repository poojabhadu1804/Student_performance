
import pandas as pd
import random

random.seed(42)

students = [
    "Aarav", "Diya", "Rohan", "Ananya", "Kabir",
    "Meera", "Arjun", "Isha", "Vivaan", "Sana",
    "Aditya", "Priya", "Rahul", "Neha", "Karan",
    "Sneha", "Riya", "Aman", "Kavya", "Ishaan",
    "Simran", "Aryan", "Aditi", "Varun", "Nisha",
    "Dev", "Pooja", "Manav", "Tanya", "Yash",
    "Shreya", "Krishna", "Manya", "Ritvik", "Anika",
    "Harsh", "Sakshi", "Nikhil", "Palak", "Dhruv",
    "Muskan", "Ayush", "Tanvi", "Rajat", "Kriti",
    "Siddharth", "Avni", "Mohit", "Ira", "Parth"
]

subjects = ["Python", "Maths", "English", "Science", "Computer"]

data = {"Student": students}

for subject in subjects:
    data[subject] = [
        random.randint(25, 100) for _ in students
    ]

df = pd.DataFrame(data)

df["Total"] = df[subjects].sum(axis=1)
df["Percentage"] = df["Total"] / 5

df["Result"] = df[subjects].ge(35).all(axis=1)
df["Result"] = df["Result"].map({
    True: "Pass",
    False: "Fail"
})

df.to_csv("student_results.csv", index=False)

print(df.to_string(index=False))
print("\nTotal students:", len(df))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Student Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Student Performance Dashboard")
st.write("Analyse the performance of 50 students.")

# Load dataset
df = pd.read_csv("student_results.csv")

subjects = [
    "Python", "Maths", "English", "Science", "Computer"
]

# Sidebar filter
st.sidebar.header("Filters")

result_filter = st.sidebar.selectbox(
    "Select Result",
    ["All", "Pass", "Fail"]
)

search = st.sidebar.text_input("Search Student")

filtered_df = df.copy()

if result_filter != "All":
    filtered_df = filtered_df[
        filtered_df["Result"] == result_filter
    ]

if search:
    filtered_df = filtered_df[
        filtered_df["Student"].str.contains(
            search, case=False, na=False
        )
    ]

# Summary metrics
c1, c2, c3 = st.columns(3)

c1.metric("Total Students", len(filtered_df))

if len(filtered_df) > 0:
    c2.metric(
        "Average Percentage",
        f"{filtered_df['Percentage'].mean():.2f}%"
    )

    topper = filtered_df.loc[
        filtered_df["Percentage"].idxmax()
    ]

    c3.metric(
        "Top Performer",
        topper["Student"]
    )
else:
    c2.metric("Average Percentage", "N/A")
    c3.metric("Top Performer", "N/A")

# Subject averages
st.subheader("Subject-wise Average Marks")

if len(filtered_df) > 0:
    averages = filtered_df[subjects].mean()

    fig, ax = plt.subplots()
    averages.plot(kind="bar", ax=ax)
    ax.set_ylabel("Average Marks")
    ax.set_xlabel("Subject")
    ax.set_ylim(0, 100)
    plt.xticks(rotation=0)
    st.pyplot(fig)
    plt.close(fig)

    # Pass / Fail chart
    st.subheader("Pass/Fail Distribution")

    counts = filtered_df["Result"].value_counts()

    fig2, ax2 = plt.subplots()
    counts.plot(
        kind="pie",
        autopct="%1.1f%%",
        ax=ax2
    )
    ax2.set_ylabel("")
    st.pyplot(fig2)
    plt.close(fig2)

else:
    st.warning("No students match your filters.")

# Student table
st.subheader("Student Records")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# Download button
st.download_button(
    "Download Student Results CSV",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="student_results.csv",
    mime="text/csv"
)
