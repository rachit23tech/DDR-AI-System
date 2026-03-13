import streamlit as st
import requests

API_URL = "https://ddr-ai-system.onrender.com/generate-ddr"

st.title("DDR Generator")

inspection = st.file_uploader("Inspection report", type="pdf")
thermal = st.file_uploader("Thermal report", type="pdf")

if st.button("Generate DDR"):

    if not inspection or not thermal:
        st.error("Both files are required.")
        st.stop()

    files = {
        "inspection_report": (inspection.name, inspection, "application/pdf"),
        "thermal_report": (thermal.name, thermal, "application/pdf"),
    }

    try:
        with st.spinner("Generating DDR report... This may take 1–2 minutes"):
            resp = requests.post(
                API_URL,
                files=files,
                timeout=300   # increased timeout
            )
    except requests.exceptions.Timeout:
        st.error("The server took too long to respond. Please try again.")
        st.stop()
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        st.stop()

    if resp.status_code != 200:
        st.error(f"Server error: {resp.text}")
        st.stop()

    data = resp.json()

    extracted = data.get("extracted", {})
    report = data.get("report", {})

    st.subheader("Extracted Text")

    st.write(extracted.get("inspection_text", "No inspection text found"))
    st.write(extracted.get("thermal_text", "No thermal text found"))

    st.subheader("Images")

    images = extracted.get("images", [])

    if images:
        cols = st.columns(3)  # display images in grid
        for i, img in enumerate(images):
            cols[i % 3].image(img, use_container_width=True)
    else:
        st.info("No images extracted.")

    st.subheader("DDR Report")

    st.json(report)