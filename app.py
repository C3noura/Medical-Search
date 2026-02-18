import json
import os
import smtplib
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Tuple

import requests
from dotenv import load_dotenv
from flask import Flask, flash, render_template, request

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "medical-search-secret")

EUROPE_PMC_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

HIGH_REPUTATION_JOURNALS = {
    "The Lancet",
    "The New England Journal of Medicine",
    "JAMA",
    "JAMA Surgery",
    "Annals of Surgery",
    "BMJ",
    "British Journal of Surgery",
    "Journal of the American College of Surgeons",
    "Anesthesiology",
    "The BMJ",
}


@dataclass
class Article:
    title: str
    authors: str
    journal: str
    year: str
    doi: str
    pmid: str
    url: str
    abstract: str


def _build_query(user_topic: str) -> str:
    topic = user_topic.strip() or "general surgery"
    return (
        '("bloodless" OR "transfusion-free" OR "patient blood management" OR "blood conservation") '
        f'AND (surgery OR surgical OR operative) AND ({topic})'
    )


def _reputation_score(journal: str, cited_by: int) -> int:
    score = cited_by
    if journal in HIGH_REPUTATION_JOURNALS:
        score += 100
    return score


def search_articles(user_topic: str, max_results: int = 8) -> List[Article]:
    query = _build_query(user_topic)
    params = {
        "query": query,
        "format": "json",
        "pageSize": 40,
        "resultType": "core",
    }

    response = requests.get(EUROPE_PMC_URL, params=params, timeout=20)
    response.raise_for_status()
    payload = response.json()

    raw_results = payload.get("resultList", {}).get("result", [])
    ranked_results: List[Tuple[int, Article]] = []

    for item in raw_results:
        journal = item.get("journalTitle", "")
        cited_by = int(item.get("citedByCount") or 0)

        if journal not in HIGH_REPUTATION_JOURNALS and cited_by < 20:
            continue

        doi = item.get("doi", "")
        pmid = item.get("pmid", "")
        article = Article(
            title=item.get("title", "Título indisponível"),
            authors=item.get("authorString", "Autores indisponíveis"),
            journal=journal or "Revista indisponível",
            year=item.get("pubYear", "Ano indisponível"),
            doi=doi,
            pmid=pmid,
            url=(
                f"https://doi.org/{doi}"
                if doi
                else f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                if pmid
                else ""
            ),
            abstract=(item.get("abstractText") or "Resumo indisponível")[:450] + "...",
        )
        ranked_results.append((_reputation_score(journal, cited_by), article))

    ranked_results.sort(key=lambda x: x[0], reverse=True)
    return [article for _, article in ranked_results[:max_results]]


def send_email_with_results(to_email: str, topic: str, articles: List[Article]) -> None:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM", smtp_user)

    if not all([smtp_host, smtp_user, smtp_password, sender]):
        raise RuntimeError(
            "Configure SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD e SMTP_FROM."
        )

    html_items = "".join(
        [
            (
                f"<li><strong>{a.title}</strong><br>"
                f"{a.authors}<br>"
                f"<em>{a.journal} ({a.year})</em><br>"
                f"{'DOI: ' + a.doi if a.doi else ''}<br>"
                f"<a href='{a.url}'>{a.url}</a></li><br>"
            )
            for a in articles
        ]
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Resultados de pesquisa médica: {topic}"
    msg["From"] = sender
    msg["To"] = to_email
    msg.attach(
        MIMEText(
            f"<h2>Resultados para: {topic}</h2><ol>{html_items}</ol>", "html", "utf-8"
        )
    )

    with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as smtp:
        smtp.starttls()
        smtp.login(smtp_user, smtp_password)
        smtp.send_message(msg)


@app.route("/", methods=["GET", "POST"])
def index():
    topic = ""
    articles: List[Article] = []

    if request.method == "POST":
        action = request.form.get("action")

        if action == "search":
            topic = request.form.get("topic", "")
            try:
                articles = search_articles(topic)
                if not articles:
                    flash(
                        "Nenhum resultado com critério de reputação foi encontrado. Tente outro termo.",
                        "warning",
                    )
            except requests.RequestException:
                flash("Falha ao consultar a base de artigos. Tente novamente.", "error")

        elif action == "send_email":
            topic = request.form.get("topic", "")
            to_email = request.form.get("to_email", "").strip()
            articles_json = request.form.get("articles_json", "[]")

            try:
                article_dicts = json.loads(articles_json)
                articles = [Article(**a) for a in article_dicts]
                send_email_with_results(to_email, topic, articles)
                flash(f"Resultados enviados com sucesso para {to_email}.", "success")
            except json.JSONDecodeError:
                flash("Não foi possível ler os resultados para envio por e-mail.", "error")
            except RuntimeError as exc:
                flash(str(exc), "error")
            except Exception:
                flash("Falha ao enviar e-mail. Verifique as configurações SMTP.", "error")

    articles_json = json.dumps([a.__dict__ for a in articles], ensure_ascii=False)
    return render_template("index.html", topic=topic, articles=articles, articles_json=articles_json)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
