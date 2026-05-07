# OpenVAS Alert Automation Pipeline

Sistema de automação para notificação em tempo real de scans de vulnerabilidade utilizando OpenVAS, webhook HTTP, Bash e Python. Implementado em ambiente corporativo (produção).

---

## Visão Geral

Ao finalizar um scan no OpenVAS, o sistema dispara automaticamente um alerta via **Telegram** e **e-mail corporativo**, sem intervenção manual. O pipeline foi construído com ferramentas nativas do Linux (Bash, netcat, Python) e integrado diretamente ao OpenVAS rodando em Docker.

---

## Arquitetura

```
OpenVAS (Docker)
     ↓  HTTP GET Alert (Task Done)
Webhook Listener (netcat :8080)
     ↓  stdin pipe
Script Bash (parser + Telegram)
     ↓  env vars + setpriv
Script Python (e-mail via relay SMTP)
     ↓
Telegram Bot  +  E-mail Corporativo
```

---

## Funcionalidades

- Alerta automático ao finalizar qualquer scan no OpenVAS
- Notificação em tempo real via **Telegram Bot**
- Envio de **e-mail corporativo** via relay SMTP interno
- Parsing manual de requisição HTTP GET (sem dependências externas)
- Mensagem estruturada com status, task name, data/hora e ação recomendada
- Execução segura com troca de contexto de usuário via `setpriv`
- Pipeline leve: netcat + Bash + Python puro

---

## Estrutura do Repositório

```
openvas-alert-automation/
│
├── scripts/
│   ├── openvas_telegram.sh        # Webhook listener + parser + envio Telegram
│   └── send_email_openvas.py      # Envio de e-mail via SMTP relay
│
├── docs/
│   ├── arquitetura.md             # Detalhamento do fluxo
│   └── configuracao_openvas.md    # Como configurar o alerta HTTP no OpenVAS
│
└── README.md
```

---

## Configuração do Alerta no OpenVAS

No OpenVAS, crie um **Alert** com as seguintes configurações:

| Campo   | Valor                                      |
|---------|--------------------------------------------|
| Method  | HTTP Get                                   |
| Event   | Task run status changed → Done             |
| URL     | `http://SEU_IP:8080/?event=$e&task=$n`     |

---

## Webhook Listener

O listener fica em loop aguardando conexões na porta `8080` e passa o conteúdo da requisição diretamente para o script Bash via stdin:

```bash
while true; do
  nc -l -p 8080 -q 1 | /usr/local/bin/openvas_telegram.sh
done
```

---

## Script Bash — `openvas_telegram.sh`

Responsável por:
1. Capturar e fazer o parsing da requisição HTTP GET
2. Extrair os parâmetros `event` e `task` via `grep -oP`
3. Enviar a notificação para o **Telegram Bot**
4. Exportar as variáveis de ambiente e chamar o script Python com contexto de usuário limitado via `setpriv`

```bash
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
• Acessar o OpenVAS
• Revisar vulnerabilidades
• Priorizar HIGH/CRITICAL
"

curl -s -X POST https://api.telegram.org/bot$TOKEN/sendMessage \
  -d chat_id=$CHAT_ID \
  -d text="$MESSAGE"

export EVENT
export TASK

setpriv --reuid=1001 --regid=1001 --clear-groups \
  /usr/bin/python3 /usr/local/bin/send_email_openvas.py
```

---

## Script Python — `send_email_openvas.py`

Responsável por enviar o e-mail via relay SMTP interno, utilizando as variáveis de ambiente exportadas pelo script Bash.

```python
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
```

---

## Variáveis a Configurar

Antes de usar, substitua os placeholders nos scripts:

| Variável          | Onde                     | Descrição                              |
|-------------------|--------------------------|----------------------------------------|
| `SEU_TOKEN`       | `openvas_telegram.sh`    | Token do Telegram Bot                  |
| `SEU_CHAT_ID`     | `openvas_telegram.sh`    | Chat ID do Telegram                    |
| `SEU_SMTP_RELAY`  | `send_email_openvas.py`  | IP ou hostname do relay SMTP interno   |
| `SEU_OPENVAS`     | `send_email_openvas.py`  | IP/hostname da interface web do OpenVAS|
| `EMAIL_FROM`      | `send_email_openvas.py`  | Endereço remetente                     |
| `EMAIL_TO`        | `send_email_openvas.py`  | Endereço destinatário                  |

---

## Principais Desafios Resolvidos

**Execução fora do contexto root**
O OpenVAS roda em Docker e o script precisava acionar o Python com um usuário sem privilégios. Solução: `setpriv` com `--reuid`, `--regid` e `--clear-groups`.

**Parsing manual de requisição HTTP**
O OpenVAS só suporta HTTP GET simples. Sem framework, o parsing foi feito com `grep -oP` e `sed` direto no stdin capturado pelo netcat.

**Comunicação entre processos via stdin**
O fluxo `nc → bash → python` exigiu cuidado com o comportamento do stdin: o netcat precisa do flag `-q 1` para fechar a conexão após o primeiro pacote e liberar o pipe.

**Integração Bash + Python via variáveis de ambiente**
Como o Python é chamado como subprocesso pelo Bash, a passagem de dados foi feita via `export` de variáveis de ambiente, evitando arquivos temporários ou soluções mais complexas.

**Ambiente Docker com rede isolada**
O container do OpenVAS precisava ter visibilidade para o host onde o listener estava rodando. Isso exigiu ajuste de rede no Docker (host networking ou mapeamento correto de interfaces).

---

## Tecnologias Utilizadas

- **OpenVAS / Greenbone** — scanner de vulnerabilidades
- **Bash** — parsing e orquestração do pipeline
- **Python 3** — envio de e-mail via smtplib
- **Netcat (nc)** — listener HTTP leve na porta 8080
- **curl** — integração com a API do Telegram
- **setpriv** — troca segura de contexto de usuário
- **Docker** — ambiente de execução do OpenVAS
- **Ubuntu Server** — sistema operacional base

---

## Resultado

- Pipeline funcional em ambiente corporativo (produção)
- Alertas automáticos ao término de cada scan, sem intervenção manual
- Notificações entregues via Telegram e e-mail em menos de 5 segundos após o evento
- Mensagem estruturada com contexto suficiente para triagem imediata
- Base preparada para integração futura com SIEM (Wazuh / StellarCyber)

---

## Próximos Passos

- Integração com Wazuh para correlação de eventos
- Enriquecimento dos alertas com dados do relatório (CVEs, hosts afetados)
- Substituição do netcat por um listener mais robusto (socat ou serviço Python)
- Dashboard de histórico de scans

---

## Aviso de Segurança

Os scripts neste repositório contêm placeholders para credenciais sensíveis (token do Telegram, endereços de e-mail, IPs internos). **Nunca comite valores reais em repositórios públicos.** Utilize variáveis de ambiente ou um gerenciador de secrets para ambientes de produção.

---

*Projeto desenvolvido e implementado em ambiente corporativo real — Nortox S/A*
