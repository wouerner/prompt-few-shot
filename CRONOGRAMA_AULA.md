# 📅 Cronograma de Aula: Engenharia de Prompt (Few-Shot) e Automação de Testes

Este cronograma foi projetado para guiar uma aula prática, workshop ou treinamento direcionado a **Engenheiros de Software e Engenheiros de QA**. Ele ensina os conceitos de **Few-Shot Prompting** na prática e como aplicar essa mesma técnica para acelerar e padronizar a criação de testes automatizados (unitários com Pytest e de comportamento com Behave/BDD) neste projeto.

---

## 📋 Visão Geral da Aula
- **Duração Total:** 3 horas (180 minutos)
- **Público-alvo:** Engenheiros de software, desenvolvedores backend e profissionais de QA.
- **Pré-requisitos:** Docker & Docker Compose instalados, noções básicas de Python e APIs REST.
- **Objetivos de Aprendizagem:**
  1. Compreender a diferença prática entre *Zero-Shot* e *Few-Shot Prompting*.
  2. Entender a importância de *Schema Enforcement* e interfaces de linguagem natural (NL-to-API).
  3. Aprender a usar a técnica de Few-Shot para guiar IAs Generativas a escreverem novos testes unitários e funcionais no mesmo padrão arquitetural da base de código existente.
  4. Executar testes em containers Docker e analisar métricas no dashboard do Allure Reports.

---

## ⏱️ Linha do Tempo e Conteúdo Programático

| Horário | Módulo | Descrição Detalhada | Arquivos Relacionados |
| :--- | :--- | :--- | :--- |
| **00:00 - 00:30**<br>(30 min) | **1. Arquitetura e Setup do Projeto** | - Introdução à API de Férias e Regras de Negócio.<br>- Análise arquitetural com o Modelo C4 (Contexto e Containers).<br>- Inicialização dos containers Docker.<br>- Exploração dos endpoints via Swagger OpenAPI. | [README.md](file:///home/wouerner/dev/wouerner/prompt-few-shot/README.md)<br>[app/main.py](file:///home/wouerner/dev/wouerner/prompt-few-shot/app/main.py) |
| **00:30 - 01:00**<br>(30 min) | **2. O Conceito de Few-Shot Prompting** | - Teoria: Zero-Shot vs. Few-Shot e In-Context Learning.<br>- Por que Engenheiros de Software usam Few-Shot em produção (Consistência e NL-to-API).<br>- Demonstração interativa do **Prompt Playground** no Dashboard. | [FEW_SHOT_GUIDE.md](file:///home/wouerner/dev/wouerner/prompt-few-shot/FEW_SHOT_GUIDE.md)<br>[app/static/app.js](file:///home/wouerner/dev/wouerner/prompt-few-shot/app/static/app.js) |
| **01:00 - 01:30**<br>(30 min) | **3. Anatomia dos Testes Existentes** | - Detalhamento dos testes de unidade/integração com Pytest.<br>- Detalhamento do BDD com Behave (Gherkin + Steps).<br>- O desafio do isolamento de estado (banco em memória e fixtures/hooks de reset).<br>- Execução da suíte atual dentro do container Docker. | [tests/unit/test_main.py](file:///home/wouerner/dev/wouerner/prompt-few-shot/tests/unit/test_main.py)<br>[tests/bdd/vacation_approval.feature](file:///home/wouerner/dev/wouerner/prompt-few-shot/tests/bdd/vacation_approval.feature)<br>[tests/bdd/steps/vacation_approval_steps.py](file:///home/wouerner/dev/wouerner/prompt-few-shot/tests/bdd/steps/vacation_approval_steps.py) |
| **01:30 - 02:30**<br>(60 min) | **4. Few-Shot Aplicado à Criação de Testes** | - Como estruturar prompts Few-Shot profissionais para gerar código de teste.<br>- Estudo de caso: Prompt Few-Shot para Pytest (FastAPI TestClient).<br>- Estudo de caso: Prompt Few-Shot para Behave BDD (Gherkin + Steps Python). | *Ver Seção Abaixo* |
| **02:30 - 02:50**<br>(20 min) | **5. Laboratório Prático (Mãos na Massa)** | - Exercício: Utilizar os prompts sugeridos em uma LLM comercial (Gemini, ChatGPT, Claude) para criar 2 novos testes e adicioná-los ao projeto.<br>- Rodar e validar os novos testes. | [tests/unit/test_main.py](file:///home/wouerner/dev/wouerner/prompt-few-shot/tests/unit/test_main.py)<br>[tests/bdd/vacation_approval.feature](file:///home/wouerner/dev/wouerner/prompt-few-shot/tests/bdd/vacation_approval.feature) |
| **02:50 - 03:00**<br>(10 min) | **6. Análise de Resultados e Fechamento** | - Geração de relatórios com Allure Reports.<br>- Análise das métricas de sucesso, histórico e gráficos de execução.<br>- Encerramento e boas práticas de Engenharia de Prompt na engenharia corporativa. | [allure-results](file:///home/wouerner/dev/wouerner/prompt-few-shot/allure-results) |

---

## 🛠️ Detalhamento dos Módulos

### 1. Arquitetura e Setup do Projeto (30 min)
Neste bloco inicial, apresente o projeto como um ecossistema real de gerenciamento de férias. 
- **Passo 1:** Rode o ambiente de desenvolvimento completo:
  ```bash
  docker compose up --build
  ```
- **Passo 2:** Acesse o dashboard em [http://localhost:8080/](http://localhost:8080/) para mostrar a interface visual (Funcionários e Férias).
- **Passo 3:** Abra o Swagger UI em [http://localhost:8080/docs](http://localhost:8080/docs) e mostre as rotas REST disponíveis (`/employees` e `/vacations`).

---

### 2. O Conceito de Few-Shot Prompting (30 min)
Discuta a teoria do *In-context Learning*.
- Mostre que enviar apenas uma instrução genérica para uma IA (*Zero-Shot*) para converter linguagem natural em ações do sistema pode corromper dados devido a alucinações (como chaves adicionais, markdown, datas mal formadas).
- Apresente o **Prompt Playground** do Dashboard e como o prompt completo é gerado contendo a instrução de sistema, a documentação dos endpoints e **três pares de exemplos claros de entrada e saída esperados** (*Few-Shot*). Isso força a IA (ou nosso simulador local) a responder estritamente no padrão JSON.

---

### 3. Anatomia dos Testes Existentes (30 min)
Antes de gerar novos testes, os engenheiros precisam compreender o padrão atual.
- **Pytest:** Analise o arquivo [test_main.py](file:///home/wouerner/dev/wouerner/prompt-few-shot/tests/unit/test_main.py). Destaque a fixture `reset_db()` e as funções com padrão AAA (Arrange, Act, Assert).
- **BDD/Behave:** Analise o arquivo [vacation_approval.feature](file:///home/wouerner/dev/wouerner/prompt-few-shot/tests/bdd/vacation_approval.feature) e seus mapeamentos em [vacation_approval_steps.py](file:///home/wouerner/dev/wouerner/prompt-few-shot/tests/bdd/steps/vacation_approval_steps.py).
- **Execução:** Demonstre como executar as suítes no container `app`:
  ```bash
  # Executar Pytest
  docker compose exec app pytest --alluredir=allure-results

  # Executar Behave (BDD)
  docker compose exec app behave -f allure_behave.formatter:AllureFormatter -o allure-results tests/bdd
  ```

---

### 4. Few-Shot Aplicado à Criação de Testes (60 min) 🚀
Este é o núcleo da aula. Explique aos alunos que IAs programam melhor e seguem melhor as convenções de arquitetura da empresa quando fornecemos **exemplos reais (Few-Shot) do nosso repositório**. 

Apresente os dois templates de prompt abaixo para os alunos copiarem e utilizarem em suas IAs.

#### 💡 Template 1: Prompt Few-Shot para Gerar Testes Unitários (Pytest)
Este prompt ensina a LLM a ler o código da nossa API e gerar testes no mesmo padrão do Pytest do projeto.

```markdown
Você é um Engenheiro de QA Sênior e especialista em Python. Sua tarefa é criar novos testes unitários usando o framework Pytest e o TestClient do FastAPI para o arquivo "app/main.py".

Para garantir que os testes sigam o nosso padrão arquitetural exato, use os exemplos Few-Shot abaixo como referência.

==================================================
EXEMPLO FEW-SHOT 1: Testar criação de funcionário com sucesso
Código do Teste:
def test_create_employee_success():
    # Arrange
    payload = {
        "name": "Ana Souza",
        "role": "Designer",
        "hire_date": "2025-01-10",
        "total_vacation_days": 30
    }

    # Act
    response = client.post("/api/v1/employees", json=payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 4
    assert data["name"] == "Ana Souza"
    assert data["vacation_days_left"] == 30
    assert data["vacation_days_taken"] == 0

==================================================
EXEMPLO FEW-SHOT 2: Testar validação de data incorreta ao criar funcionário
Código do Teste:
def test_create_employee_invalid_date():
    # Arrange
    payload = {
        "name": "Ana Souza",
        "role": "Designer",
        "hire_date": "10/01/2025",  # Formato incorreto (deve ser AAAA-MM-DD)
        "total_vacation_days": 30
    }

    # Act
    response = client.post("/api/v1/employees", json=payload)

    # Assert
    assert response.status_code == 422

==================================================
EXEMPLO FEW-SHOT 3: Testar erro de saldo insuficiente ao solicitar férias
Código do Teste:
def test_request_vacation_insufficient_balance():
    # Arrange
    # Funcionário 1 tem apenas 20 dias disponíveis
    payload = {
        "employee_id": 1,
        "start_date": "2026-01-01",
        "end_date": "2026-01-25"  # 25 dias solicitados
    }

    # Act
    response = client.post("/api/v1/vacations", json=payload)

    # Assert
    assert response.status_code == 400
    assert "Saldo insuficiente" in response.json()["detail"]

==================================================
SUA VEZ DE PROCESSAR:
Escreva um teste unitário em Pytest utilizando o TestClient do FastAPI para o seguinte cenário:
"Testar o retorno de erro 404 (Not Found) e a mensagem 'Solicitação de férias não encontrada' ao tentar deletar uma solicitação de férias com ID inexistente (ex: ID 99) na rota DELETE /api/v1/vacations/{vacation_id}."

Regras:
1. Siga estritamente a convenção de nomes, comentários (# Arrange, # Act, # Assert) e asserções dos exemplos.
2. Responda apenas com o código Python do teste solicitado, sem blocos markdown adicionais.
```

---

#### 💡 Template 2: Prompt Few-Shot para Gerar Cenários BDD (Behave + Gherkin)
Este prompt ensina a LLM a gerar novos cenários Gherkin estruturados em português e o código dos Steps correspondentes em Python.

```markdown
Você é um Engenheiro de QA especialista em testes BDD. Sua tarefa é criar novos cenários de testes em linguagem Gherkin (português) e os respectivos Steps em Python usando o framework Behave.

Use os exemplos Few-Shot abaixo que refletem nossa base de código de testes BDD.

==================================================
EXEMPLO FEW-SHOT 1: Cenário BDD e código de Step correspondente
Arquivo .feature:
  Cenário: Solicitação de férias criada com status pendente
    Dado que o empregado de nome "Roberto Santos" possui 30 dias de férias disponíveis
    Quando ele solicita férias de "2026-12-01" a "2026-12-10"
    Então uma nova solicitação de férias deve ser criada com status "PENDING" de 10 dias
    E o saldo de férias disponíveis do empregado deve permanecer 30 dias

Código de Steps associado (.py):
@given('que o empregado de nome "{nome}" possui {dias:d} dias de férias disponíveis')
def step_impl(context, nome, dias):
    response = context.client.get("/api/v1/employees")
    employees = response.json()
    emp = next((e for e in employees if e["name"] == nome), None)
    assert emp is not None, f"Empregado {nome} não encontrado"
    assert emp["vacation_days_left"] == dias
    context.employee_id = emp["id"]

@when('ele solicita férias de "{data_inicio}" a "{data_fim}"')
def step_impl(context, data_inicio, data_fim):
    payload = {
        "employee_id": context.employee_id,
        "start_date": data_inicio,
        "end_date": data_fim
    }
    response = context.client.post("/api/v1/vacations", json=payload)
    context.last_response = response
    if response.status_code == 201:
        context.vacation_id = response.json()["id"]

@then('uma nova solicitação de férias deve ser criada com status "{status}" de {dias:d} dias')
def step_impl(context, status, dias):
    assert context.last_response.status_code == 201
    data = context.last_response.json()
    assert data["status"] == status
    assert data["days"] == dias

==================================================
SUA VEZ DE PROCESSAR:
Escreva um novo cenário BDD em Gherkin (.feature) e os respectivos códigos decorados de steps em Python para o seguinte caso de uso:
"O gestor tenta aprovar uma solicitação de férias pendente, mas o funcionário já gastou seus dias e agora possui saldo insuficiente para cobrir esta solicitação. A aprovação deve falhar com código HTTP 400."

Regras:
1. Mantenha os cenários em português e os steps Python estritamente alinhados com o modelo Few-Shot.
2. Escreva o cenário Gherkin e o arquivo Python correspondente.
```

---

### 5. Laboratório Prático / Mãos na Massa (20 min)
Neste momento, os alunos aplicam os prompts gerados em uma LLM e inserem os resultados no projeto.
- **Atividade 1:** Gerar o teste de exclusão inexistente (Pytest) e inseri-lo no final de `tests/unit/test_main.py`.
- **Atividade 2:** Rodar o teste para comprovar o funcionamento:
  ```bash
  docker compose exec app pytest tests/unit/test_main.py::test_delete_vacation_not_found --alluredir=allure-results
  ```

---

### 6. Análise de Resultados e Fechamento (10 min)
Mostre como analisar o impacto dos novos testes visualmente.
- Abra o Allure Dashboard UI no navegador:
  - **URL:** [http://localhost:5252/allure-docker-service-ui/](http://localhost:5252/allure-docker-service-ui/)
- Explique como o Allure coleta os arquivos `.json` gerados na pasta `./allure-results` e reconstrói o painel dinâmico a cada 3 segundos.
- Mostre como o novo teste aparece no gráfico de sucesso, e finalize a aula enfatizando que o uso de Few-Shot reduziu o tempo de escrita de testes em mais de 70%, garantindo que os novos testes nascessem sem erros de sintaxe ou de importação.
