import imaplib
import email
import os

from email.header import decode_header
from dotenv import load_dotenv

load_dotenv()


def decode_subject(value):
    if not value:
        return ""

    parts = decode_header(value)

    return "".join(
        part.decode(encoding or "utf-8", errors="replace")
        if isinstance(part, bytes)
        else part
        for part, encoding in parts
    )


def get_recent_emails(limit: int = 5) -> list[dict]:

    gmail_address = os.getenv("GMAIL_ADDRESS")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")

    if not gmail_address or not gmail_password:
        raise ValueError("Gmail credentials are missing")

    emails = []

    with imaplib.IMAP4_SSL("imap.gmail.com") as mail:

        mail.login(gmail_address, gmail_password)

        mail.select("INBOX", readonly=True)

        status, messages = mail.uid("search", None, "ALL")

        if status != "OK":
            raise RuntimeError("Failed to search Gmail")

        email_ids = messages[0].split()[-limit:]

        for email_id in reversed(email_ids):

            status, data = mail.uid(
                "fetch", email_id, "(RFC822)"
            )

            if status != "OK":
                continue

            raw_email = next(
                (
                    item[1]
                    for item in data
                    if isinstance(item, tuple)
                ),
                None,
            )

            if raw_email is None:
                continue

            msg = email.message_from_bytes(raw_email)

            subject = decode_subject(msg["Subject"])

            body = ""

            if msg.is_multipart():

                for part in msg.walk():

                    if part.get_content_type() == "text/plain":
                        if part.get_content_disposition() == "attachment":
                            continue

                        payload = part.get_payload(decode=True)

                        if payload:
                            body = payload.decode(
                                part.get_content_charset() or "utf-8",
                                errors="replace",
                            )
                            break

            else:
                payload = msg.get_payload(decode=True)

                if payload and msg.get_content_type() == "text/plain":
                    body = payload.decode(
                        msg.get_content_charset() or "utf-8",
                        errors="replace",
                    )

            emails.append({
                "id": email_id.decode(),
                "sender": msg["From"],
                "subject": subject,
                "body": body[:3000],
            })

        mail.logout()

    return emails