
import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

try:
    WEBHOOK_URL = (
        os.getenv("N8N_WEBHOOK_URL")
        or st.secrets["N8N_WEBHOOK_URL"]
    )
except (FileNotFoundError, KeyError):
    WEBHOOK_URL = None

# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="AI Feedback Analyzer",
    page_icon="🤖",
    layout="wide"
)

# ---------------- CUSTOM STYLING ----------------

st.markdown("""
<style>
    .main {
        background-color: #f5f7fb;
    }

    .main-title {
        font-size: 36px;
        font-weight: 700;
        color: #172554;
        text-align: center;
    }

    .subtitle {
        text-align: center;
        color: #64748b;
        font-size: 16px;
        margin-bottom: 30px;
    }

    .result-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
    }

    .result-label {
        color: #64748b;
        font-size: 13px;
        font-weight: 600;
    }

    .result-value {
        color: #172554;
        font-size: 20px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)


# ---------------- HEADER ----------------

st.markdown(
    '<div class="main-title">AI Feedback Analyzer</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Analyze customer feedback using Gemini AI and n8n automation'
    '</div>',
    unsafe_allow_html=True
)


# ---------------- INPUT SECTION ----------------

st.subheader("Customer Feedback")

feedback = st.text_area(
    "Enter customer feedback below:",
    height=160,
    placeholder="Example: My order is three days late. The tracking page has not updated and customer support is not responding."
)

analyze_button = st.button(
    "Analyze Feedback",
    type="primary",
    use_container_width=True
)


# ---------------- ANALYSIS FUNCTION ----------------

def analyze_feedback(feedback_text):

    if not WEBHOOK_URL:
        raise ValueError(
            "N8N_WEBHOOK_URL is missing from your .env file."
        )

    response = requests.post(
        WEBHOOK_URL,
        json={
            "feedback": feedback_text
        },
        timeout=120
    )

    response.raise_for_status()

    result = response.json()

    if not isinstance(result, dict):
        raise ValueError("The backend returned an unexpected response format.")

    required_fields = [
        "category",
        "sentiment",
        "urgency",
        "summary",
        "recommendation"
    ]

    missing_fields = [
        field for field in required_fields
        if not isinstance(result.get(field), str)
        or not result[field].strip()
    ]

    if missing_fields:
        raise ValueError(
            "Backend response is missing valid fields: "
            + ", ".join(missing_fields)
        )

    return result


# ---------------- DISPLAY RESULTS ----------------

if analyze_button:

    if not feedback.strip():

        st.warning("Please enter some customer feedback first.")

    else:

        try:

            with st.spinner("Gemini AI is analyzing the feedback..."):

                result = analyze_feedback(feedback.strip())

            st.success("Feedback analysis completed successfully!")

            st.divider()

            st.subheader("Analysis Results")

            # First row: Classification
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(
                    f'<div class="result-card">'
                    f'<div class="result-label">CATEGORY</div>'
                    f'<div class="result-value">{result["category"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            with col2:
                st.markdown(
                    f'<div class="result-card">'
                    f'<div class="result-label">SENTIMENT</div>'
                    f'<div class="result-value">{result["sentiment"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            with col3:
                st.markdown(
                    f'<div class="result-card">'
                    f'<div class="result-label">URGENCY</div>'
                    f'<div class="result-value">{result["urgency"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            # Summary
            st.markdown("### Feedback Summary")
            st.info(result["summary"])

            # Recommendation
            st.markdown("### Recommended Action")
            st.success(result["recommendation"])

        except requests.exceptions.Timeout:

            st.error(
                "The AI workflow took too long to respond. "
                "Please try again."
            )

        except requests.exceptions.RequestException as error:

            st.error(
                "Could not communicate with the n8n backend."
            )
            st.caption(str(error))

        except ValueError as error:

            st.error(str(error))

        except Exception as error:

            st.error("An unexpected error occurred.")
            st.caption(str(error))
