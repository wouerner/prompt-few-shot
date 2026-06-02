# Relatório de Execução e Comparação de Prompts (Gherkin vs Teste Unitário)

Este relatório detalha os resultados da execução em paralelo de duas abordagens distintas de Engenharia de Prompt (Few-Shot/In-Context) para o objetivo de rejeitar a solicitação de férias de ID 4.

---

## 1. Tabela Comparativa de Desempenho

| Critério | Agente Gherkin (BDD) | Agente Teste Unitário (Few-Shot) | Vencedor |
| :--- | :--- | :--- | :--- |
| **ID da Conversa** | `384d9f7e-eb3b-4356-b361-5febf3c2f985` | `ce01d0bc-594c-4092-bace-2b36bfe87d8a` | - |
| **Passos Executados** | **8 passos** (chamadas de ferramentas) | **6 passos** (chamadas de ferramentas) | **Teste Unitário** |
| **Leitura de Arquivos** | Leu `docker-compose.yml` e `app/main.py` | Não leu arquivos de código de produção | **Teste Unitário** |
| **Consumo de Tokens** | **Alto** (carregou `app/main.py` de 315 linhas no contexto) | **Muito Baixo** (apenas traduziu o prompt) | **Teste Unitário** |
| **Tempo de Execução** | Mais lento (passos extras de validação) | Mais rápido (tradução e execução direta) | **Teste Unitário** |

---

## 2. Detalhes do Fluxo de Trabalho

### Fluxo do Agente Gherkin (8 passos)
1. **Listagem**: Listou o diretório do projeto (`list_dir`).
2. **Checagem**: Verificou o estado dos containers Docker (`docker ps`).
3. **Leitura de Infra**: Leu `docker-compose.yml` para descobrir a porta da aplicação (`view_file`).
4. **Leitura de Produção**: Leu `app/main.py` completo (`view_file`) para garantir que o mapeamento conceitual do cenário Gherkin correspondia ao endpoint real do código.
5. **Inicialização**: Subiu os containers Docker (`docker compose up --build -d`).
6. **Validação Prévia**: Realizou uma chamada GET de teste para verificar se o ID 4 existia e qual seu status original.
7. **Mutação**: Executou a chamada HTTP PATCH para recusar a solicitação.
8. **Finalização**: Enviou a resposta de sucesso para o agente pai.

### Fluxo do Agente de Teste Unitário (6 passos)
1. **Listagem**: Listou o diretório do projeto (`list_dir`).
2. **Checagem**: Verificou o status do Docker Compose (`docker compose ps`).
3. **Inicialização**: Subiu os containers Docker (`docker compose up -d --build`).
4. **Checagem**: Validou novamente o status dos containers (`docker compose ps`).
5. **Mutação Direta**: Executou diretamente o PATCH via `curl`. Graças ao código do teste unitário no prompt que continha a URI exata e o payload do contrato, não houve necessidade de checagens ou leituras extras do arquivo `app/main.py`.
6. **Finalização**: Enviou a resposta de sucesso para o agente pai.

---

## 3. Conclusão da Análise

A especificação técnica via **Teste Unitário (Few-Shot)** provou ser a forma mais otimizada de interagir com o agente para tarefas baseadas em código ou APIs. Ela diminui a ambiguidade de tradução de linguagem natural para contratos técnicos, reduzindo drasticamente a quantidade de passos de exploração do agente e o consumo geral de tokens.
