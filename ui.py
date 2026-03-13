import streamlit as st
import requests

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

    with st.spinner("Generating DDR report..."):
        resp = requests.post(
            "https://ddr-ai-system.onrender.com/generate-ddr",
            files=files,
            timeout=120
        )

    if resp.status_code != 200:
        st.error(resp.text)
        st.stop()

    data = resp.json()

    st.subheader("Extracted Text")

    st.write(data["extracted"]["inspection_text"])
    st.write(data["extracted"]["thermal_text"])

    st.subheader("Images")

    for img in data["extracted"]["images"]:
        st.image(img, use_container_width=True)

    st.subheader("DDR Report")
    st.json(data["report"])