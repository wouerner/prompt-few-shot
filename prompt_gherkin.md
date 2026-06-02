# Prompt de Engenharia de Contexto: Abordagem Gherkin (BDD)

Você deve utilizar o prompt abaixo com um agente de IA para executar a recusa da solicitação de férias de ID 4 usando aprendizado em contexto (In-Context BDD/Gherkin).

---

## CONTEÚDO DO PROMPT (Copie a partir daqui)

Você é um Engenheiro de Software especialista em Automação de APIs. 
Sua tarefa é executar uma requisição HTTP na API local (rodando em http://localhost:8080) para realizar a recusa de uma solicitação de férias com base no cenário de especificação abaixo.

### Contexto e Especificação (Gherkin):
```gherkin
Funcionalidade: Fluxo de Rejeição de Solicitação de Férias

  Cenário: Rejeitar uma solicitação pendente existente
    Dado que existe uma solicitação de férias com ID 4 e status atual "PENDING"
    Quando eu enviar uma requisição PATCH para a URL "/api/v1/vacations/4/status" contendo o JSON:
      """
      {
        "status": "REJECTED"
      }
      """
    Então o status da solicitação de férias deve ser alterado para "REJECTED" e a API deve retornar HTTP 200 com a solicitação atualizada.
```

### Instruções de Execução:
1. **Analise o Cenário Gherkin**: Identifique o método HTTP, a URI relativa e o payload JSON necessários.
2. **Execute a Ação**: Construa um comando `curl` apontando para a API local (porta 8080) e execute-o.
3. **Valide a Resposta**: Certifique-se de que a resposta retornada pela chamada contenha o status `"REJECTED"`.
4. **Retorne**: Apresente a chamada curl executada e a resposta JSON recebida.
