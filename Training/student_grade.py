
import streamlit as st

# --------------------------------
# PAGE CONFIGURATION
# --------------------------------

st.set_page_config(
    page_title="Student Grade Manager",
    page_icon="🎓",
    layout="centered"
)

# --------------------------------
# INITIALIZE SESSION STATE
# --------------------------------

if "students" not in st.session_state:
    st.session_state.students = []


# --------------------------------
# GRADE CALCULATION FUNCTION
# --------------------------------

def get_grade(mark):

    if mark >= 90:
        return "A"

    elif mark >= 80:
        return "B"

    elif mark >= 70:
        return "C"

    elif mark >= 60:
        return "D"

    else:
        return "E"


# --------------------------------
# PAGE TITLE
# --------------------------------

st.title("🎓 Student Grade Manager")

st.write("Add students and manage their academic performance.")

st.divider()


# --------------------------------
# ADD STUDENT FORM
# --------------------------------

st.subheader("➕ Add New Student")

with st.form("add_student_form"):

    name = st.text_input("Student Name")

    mark = st.number_input(
        "Student Mark",
        min_value=0,
        max_value=100,
        value=0,
        step=1
    )

    submitted = st.form_submit_button(
        "Add Student",
        use_container_width=True
    )

    if submitted:

        if not name.strip():

            st.error("Please enter student name.")

        elif not 0 <= mark <= 100:

            st.error("Marks must be between 0 and 100.")

        else:

            student = {
                "Name": name.strip(),
                "Mark": mark,
                "Grade": get_grade(mark)
            }

            st.session_state.students.append(student)

            st.success(f"{name.strip()} added successfully!")

# --------------------------------
# DISPLAY STUDENT RECORDS
# --------------------------------

st.divider()

st.subheader("📋 Student Records")

students = st.session_state.students

if students:

    # Display all students
    st.dataframe(
        students,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------
    # CLASS PERFORMANCE CALCULATIONS
    # --------------------------------

    marks = [student["Mark"] for student in students]

    average = sum(marks) / len(marks)

    highest = max(marks)

    lowest = min(marks)

    # --------------------------------
    # DISPLAY CLASS METRICS
    # --------------------------------

    st.divider()

    st.subheader("📊 Class Performance")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Class Average",
        f"{average:.2f}"
    )

    col2.metric(
        "Highest Mark",
        highest
    )

    col3.metric(
        "Lowest Mark",
        lowest
    )

    st.info(f"Total Students: {len(students)}")

else:

    st.info("No students added yet. Please add your first student.")

# --------------------------------
# FOOTER
# --------------------------------

st.divider()

st.caption("Student Grade Manager | Built using Python & Streamlit")
