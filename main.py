import json

from src.gmail import (
    get_gmail_service,
    get_latest_email,
    get_email_body,
    send_email,
)

from src.llm import get_llm
from src.agent import decide_action
from src.reply import generate_reply
from src.approval import get_human_approval


def main():
    print("Connecting to Gmail...")
    service = get_gmail_service()
    print("Gmail connected successfully!")

    email = get_latest_email(service)
    if not email:
        return

    headers = email["payload"]["headers"]
    sender = ""
    subject = ""

    for header in headers:
        if header["name"] == "From":
            sender = header["value"]
        elif header["name"] == "Subject":
            subject = header["value"]

    body = get_email_body(email)

    print("\nEmail received!")
    print("From:", sender)
    print("Subject:", subject)

    client = get_llm()

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
From: {sender}
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

    llm_output = response.choices[0].message.content
    analysis = json.loads(llm_output)

    print("\n===== HERMES ANALYSIS =====")
    print("Category:", analysis["category"])
    print("Priority:", analysis["priority"])
    print("Action Required:", analysis["action_required"])
    print("Summary:", analysis["summary"])

    decision = decide_action(analysis)
    print("\n===== HERMES DECISION =====")
    print("Decision:", decision)

    if analysis["action_required"]:
        draft = generate_reply(client, sender, subject, body)
        approved = get_human_approval(draft)

        if approved:
            print("\nReply approved by human.")
            send_result = send_email(
                service,
                sender,
                f"Re: {subject}",
                draft,
            )
            print("Reply sent successfully!")
            print("Message ID:", send_result["id"])
        else:
            print("\nReply rejected by human.")
    else:
        print("\nNo reply is required.")


if __name__ == "__main__":
    main()
