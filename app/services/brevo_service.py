import os
import requests

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

def send_otp_email(to_email: str, otp_code: str):
    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("BREVO_SENDER_EMAIL")
    sender_name = os.getenv("BREVO_SENDER_NAME", "SockerKE")

    # If no API key set, allow a development fallback so local testing can continue.
    # Set `BREVO_DISABLE_SEND=true` or run with FLASK_ENV=development to enable logging OTPs instead of calling Brevo.
    disable_send = os.getenv("BREVO_DISABLE_SEND", "false").lower() == "true"
    flask_env = os.getenv("FLASK_ENV", "").lower()
    if not api_key:
        if disable_send or flask_env == 'development':
            # Log and skip sending in dev mode
            print(f"[brevo_service] DEV MODE: would send OTP {otp_code} to {to_email}")
            return True
        raise Exception("Brevo API key not configured")

    # Log masked API key and intent to send (helps debug 401/403/ DNS issues)
    masked_key = api_key[:4] + '...' + api_key[-4:] if len(api_key) > 8 else '***'
    print(f"[brevo_service] Sending OTP to {to_email} using Brevo key {masked_key}")
    
    payload = {
        "sender":{"name": sender_name, "email": sender_email},
        "to":[{"email": to_email}],
        "subject": "SoccerKE OTP Verification Code",
        "htmlContent": f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
         <h2>Dear Coach Verify Your Email</h2>
         <p>Your OTP code is: </p>
          <h1 style="letter-spacing: 5px;">{otp_code}</h1>
            <p>This code expires in 10 minutes.</p>
            <p>If you didn’t request this, ignore this email.</p>
        </div>
         """
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": api_key
    }

    try:
        res = requests.post(BREVO_API_URL, json=payload, headers=headers, timeout=15)
    except Exception as e:
        # Surface a clearer message for network/DNS/proxy errors
        raise Exception(f"Network error contacting Brevo: {e}")

    # Log Brevo response for debugging (do not log full API key)
    try:
        resp_text = res.text
    except Exception:
        resp_text = '<unreadable response>'

    print(f"[brevo_service] Brevo response: {res.status_code} - {resp_text}")

    if res.status_code not in [200, 201, 202]:
        # Include Brevo body in the raised exception for client visibility
        raise Exception(f"Failed to send OTP email: {res.status_code} - {resp_text}")

    return True