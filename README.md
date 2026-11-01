# Hermes Email Agent

Hermes is a Python-based AI email assistant that reads the latest Gmail message, classifies it with Qwen through the Groq API, decides whether action is needed, drafts a reply, and asks for human approval before sending.

## Features

- Connects to Gmail using the Gmail API and Google OAuth 2.0
- Fetches the latest email
- Extracts sender, subject, and readable message body
- Classifies emails into Work, Personal, Finance, Security, Promotion, Social, or Other
- Assigns Low, Medium, or High priority
- Produces structured JSON output
- Generates a concise reply draft when action is required
- Requires human approval before sending a reply

## Architecture

```text
Gmail API
   |
Fetch latest email
   |
Extract email details
   |
Groq API -> Qwen
   |
Structured classification
   |
Python decision logic
   |
Reply draft (if action is required)
   |
Human approval
   |
Gmail API sends the approved reply
```

## Tech stack

- Python
- Gmail API
- Google OAuth 2.0
- Groq API
- Qwen model: `qwen/qwen3.8-27b`
- JSON Schema structured output

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Kosurisaipriyanka/hermes-email-agent.git
cd hermes-email-agent
```

### 2. Create and activate a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and add your own Groq API key and name:

```env
GROQ_API_KEY=your_groq_api_key
USER_NAME=Your Name
```

Never commit your real `.env` file.

### 5. Configure Gmail API credentials

Create a Google Cloud project, enable the Gmail API, configure the OAuth consent screen, and create a Desktop OAuth client.

Download the OAuth client file and save it in the project root as `credentials.json`. The application requests the Gmail `gmail.modify` scope. On first run, a browser window opens so you can authorize access. The resulting `token.pickle` is stored locally.

Do not share or commit `credentials.json` or `token.pickle`.

### 6. Run Hermes

```bash
python main.py
```

## Current limitations

- The application checks only the single latest Gmail message when run; it does not continuously monitor the inbox.
- It does not yet track processed message IDs, so the same message may be processed again on another run.
- Email body parsing handles simple text and first-level `text/plain` parts; deeply nested or HTML-only messages may not be extracted.
- Replies are sent as new messages with a `Re:` subject; Gmail thread headers are not yet managed explicitly.
- Human approval is required in the terminal before a reply is sent.

## Security

- Keep `.env`, `credentials.json`, and `token.pickle` private.
- The repository intentionally excludes these files through `.gitignore`.
- Review every generated draft before approving it.
- Do not use this project to send sensitive or consequential messages without careful human review.

## Project status

This is an educational MVP. Automatic inbox monitoring, notifications, duplicate prevention, robust MIME parsing, proper Gmail threading, automated tests, and production-grade error handling are future improvements.
