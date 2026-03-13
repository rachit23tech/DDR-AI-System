# AI-powered DDR Generator

This project provides a minimal backend system for generating Detailed Diagnostic Reports (DDR) by extracting information from two PDF documents (Inspection Report and Thermal Report) and leveraging an LLM to structure the summary.

## Tech Stack
- Python (>=3.8)
- FastAPI
- PyMuPDF (fitz)
- OpenAI (GPT) or any LLM via environment key

## Folder Structure
```
ddr-ai-system/
│
├── main.py
├── pdf_parser.py
├── image_extractor.py
├── ai_processor.py
├── report_generator.py
├── requirements.txt
├── README.md
└── uploads/              # stores uploaded PDFs and extracted images
```

## Setup Instructions
1. **Clone or copy** this repository to your local machine.
2. **Create a virtual environment** and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate    # macOS/Linux
   venv\Scripts\activate     # Windows
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set your LLM API key**.
   - Option A (recommended): create a `.env` file in the project root.

     Example `.env`:
     ```env
     GEMINI_API_KEY=your_key_here
     AI_PROVIDER=gemini
     ```

   - Option B (environment variables):

     For OpenAI:
     ```bash
     export OPENAI_API_KEY="your_key_here"         # macOS/Linux
     setx OPENAI_API_KEY "your_key_here"          # Windows (requires new shell)
     ```

     For Gemini:
     ```bash
     export AI_PROVIDER=gemini
     export GEMINI_API_KEY="your_key_here"
     ```

   Note: the server must be started after setting env vars so they are visible to the running process.
5. **Run the server**:
   ```bash
   uvicorn main:app --reload
   ```
6. **Use the endpoint**:
   - POST `/generate-ddr` with form-data fields `inspection_report` and `thermal_report` both as file uploads.
   - Returns JSON containing extracted text, image paths, and the generated DDR report.

## Example cURL
```bash
curl -X POST "http://127.0.0.1:8000/generate-ddr" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "inspection_report=@inspection.pdf;type=application/pdf" \
  -F "thermal_report=@thermal.pdf;type=application/pdf"
```

## Simple Streamlit UI
You can also launch a basic upload form and display results with Streamlit.

```bash
streamlit run ui.py --server.maxUploadSize=200
```

The interface allows you to choose two PDFs and shows the DDR output inline. (Note: Streamlit upload size is controlled via command line/config, not in Python code.)

## Notes
- Image extraction uses `PyMuPDF`; if the PDFs have no images, the `images` list will be empty.
- The LLM prompt enforces structure and rules; if the model returns non-JSON, the raw output is returned under the `raw` key.
- Uploaded files and extracted images are stored in the `uploads/` directory.

Feel free to extend functionality, add authentication, or swap in a different PDF parser or LLM provider.
