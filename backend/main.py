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
    tshirt_size: str = Form(...),
    payment_proof: UploadFile = File(...)
):
    # Read image
    image_bytes = await payment_proof.read()

    # -------- SEND IMAGE TO TELEGRAM --------
    caption = (
        f"🧾 *MAGIS Registration*\n\n"
        f"👤 Name: {name}\n"
        f"🆔 Reg No: {register_no}\n"
        f"📞 Phone: {phone}\n"
        f"📧 Email: {email}\n"
        f"🏫 College: {college}\n"
        f"🏷 Class: {class_name}\n"
        f"👕 T-Shirt: {tshirt_size}\n"
        f"⏰ Time: {datetime.now().strftime('%d-%m-%Y %H:%M')}"
    )

    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    response = requests.post(
        telegram_url,
        data={
            "chat_id": CHAT_ID,
            "caption": caption,
            "parse_mode": "Markdown"
        },
        files={
            "photo": (payment_proof.filename, image_bytes)
        }
    )

    if response.status_code != 200:
        print("Telegram Error:", response.text)

    # -------- SAVE TO GOOGLE SHEETS (UNCHANGED STRUCTURE) --------
    sheet.append_row([
        name,
        register_no,
        phone,
        email,
        college,
        class_name,
        tshirt_size,
        "Sent to Telegram",
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
