---
name: email-himalaya
description: Read, send, and manage email using the Himalaya CLI (IMAP/SMTP). Use when checking inbox, reading emails, sending emails, searching mail, or any email-related task. Triggers on mentions of email, inbox, mail, unread messages, or sending messages via email.
---

# Email — Himalaya CLI

## Setup

Binary: `/home/openclaw/.local/bin/himalaya`
Config: `/home/openclaw/.config/himalaya/config.toml`
Account: `mrandaclient2024@gmail.com`

**Important:** Gmail requires an App Password for IMAP/SMTP access. If auth fails, a new App Password must be generated at https://myaccount.google.com/apppasswords

## Commands

### List emails (inbox)
```bash
himalaya envelope list
himalaya envelope list --folder "INBOX" --page-size 10
```

### Read an email
```bash
himalaya message read <id>
```

### Search emails
```bash
himalaya envelope list --folder "INBOX" --query "subject:keyword"
himalaya envelope list --folder "INBOX" --query "from:sender@example.com"
```

### Send email
```bash
himalaya message write --to "recipient@email.com" --subject "Subject" --body "Body text"
```

### List folders
```bash
himalaya folder list
```

### Move/delete
```bash
himalaya message move <id> --folder "Trash"
himalaya message delete <id>
```

## Safety Rules
- **Never send emails without explicit user approval** (external communication)
- Reading/checking inbox is safe to do proactively
- Log important emails to daily memory files
- Alert user about urgent unread messages during heartbeats

## Heartbeat Integration
During heartbeat checks, run:
1. `himalaya envelope list --page-size 5` — check for new unread
2. If urgent/important emails found, alert the user
3. Log check timestamp to heartbeat state
