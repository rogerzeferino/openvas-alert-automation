#!/bin/bash

TOKEN="SEU_TOKEN"
CHAT_ID="SEU_CHAT_ID"

REQUEST=$(head -n 1)

EVENT=$(echo "$REQUEST" | grep -oP 'event=\K[^& ]+')
TASK=$(echo "$REQUEST" | grep -oP 'task=\K[^& ]+')

EVENT=$(echo "$EVENT" | sed 's/+/ /g')
TASK=$(echo "$TASK" | sed 's/+/ /g')

[ -z "$EVENT" ] && EVENT="Scan Finalizado"
[ -z "$TASK" ] && TASK="N/A"

DATA=$(date "+%d/%m/%Y %H:%M")

MESSAGE="🚨 ALERTA DE SEGURANÇA 🚨

━━━━━━━━━━━━━━━━━━━━━━━
📌 Status: $EVENT
🖥️ Task: $TASK
📅 Data: $DATA
━━━━━━━━━━━━━━━━━━━━━━━

🔎 Scan de vulnerabilidades concluído.

⚠️ Ação recomendada:
- Acessar o OpenVAS
- Revisar vulnerabilidades
- Priorizar HIGH/CRITICAL
"

curl -s -X POST https://api.telegram.org/bot$TOKEN/sendMessage \
  -d chat_id=$CHAT_ID \
  -d text="$MESSAGE"

export EVENT
export TASK

setpriv --reuid=1001 --regid=1001 --clear-groups \
  /usr/bin/python3 /usr/local/bin/send_email_openvas.py
