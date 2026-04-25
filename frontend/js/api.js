const API_BASE = "/api";

const ERROR_MAPPINGS = {
  // Auth
  "Incorrect email or password": "E-mail ou senha incorretos.",
  "Could not validate credentials": "Sessão expirada ou inválida. Por favor, faça login novamente.",

  // Users
  "Username already exists": "Este nome de usuário já está sendo usado.",
  "Email already exists": "Este e-mail já está cadastrado.",
  "Username or Email already exists": "Usuário ou e-mail já cadastrado.",
  "Invalid current password": "A senha atual está incorreta.",
  "Not enough permissions": "Você não tem permissão para realizar esta ação.",

  // Companies
  "Company name already exists for this user.": "Já existe uma empresa com este nome cadastrada para você.",
  "Company name or CNPJ already exists for this user.": "Já existe uma empresa com este nome ou CNPJ cadastrada para você.",
  "Company not found.": "Empresa não encontrada.",
  "A company with these details already exists or database integrity error.": "Uma empresa com estes dados já existe ou houve um erro de integridade.",
  "Cannot delete company. It may have associated records such as tenders.": "Não é possível excluir esta empresa pois ela possui licitações vinculadas.",

  // Tenders
  "Tender not found.": "Licitação não encontrada.",
  "A tender with these details is already registered for this company.": "Uma licitação com estes dados já está cadastrada para esta empresa.",
  "Database integrity error.": "Ocorreu um erro de integridade no banco de dados.",
  "Cannot delete tender due to database integrity constraints.": "Não é possível excluir esta licitação pois ela possui registros vinculados.",

  // Business Rules (Tenders)
  "Awarded value must be zero when participation result is LOST.": "O valor adjudicado deve ser zero quando o resultado for Perdeu.",
  "Awarded value must be greater than zero when participation result is WON.": "O valor adjudicado deve ser maior que zero quando o resultado for Ganhou.",
};

const FIELD_LABELS = {
  username: "Usuário/E-mail",
  email: "E-mail",
  password: "Senha",
  current_password: "Senha atual",
  new_password: "Nova senha",
  name: "Razão Social",
  trade_name: "Nome Fantasia",
  cnpj: "CNPJ",
  tender_number: "Número",
  tender_year: "Ano",
  public_body_name: "Órgão Público",
  object_description: "Objeto",
  modality: "Modalidade",
  format: "Formato",
  status: "Status",
  participation_result: "Resultado",
  awarded_value: "Valor Adjudicado",
  session_date: "Data da Sessão",
};

const STATUSES = {
  "monitoring": "Monitoramento",
  "analysis": "Análise",
  "approved": "Aprovado",
  "rejected": "Rejeitado",
  "registered": "Cadastrado",
  "in_progress": "Em andamento",
  "appeal": "Recurso",
  "finished": "Finalizado",
  "suspended": "Suspenso",
  "canceled": "Cancelado",
}

export async function parseErrorResponse(resp) {
  if (!resp) return "Erro de conexão com o servidor.";

  let data;
  try {
    data = await resp.json();
  } catch (e) {
    return `Erro inesperado (${resp.status}): ${resp.statusText}`;
  }

  const detail = data?.detail;

  // Case 1: Validation Error (FastAPI 422)
  if (Array.isArray(detail)) {
    return detail
      .map((err) => {
        const field = err.loc[err.loc.length - 1];
        const label = FIELD_LABELS[field] || field;
        let msg = err.msg;

        if (msg.toLowerCase() === "field required") msg = "é obrigatório";
        else if (msg.toLowerCase().includes("value is not a valid email")) msg = "deve ser um e-mail válido";
        else if (msg.toLowerCase().includes("should be greater than 0")) msg = "deve ser maior que 0";
        else if (msg.toLowerCase().includes("should have at least")) {
          const limit = msg.match(/\d+/)?.[0];
          msg = `deve ter pelo menos ${limit} caracteres`;
        }

        return `O campo "${label}" ${msg}.`;
      })
      .join("\n");
  }

  // Case 2: String Detail (Custom HTTPException)
  if (typeof detail === "string") {
    // Check if we have a direct mapping
    if (ERROR_MAPPINGS[detail]) return ERROR_MAPPINGS[detail];

    // Business rule error with dynamic status value
    if (detail.startsWith("Value cannot be greater than zero for status:")) {
      const status = STATUSES[detail.split("for status:")[1].trim()];
      return "O valor adjudicado não pode ser maior que zero para o status selecionado: " + status + ".";
    }

    return detail;
  }

  return "Ocorreu um erro inesperado. Tente novamente.";
}

export async function apiFetch(path, options = {}) {
  const token = localStorage.getItem("access_token");

  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (response.status === 401) {
    localStorage.removeItem("access_token");
    window.location.href = "/index.html";
    return;
  }

  return response;
}

export function isAuthenticated() {
  return !!localStorage.getItem("access_token");
}

export function logout() {
  localStorage.removeItem("access_token");
  window.location.href = "/index.html";
}
