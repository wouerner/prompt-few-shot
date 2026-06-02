// Base API URL (absolute path on same origin)
const API_BASE = '/api/v1';

// Global state
let employees = [];
let vacations = [];

// ==========================================
// INITIALIZATION
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    // Setup Navigation Tabs
    setupTabs();
    
    // Fetch initial data
    fetchEmployees();
    fetchVacations();
    
    // Set default prompt selection in dropdown
    document.getElementById('prompt-input-select').value = '1';
    usePredefinedPrompt();
});

// ==========================================
// TABS & UI NAVIGATION
// ==========================================
function setupTabs() {
    const tabs = document.querySelectorAll('.nav-tab');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active classes
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => {
                c.classList.remove('active');
                c.style.opacity = '0';
                c.style.transform = 'translateY(10px)';
            });

            // Add active class to clicked tab
            tab.classList.add('active');
            const targetId = tab.getAttribute('data-tab');
            const targetContent = document.getElementById(targetId);
            
            targetContent.classList.add('active');
            // Trigger animation frame for transition
            setTimeout(() => {
                targetContent.style.opacity = '1';
                targetContent.style.transform = 'translateY(0)';
            }, 50);
        });
    });
}

// ==========================================
// DATA FETCHING & RENDERING (API)
// ==========================================
async function fetchEmployees() {
    try {
        const res = await fetch(`${API_BASE}/employees`);
        if (!res.ok) throw new Error("Erro ao carregar funcionários");
        employees = await res.json();
        
        renderEmployeesTable();
        populateEmployeeSelects();
    } catch (err) {
        console.error(err);
    }
}

async function fetchVacations() {
    try {
        const res = await fetch(`${API_BASE}/vacations`);
        if (!res.ok) throw new Error("Erro ao carregar férias");
        vacations = await res.json();
        
        renderVacationsTable();
    } catch (err) {
        console.error(err);
    }
}

function renderEmployeesTable() {
    const tbody = document.getElementById('employees-tbody');
    tbody.innerHTML = '';

    if (employees.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">Nenhum funcionário cadastrado.</td></tr>`;
        return;
    }

    employees.forEach(emp => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><span class="badge badge-purple">#${emp.id}</span></td>
            <td>
                <span class="emp-name-tag">${emp.name}</span>
            </td>
            <td>${emp.role}</td>
            <td>${emp.hire_date}</td>
            <td>
                <span class="badge badge-purple">${emp.vacation_days_left} / ${emp.total_vacation_days} dias</span>
            </td>
            <td>
                <button class="btn-icon-only btn-danger-action" onclick="deleteEmployee(${emp.id})" title="Excluir funcionário">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function renderVacationsTable() {
    const tbody = document.getElementById('vacations-tbody');
    tbody.innerHTML = '';

    if (vacations.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">Nenhuma solicitação de férias registrada.</td></tr>`;
        return;
    }

    vacations.forEach(vac => {
        const employee = employees.find(e => e.id === vac.employee_id);
        const employeeName = employee ? employee.name : `Funcionário #${vac.employee_id}`;
        
        // Status Badge styling
        let statusBadge = '';
        if (vac.status === 'APPROVED') {
            statusBadge = `<span class="badge badge-success"><i class="fa-solid fa-circle-check"></i> Aprovado</span>`;
        } else if (vac.status === 'PENDING') {
            statusBadge = `<span class="badge badge-pending"><i class="fa-solid fa-clock"></i> Pendente</span>`;
        } else {
            statusBadge = `<span class="badge badge-danger"><i class="fa-solid fa-circle-xmark"></i> Rejeitado</span>`;
        }

        // Actions
        let actionButtons = '';
        if (vac.status === 'PENDING') {
            actionButtons = `
                <div class="actions-cell">
                    <button class="btn-icon-only btn-success-action" onclick="updateVacationStatus(${vac.id}, 'APPROVED')" title="Aprovar">
                        <i class="fa-solid fa-check"></i>
                    </button>
                    <button class="btn-icon-only btn-danger-action" onclick="updateVacationStatus(${vac.id}, 'REJECTED')" title="Rejeitar">
                        <i class="fa-solid fa-xmark"></i>
                    </button>
                </div>
            `;
        } else {
            actionButtons = `
                <button class="btn-icon-only btn-danger-action" onclick="deleteVacation(${vac.id})" title="Excluir solicitação e restaurar dias">
                    <i class="fa-solid fa-trash"></i>
                </button>
            `;
        }

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><span class="badge badge-purple">#${vac.id}</span></td>
            <td>
                <span class="emp-name-tag">${employeeName}</span>
            </td>
            <td>${vac.start_date} até ${vac.end_date}</td>
            <td><strong>${vac.days}</strong> dias</td>
            <td>${statusBadge}</td>
            <td>${actionButtons}</td>
        `;
        tbody.appendChild(tr);
    });
}

function populateEmployeeSelects() {
    const select = document.getElementById('vac-employee-id');
    select.innerHTML = '<option value="" disabled selected>Escolha um funcionário...</option>';
    
    employees.forEach(emp => {
        const opt = document.createElement('option');
        opt.value = emp.id;
        opt.textContent = `${emp.name} (ID: ${emp.id} | Saldo: ${emp.vacation_days_left} dias)`;
        select.appendChild(opt);
    });
}

// ==========================================
// FORM SUBMISSIONS & CRUD
// ==========================================
async function submitEmployeeForm(event) {
    event.preventDefault();
    
    const name = document.getElementById('emp-name').value;
    const role = document.getElementById('emp-role').value;
    const hire_date = document.getElementById('emp-hire-date').value;
    const total_vacation_days = parseInt(document.getElementById('emp-vacation-days').value);
    
    try {
        const res = await fetch(`${API_BASE}/employees`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, role, hire_date, total_vacation_days })
        });
        
        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || "Erro ao cadastrar funcionário");
        }
        
        closeModal('employee-modal');
        document.getElementById('employee-form').reset();
        
        await fetchEmployees();
    } catch (err) {
        alert(err.message);
    }
}

async function submitVacationForm(event) {
    event.preventDefault();
    
    const employee_id = parseInt(document.getElementById('vac-employee-id').value);
    const start_date = document.getElementById('vac-start-date').value;
    const end_date = document.getElementById('vac-end-date').value;
    
    const errBox = document.getElementById('vacation-error');
    errBox.style.display = 'none';
    
    try {
        const res = await fetch(`${API_BASE}/vacations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ employee_id, start_date, end_date })
        });
        
        if (!res.ok) {
            const errData = await res.json();
            let errMsg = errData.detail;
            if (Array.isArray(errMsg)) {
                errMsg = errMsg.map(e => e.msg).join("<br>");
            }
            throw new Error(errMsg || "Erro ao registrar solicitação de férias");
        }
        
        closeModal('vacation-modal');
        document.getElementById('vacation-form').reset();
        
        await fetchVacations();
        await fetchEmployees(); // Recalculates available days
    } catch (err) {
        errBox.innerHTML = err.message;
        errBox.style.display = 'block';
    }
}

async function updateVacationStatus(id, newStatus) {
    try {
        const res = await fetch(`${API_BASE}/vacations/${id}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        
        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || "Erro ao atualizar status");
        }
        
        await fetchVacations();
        await fetchEmployees();
    } catch (err) {
        alert(err.message);
    }
}

async function deleteEmployee(id) {
    if (!confirm("Tem certeza que deseja excluir este funcionário? Isso removerá todas as suas solicitações de férias associadas!")) return;
    
    try {
        const res = await fetch(`${API_BASE}/employees/${id}`, {
            method: 'DELETE'
        });
        
        if (!res.ok) throw new Error("Erro ao excluir funcionário");
        
        await fetchEmployees();
        await fetchVacations();
    } catch (err) {
        alert(err.message);
    }
}

async function deleteVacation(id) {
    if (!confirm("Tem certeza que deseja cancelar esta solicitação de férias?")) return;
    
    try {
        const res = await fetch(`${API_BASE}/vacations/${id}`, {
            method: 'DELETE'
        });
        
        if (!res.ok) throw new Error("Erro ao cancelar solicitação");
        
        await fetchVacations();
        await fetchEmployees();
    } catch (err) {
        alert(err.message);
    }
}

// ==========================================
// MODAL WORKFLOWS
// ==========================================
function openModal(id) {
    document.getElementById(id).classList.add('active');
    
    // Set default dates to today for ease of testing
    if (id === 'vacation-modal') {
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('vac-start-date').min = today;
        document.getElementById('vac-end-date').min = today;
    } else if (id === 'employee-modal') {
        document.getElementById('emp-hire-date').value = new Date().toISOString().split('T')[0];
    }
}

function closeModal(id) {
    document.getElementById(id).classList.remove('active');
    if (id === 'vacation-modal') {
        document.getElementById('vacation-error').style.display = 'none';
    }
}

// ==========================================
// FEW-SHOT PROMPT GENERATION ENGINE
// ==========================================
function usePredefinedPrompt() {
    const select = document.getElementById('prompt-input-select');
    const customInput = document.getElementById('prompt-custom-input');
    
    if (select.value === 'custom') {
        customInput.value = '';
        customInput.focus();
    } else {
        const selectedOption = select.options[select.selectedIndex];
        customInput.value = selectedOption.textContent;
    }
}

// Construct the ultimate few-shot prompt template
function generateFewShotPrompt() {
    const input = document.getElementById('prompt-custom-input').value.trim();
    if (!input) {
        alert("Por favor, selecione ou digite um comando primeiro!");
        return;
    }
    
    const systemInstruction = 
`Você é um assistente de inteligência artificial ultra-especializado em traduzir solicitações em linguagem natural de usuários em chamadas REST exatas para a nossa API de Gerenciamento de Férias.

Regras de Saída:
1. Responda APENAS com um objeto JSON estruturado contendo as chaves: "method" (método HTTP), "url" (endpoint relativo) e opcionalmente "body" (objeto JSON de payload).
2. Não inclua nenhuma introdução, explicação ou bloco de código em markdown extra.`;

    const apiDocumentation = 
`DOCUMENTAÇÃO DE ENDPOINTS DISPONÍVEIS:
1. Listar funcionários:
   - Método: GET
   - Rota: /api/v1/employees
2. Cadastrar novo funcionário:
   - Método: POST
   - Rota: /api/v1/employees
   - Payload: { "name": "string", "role": "string", "hire_date": "AAAA-MM-DD", "total_vacation_days": 30 }
3. Solicitar férias:
   - Método: POST
   - Rota: /api/v1/vacations
   - Payload: { "employee_id": 1, "start_date": "AAAA-MM-DD", "end_date": "AAAA-MM-DD" }
4. Aprovar ou Rejeitar solicitação de férias:
   - Método: PATCH
   - Rota: /api/v1/vacations/{vacation_id}/status
   - Payload: { "status": "APPROVED" | "REJECTED" }`;

    const fewShotExamples = 
`EXEMPLOS DE PROCESSAMENTO (FEW-SHOT):

---
Entrada: Quero cadastrar um novo funcionário chamado Roberto Alves contratado em 2024-05-15 como Product Manager
Saída:
{
  "method": "POST",
  "url": "/api/v1/employees",
  "body": {
    "name": "Roberto Alves",
    "role": "Product Manager",
    "hire_date": "2024-05-15",
    "total_vacation_days": 30
  }
}

---
Entrada: Registrar uma solicitação de férias para a funcionária de ID 2 iniciando em 2026-12-01 e terminando em 2026-12-15
Saída:
{
  "method": "POST",
  "url": "/api/v1/vacations",
  "body": {
    "employee_id": 2,
    "start_date": "2026-12-01",
    "end_date": "2026-12-15"
  }
}

---
Entrada: Aprovar a solicitação de férias de ID número 7 imediatamente
Saída:
{
  "method": "PATCH",
  "url": "/api/v1/vacations/7/status",
  "body": {
    "status": "APPROVED"
  }
}`;

    const promptOutput = 
`${systemInstruction}

==================================================
${apiDocumentation}

==================================================
${fewShotExamples}

==================================================
SUA VEZ DE PROCESSAR:
Entrada: ${input}
Saída:`;

    document.getElementById('few-shot-prompt-code').textContent = promptOutput;
    
    // Highlight the card header or visual cue
    const outCard = document.getElementById('output-prompt-card');
    outCard.style.boxShadow = '0 0 25px rgba(139, 92, 246, 0.4)';
    setTimeout(() => {
        outCard.style.boxShadow = 'var(--shadow-premium)';
    }, 1500);

    // Reset simulation block
    document.getElementById('simulation-output-raw').textContent = 'Pronto para simulação...';
    document.getElementById('simulation-execution-result').textContent = 'Aguardando execução...';
}

function copyPromptToClipboard() {
    const code = document.getElementById('few-shot-prompt-code').textContent;
    if (code.includes('Clique em "Gerar Prompt Few-Shot"')) {
        alert("Gere um prompt primeiro!");
        return;
    }
    navigator.clipboard.writeText(code).then(() => {
        const btn = document.getElementById('btn-copy-prompt');
        const oldHtml = btn.innerHTML;
        btn.innerHTML = `<i class="fa-solid fa-check"></i> Copiado!`;
        btn.style.background = 'var(--color-success-bg)';
        btn.style.color = 'var(--color-success)';
        
        setTimeout(() => {
            btn.innerHTML = oldHtml;
            btn.style.background = '';
            btn.style.color = '';
        }, 2000);
    });
}

// ==========================================
// EMBEDDED AI SIMULATOR & EXECUTION
// ==========================================
function simulateLLMResponse() {
    const promptText = document.getElementById('few-shot-prompt-code').textContent;
    if (promptText.includes('Clique em "Gerar Prompt"')) {
        alert("Por favor, gere o prompt few-shot primeiro!");
        return;
    }
    
    const userInput = document.getElementById('prompt-custom-input').value.trim();
    
    // Run an intelligent parser simulating standard LLM reasoning based on our Few-Shot examples
    const result = parseInputNLP(userInput);
    
    // Output simulated LLM response
    const outputCodeElement = document.getElementById('simulation-output-raw');
    outputCodeElement.textContent = JSON.stringify(result, null, 2);
    
    // Execute call against real API
    executeSimulatedCall(result);
}

// Smart local parsing engine mimicking LLM output for our specific vacation model
function parseInputNLP(text) {
    const lowercase = text.toLowerCase();
    
    // 1. Check for Employee Registration
    if (lowercase.includes('cadastrar') || lowercase.includes('criar') || lowercase.includes('adicionar') || lowercase.includes('novo funcionário')) {
        // Attempt to extract Name
        let name = "Ana Souza"; // default fallback matching seed data option
        const nameMatch = text.match(/(?:chamada|chamado|nome)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/);
        if (nameMatch) {
            name = nameMatch[1];
        } else {
            // regex for Ana Souza or others
            const candidate = text.match(/(?:funcionária|funcionário)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)/);
            if (candidate) name = candidate[1];
        }

        // Attempt to extract Role
        let role = "Engenheira de Software";
        const roleMatch = text.match(/(?:como|cargo de)\s+([A-Za-zÀ-ÿ\s]+?)(?:\s+contratada|\s+contratado|\s+em|\s+com|\.|$)/i);
        if (roleMatch) {
            role = roleMatch[1].trim();
        }

        // Attempt to extract Hire Date (YYYY-MM-DD)
        let hireDate = new Date().toISOString().split('T')[0];
        const dateMatch = text.match(/\d{4}-\d{2}-\d{2}/);
        if (dateMatch) {
            hireDate = dateMatch[0];
        }

        return {
            method: "POST",
            url: "/api/v1/employees",
            body: {
                name: name,
                role: role,
                hire_date: hireDate,
                total_vacation_days: 30
            }
        };
    }
    
    // 2. Check for Vacation Requests (POST)
    if (lowercase.includes('férias') && (lowercase.includes('solicitar') || lowercase.includes('registrar') || lowercase.includes('pedir') || lowercase.includes('de'))) {
        // Extract employee ID
        let empId = 1;
        const idMatch = text.match(/(?:id|número)\s+(\d+)/i);
        if (idMatch) {
            empId = parseInt(idMatch[1]);
        } else {
            // Find by name if possible in local database
            const nameWords = ["joão", "maria", "carlos"];
            for (let word of nameWords) {
                if (lowercase.includes(word)) {
                    const matchEmp = employees.find(e => e.name.toLowerCase().includes(word));
                    if (matchEmp) empId = matchEmp.id;
                }
            }
        }

        // Extract dates (find YYYY-MM-DD or parse relative text)
        let startDate = "2026-12-25";
        let endDate = "2027-01-05";
        
        const dates = text.match(/\d{4}-\d{2}-\d{2}/g);
        if (dates && dates.length >= 2) {
            startDate = dates[0];
            endDate = dates[1];
        } else {
            // Search other common pattern like "25 de Dezembro de 2026"
            // For simplicity, if standard test strings are used, we map them
            if (lowercase.includes("25 de dezembro") && lowercase.includes("2026")) {
                startDate = "2026-12-25";
            }
            if (lowercase.includes("5 de janeiro") && lowercase.includes("2027")) {
                endDate = "2027-01-05";
            }
        }

        return {
            method: "POST",
            url: "/api/v1/vacations",
            body: {
                employee_id: empId,
                start_date: startDate,
                end_date: endDate
            }
        };
    }

    // 3. Check for Approval/Rejection (PATCH)
    if (lowercase.includes('aprovar') || lowercase.includes('aceitar') || lowercase.includes('recusar') || lowercase.includes('rejeitar')) {
        let vacId = 2; // fallback
        const idMatch = text.match(/(?:id|número)\s+(\d+)/i);
        if (idMatch) {
            vacId = parseInt(idMatch[1]);
        }

        const isApprove = lowercase.includes('aprovar') || lowercase.includes('aceitar');
        return {
            method: "PATCH",
            url: `/api/v1/vacations/${vacId}/status`,
            body: {
                status: isApprove ? "APPROVED" : "REJECTED"
            }
        };
    }

    // 4. Check for List (GET)
    if (lowercase.includes('listar') || lowercase.includes('ver') || lowercase.includes('mostrar') || lowercase.includes('buscar')) {
        return {
            method: "GET",
            url: "/api/v1/employees"
        };
    }

    // Default fallback (Unknown query)
    return {
        error: "Não foi possível reconhecer o comando na nossa base Few-Shot local. Tente reescrever no formato dos exemplos."
    };
}

async function executeSimulatedCall(simResult) {
    const resultElement = document.getElementById('simulation-execution-result');
    resultElement.textContent = 'Enviando chamada de API...';
    
    if (simResult.error) {
        resultElement.textContent = `Falha na Simulação:\n${simResult.error}`;
        resultElement.style.color = 'var(--color-danger)';
        return;
    }

    const { method, url, body } = simResult;
    
    try {
        const fetchOptions = {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        if (body) {
            fetchOptions.body = JSON.stringify(body);
        }

        const res = await fetch(url, fetchOptions);
        
        if (res.status === 204) {
            resultElement.textContent = `Status: 204 No Content\n\nChamada executada com sucesso!`;
            resultElement.style.color = 'var(--color-success)';
        } else {
            const data = await res.json();
            resultElement.textContent = `Status: ${res.status} ${res.statusText}\n\n${JSON.stringify(data, null, 2)}`;
            if (res.ok) {
                resultElement.style.color = 'var(--color-success)';
            } else {
                resultElement.style.color = 'var(--color-danger)';
            }
        }
        
        // Refresh dashboard tables automatically
        await fetchEmployees();
        await fetchVacations();
        
    } catch (err) {
        resultElement.textContent = `Erro de Conexão:\n${err.message}`;
        resultElement.style.color = 'var(--color-danger)';
    }
}
