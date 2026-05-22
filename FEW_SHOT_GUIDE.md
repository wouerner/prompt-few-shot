# Guia Completo: Engenharia de Prompt Few-Shot em Engenharia de Software

Este guia explica detalhadamente o conceito de **Few-Shot Prompting**, demonstrando sua importância prática no dia a dia da Engenharia de Software e como ele é aplicado para construir interfaces inteligentes que conectam linguagem natural a sistemas reais (APIs).

---

## 1. O que é Few-Shot Prompting?

O **Few-Shot Prompting** (ou aprendizado com poucos exemplos) é uma técnica de engenharia de prompt baseada em *in-context learning* (aprendizado em contexto). Ela consiste em apresentar ao Modelo de Linguagem (LLM) de **2 a 5 exemplos explícitos de entradas e saídas esperadas** antes de apresentar a pergunta ou comando final.

### Zero-Shot vs. Few-Shot

*   **Zero-Shot (Sem Exemplos):** Você pede para a IA realizar uma tarefa apenas descrevendo-a textualmente.
    *   *Exemplo:* *"Traduza a frase 'quero tirar 10 dias de férias de 12 a 22 de dezembro' em um JSON para uma API."*
    *   *Risco:* O modelo pode gerar o JSON com chaves incorretas, adicionar formatações markdown extras (como ```json) ou inventar campos inexistentes.
*   **Few-Shot (Com Exemplos):** Você dá a mesma instrução, mas antes de enviar a frase do usuário, você fornece exemplos de conversões corretas.
    *   *Resultado:* O modelo espelha perfeitamente a estrutura, formatação e tom fornecidos nos exemplos, eliminando alucinações de formato.

---

## 2. Relevância na Engenharia de Software

Para engenheiros de software, a consistência de dados é fundamental. Sistemas não toleram chaves de JSON extras ou formatos de data corrompidos. Few-Shot Prompting resolve esse problema ao fornecer:

1.  **Garantia de Esquema Rígido (Schema Enforcement):** Ensina o modelo a responder estritamente em um formato estruturado (JSON, XML, YAML) sem a necessidade de parsing complexo no backend.
2.  **Interfaces de Linguagem Natural para APIs (NL-to-API):** Permite criar recursos como assistentes virtuais ou chatbots corporativos que acionam ações reais do sistema (ex: "marcar uma reunião", "agendar férias", "criar um chamado").
3.  **Geração de Código Corporativo Padronizado:** Ao fornecer 3 exemplos de classes ou testes escritos seguindo os padrões arquiteturais da sua empresa, a LLM gerará novos códigos que parecem ter sido escritos pelo próprio time.
4.  **Tradução de Logs e Depuração:** Fornecer exemplos de como logs complexos e empilhados (stacktraces) devem ser resumidos em relatórios de incidentes.

---

## 3. Estrutura de um Prompt Few-Shot Profissional

Um prompt robusto para sistemas de produção deve seguir uma estrutura bem definida e dividida por delimitadores claros:

```
[System Prompt / Instrução de Papel]
Define a identidade do modelo e as regras globais de comportamento e restrições.

==================================================
[Contexto Técnico / Esquema de Dados]
Explica o ambiente, endpoints da API, tipos de dados e limites de negócio.

==================================================
[Exemplos de Demonstração (Few-Shot Pairs)]
Pares de Entrada e Saída claramente demarcados.
Recomenda-se cobrir variações de métodos (GET, POST, PATCH) e caminhos felizes/tristes.

==================================================
SUA VEZ DE PROCESSAR:
Entrada: [Input do Usuário Atual]
Saída:
```

---

## 4. O Nosso Caso de Estudo: Prompt de Gerenciamento de Férias

Abaixo está o template exato de prompt Few-Shot que desenvolvemos neste projeto. Ele ensina uma LLM a traduzir linguagem natural de RH/Funcionários em chamadas REST para a nossa **API de Férias** com base em FastAPI.

### O Template do Prompt

```markdown
Você é um assistente de inteligência artificial ultra-especializado em traduzir solicitações em linguagem natural de usuários em chamadas REST exatas para a nossa API de Gerenciamento de Férias.

Regras de Saída:
1. Responda APENAS com um objeto JSON estruturado contendo as chaves: "method" (método HTTP), "url" (endpoint relativo) e opcionalmente "body" (objeto JSON de payload).
2. Não inclua nenhuma introdução, explicação ou bloco de código em markdown extra.

==================================================
DOCUMENTAÇÃO DE ENDPOINTS DISPONÍVEIS:
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
   - Payload: { "status": "APPROVED" | "REJECTED" }

==================================================
EXEMPLOS DE PROCESSAMENTO (FEW-SHOT):

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
}

==================================================
SUA VEZ DE PROCESSAR:
Entrada: {COMANDO_DO_USUARIO}
Saída:
```

---

## 5. Como Testar Interativamente Neste Projeto

Criamos uma interface web completa e automatizada para você ver esse fluxo acontecendo na prática.

1.  **Inicialize o Servidor:** Rode o comando `python -m uvicorn app.main:app --reload` no terminal.
2.  **Acesse a Interface:** Abra `http://localhost:8000/` em seu navegador.
3.  **Abra o Swagger:** Você pode clicar no botão **Swagger OpenAPI** no canto superior direito para acessar a documentação padrão dos endpoints gerados nativamente pelo FastAPI (`http://localhost:8000/docs`).
4.  **Acesse a aba "Prompt Playground":**
    *   Selecione um dos comandos pré-definidos (ex: "Cadastrar a funcionária Ana Souza...") ou escreva o seu em linguagem natural.
    *   Clique em **Gerar Prompt Few-Shot** para ver a estrutura final montada.
    *   Clique no botão **Simular Resposta da IA** para ver a IA (via nosso simulador embutido de altíssima precisão) interpretando a entrada e executando a chamada de API de forma 100% funcional no nosso backend real! O resultado será refletido instantaneamente na tabela do Dashboard!
