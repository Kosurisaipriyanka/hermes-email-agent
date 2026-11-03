# Hermes Email Agent

Hermes is a Python-based AI email assistant that continuously checks a Gmail inbox, uses an LLM to understand incoming emails, decides whether they need attention, and drafts replies for human approval.

This is an educational project built to gain hands-on experience with **AI Engineering and Agentic AI concepts**. It is intended for learning and experimentation, not as a production email service.

## What Hermes does

1. Connects to Gmail using the Gmail API and Google OAuth 2.0.
2. Checks the Inbox for unread emails every 30 seconds.
3. Fetches up to 10 unread emails per check.
4. Extracts the sender, subject, and message body.
5. Sends the email content to Qwen through the Groq API for analysis.
6. Classifies the email and assigns a priority.
7. Uses Python decision logic to decide what action is needed.
8. Generates a reply draft when a response is required.
9. Shows the draft in the terminal and asks for approval.
10. Sends the reply through Gmail only after approval.
11. Records processing status in a local SQLite database and marks completed emails as read.

## Features

- **Continuous inbox monitoring:** Checks for unread Inbox messages every 30 seconds.
- **Email classification:** Categories include Work, Personal, Finance, Security, Promotion, Social, and Other.
- **Priority detection:** Assigns Low, Medium, or High priority.
- **Action decisions:** Identifies emails that need action and highlights high-priority items.
- **Reply generation:** Creates concise, professional reply drafts when a response is needed.
- **Human-in-the-loop approval:** The user can approve or reject each generated draft before sending.
- **Structured LLM output:** Tries JSON Schema output first and falls back to JSON mode if the model returns a schema-validation error.
- **Email length limit:** Limits the email body sent for analysis and reply generation to 5,000 characters.
- **Processing state:** Uses SQLite to remember completed and sending-related statuses across restarts.
- **Basic retry handling:** Retries failed email processing a limited number of times during the current run.
- **Safe handling of email content:** Prompts instruct the model to treat email content as untrusted input rather than instructions to follow.

## Architecture

~~~text
                 Gmail Inbox
                      |
             Gmail API / OAuth 2.0
                      |
           Poll unread emails (30 sec)
                      |
             Fetch and extract email
                      |
             Limit body to 5,000 chars
                      |
              Groq API -> Qwen
                      |
          Structured email classification
                      |
              Python decision logic
                      |
          +-----------+-----------+
          |                       |
       No action             Action required
          |                       |
    Record status             Generate reply
          |                       |
          |                 Human approval
          |                  /          \
          |              Approve       Reject
          |                |              |
          |           Send with Gmail   Record status
          |                |
          +-------- Record processing status
                      |
               Mark email as read
~~~

## Tech stack

| Technology | Purpose |
|---|---|
| Python 3 | Main application and decision logic |
| Gmail API | Read emails and send approved replies |
| Google OAuth 2.0 | Authorize access to the Gmail account |
| Groq API | Provides access to the language model |
| Qwen (qwen/qwen3.8-27b) | Email analysis and reply generation |
| JSON / JSON Schema | Structured classification output |
| SQLite | Local email-processing state |
| python-dotenv | Load environment variables |

**Note:** Qwen is the language model, while Groq is the API service used to access it. Model inference happens through the online Groq API, so a local GPU is not required.

## Project structure

~~~text
hermes-email-agent/
├── src/
│   ├── __init__.py
│   ├── agent.py       # Python decision logic
│   ├── approval.py    # Human approval in the terminal
│   ├── gmail.py       # Gmail connection and email operations
│   ├── llm.py         # Groq client setup
│   ├── reply.py       # Reply generation
│   └── state.py       # SQLite processing state
├── main.py            # Continuous monitoring and workflow
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
~~~

The SQLite database file is created locally when the application runs. It is not committed to GitHub.

## Setup and run

### 1. Clone the repository

~~~bash
git clone https://github.com/Kosurisaipriyanka/hermes-email-agent.git
cd hermes-email-agent
~~~

### 2. Create and activate a virtual environment

**Windows PowerShell:**

~~~powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
~~~

**macOS/Linux:**

~~~bash
python3 -m venv .venv
source .venv/bin/activate
~~~

### 3. Install dependencies

~~~bash
pip install -r requirements.txt
~~~

### 4. Configure environment variables

Copy .env.example to .env and add your own values:

~~~env
GROQ_API_KEY=your_groq_api_key
USER_NAME=Your Name
~~~

Keep your real .env file private. Never commit your API key.

### 5. Set up Gmail API access

1. Create a project in Google Cloud Console.
2. Enable the Gmail API.
3. Configure the OAuth consent screen.
4. Create an OAuth client ID for a Desktop application.
5. Download the OAuth client file and save it in the project root as credentials.json.
6. Run Hermes. On the first run, a browser window opens for Google account authorization.

The application uses the Gmail gmail.modify scope so it can read messages, send approved replies, and mark processed messages as read. The OAuth token is stored locally as token.pickle.

Do not commit or share credentials.json or token.pickle.

### 6. Start Hermes

~~~bash
python main.py
~~~

Hermes keeps running and checks for unread Inbox messages every 30 seconds. Keep the terminal open while you want monitoring to continue. Press Ctrl+C to stop it.

## How approval works

When Hermes decides an email needs a response, it displays a generated draft in the terminal:

- Enter 1 to approve and send the reply.
- Enter 2 to reject the draft.

Hermes does not send generated replies without approval.

## Processing state and duplicate-send caution

Hermes stores message-processing statuses in a local SQLite database. Before sending an approved reply, it records a sending status. If a send operation fails in a way that leaves the result uncertain, Hermes records that state and avoids automatically sending the same reply again.

This is a basic safeguard, **not a guarantee of exactly-once email delivery**. If Hermes reports an uncertain send, check Gmail's Sent folder before taking further action. Keep the local SQLite database between runs; deleting it removes the saved processing history.

## Current scope and limitations

- Email checks are limited to unread messages in the Gmail Inbox.
- Up to 10 unread messages are fetched per polling cycle.
- The email body sent to the LLM is limited to 5,000 characters, so some long messages may be truncated.
- MIME parsing is basic and may not correctly extract content from every deeply nested or HTML-only email.
- Replies are sent through Gmail, but full Gmail conversation threading is not explicitly managed.
- Failed-processing attempt counts are kept in memory and reset when the application restarts.
- Classification and generated replies can be incorrect; always review drafts before approving them.
- The project has not been designed or tested as a production-grade email service.

## Security notes

- Never upload your Groq API key, .env, credentials.json, or token.pickle to GitHub.
- Keep your Gmail OAuth credentials private.
- Review every generated reply before approving it.
- Use a test Gmail account while experimenting.

## Learning outcomes

This project provides practical experience with:

- Integrating an LLM into a Python application
- Prompt engineering and structured model outputs
- Building an agent-style **analyze -> decide -> act** workflow
- Connecting an AI application to an external tool through the Gmail API
- Human-in-the-loop approval
- Continuous polling and automation
- Persistent state with SQLite
- Error handling and API fallback strategies
- Managing environment variables and a GitHub project

---

**Project status:** Educational Agentic AI MVP — core workflow implemented and tested. The focus is learning and hands-on practice, not production deployment.
