import os
import shutil
from urllib.parse import quote

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from pdf_parser import extract_text_and_images
from report_generator import create_report

app = FastAPI()

# Upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Serve uploaded images
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_URL = "https://ddr-ai-system.onrender.com"


@app.post("/generate-ddr")
async def generate_ddr(
    inspection_report: UploadFile = File(...),
    thermal_report: UploadFile = File(...)
):

    try:
        # Save inspection report
        inspection_path = os.path.join(UPLOAD_DIR, inspection_report.filename)
        with open(inspection_path, "wb") as f:
            shutil.copyfileobj(inspection_report.file, f)

        # Save thermal report
        thermal_path = os.path.join(UPLOAD_DIR, thermal_report.filename)
        with open(thermal_path, "wb") as f:
            shutil.copyfileobj(thermal_report.file, f)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploads: {e}")

    # Extract text and images
    ins_data = extract_text_and_images(inspection_path, UPLOAD_DIR)
    ther_data = extract_text_and_images(thermal_path, UPLOAD_DIR)

    # Combine images
    images = ins_data.get("images", []) + ther_data.get("images", [])

    # Remove duplicate images while keeping order
    seen = set()
    unique_images = []

    for img in images:
        name = os.path.basename(img)
        if name not in seen:
            seen.add(name)
            unique_images.append(img)

    extracted = {
        "inspection_text": ins_data.get("text", ""),
        "thermal_text": ther_data.get("text", ""),
        "images": unique_images,
    }

    # Convert filesystem paths → public URLs
    extracted["images"] = [
        f"{BASE_URL}/uploads/{quote(os.path.basename(img))}"
        for img in extracted["images"]
    ]

    # Generate AI report
    try:
        report = create_report(extracted)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing failed: {e}")

    return JSONResponse(content={"extracted": extracted, "report": report})


@app.get("/")
def root():
    return {"message": "DDR generator API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)