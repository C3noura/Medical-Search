const HIGH_REPUTATION_JOURNALS = new Set([
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
]);

const searchForm = document.getElementById("search-form");
const feedbackEl = document.getElementById("feedback");
const resultsCard = document.getElementById("results-card");
const resultsList = document.getElementById("results-list");
const emailCard = document.getElementById("email-card");
const emailForm = document.getElementById("email-form");
const mailtoLink = document.getElementById("mailto-link");
const toEmailInput = document.getElementById("to-email");
const topicInput = document.getElementById("topic");

let latestResults = [];
let latestTopic = "";

function showMessage(type, text) {
  feedbackEl.innerHTML = `<div class="message ${type}">${text}</div>`;
}

function clearMessage() {
  feedbackEl.innerHTML = "";
}

function buildQuery(topic) {
  return `("bloodless" OR "transfusion-free" OR "patient blood management" OR "blood conservation") AND (surgery OR surgical OR operative) AND (${topic})`;
}

function score(item) {
  const citedBy = Number(item.citedByCount || 0);
  const journal = item.journalTitle || "";
  return citedBy + (HIGH_REPUTATION_JOURNALS.has(journal) ? 100 : 0);
}

function formatResult(item) {
  const title = item.title || "Título indisponível";
  const authors = item.authorString || "Autores indisponíveis";
  const journal = item.journalTitle || "Revista indisponível";
  const year = item.pubYear || "Ano indisponível";
  const doi = item.doi || "";
  const pmid = item.pmid || "";
  const url = doi ? `https://doi.org/${doi}` : (pmid ? `https://pubmed.ncbi.nlm.nih.gov/${pmid}/` : "");
  const abstract = ((item.abstractText || "Resumo indisponível").slice(0, 450) + "...");

  return { title, authors, journal, year, doi, pmid, url, abstract };
}

function renderResults(results) {
  resultsList.innerHTML = results.map((article) => `
    <li>
      <h3>${article.title}</h3>
      <p><strong>Autores:</strong> ${article.authors}</p>
      <p><strong>Revista:</strong> ${article.journal} (${article.year})</p>
      <p>${article.abstract}</p>
      ${article.url ? `<a href="${article.url}" target="_blank" rel="noopener noreferrer">Abrir artigo</a>` : ""}
    </li>
  `).join("");

  resultsCard.classList.remove("hidden");
  emailCard.classList.remove("hidden");
}

function updateMailtoLink() {
  const to = toEmailInput.value.trim();
  if (!to || latestResults.length === 0) {
    mailtoLink.setAttribute("href", "#");
    return;
  }

  const subject = `Resultados de pesquisa médica: ${latestTopic}`;
  const body = [
    `Resultados para: ${latestTopic}`,
    "",
    ...latestResults.map((a, i) => `${i + 1}. ${a.title}\n${a.authors}\n${a.journal} (${a.year})\n${a.url || "Sem link"}\n`),
  ].join("\n");

  const href = `mailto:${encodeURIComponent(to)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  mailtoLink.setAttribute("href", href);
}

searchForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearMessage();

  const topic = topicInput.value.trim();
  latestTopic = topic;

  if (!topic) {
    showMessage("error", "Informe um tema para pesquisa.");
    return;
  }

  showMessage("success", "Consultando base de dados...");

  const params = new URLSearchParams({
    query: buildQuery(topic),
    format: "json",
    pageSize: "50",
    resultType: "core",
  });

  try {
    const response = await fetch(`https://www.ebi.ac.uk/europepmc/webservices/rest/search?${params.toString()}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const payload = await response.json();
    const raw = (payload.resultList && payload.resultList.result) || [];

    const filtered = raw
      .filter((item) => HIGH_REPUTATION_JOURNALS.has(item.journalTitle || "") || Number(item.citedByCount || 0) >= 20)
      .sort((a, b) => score(b) - score(a))
      .slice(0, 8)
      .map(formatResult);

    latestResults = filtered;

    if (filtered.length === 0) {
      resultsCard.classList.add("hidden");
      emailCard.classList.add("hidden");
      showMessage("error", "Nenhum resultado com critério de reputação foi encontrado. Tente outro termo.");
      return;
    }

    renderResults(filtered);
    updateMailtoLink();
    showMessage("success", `${filtered.length} artigo(s) encontrado(s).`);
  } catch (error) {
    resultsCard.classList.add("hidden");
    emailCard.classList.add("hidden");
    showMessage("error", "Falha ao consultar Europe PMC. Verifique conexão/CORS e tente novamente.");
  }
});

emailForm.addEventListener("input", updateMailtoLink);
mailtoLink.addEventListener("click", (event) => {
  if (mailtoLink.getAttribute("href") === "#") {
    event.preventDefault();
    showMessage("error", "Pesquise artigos e informe o e-mail de destino antes de gerar o envio.");
  }
});
