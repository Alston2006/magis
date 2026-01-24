from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import RedirectResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime
import os
import shutil

# ---------------- APP SETUP ----------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------- GOOGLE AUTH ----------------
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", SCOPES
)

# Sheets
sheet_client = gspread.authorize(creds)
sheet = sheet_client.open("MAGIS_REGISTRATIONS").sheet1

# Drive
drive_service = build("drive", "v3", credentials=creds)

# 🔴 CHANGE THIS
DRIVE_FOLDER_ID = "1gDougVAu7Hb3acB9Ym5WaI_gCI5htWjn"

# ---------------- FORM SUBMIT ----------------
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
    local_path = os.path.join(UPLOAD_DIR, filename)

    # Save locally (temporary)
    with open(local_path, "wb") as buffer:
        shutil.copyfileobj(payment_proof.file, buffer)

        # Upload to Google Drive
    media = MediaFileUpload(
        local_path,
        mimetype=payment_proof.content_type,
        resumable=False
    )

    drive_file = drive_service.files().create(
        body={
            "name": filename,
            "parents": [DRIVE_FOLDER_ID]
        },
        media_body=media,
        fields="id",
        supportsAllDrives=False
    ).execute()



    file_id = drive_file.get("id")

    # Make file public
    drive_service.permissions().create(
        fileId=file_id,
        body={"role": "reader", "type": "anyone"}
    ).execute()

    drive_link = f"https://drive.google.com/file/d/{file_id}/view"

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

# ---------------- HEALTH ----------------
@app.get("/")
def health():
    return {"status": "Backend running successfully"}


