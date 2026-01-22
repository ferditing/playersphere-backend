import requests
import os
import logging
from dotenv import load_dotenv, find_dotenv

# Load .env if present (safe to call repeatedly)
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)

logger = logging.getLogger('playersphere.whatsapp')

def _get_config():
    """Read WhatsApp config from environment at call time."""
    token = os.getenv("WHATSAPP_TOKEN")
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    base_url = f"https://graph.facebook.com/v18.0/{phone_id}/messages" if phone_id else None
    return token, phone_id, base_url

def send_whatsapp_message(to_number: str, message: str):
    token, phone_id, base_url = _get_config()

    # Visible debug print so it's shown in the Flask console even if logging is not DEBUG
    try:
        print(f"[WHATSAPP DEBUG] dotenv_path={dotenv_path}, WHATSAPP_TOKEN_set={bool(token)}, WHATSAPP_PHONE_NUMBER_ID={phone_id}")
    except Exception:
        pass

    if not token or not phone_id:
        raise ValueError("Missing WhatsApp credentials. Check your .env file!")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Clean phone number (remove +) as required by Meta API
    clean_number = to_number.replace("+", "").strip()

    payload = {
        "messaging_product": "whatsapp",
        "to": clean_number,
        "type": "text",
        "text": {"body": message},
    }

    response = requests.post(base_url, json=payload, headers=headers)

    # If the API returns an error, log the response body to help debugging
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        try:
            print(f"[WHATSAPP ERROR] status={response.status_code}, body={response.text}")
        except Exception:
            pass
        raise

    return response.json()


def send_whatsapp_template_message(to_number: str, template_name: str, parameters: list[str], language: str = "en_US"):
    """Send a WhatsApp template message with body parameters.

    - `parameters` is a list of strings that will be substituted into the template body
      placeholders in order ({{1}}, {{2}}, ...).
    """
    token, phone_id, base_url = _get_config()

    # Visible debug print
    try:
        print(f"[WHATSAPP DEBUG] sending template. token_set={bool(token)}, phone_id={phone_id}, dotenv={dotenv_path}")
    except Exception:
        pass

    if not token or not phone_id:
        raise ValueError("Missing WhatsApp credentials. Check your .env file!")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    clean_number = to_number.replace("+", "").strip()

    # Build body parameters for the template
    body_params = [{"type": "text", "text": p} for p in parameters]

    payload = {
        "messaging_product": "whatsapp",
        "to": clean_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language},
            "components": [
                {
                    "type": "body",
                    "parameters": body_params
                }
            ]
        }
    }

    response = requests.post(base_url, json=payload, headers=headers)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        try:
            print(f"[WHATSAPP ERROR] status={response.status_code}, body={response.text}")
        except Exception:
            pass
        raise

    return response.json()


# import requests
# import os
# from dotenv import load_dotenv

# load_dotenv()

# WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
# PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
# BASE_URL = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

# def send_whatsapp_template_message(to_number: str, template_name: str):
#     """
#     Use this to START a conversation (replaces plain text).
#     """
#     headers = {
#         "Authorization": f"Bearer {WHATSAPP_TOKEN}",
#         "Content-Type": "application/json",
#     }

#     # Format the number: Remove '+' if present
#     clean_number = to_number.replace("+", "")

#     payload = {
#         "messaging_product": "whatsapp",
#         "to": clean_number,
#         "type": "template",
#         "template": {
#             "name": template_name,
#             "language": { "code": "en_US" }
#         }
#     }

#     response = requests.post(BASE_URL, json=payload, headers=headers)
#     response.raise_for_status()
#     return response.json()