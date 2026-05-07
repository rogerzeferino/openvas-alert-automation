# Arquitetura do Pipeline

OpenVAS (Docker)
     ↓  HTTP GET Alert (Task Done)
Webhook Listener (netcat :8080)
     ↓  stdin pipe
Script Bash (parser + Telegram)
     ↓  env vars + setpriv
Script Python (e-mail via relay SMTP)
     ↓
Telegram Bot  +  E-mail Corporativo
