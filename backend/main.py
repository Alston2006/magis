from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import cloudinary
import cloudinary.uploader
import os

# ---------------- APP SETUP ----------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- CLOUDINARY (SIGNED) ----------------
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# ---------------- GOOGLE SHEETS ----------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", SCOPES
)

sheet_client = gspread.authorize(creds)
sheet = sheet_client.open("MAGIS_REGISTRATIONS").sheet1

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
    # ✅ READ FILE AS BYTES (CRITICAL)
    file_bytes = await payment_proof.read()

    # ✅ SIGNED CLOUDINARY UPLOAD (NO PRESET)
    upload_result = cloudinary.uploader.upload(
        file_bytes,
        folder="MAGIS_PAYMENTS",
        public_id=register_no,
        resource_type="image"
    )

    image_url = upload_result["secure_url"]

    # ✅ SAVE TO GOOGLE SHEETS
    sheet.append_row([
        name,
        register_no,
        phone,
        email,
        college,
        class_name,
        tshirt_size,
        image_url,
        datetime.now().strftime("%d-%m-%Y %H:%M")
    ])

    return RedirectResponse(
        url="https://magis-frontend.onrender.com/submit.html",
        status_code=303
    )


