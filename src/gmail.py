import os
import pickle
import base64

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText


SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def get_gmail_service():
    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES,
            )
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)


def get_latest_email(service):
    results = service.users().messages().list(
        userId="me",
        maxResults=1,
    ).execute()

    messages = results.get("messages", [])
    if not messages:
        print("No emails found.")
        return None

    message_id = messages[0]["id"]
    return service.users().messages().get(
        userId="me",
        id=message_id,
        format="full",
    ).execute()


def get_email_body(message):
    payload = message.get("payload", {})

    if payload.get("body", {}).get("data"):
        data = payload["body"]["data"]
        return base64.urlsafe_b64decode(data).decode("utf-8")

    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/plain":
            body_data = part.get("body", {}).get("data")
            if body_data:
                return base64.urlsafe_b64decode(body_data).decode("utf-8")

    return "No readable email body found."


def send_email(service, to, subject, body):
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    sent_message = service.users().messages().send(
        userId="me",
        body={"raw": encoded_message},
    ).execute()

    return sent_message
