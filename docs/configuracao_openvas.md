# Configuração do Alerta HTTP no OpenVAS

1. Acesse o OpenVAS → **Configuration → Alerts**
2. Clique em **New Alert**
3. Configure:
   - **Name:** Webhook Alert
   - **Event:** Task run status changed → Done
   - **Method:** HTTP Get
   - **URL:** `http://SEU_IP:8080/?event=$e&task=$n`
4. Salve e associe o alert à sua task de scan

O OpenVAS vai disparar o GET automaticamente ao finalizar cada scan.
