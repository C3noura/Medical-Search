# Medical-Search

Website para pesquisar artigos médicos sobre intervenções cirúrgicas sem uso de sangue ou derivados, priorizando revistas de boa reputação, com opção de envio dos resultados por e-mail.

## Funcionalidades
- Busca de artigos via Europe PMC API.
- Filtro de reputação (revistas reconhecidas e/ou número de citações).
- Interface simples e sóbria.
- Envio dos resultados por e-mail via SMTP.

## Requisitos
- Python 3.10+
- Dependências em `requirements.txt`

## Como executar
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Abra `http://localhost:5000`.

## Configuração de e-mail
Defina as variáveis no `.env` (ou no ambiente):
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `SMTP_FROM`

Sem essas variáveis, a aplicação permite pesquisar, mas mostrará erro ao tentar enviar e-mail.
