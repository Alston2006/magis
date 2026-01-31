from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import requests

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---------------- APP SETUP ----------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- TELEGRAM CONFIG ----------------
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

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
    gender: str = Form(...),
    blood_group: str = Form(...),
    tshirt_size: str = Form(...),
    payment_proof: UploadFile = File(...)
):
    telegram_status = "Not sent"

    # 1️⃣ READ FILE
    image_bytes = await payment_proof.read()

    # 2️⃣ TRY TELEGRAM (NON-BLOCKING)
    try:
        caption = (
            f"🧾 *MAGIS Registration*\n\n"
            f"👤 Name: {name}\n"
            f"🆔 Reg No: {register_no}\n"
            f"📞 Phone: {phone}\n"
            f"📧 Email: {email}\n"
            f"🏫 College: {college}\n"
            f"🏷 Class: {class_name}\n"
            f"🚻 Gender: {gender}\n"
            f"🩸 Blood Group: {blood_group}\n"
            f"👕 T-Shirt: {tshirt_size}\n"
            f"⏰ Time: {datetime.now().strftime('%d-%m-%Y %H:%M')}"
        )

        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

        r = requests.post(
            telegram_url,
            data={
                "chat_id": CHAT_ID,
                "caption": caption,
                "parse_mode": "Markdown"
            },
            files={
                "photo": (payment_proof.filename, image_bytes)
            },
            timeout=10
        )

        if r.status_code == 200:
            telegram_status = "Sent to Telegram"
        else:
            telegram_status = "Telegram failed"

    except Exception as e:
        print("Telegram error:", e)
        telegram_status = "Telegram exception"

    # 3️⃣ ALWAYS SAVE TO GOOGLE SHEETS
    try:
        sheet.append_row([
            name,
            register_no,
            phone,
            email,
            college,
            class_name,
            gender,
            blood_group,
            tshirt_size,
            telegram_status,
            datetime.now().strftime("%d-%m-%Y %H:%M")
        ])
    except Exception as e:
        print("Sheet error:", e)
        # Even if sheet fails, user still gets redirect

    # 4️⃣ ALWAYS REDIRECT USER
    return RedirectResponse(
        url="https://magis-frontend.onrender.com/submit.html",
        status_code=303
    )

