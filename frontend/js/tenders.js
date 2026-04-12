import { apiFetch, isAuthenticated, logout } from "./api.js";

if (!isAuthenticated()) {
  window.location.href = "/frontend/index.html";
}

// ── DOM refs ──────────────────────────────────────────────────────────
const tendersList      = document.getElementById("tenders-list");
const companySelect    = document.getElementById("company-select");
const btnNew           = document.getElementById("btn-new-tender");
const modalOverlay     = document.getElementById("modal-overlay");
const modalTitle       = document.getElementById("modal-title");
const tenderForm       = document.getElementById("tender-form");
const tenderIdInput    = document.getElementById("tender-id");
const numberInput      = document.getElementById("tender-number");
const yearInput        = document.getElementById("tender-year");
const bodyInput        = document.getElementById("tender-body");
const descInput        = document.getElementById("tender-desc");
const modalitySelect   = document.getElementById("tender-modality");
const formatSelect     = document.getElementById("tender-format");
const sessionDateInput = document.getElementById("tender-session-date");
const statusSelect     = document.getElementById("tender-status");
const resultSelect     = document.getElementById("tender-result");
const awardedInput     = document.getElementById("tender-awarded");
const formError        = document.getElementById("form-error");
const btnSave          = document.getElementById("btn-save");
const btnCancel        = document.getElementById("btn-cancel");
const modalClose       = document.getElementById("modal-close");
const deleteOverlay    = document.getElementById("delete-overlay");
const deleteLabelEl    = document.getElementById("delete-tender-label");
const btnConfirmDel    = document.getElementById("btn-confirm-delete");
const btnCancelDel     = document.getElementById("btn-cancel-delete");
const deleteModalClose = document.getElementById("delete-modal-close");
const logoutBtn        = document.getElementById("logout-btn");
const usernameEl       = document.getElementById("username-display");
const userInitialEl    = document.getElementById("user-initial");

logoutBtn.addEventListener("click", logout);

// ── Labels ────────────────────────────────────────────────────────────
const MODALITY_LABELS = {
  public_tender: "Concorrência",
  price_quotation: "Tomada de Preços",
  invitation: "Convite",
  auction: "Leilão",
  contest: "Concurso",
  trading_session: "Pregão",
  direct_contracting: "Dispensa/Inexigibilidade",
};

const STATUS_LABELS = {
  monitoring: "Monitoramento",
  analysis: "Análise",
  approved: "Aprovado",
  rejected: "Rejeitado",
  registered: "Cadastrado",
  in_progress: "Em andamento",
  appeal: "Recurso",
  finished: "Finalizado",
  suspended: "Suspenso",
  canceled: "Cancelado",
};

const RESULT_LABELS = {
  pending: "Pendente",
  won: "Ganhou ✅",
  lost: "Perdeu ❌",
};

const STATUS_COLORS = {
  monitoring: "badge-blue",
  analysis: "badge-blue",
  approved: "badge-green",
  rejected: "badge-red",
  registered: "badge-purple",
  in_progress: "badge-yellow",
  appeal: "badge-yellow",
  finished: "badge-green",
  suspended: "badge-red",
  canceled: "badge-red",
};

// ── User info ─────────────────────────────────────────────────────────
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

// ── Helpers ───────────────────────────────────────────────────────────
function escapeHtml(str) {
  const d = document.createElement("div");
  d.textContent = str;
  return d.innerHTML;
}

function formatCurrency(val) {
  if (val === null || val === undefined) return "—";
  return parseFloat(val).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function formatDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

// ISO datetime-local format: "2026-04-01T14:00"
function toDatetimeLocal(iso) {
  if (!iso) return "";
  return iso.slice(0, 16);
}

// ── Load companies into selector ──────────────────────────────────────
async function loadCompanies() {
  const resp = await apiFetch("/companies/?limit=100");
  if (!resp) return;
  const data = await resp.json();
  const companies = data.companies ?? [];

  companySelect.innerHTML = '<option value="">— Selecione uma empresa —</option>';
  companies.forEach((c) => {
    const opt = document.createElement("option");
    opt.value = c.id;
    opt.textContent = c.name;
    companySelect.appendChild(opt);
  });

  // Restore selection from URL param ?company=id
  const params = new URLSearchParams(window.location.search);
  const preselected = params.get("company");
  if (preselected && companies.find((c) => String(c.id) === preselected)) {
    companySelect.value = preselected;
    loadTenders(preselected);
    btnNew.disabled = false;
  }
}

// ── Company selector change ───────────────────────────────────────────
companySelect.addEventListener("change", () => {
  const id = companySelect.value;
  btnNew.disabled = !id;
  if (id) {
    loadTenders(id);
    const url = new URL(window.location);
    url.searchParams.set("company", id);
    window.history.replaceState({}, "", url);
  } else {
    tendersList.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🏢</div>
        <h3>Selecione uma empresa</h3>
        <p>Escolha uma empresa acima para ver suas licitações.</p>
      </div>`;
  }
});

// ── Load tenders ──────────────────────────────────────────────────────
async function loadTenders(companyId) {
  tendersList.innerHTML = `
    <div class="loading-state">
      <span class="spinner" style="width:28px;height:28px;border-width:3px"></span>
      <span>Carregando licitações...</span>
    </div>`;

  const resp = await apiFetch(`/companies/${companyId}/tenders/?limit=100`);
  if (!resp) return;

  const data = await resp.json();
  const tenders = data.tenders ?? [];

  if (tenders.length === 0) {
    tendersList.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">📄</div>
        <h3>Nenhuma licitação encontrada</h3>
        <p>Clique em <strong>Nova Licitação</strong> para começar.</p>
      </div>`;
    return;
  }

  tendersList.innerHTML = `<div class="table-wrapper"><table class="data-table">
    <thead>
      <tr>
        <th>Nº / Ano</th>
        <th>Órgão</th>
        <th>Modalidade</th>
        <th>Status</th>
        <th>Resultado</th>
        <th>Valor</th>
        <th>Sessão</th>
        <th class="col-actions">Ações</th>
      </tr>
    </thead>
    <tbody id="tenders-tbody"></tbody>
  </table></div>`;

  const tbody = document.getElementById("tenders-tbody");
  tenders.forEach((t, i) => {
    const tr = document.createElement("tr");
    tr.className = "table-row-anim";
    tr.style.animationDelay = `${i * 0.03}s`;
    const resultClass = t.participation_result === "won"
      ? "result-won"
      : t.participation_result === "lost"
        ? "result-lost"
        : "result-pending";
    tr.innerHTML = `
      <td><span class="td-name">${t.tender_number}/${t.tender_year}</span></td>
      <td>${escapeHtml(t.public_body_name)}</td>
      <td>${MODALITY_LABELS[t.modality] ?? t.modality}</td>
      <td><span class="badge ${STATUS_COLORS[t.status] ?? "badge-blue"}">${STATUS_LABELS[t.status] ?? t.status}</span></td>
      <td><span class="${resultClass}">${RESULT_LABELS[t.participation_result] ?? "—"}</span></td>
      <td>${formatCurrency(t.awarded_value)}</td>
      <td>${formatDate(t.session_date)}</td>
      <td class="col-actions">
        <button class="btn-icon btn-edit" title="Editar">✏️</button>
        <button class="btn-icon btn-delete" title="Excluir">🗑️</button>
      </td>`;
    tbody.appendChild(tr);
    tr.querySelector(".btn-edit").addEventListener("click", () => openModal(t));
    tr.querySelector(".btn-delete").addEventListener("click", () => openDeleteModal(t));
  });
}

// ── Modal: open / close ───────────────────────────────────────────────
function openModal(tender = null) {
  formError.classList.add("hidden");
  tenderForm.reset();

  if (tender) {
    modalTitle.textContent = "Editar Licitação";
    tenderIdInput.value        = tender.id;
    numberInput.value          = tender.tender_number;
    yearInput.value            = tender.tender_year;
    bodyInput.value            = tender.public_body_name;
    descInput.value            = tender.object_description;
    modalitySelect.value       = tender.modality;
    formatSelect.value         = tender.format;
    sessionDateInput.value     = toDatetimeLocal(tender.session_date);
    statusSelect.value         = tender.status;
    resultSelect.value         = tender.participation_result ?? "pending";
    awardedInput.value         = tender.awarded_value ?? "";
  } else {
    modalTitle.textContent = "Nova Licitação";
    tenderIdInput.value    = "";
    yearInput.value        = new Date().getFullYear();
  }
  modalOverlay.classList.remove("hidden");
  numberInput.focus();
}

function closeModal() { modalOverlay.classList.add("hidden"); }

let pendingDeleteId = null;
let pendingDeleteLabel = "";

function openDeleteModal(tender) {
  pendingDeleteId    = tender.id;
  pendingDeleteLabel = `${tender.tender_number}/${tender.tender_year}`;
  deleteLabelEl.textContent = pendingDeleteLabel;
  deleteOverlay.classList.remove("hidden");
}

function closeDeleteModal() {
  pendingDeleteId = null;
  deleteOverlay.classList.add("hidden");
}

// Events
btnNew.addEventListener("click", () => openModal());
btnCancel.addEventListener("click", closeModal);
modalClose.addEventListener("click", closeModal);
btnCancelDel.addEventListener("click", closeDeleteModal);
deleteModalClose.addEventListener("click", closeDeleteModal);
modalOverlay.addEventListener("click", (e) => { if (e.target === modalOverlay) closeModal(); });
deleteOverlay.addEventListener("click", (e) => { if (e.target === deleteOverlay) closeDeleteModal(); });

// ── Save ──────────────────────────────────────────────────────────────
tenderForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  formError.classList.add("hidden");
  const companyId = companySelect.value;
  if (!companyId) return;

  const id = tenderIdInput.value;

  const body = {
    tender_number:      Number(numberInput.value),
    tender_year:        Number(yearInput.value),
    public_body_name:   bodyInput.value.trim(),
    object_description: descInput.value.trim(),
    modality:           modalitySelect.value,
    format:             formatSelect.value,
    session_date:       new Date(sessionDateInput.value).toISOString(),
  };

  // On update, also include status / result / awarded
  if (id) {
    body.status               = statusSelect.value;
    body.participation_result = resultSelect.value;
    const awarded = parseFloat(awardedInput.value);
    if (!isNaN(awarded)) body.awarded_value = awarded;
  }

  btnSave.disabled = true;
  btnSave.innerHTML = '<span class="spinner"></span> Salvando...';

  const resp = id
    ? await apiFetch(`/companies/${companyId}/tenders/${id}`, { method: "PATCH", body: JSON.stringify(body) })
    : await apiFetch(`/companies/${companyId}/tenders/`, { method: "POST", body: JSON.stringify(body) });

  btnSave.disabled = false;
  btnSave.innerHTML = "Salvar";

  if (!resp || !resp.ok) {
    const err = await resp?.json().catch(() => ({}));
    formError.textContent = err?.detail ?? "Ocorreu um erro. Tente novamente.";
    formError.classList.remove("hidden");
    return;
  }

  closeModal();
  loadTenders(companyId);
});

// ── Delete ────────────────────────────────────────────────────────────
btnConfirmDel.addEventListener("click", async () => {
  const companyId = companySelect.value;
  if (!pendingDeleteId || !companyId) return;

  btnConfirmDel.disabled = true;
  btnConfirmDel.innerHTML = '<span class="spinner"></span>';

  const resp = await apiFetch(`/companies/${companyId}/tenders/${pendingDeleteId}`, { method: "DELETE" });

  btnConfirmDel.disabled = false;
  btnConfirmDel.innerHTML = "Excluir";

  if (resp && resp.ok) {
    closeDeleteModal();
    loadTenders(companyId);
  }
});

// ── Init ──────────────────────────────────────────────────────────────
loadCompanies();
