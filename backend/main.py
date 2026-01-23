from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from datetime import datetime
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# GOOGLE AUTH (Sheets + Drive)
# -------------------------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json",
    SCOPES
)

# Sheets
sheet_client = gspread.authorize(creds)
sheet = sheet_client.open("MAGIS_REGISTRATIONS").sheet1

# Drive
drive_service = build("drive", "v3", credentials=creds)

# 🔴 REPLACE WITH YOUR FOLDER ID
DRIVE_FOLDER_ID = "1ovoxAvjdiS3Zq68k3KzMSqIMrygBiar0"

# -------------------------------
# FORM SUBMIT
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
    # Read uploaded file
    file_bytes = await payment_proof.read()

    # Rename file as REGNO.ext
    ext = payment_proof.filename.split(".")[-1]
    filename = f"{register_no}.{ext}"

    # Upload to Google Drive
    media = MediaIoBaseUpload(
        io.BytesIO(file_bytes),
        mimetype=payment_proof.content_type,
        resumable=False
    )

    file_metadata = {
        "name": filename,
        "parents": [DRIVE_FOLDER_ID]
    }

    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, webViewLink"
    ).execute()

    drive_link = uploaded_file.get("webViewLink")

    # Save data to Google Sheets
    sheet.append_row([
        name,
        register_no,
        phone,
        email,
        college,
        class_name,
        tshirt_size,
        drive_link,
        datetime.now().strftime("%d-%m-%Y %H:%M")
    ])

    return RedirectResponse(
        url="https://magis-frontend.onrender.com/submit.html",
        status_code=303
    )

# -------------------------------
# HEALTH CHECK
# -------------------------------
@app.get("/")
def health():
    return {"status": "Backend running successfully"}



