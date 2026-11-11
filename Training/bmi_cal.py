
import streamlit as st

# --------------------------------
# PAGE CONFIGURATION
# --------------------------------
st.set_page_config(
    page_title="BMI Calculator",
    page_icon="⚖️",
    layout="centered"
)

# --------------------------------
# CUSTOM CSS
# --------------------------------
st.markdown("""
<style>
    .main {
        background-color: #f5f7fb;
    }

    .title {
        text-align: center;
        color: #2563eb;
        font-size: 38px;
        font-weight: bold;
    }

    .subtitle {
        text-align: center;
        color: gray;
        font-size: 16px;
    }

    .result {
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        background-color: #e8f0fe;
    }

    .bmi-value {
        font-size: 42px;
        font-weight: bold;
        color: #2563eb;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------
# HEADER
# --------------------------------
st.markdown(
    '<div class="title">⚖️ BMI Calculator</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Calculate your Body Mass Index</div>',
    unsafe_allow_html=True
)

st.write("")

# --------------------------------
# USER INPUT
# --------------------------------
st.subheader("👤 Enter Your Details")

name = st.text_input("Your Name")

col1, col2 = st.columns(2)

with col1:
    age = st.number_input(
        "Age (Years)",
        min_value=2,
        max_value=120,
        value=30
    )

with col2:
    gender = st.selectbox(
        "Gender",
        ["Male", "Female", "Other"]
    )

weight = st.number_input(
    "Weight (KG)",
    min_value=1.0,
    max_value=300.0,
    value=60.0,
    step=0.5
)

height = st.number_input(
    "Height (CM)",
    min_value=50.0,
    max_value=250.0,
    value=150.0,
    step=1.0
)

# --------------------------------
# BMI CALCULATION FUNCTION
# --------------------------------
def calculate_bmi(weight, height):

    height_m = height / 100

    bmi = weight / (height_m ** 2)

    return bmi


# --------------------------------
# BMI CATEGORY FUNCTION
# --------------------------------
def get_bmi_category(bmi):

    if bmi < 18.5:
        return "Underweight", "Consider reviewing your nutrition.", "warning"

    elif bmi < 25:
        return "Normal Weight", "Your BMI is within the normal adult range.", "success"

    elif bmi < 30:
        return "Overweight", "Consider balanced nutrition and regular activity.", "warning"

    else:
        return "Obesity", "Consider discussing your health with a professional.", "error"


# --------------------------------
# CALCULATE BUTTON
# --------------------------------
if st.button("Calculate My BMI", type="primary", use_container_width=True):

    if not name.strip():
        st.error("Please enter your name.")

    else:

        bmi = calculate_bmi(weight, height)

        category, advice, status = get_bmi_category(bmi)

        st.divider()

        st.subheader("📊 Your BMI Result")

        st.markdown(
            f"""
            <div class="result">
                <p>Your BMI</p>
                <div class="bmi-value">{bmi:.2f}</div>
                <h3>{category}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        st.write(f"**Name:** {name}")
        st.write(f"**Age:** {age}")
        st.write(f"**Gender:** {gender}")
        st.write(f"**Weight:** {weight} KG")
        st.write(f"**Height:** {height} CM")

        if status == "success":
            st.success(advice)

        elif status == "warning":
            st.warning(advice)

        else:
            st.error(advice)

        # BMI reference
        st.subheader("📋 BMI Reference")

        st.table({
            "BMI Range": [
                "Below 18.5",
                "18.5 - 24.9",
                "25 - 29.9",
                "30 and above"
            ],
            "Category": [
                "Underweight",
                "Normal Weight",
                "Overweight",
                "Obesity"
            ]
        })

        st.caption(
            "BMI is a screening measure, not a diagnosis. "
            "Adult BMI categories should not be applied to children."
        )

# --------------------------------
# FOOTER
# --------------------------------
st.divider()

st.markdown(
    "<center>Built with Python and Streamlit ❤️</center>",
    unsafe_allow_html=True
)
