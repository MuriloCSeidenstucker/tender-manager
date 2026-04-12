import { isAuthenticated } from "./api.js";

if (isAuthenticated()) {
  window.location.href = "/frontend/dashboard.html";
}

const form = document.getElementById("login-form");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const submitBtn = document.getElementById("submit-btn");
const errorMsg = document.getElementById("error-msg");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  errorMsg.classList.add("hidden");
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="spinner"></span> Entrando...';

  const body = new URLSearchParams({
    username: emailInput.value,
    password: passwordInput.value,
  });

  try {
    const response = await fetch("http://localhost:8000/auth/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });

    if (!response.ok) {
      throw new Error("Credenciais inválidas. Verifique seu e-mail e senha.");
    }

    const data = await response.json();
    localStorage.setItem("access_token", data.access_token);
    window.location.href = "/frontend/dashboard.html";
  } catch (err) {
    errorMsg.textContent = err.message;
    errorMsg.classList.remove("hidden");
    submitBtn.disabled = false;
    submitBtn.innerHTML = "Entrar";
  }
});
