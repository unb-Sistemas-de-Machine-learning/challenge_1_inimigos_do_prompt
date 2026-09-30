import os
import logging
import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
from celery import Celery

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery("worker", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

celery_app.conf.beat_schedule = {
    "check-inbox-every-60-seconds": {
        "task": "app.worker.check_inbox",
        "schedule": 60.0,
    }
}
celery_app.conf.timezone = "UTC"


def clean_html_body(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style", "footer", "iframe"]):
        tag.decompose()
    
    text = soup.get_text(separator=" ")
    text = " ".join(text.split())
    return text


def _decode_header_value(value: str) -> str:
    if not value:
        return ""
    decoded_parts = decode_header(value)
    result = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result += part.decode(encoding or "utf-8", errors="ignore")
        else:
            result += part
    return result


def _get_html_body(msg) -> str:
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if content_type == "text/html" and "attachment" not in content_disposition:
                payload = part.get_payload(decode=True)
                if payload:
                    body += payload.decode("utf-8", errors="ignore")
            elif content_type == "text/plain" and "attachment" not in content_disposition and not body:
                payload = part.get_payload(decode=True)
                if payload:
                    body += payload.decode("utf-8", errors="ignore")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode("utf-8", errors="ignore")
    return body


@celery_app.task(name="app.worker.check_inbox")
def check_inbox():
    imap_server = os.environ.get("IMAP_SERVER")
    imap_user = os.environ.get("IMAP_USER")
    imap_pass = os.environ.get("IMAP_PASS")

    if not all([imap_server, imap_user, imap_pass]):
        logger.error("IMAP_SERVER, IMAP_USER or IMAP_PASS environment variables are missing.")
        return

    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(imap_user, imap_pass)
        mail.select("inbox")

        status, messages = mail.search(None, "UNSEEN")
        if status != "OK":
            logger.error("Failed to search for unseen messages.")
            mail.logout()
            return
            
        mail_ids = messages[0].split()
        for mail_id in mail_ids:
            res, msg_data = mail.fetch(mail_id, "(RFC822)")
            if res != "OK":
                logger.error(f"Failed to fetch message ID {mail_id}")
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = _decode_header_value(msg.get("Subject", ""))
                    html_body = _get_html_body(msg)
                    
                    cleaned_body = clean_html_body(html_body)
                    
                    logger.info(f"Successfully ingested newsletter: '{subject}'. Cleaned body length: {len(cleaned_body)} characters.")
                    
        mail.close()
        mail.logout()
    except Exception as e:
        logger.error(f"An error occurred while checking the inbox: {e}")
