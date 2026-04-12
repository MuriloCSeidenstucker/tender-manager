import { apiFetch, isAuthenticated, logout } from "./api.js";

if (!isAuthenticated()) {
  window.location.href = "/frontend/index.html";
}

// ── DOM refs ────────────────────────────────────────────────────────
const companiesList   = document.getElementById("companies-list");
const btnNew          = document.getElementById("btn-new-company");
const modalOverlay    = document.getElementById("modal-overlay");
const modalTitle      = document.getElementById("modal-title");
const companyForm     = document.getElementById("company-form");
const companyIdInput  = document.getElementById("company-id");
const nameInput       = document.getElementById("company-name");
const tradeInput      = document.getElementById("company-trade-name");
const cnpjInput       = document.getElementById("company-cnpj");
const formError       = document.getElementById("form-error");
const btnSave         = document.getElementById("btn-save");
const btnCancel       = document.getElementById("btn-cancel");
const modalClose      = document.getElementById("modal-close");
const deleteOverlay   = document.getElementById("delete-overlay");
const deleteNameEl    = document.getElementById("delete-company-name");
const btnConfirmDel   = document.getElementById("btn-confirm-delete");
const btnCancelDel    = document.getElementById("btn-cancel-delete");
const deleteModalClose = document.getElementById("delete-modal-close");
const logoutBtn       = document.getElementById("logout-btn");
const usernameEl      = document.getElementById("username-display");
const userInitialEl   = document.getElementById("user-initial");

logoutBtn.addEventListener("click", logout);

// ── User info ───────────────────────────────────────────────────────
(function loadUser() {
  const token = localStorage.getItem("access_token");
  if (!token) return;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    const email = payload.sub || "";
    if (usernameEl) usernameEl.textContent = email;
    if (userInitialEl) userInitialEl.textContent = email[0]?.toUpperCase() || "U";
  } catch (_) { /* ignore */ }
})();

// ── Helpers ─────────────────────────────────────────────────────────
function escapeHtml(str) {
  const d = document.createElement("div");
  d.textContent = str;
  return d.innerHTML;
}

function openModal(company = null) {
  formError.classList.add("hidden");
  formError.textContent = "";
  companyForm.reset();

  if (company) {
    modalTitle.textContent = "Editar Empresa";
    companyIdInput.value   = company.id;
    nameInput.value        = company.name;
    tradeInput.value       = company.trade_name;
    cnpjInput.value        = company.cnpj;
  } else {
    modalTitle.textContent = "Nova Empresa";
    companyIdInput.value   = "";
  }
  modalOverlay.classList.remove("hidden");
  nameInput.focus();
}

function closeModal() {
  modalOverlay.classList.add("hidden");
}

let pendingDeleteId = null;

function openDeleteModal(company) {
  pendingDeleteId = company.id;
  deleteNameEl.textContent = company.name;
  deleteOverlay.classList.remove("hidden");
}

function closeDeleteModal() {
  pendingDeleteId = null;
  deleteOverlay.classList.add("hidden");
}

// ── Modal events ─────────────────────────────────────────────────────
btnNew.addEventListener("click", () => openModal());
btnCancel.addEventListener("click", closeModal);
modalClose.addEventListener("click", closeModal);
btnCancelDel.addEventListener("click", closeDeleteModal);
deleteModalClose.addEventListener("click", closeDeleteModal);
modalOverlay.addEventListener("click", (e) => { if (e.target === modalOverlay) closeModal(); });
deleteOverlay.addEventListener("click", (e) => { if (e.target === deleteOverlay) closeDeleteModal(); });

// ── Load companies ───────────────────────────────────────────────────
async function loadCompanies() {
  companiesList.innerHTML = `
    <div class="loading-state">
      <span class="spinner" style="width:28px;height:28px;border-width:3px"></span>
      <span>Carregando empresas...</span>
    </div>`;

  const resp = await apiFetch("/companies/?limit=100");
  if (!resp) return;

  const data = await resp.json();
  const companies = data.companies ?? [];

  if (companies.length === 0) {
    companiesList.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🏢</div>
        <h3>Nenhuma empresa cadastrada</h3>
        <p>Clique em <strong>Nova Empresa</strong> para começar.</p>
      </div>`;
    return;
  }

  companiesList.innerHTML = `<div class="table-wrapper"><table class="data-table">
    <thead>
      <tr>
        <th>Razão Social</th>
        <th>Nome Fantasia</th>
        <th>CNPJ</th>
        <th class="col-actions">Ações</th>
      </tr>
    </thead>
    <tbody id="companies-tbody"></tbody>
  </table></div>`;

  const tbody = document.getElementById("companies-tbody");
  companies.forEach((c, i) => {
    const tr = document.createElement("tr");
    tr.style.animationDelay = `${i * 0.04}s`;
    tr.className = "table-row-anim";
    tr.innerHTML = `
      <td><span class="td-name">${escapeHtml(c.name)}</span></td>
      <td>${escapeHtml(c.trade_name)}</td>
      <td><code class="cnpj-code">${escapeHtml(c.cnpj)}</code></td>
      <td class="col-actions">
        <button class="btn-icon btn-edit" data-id="${c.id}" title="Editar">✏️</button>
        <button class="btn-icon btn-delete" data-id="${c.id}" title="Excluir">🗑️</button>
      </td>`;
    tbody.appendChild(tr);

    tr.querySelector(".btn-edit").addEventListener("click", () => openModal(c));
    tr.querySelector(".btn-delete").addEventListener("click", () => openDeleteModal(c));
  });
}

// ── Save (create / update) ───────────────────────────────────────────
companyForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  formError.classList.add("hidden");

  const id     = companyIdInput.value;
  const name   = nameInput.value.trim();
  const trade  = tradeInput.value.trim();
  const cnpj   = cnpjInput.value.trim().replace(/\D/g, "");

  if (cnpj.length !== 14) {
    formError.textContent = "O CNPJ deve conter exatamente 14 dígitos numéricos.";
    formError.classList.remove("hidden");
    return;
  }

  btnSave.disabled = true;
  btnSave.innerHTML = '<span class="spinner"></span> Salvando...';

  const body = JSON.stringify({ name, trade_name: trade, cnpj });
  const resp = id
    ? await apiFetch(`/companies/${id}`, { method: "PATCH", body })
    : await apiFetch("/companies/", { method: "POST", body });

  btnSave.disabled = false;
  btnSave.innerHTML = "Salvar";

  if (!resp || !resp.ok) {
    const err = await resp?.json().catch(() => ({}));
    formError.textContent = err?.detail ?? "Ocorreu um erro. Tente novamente.";
    formError.classList.remove("hidden");
    return;
  }

  closeModal();
  loadCompanies();
});

// ── Delete ───────────────────────────────────────────────────────────
btnConfirmDel.addEventListener("click", async () => {
  if (!pendingDeleteId) return;
  btnConfirmDel.disabled = true;
  btnConfirmDel.innerHTML = '<span class="spinner"></span>';

  const resp = await apiFetch(`/companies/${pendingDeleteId}`, { method: "DELETE" });

  btnConfirmDel.disabled = false;
  btnConfirmDel.innerHTML = "Excluir";

  if (resp && resp.ok) {
    closeDeleteModal();
    loadCompanies();
  }
});

// ── Init ─────────────────────────────────────────────────────────────
loadCompanies();
