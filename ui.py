import streamlit as st
import requests

st.title("DDR Generator")

st.write("Upload an inspection and thermal PDF to generate a DDR report.")

inspection = st.file_uploader("Inspection report", type="pdf")
thermal = st.file_uploader("Thermal report", type="pdf")

if st.button("Generate DDR"):
    if not inspection or not thermal:
        st.error("Both files are required.")
    else:
        files = {
            "inspection_report": (inspection.name, inspection, "application/pdf"),
            "thermal_report": (thermal.name, thermal, "application/pdf"),
        }
        resp = requests.post("http://127.0.0.1:8000/generate-ddr", files=files)
        if resp.status_code == 200:
            data = resp.json()
            st.subheader("Extracted Text")
            st.write(data.get("extracted", {}).get("inspection_text", ""))
            st.write(data.get("extracted", {}).get("thermal_text", ""))
            st.subheader("Images")
            for img in data.get("extracted", {}).get("images", []):
                st.image(img)
            st.subheader("Report")
            st.json(data.get("report", {}))
        else:
            st.error(f"Error: {resp.status_code} - {resp.text}")
