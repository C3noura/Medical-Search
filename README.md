# Medical-Search

Site estático para pesquisar artigos médicos sobre intervenções cirúrgicas sem uso de sangue ou derivados, com foco em revistas de boa reputação e opção de enviar resultados por e-mail.

## Como funciona
- Busca de artigos via **Europe PMC** diretamente no navegador (JavaScript).
- Filtro por reputação:
  - Revistas reconhecidas (ex.: The Lancet, NEJM, JAMA, BMJ, Annals of Surgery).
  - Ou pelo menos 20 citações.
- Envio por e-mail usando `mailto:` (abre o cliente de e-mail padrão com assunto/corpo preenchidos).

## Compatibilidade com GitHub Pages
Este projeto foi preparado para rodar como site estático no GitHub Pages.

Arquivos principais:
- `index.html`
- `styles.css`
- `script.js`
- `.nojekyll`

## Publicar no GitHub Pages
### Opção 1 — via GitHub Actions (recomendado)
Já existe workflow em `.github/workflows/pages.yml`.

1. Faça push para `main`.
2. No GitHub, vá em **Settings → Pages**.
3. Em **Build and deployment**, escolha **GitHub Actions**.
4. Aguarde o workflow finalizar.

### Opção 2 — deploy direto do branch
1. Vá em **Settings → Pages**.
2. Em **Build and deployment**, escolha **Deploy from a branch**.
3. Selecione branch `main` e pasta `/ (root)`.

## Rodar localmente
Como é um site estático, pode abrir `index.html` diretamente no navegador.
Se preferir um servidor local:

```bash
python3 -m http.server 8000
```

Depois abra `http://localhost:8000`.

## Observações
- O `mailto:` depende de cliente de e-mail configurado no dispositivo do usuário.
- Se houver bloqueio de rede/CORS no ambiente do usuário, a busca na API do Europe PMC pode falhar.
