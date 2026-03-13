import streamlit as st
import requests

st.title("DDR Generator")

st.write("Upload an inspection and thermal PDF to generate a DDR report.")

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

    with st.spinner("Processing PDFs and generating DDR..."):

        try:
            resp = requests.post(
                "https://ddr-ai-system.onrender.com/generate-ddr",
                files=files,
                timeout=120
            )
        except Exception as e:
            st.error(f"API connection failed: {e}")
            st.stop()

    if resp.status_code != 200:
        st.error(f"Error: {resp.status_code} - {resp.text}")
        st.stop()

    data = resp.json()

    st.subheader("Extracted Text")

    st.write(data.get("extracted", {}).get("inspection_text", ""))
    st.write(data.get("extracted", {}).get("thermal_text", ""))

    st.subheader("Images")

    images = data.get("extracted", {}).get("images", [])

    if not images:
        st.info("No images extracted.")
    else:
        st.write(f"{len(images)} images extracted (stored on backend).")

    st.subheader("Generated DDR Report")

    report = data.get("report", {})
    st.json(report)

    # Download button
    import json
    st.download_button(
        "Download DDR Report",
        json.dumps(report, indent=2),
        file_name="ddr_report.json"
    )