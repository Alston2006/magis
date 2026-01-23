from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import RedirectResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import shutil
import zipfile

# -------------------------------
# APP SETUP
# -------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# DIRECTORIES
# -------------------------------
UPLOAD_DIR = "uploads"
ZIP_PATH = "all_payment_proofs.zip"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# -------------------------------
# GOOGLE SHEETS SETUP
# -------------------------------
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json",
    SCOPE
)

client = gspread.authorize(creds)

# 🔴 CHANGE THIS TO YOUR SHEET NAME
sheet = client.open("MAGIS_REGISTRATIONS").sheet1

# -------------------------------
# FORM SUBMISSION
# -------------------------------
@app.post("/submit")
async def submit_form(
    name: str = Form(...),
    register_no: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    college: str = Form(...),
    class_name: str = Form(..., alias="class"),
    tshirt_size: str = Form(...),
    payment_proof: UploadFile = File(...)
):
    ext = payment_proof.filename.split(".")[-1]
    filename = f"{register_no}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(payment_proof.file, buffer)

    sheet.append_row([
        name,
        register_no,
        phone,
        email,
        college,
        class_name,
        tshirt_size,
        filename,
        datetime.now().strftime("%d-%m-%Y %H:%M")
    ])

    return RedirectResponse(
        url="https://magis-frontend.onrender.com/submit.html",
        status_code=303
    )

# -------------------------------
# DOWNLOAD SINGLE PAYMENT PROOF
# -------------------------------
@app.get("/download/{regno}")
def download_single(regno: str):
    for file in os.listdir(UPLOAD_DIR):
        if file.startswith(regno):
            return FileResponse(
                path=os.path.join(UPLOAD_DIR, file),
                filename=file
            )
    return JSONResponse(
        status_code=404,
        content={"error": "File not found"}
    )

# -------------------------------
# 🔥 DOWNLOAD ALL PAYMENT PROOFS (ZIP)
# -------------------------------
@app.get("/download-all")
def download_all():
    files = os.listdir(UPLOAD_DIR)

    if not files:
        return JSONResponse(
            status_code=404,
            content={"error": "No payment proofs found"}
        )

    # Create ZIP
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file)
            zipf.write(file_path, arcname=file)

    return FileResponse(
        path=ZIP_PATH,
        filename="all_payment_proofs.zip",
        media_type="application/zip"
    )

# -------------------------------
# HEALTH CHECK
# -------------------------------
@app.get("/")
def health():
    return {"status": "Backend running successfully"}

