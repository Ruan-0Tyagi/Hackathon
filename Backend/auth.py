from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import secrets
import smtplib
import os
import time
from email.mime.text import MIMEText
from dotenv import load_dotenv
from jose import jwt
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

router = APIRouter()

# Temporary OTP storage (for hackathon demo)
otp_store = {}

OTP_EXPIRY_SECONDS = 300  # 5 minutes

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
JWT_SECRET = os.getenv("JWT_SECRET")


# ----------------------------
# Request Models
# ----------------------------

class EmailRequest(BaseModel):
    email: EmailStr


class OTPVerify(BaseModel):
    email: EmailStr
    otp: str


# ----------------------------
# 1️⃣ Send OTP
# ----------------------------

@router.post("/send-otp")
def send_otp(data: EmailRequest):
    email = data.email

    # Generate secure 6-digit OTP
    otp = str(secrets.randbelow(900000) + 100000)

    # Store OTP with expiry
    otp_store[email] = {
        "otp": otp,
        "expiry": time.time() + OTP_EXPIRY_SECONDS
    }

    # Email content
    message = MIMEText(f"""
Hello,

Your Mediscan AI login OTP is: {otp}

This OTP will expire in 5 minutes.

Thank you,
Mediscan AI Team
""")

    message["Subject"] = "Mediscan AI Login OTP"
    message["From"] = EMAIL_USER
    message["To"] = email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, email, message.as_string())
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to send OTP")

    return {"message": "OTP sent successfully"}


# ----------------------------
# 2️⃣ Verify OTP + Generate JWT
# ----------------------------

@router.post("/verify-otp")
def verify_otp(data: OTPVerify):
    email = data.email
    record = otp_store.get(email)

    if not record:
        raise HTTPException(status_code=400, detail="No OTP found")

    # Check expiry
    if time.time() > record["expiry"]:
        del otp_store[email]
        raise HTTPException(status_code=400, detail="OTP expired")

    # Check OTP match
    if record["otp"] != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # OTP correct → remove it
    del otp_store[email]

    # Generate JWT token (valid 2 hours)
    token_data = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }

    token = jwt.encode(token_data, JWT_SECRET, algorithm="HS256")

    return {
        "message": "Login successful",
        "access_token": token
    }