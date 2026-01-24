from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import cloudinary
import cloudinary.uploader
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

# ---------------- GOOGLE SHEETS AUTH ----------------
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", SCOPES
)

sheet_client = gspread.authorize(creds)
sheet = sheet_client.open("MAGIS_REGISTRATIONS").sheet1

# ---------------- CLOUDINARY CONFIG ----------------
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

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

    # 1️⃣ Save locally (temporary)
    with open(local_path, "wb") as buffer:
        shutil.copyfileobj(payment_proof.file, buffer)

    cloudinary_url = "UPLOAD_FAILED"

    # 2️⃣ Upload to Cloudinary
    try:
        result = cloudinary.uploader.upload(
            local_path,
            folder="MAGIS_PAYMENTS",
            public_id=register_no,
            overwrite=True,
            resource_type="image"
        )
        cloudinary_url = result.get("secure_url")

    except Exception as e:
        print("⚠️ Cloudinary upload failed:", e)

    # 3️⃣ Save to Google Sheets
    sheet.append_row([
        name,
        register_no,
        phone,
        email,
        college,
        class_name,
        tshirt_size,
        cloudinary_url,
        datetime.now().strftime("%d-%m-%Y %H:%M")
    ])

    # 4️⃣ Redirect user
    return RedirectResponse(
        url="https://magis-frontend.onrender.com/submit.html",
        status_code=303
    )

# ---------------- HEALTH ----------------
@app.get("/")
def health():
    return {"status": "Backend running successfully"}
