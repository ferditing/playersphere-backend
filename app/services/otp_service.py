import random
from app.extensions.db import db
from app.models.email_otp import EmailOTP
from app.services.brevo_service import send_otp_email


def generate_otp():
    return str(random.randint(100000, 999999))


def send_signup_otp(email: str):
    email = email.lower().strip()

    # Optional: delete old OTPs for this email
    EmailOTP.query.filter_by(email=email, purpose="signup").delete()

    otp_code = generate_otp()
    otp = EmailOTP.new(email=email, otp_code=otp_code, minutes_valid=10)

    db.session.add(otp)
    db.session.commit()

    send_otp_email(email, otp_code)

    return True


def verify_signup_otp(email: str, otp_code: str):
    email = email.lower().strip()
    otp_code = otp_code.strip()

    otp = (
        EmailOTP.query
        .filter_by(email=email, purpose="signup", is_used=False)
        .order_by(EmailOTP.created_at.desc())
        .first()
    )

    if not otp:
        raise Exception("OTP not found")

    if otp.is_expired():
        raise Exception("OTP expired")

    if otp.otp_code != otp_code:
        raise Exception("Invalid OTP")

    otp.is_used = True
    db.session.commit()

    return True


def is_email_verified_for_signup(email: str):
    email = email.lower().strip()

    otp = (
        EmailOTP.query
        .filter_by(email=email, purpose="signup", is_used=True)
        .order_by(EmailOTP.created_at.desc())
        .first()
    )

    if not otp:
        return False

    # still enforce expiry
    if otp.is_expired():
        return False

    return True
