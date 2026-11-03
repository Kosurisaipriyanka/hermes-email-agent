import json
import time
import traceback
from email.utils import parseaddr

from src.gmail import (
    get_gmail_service,
    get_unread_emails,
    get_email_by_id,
    get_email_body,
    send_email,
)

from src.llm import get_llm
from src.agent import decide_action
from src.reply import generate_reply
from src.approval import get_human_approval


POLL_INTERVAL_SECONDS = 30
MAX_RESULTS_PER_CHECK = 10


def process_email(service, client, message_id):
    """Run the existing Hermes analysis and approval workflow for one message."""
    email = get_email_by_id(service, message_id)
    headers = email.get("payload", {}).get("headers", [])

    header_values = {
        header.get("name", "").lower(): header.get("value", "")
        for header in headers
    }
    sender_header = header_values.get("from", "")
    sender_email = parseaddr(sender_header)[1] or sender_header
    subject = header_values.get("subject", "(No subject)")
    body = get_email_body(email)

    print("\n" + "=" * 60)
    print("New unread email received!")
    print("From:", sender_header)
    print("Subject:", subject)
    print("=" * 60)

    prompt = f"""
You are Hermes, an email classification agent.

Analyze the email and classify it.

Allowed categories:
- Work
- Personal
- Finance
- Security
- Promotion
- Social
- Other

Allowed priorities:
- Low
- Medium
- High

Rules:
- Security alerts are High priority.
- Emails requiring user action should have action_required = true.
- Promotional emails are normally Low priority.
- If no action is needed, action_required = false.
- Return only the requested JSON structure.

Email:
From: {sender_header}
Subject: {subject}
Body: {body}
"""

    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        temperature=0,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "email_analysis",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": [
                                "Work",
                                "Personal",
                                "Finance",
                                "Security",
                                "Promotion",
                                "Social",
                                "Other",
                            ],
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["Low", "Medium", "High"],
                        },
                        "action_required": {"type": "boolean"},
                        "summary": {"type": "string"},
                    },
                    "required": [
                        "category",
                        "priority",
                        "action_required",
                        "summary",
                    ],
                    "additionalProperties": False,
                },
            },
        },
        messages=[{"role": "user", "content": prompt}],
    )

    analysis = json.loads(response.choices[0].message.content)

    print("\n===== HERMES ANALYSIS =====")
    print("Category:", analysis["category"])
    print("Priority:", analysis["priority"])
    print("Action Required:", analysis["action_required"])
    print("Summary:", analysis["summary"])

    decision = decide_action(analysis)
    print("\n===== HERMES DECISION =====")
    print("Decision:", decision)

    if analysis["action_required"]:
        draft = generate_reply(client, sender_header, subject, body)
        approved = get_human_approval(draft)

        if approved:
            print("\nReply approved by human.")
            send_result = send_email(
                service,
                sender_email,
                f"Re: {subject}",
                draft,
            )
            print("Reply sent successfully!")
            print("Message ID:", send_result["id"])
        else:
            print("\nReply rejected by human.")
    else:
        print("\nNo reply is required.")

    # Mark the message as read only after processing completes.
    # This prevents it from being analysed again on the next poll.
    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"removeLabelIds": ["UNREAD"]},
    ).execute()
    print("Email marked as read.")


def main():
    print("Starting Hermes continuous email monitoring...")
    print(f"Checking unread Inbox emails every {POLL_INTERVAL_SECONDS} seconds.")
    print("Press Ctrl+C to stop Hermes.\n")

    service = get_gmail_service()
    print("Gmail connected successfully!")

    client = get_llm()
    processed_this_run = set()

    try:
        while True:
            try:
                messages = get_unread_emails(
                    service,
                    max_results=MAX_RESULTS_PER_CHECK,
                )

                pending = [
                    message for message in messages
                    if message["id"] not in processed_this_run
                ]

                if not pending:
                    print("No new unread emails. Checking again soon...")
                else:
                    print(f"Found {len(pending)} unread email(s).")

                for message in pending:
                    message_id = message["id"]
                    try:
                        process_email(service, client, message_id)
                        processed_this_run.add(message_id)
                    except Exception as exc:
                        print(f"Error processing email {message_id}: {exc}")
                        traceback.print_exc()
                        # Leave it unread so it can be retried on a later poll.

            except Exception as exc:
                print(f"Error while checking Gmail: {exc}")
                traceback.print_exc()

            time.sleep(POLL_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nHermes stopped by user.")


if __name__ == "__main__":
    main()
