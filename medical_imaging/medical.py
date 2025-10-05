import os
from dotenv import load_dotenv
from PIL import Image as PILImage
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.media import Image as AgnoImage
import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# =========================
# 🔑 Load API Key securely
# =========================
# Explicitly load .env from current folder
load_dotenv(dotenv_path="C:/Users/varsh/OneDrive/code with me/varshu/medical_imaging/.env")

# Get the key from .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("⚠️ Please set your GEMINI_API_KEY in a `.env` file.")
    st.stop()

# Some libraries expect GOOGLE_API_KEY, so map it
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

# =========================
# 🤖 Initialize Medical Agent
# =========================
medical_agent = Agent(
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[DuckDuckGoTools()],
    markdown=True
)

# =========================
# 📌 Medical Analysis Query
# =========================
query = """
You are a highly skilled medical imaging expert with extensive knowledge in radiology and diagnostic imaging. Analyze the medical image and structure your response as follows:

### 1. Image Type & Region
- Identify imaging modality (X-ray/MRI/CT/Ultrasound/etc.).
- Specify anatomical region and positioning.
- Evaluate image quality and technical adequacy.

### 2. Key Findings
- Highlight primary observations systematically.
- Identify potential abnormalities with detailed descriptions.
- Include measurements and densities where relevant.

### 3. Diagnostic Assessment
- Provide primary diagnosis with confidence level.
- List differential diagnoses ranked by likelihood.
- Support each diagnosis with observed evidence.
- Highlight critical/urgent findings.

### 4. Patient-Friendly Explanation
- Simplify findings in clear, non-technical language.
- Avoid medical jargon or provide easy definitions.
- Include relatable visual analogies.

### 5. Research Context
- Use DuckDuckGo search to find recent medical literature.
- Search for standard treatment protocols.
- Provide 2-3 key references supporting the analysis.

Ensure a structured and medically accurate response using clear markdown formatting.
"""

# =========================
# 🔬 Image Analysis Function
# =========================
def analyze_medical_image(image_path):
    image = PILImage.open(image_path)
    width, height = image.size
    aspect_ratio = width / height
    new_width = 500
    new_height = int(new_width / aspect_ratio)
    resized_image = image.resize((new_width, new_height))

    temp_path = "temp_resized_image.png"
    resized_image.save(temp_path)

    agno_image = AgnoImage(filepath=temp_path)

    try:
        response = medical_agent.run(query, images=[agno_image])
        return response.content
    except Exception as e:
        return f"⚠️ Analysis error: {e}"
    finally:
        os.remove(temp_path)

# =========================
# 📄 Export Report as PDF
# =========================
def create_pdf(report_text):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    text = pdf.beginText(40, height - 50)
    text.setFont("Helvetica", 10)

    for line in report_text.split("\n"):
        text.textLine(line)
    pdf.drawText(text)
    pdf.save()
    buffer.seek(0)
    return buffer

# =========================
# 🎨 Streamlit UI Setup
# =========================
st.set_page_config(page_title="Medical Image Analysis", layout="wide")
st.title("🩺 AI-Powered Medical Image Analysis Tool 🔬")
st.markdown(
    """
    Upload a medical image (X-ray, MRI, CT, Ultrasound, etc.), and our AI-powered system will analyze it,  
    providing **detailed findings, diagnosis, and research insights**.
    
    ⚠️ *Disclaimer: This tool is for **educational/research purposes only** and is **not a substitute for professional medical advice**.*
    """
)

# Keep session history
if "history" not in st.session_state:
    st.session_state.history = []

# =========================
# 📤 Upload Image(s)
# =========================
st.sidebar.header("Upload Your Medical Images")
uploaded_files = st.sidebar.file_uploader(
    "Choose medical images", type=["jpg", "jpeg", "png", "bmp", "gif"], accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.image(uploaded_file, caption=f"Uploaded: {uploaded_file.name}", use_container_width=True)

    if st.sidebar.button("Analyze All"):
        for uploaded_file in uploaded_files:
            with st.spinner(f"🔍 Analyzing {uploaded_file.name}..."):
                # Save temporarily
                image_path = f"temp_{uploaded_file.name}"
                with open(image_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Run AI analysis
                report = analyze_medical_image(image_path)

                # Save to history
                st.session_state.history.append({
                    "filename": uploaded_file.name,
                    "report": report
                })

                os.remove(image_path)

# =========================
# 📋 Display Reports + Downloads
# =========================
if st.session_state.history:
    st.subheader("📊 Analysis Results")

    for idx, entry in enumerate(st.session_state.history, 1):
        st.markdown(f"### 🖼️ {entry['filename']}")
        st.markdown(entry["report"], unsafe_allow_html=True)

        # Download as TXT
        st.download_button(
            label=f"⬇️ Download {entry['filename']} Report (TXT)",
            data=entry["report"],
            file_name=f"{entry['filename']}_report.txt",
            mime="text/plain",
        )

        # Download as PDF
        pdf_file = create_pdf(entry["report"])
        st.download_button(
            label=f"⬇️ Download {entry['filename']} Report (PDF)",
            data=pdf_file,
            file_name=f"{entry['filename']}_report.pdf",
            mime="application/pdf",
        )

# =========================
# 🔀 Compare Reports Feature
# =========================
if len(st.session_state.history) >= 2:
    st.subheader("🔀 Compare Reports")

    # Let user pick two reports
    filenames = [entry["filename"] for entry in st.session_state.history]
    col1, col2 = st.columns(2)

    with col1:
        file1 = st.selectbox("Select First Report", filenames, key="report1")
    with col2:
        file2 = st.selectbox("Select Second Report", filenames, key="report2")

    if file1 and file2 and file1 != file2:
        r1 = next(entry for entry in st.session_state.history if entry["filename"] == file1)
        r2 = next(entry for entry in st.session_state.history if entry["filename"] == file2)

        colA, colB = st.columns(2)
        with colA:
            st.markdown(f"### 🖼️ {r1['filename']}")
            st.markdown(r1["report"], unsafe_allow_html=True)
        with colB:
            st.markdown(f"### 🖼️ {r2['filename']}")
            st.markdown(r2["report"], unsafe_allow_html=True)