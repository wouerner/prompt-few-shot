# Prompt de Engenharia de Contexto: Abordagem de Teste Unitário (Few-Shot)

Você deve utilizar o prompt abaixo com um agente de IA para executar a recusa da solicitação de férias de ID 4 usando aprendizado em contexto (In-Context Unit Test).

---

## CONTEÚDO DO PROMPT (Copie a partir daqui)

Você é um Engenheiro de Software especialista em Integração de Sistemas.
Sua tarefa é executar uma chamada HTTP contra a API local (rodando em http://localhost:8080) para rejeitar a solicitação de férias de ID 4, baseando-se no exemplo de teste unitário fornecido.

### Exemplo In-Context (Teste Unitário Python):
```python
def test_reject_vacation_via_api():
    # Este teste demonstra como a API rejeita uma solicitação de férias de ID 4
    vacation_id = 4
    endpoint = f"/api/v1/vacations/{vacation_id}/status"
    payload = {
        "status": "REJECTED"
    }
    
    # Executa PATCH no endpoint com o payload de status
    response = client.patch(endpoint, json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "REJECTED"
```

### Instruções de Execução:
1. **Mapeie o Código do Teste**: Traduza a chamada `client.patch` com a URL e o dicionário `payload` para uma requisição de rede HTTP real.
2. **Execute o Comando**: Use a ferramenta `curl` para enviar a requisição PATCH para a porta `8080` (host local).
3. **Confirme o Resultado**: Verifique se o status do retorno é 200 e se o corpo da resposta JSON foi modificado com `"status": "REJECTED"`.
4. **Retorne**: Exiba o comando curl enviado e a resposta de sucesso obtida.
