import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List

from pdf_parser import extract_text_and_images
from report_generator import create_report

app = FastAPI()

# Allow Streamlit (and other local frontends) to call this API from a different port.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/generate-ddr")
async def generate_ddr(inspection_report: UploadFile = File(...), thermal_report: UploadFile = File(...)):
    # save uploaded files
    try:
        inspection_path = os.path.join(UPLOAD_DIR, inspection_report.filename)
        with open(inspection_path, "wb") as f:
            shutil.copyfileobj(inspection_report.file, f)

        thermal_path = os.path.join(UPLOAD_DIR, thermal_report.filename)
        with open(thermal_path, "wb") as f:
            shutil.copyfileobj(thermal_report.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploads: {e}")

    # parse PDFs
    ins_data = extract_text_and_images(inspection_path, UPLOAD_DIR)
    ther_data = extract_text_and_images(thermal_path, UPLOAD_DIR)

    extracted = {
        "inspection_text": ins_data.get("text", ""),
        "thermal_text": ther_data.get("text", ""),
        "images": ins_data.get("images", []) + ther_data.get("images", []),
    }

    # process AI
    try:
        report = create_report(extracted)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing failed: {e}")

    return JSONResponse(content={"extracted": extracted, "report": report})


@app.get("/")
def root():
    return {"message": "DDR generator API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True, limit_max_requests=100, http="auto", max_request_size=100*1024*1024)  # 100MB limit
