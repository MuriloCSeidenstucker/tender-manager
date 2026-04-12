import { apiFetch, isAuthenticated, logout } from "./api.js";

if (!isAuthenticated()) {
  window.location.href = "/frontend/index.html";
}

// ── DOM refs ──────────────────────────────────────────────────────────
const usernameEl      = document.getElementById("username-display");
const emailEl         = document.getElementById("email-display");
const userInitialEl   = document.getElementById("user-initial");
const logoutBtn       = document.getElementById("logout-btn");

// Profile form
const profileForm     = document.getElementById("profile-form");
const usernameInput   = document.getElementById("profile-username");
const emailInput      = document.getElementById("profile-email");
const profileError    = document.getElementById("profile-error");
const profileSuccess  = document.getElementById("profile-success");
const btnSaveProfile  = document.getElementById("btn-save-profile");

// Password form
const passwordForm    = document.getElementById("password-form");
const currentPassInput = document.getElementById("current-password");
const newPassInput    = document.getElementById("new-password");
const confirmPassInput = document.getElementById("confirm-password");
const passwordError   = document.getElementById("password-error");
const passwordSuccess = document.getElementById("password-success");
const btnSavePassword = document.getElementById("btn-save-password");

// Delete account
const btnDeleteAccount = document.getElementById("btn-delete-account");
const deleteOverlay    = document.getElementById("delete-overlay");
const deleteModalClose = document.getElementById("delete-modal-close");
const btnCancelDelete  = document.getElementById("btn-cancel-delete");
const btnConfirmDelete = document.getElementById("btn-confirm-delete");

logoutBtn.addEventListener("click", logout);

// ── Helpers ───────────────────────────────────────────────────────────
function showMsg(el, text) {
  el.textContent = text;
  el.classList.remove("hidden");
  setTimeout(() => el.classList.add("hidden"), 4000);
}

function setLoading(btn, loading, defaultText) {
  btn.disabled = loading;
  btn.innerHTML = loading ? '<span class="spinner"></span>' : defaultText;
}

// ── Load current user from JWT + /users/ ─────────────────────────────
let currentUserId = null;

async function loadCurrentUser() {
  // Decode user id and email from JWT payload
  const token = localStorage.getItem("access_token");
  if (!token) return;

  let email = "";
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    email = payload.sub || "";
  } catch (_) { /* ignore */ }

  // Fetch full user list and find ours by email
  const resp = await apiFetch("/users/?limit=200");
  if (!resp) return;
  const data = await resp.json();
  const me = (data.users ?? []).find((u) => u.email === email);

  if (!me) return;

  currentUserId = me.id;

  // Populate sidebar
  if (usernameEl) usernameEl.textContent = me.username;
  if (emailEl)    emailEl.textContent    = me.email;
  if (userInitialEl) userInitialEl.textContent = me.username[0]?.toUpperCase() || "U";

  // Pre-fill form
  usernameInput.value = me.username;
  emailInput.value    = me.email;
}

// ── Update profile ────────────────────────────────────────────────────
profileForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  profileError.classList.add("hidden");
  profileSuccess.classList.add("hidden");

  if (!currentUserId) return;

  const body = {};
  const newUsername = usernameInput.value.trim();
  const newEmail    = emailInput.value.trim();

  // Only include changed fields (PATCH partial update)
  if (newUsername) body.username = newUsername;
  if (newEmail)    body.email    = newEmail;

  if (Object.keys(body).length === 0) return;

  setLoading(btnSaveProfile, true, "Salvar alterações");

  const resp = await apiFetch(`/users/${currentUserId}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });

  setLoading(btnSaveProfile, false, "Salvar alterações");

  if (!resp || !resp.ok) {
    const err = await resp?.json().catch(() => ({}));
    showMsg(profileError, err?.detail ?? "Erro ao atualizar os dados.");
    return;
  }

  const updated = await resp.json();

  // Sync sidebar display
  if (usernameEl) usernameEl.textContent = updated.username;
  if (emailEl)    emailEl.textContent    = updated.email;
  if (userInitialEl) userInitialEl.textContent = updated.username[0]?.toUpperCase() || "U";

  usernameInput.value = updated.username;
  emailInput.value    = updated.email;

  showMsg(profileSuccess, "Dados atualizados com sucesso!");
});

// ── Change password ───────────────────────────────────────────────────
passwordForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  passwordError.classList.add("hidden");
  passwordSuccess.classList.add("hidden");

  if (!currentUserId) return;

  const current = currentPassInput.value;
  const newPass  = newPassInput.value;
  const confirm  = confirmPassInput.value;

  if (newPass !== confirm) {
    showMsg(passwordError, "A nova senha e a confirmação não coincidem.");
    return;
  }

  if (newPass.length < 6) {
    showMsg(passwordError, "A nova senha deve ter pelo menos 6 caracteres.");
    return;
  }

  setLoading(btnSavePassword, true, "Alterar senha");

  const resp = await apiFetch(`/users/${currentUserId}/password`, {
    method: "PATCH",
    body: JSON.stringify({ current_password: current, new_password: newPass }),
  });

  setLoading(btnSavePassword, false, "Alterar senha");

  if (!resp || !resp.ok) {
    const err = await resp?.json().catch(() => ({}));
    showMsg(passwordError, err?.detail ?? "Erro ao alterar a senha.");
    return;
  }

  passwordForm.reset();
  showMsg(passwordSuccess, "Senha alterada com sucesso!");
});

// ── Delete account ────────────────────────────────────────────────────
btnDeleteAccount.addEventListener("click", () => {
  deleteOverlay.classList.remove("hidden");
});

function closeDeleteModal() {
  deleteOverlay.classList.add("hidden");
}

deleteModalClose.addEventListener("click", closeDeleteModal);
btnCancelDelete.addEventListener("click", closeDeleteModal);
deleteOverlay.addEventListener("click", (e) => {
  if (e.target === deleteOverlay) closeDeleteModal();
});

btnConfirmDelete.addEventListener("click", async () => {
  if (!currentUserId) return;

  setLoading(btnConfirmDelete, true, "Sim, excluir minha conta");

  const resp = await apiFetch(`/users/${currentUserId}`, { method: "DELETE" });

  if (resp && resp.ok) {
    localStorage.removeItem("access_token");
    window.location.href = "/frontend/index.html";
  } else {
    setLoading(btnConfirmDelete, false, "Sim, excluir minha conta");
    closeDeleteModal();
  }
});

// ── Init ──────────────────────────────────────────────────────────────
loadCurrentUser();
