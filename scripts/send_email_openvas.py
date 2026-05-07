#!/usr/bin/env python3

import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os

SMTP_SERVER = "SEU_SMTP_RELAY"
SMTP_PORT = 25

EMAIL_FROM = "alert.openvas@seudominio.com"
EMAIL_TO   = "destinatario@seudominio.com"

TASK  = os.getenv("TASK",  "N/A")
EVENT = os.getenv("EVENT", "Scan Finalizado")
now   = datetime.now().strftime("%d/%m/%Y %H:%M")

body = f"""
🚨 ALERTA DE SEGURANÇA - OPENVAS 🚨

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 STATUS: {EVENT}
🖥️ TASK:   {TASK}
📅 DATA:   {now}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔎 O scan de vulnerabilidades foi concluído.

⚠️ AÇÃO RECOMENDADA:
- Acessar o OpenVAS
- Revisar vulnerabilidades
- Priorizar HIGH/CRITICAL

🔗 ACESSO: https://SEU_OPENVAS:9392

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Alerta automático do sistema de segurança.
"""

msg = MIMEText(body)
msg["Subject"] = f"[SECURITY ALERT] OpenVAS - {TASK}"
msg["From"]    = EMAIL_FROM
msg["To"]      = EMAIL_TO

try:
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.send_message(msg)
    server.quit()
    print("Email enviado com sucesso.")
except Exception as e:
    print(f"Erro ao enviar email: {e}")
