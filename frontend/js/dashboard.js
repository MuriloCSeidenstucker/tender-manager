import { apiFetch, isAuthenticated, logout } from "./api.js";

if (!isAuthenticated()) {
  window.location.href = "/frontend/index.html";
}

const companiesContainer = document.getElementById("companies-container");
const yearSelect = document.getElementById("year-select");
const usernameEl = document.getElementById("username-display");
const userInitialEl = document.getElementById("user-initial");
const logoutBtn = document.getElementById("logout-btn");

logoutBtn.addEventListener("click", logout);

// Populate year selector (current year and 4 years back)
const currentYear = new Date().getFullYear();
for (let y = currentYear; y >= currentYear - 4; y--) {
  const opt = document.createElement("option");
  opt.value = y;
  opt.textContent = y;
  yearSelect.appendChild(opt);
}
yearSelect.value = currentYear;
yearSelect.addEventListener("change", () => loadMetrics(Number(yearSelect.value)));

async function loadUser() {
  const resp = await apiFetch("/users/?limit=1");
  if (!resp) return;
  // Use the token payload to get the username via a simple decode
  const token = localStorage.getItem("access_token");
  const payload = JSON.parse(atob(token.split(".")[1]));
  const email = payload.sub || "";
  if (usernameEl) usernameEl.textContent = email;
  if (userInitialEl) userInitialEl.textContent = email[0]?.toUpperCase() || "U";
}

async function loadMetrics(year = currentYear) {
  companiesContainer.innerHTML = `
    <div class="loading-state">
      <span class="spinner" style="width:28px;height:28px;border-width:3px"></span>
      <span>Carregando dados...</span>
    </div>`;

  const resp = await apiFetch(`/dashboard/metrics?year=${year}`);
  if (!resp) return;

  const data = await resp.json();
  const companies = data.companies;

  if (!companies || companies.length === 0) {
    companiesContainer.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🏢</div>
        <h3>Nenhuma empresa cadastrada</h3>
        <p>Cadastre uma empresa para começar a acompanhar suas licitações.</p>
      </div>`;
    return;
  }

  companiesContainer.innerHTML = "";
  companies.forEach((company, index) => {
    const awarded = parseFloat(company.total_awarded_value).toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
    });
    const initial = company.company_name[0]?.toUpperCase() || "E";
    const card = document.createElement("div");
    card.className = "company-card";
    card.style.animationDelay = `${index * 0.06}s`;
    card.innerHTML = `
      <div class="company-header">
        <div class="company-icon">${initial}</div>
        <div class="company-title">
          <h3>${escapeHtml(company.company_name)}</h3>
          <span>Ano ${year}</span>
        </div>
      </div>
      <div class="metrics-grid">
        <div class="metric-box">
          <div class="metric-label">Licitações</div>
          <div class="metric-value">${company.total_tenders}</div>
        </div>
        <div class="metric-box success">
          <div class="metric-label">Vitórias</div>
          <div class="metric-value">${company.won_tenders}</div>
        </div>
        <div class="metric-box warning wide">
          <div class="metric-label">Total Arrecadado</div>
          <div class="metric-value">${awarded}</div>
        </div>
      </div>`;
    companiesContainer.appendChild(card);
  });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

loadUser();
loadMetrics(currentYear);
