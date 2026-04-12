import { isAuthenticated } from "./api.js";

if (isAuthenticated()) {
  window.location.href = "/frontend/dashboard.html";
}

const API_BASE = "http://localhost:8000";

// ── Tab switching ─────────────────────────────────────────────────────
const tabLogin    = document.getElementById("tab-login");
const tabRegister = document.getElementById("tab-register");
const panelLogin  = document.getElementById("panel-login");
const panelReg    = document.getElementById("panel-register");

function showLogin() {
  panelLogin.classList.remove("hidden");
  panelReg.classList.add("hidden");
  tabLogin.classList.add("active");
  tabLogin.setAttribute("aria-selected", "true");
  tabRegister.classList.remove("active");
  tabRegister.setAttribute("aria-selected", "false");
  document.getElementById("login-email").focus();
}

function showRegister() {
  panelReg.classList.remove("hidden");
  panelLogin.classList.add("hidden");
  tabRegister.classList.add("active");
  tabRegister.setAttribute("aria-selected", "true");
  tabLogin.classList.remove("active");
  tabLogin.setAttribute("aria-selected", "false");
  document.getElementById("reg-username").focus();
}

tabLogin.addEventListener("click", showLogin);
tabRegister.addEventListener("click", showRegister);

// ── Login ─────────────────────────────────────────────────────────────
const loginForm  = document.getElementById("login-form");
const loginEmail = document.getElementById("login-email");
const loginPass  = document.getElementById("login-password");
const loginBtn   = document.getElementById("login-submit-btn");
const loginError = document.getElementById("login-error");

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  loginError.classList.add("hidden");
  loginBtn.disabled = true;
  loginBtn.innerHTML = '<span class="spinner"></span> Entrando...';

  const body = new URLSearchParams({
    username: loginEmail.value,
    password: loginPass.value,
  });

  try {
    const response = await fetch(`${API_BASE}/auth/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err?.detail ?? "Credenciais inválidas. Verifique seu e-mail e senha.");
    }

    const data = await response.json();
    localStorage.setItem("access_token", data.access_token);
    window.location.href = "/frontend/dashboard.html";
  } catch (err) {
    loginError.textContent = err.message;
    loginError.classList.remove("hidden");
    loginBtn.disabled = false;
    loginBtn.innerHTML = "Entrar";
  }
});

// ── Register ──────────────────────────────────────────────────────────
const regForm    = document.getElementById("register-form");
const regUser    = document.getElementById("reg-username");
const regEmail   = document.getElementById("reg-email");
const regPass    = document.getElementById("reg-password");
const regBtn     = document.getElementById("register-submit-btn");
const regError   = document.getElementById("register-error");
const regSuccess = document.getElementById("register-success");

regForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  regError.classList.add("hidden");
  regSuccess.classList.add("hidden");
  regBtn.disabled = true;
  regBtn.innerHTML = '<span class="spinner"></span> Criando conta...';

  try {
    // 1. Create account
    const createResp = await fetch(`${API_BASE}/users/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: regUser.value.trim(),
        email: regEmail.value.trim(),
        password: regPass.value,
      }),
    });

    if (!createResp.ok) {
      const err = await createResp.json().catch(() => ({}));
      throw new Error(err?.detail ?? "Erro ao criar conta. Tente novamente.");
    }

    // 2. Show success briefly
    regSuccess.classList.remove("hidden");
    regBtn.innerHTML = "Conta criada!";

    // 3. Auto-login with the new credentials
    const loginBody = new URLSearchParams({
      username: regEmail.value.trim(),
      password: regPass.value,
    });

    const tokenResp = await fetch(`${API_BASE}/auth/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: loginBody,
    });

    if (!tokenResp.ok) {
      // Account created but login failed — redirect to login tab
      regForm.reset();
      showLogin();
      return;
    }

    const tokenData = await tokenResp.json();
    localStorage.setItem("access_token", tokenData.access_token);

    setTimeout(() => {
      window.location.href = "/frontend/dashboard.html";
    }, 800);
  } catch (err) {
    regError.textContent = err.message;
    regError.classList.remove("hidden");
    regBtn.disabled = false;
    regBtn.innerHTML = "Criar conta";
  }
});
