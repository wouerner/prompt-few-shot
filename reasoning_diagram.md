# Diagrama de Raciocínio

Este diagrama de fluxo demonstra os passos lógicos seguidos para analisar o repositório, descobrir o endpoint correto, mapear o payload necessário e executar a recusa da solicitação de férias de ID número 4.

```mermaid
graph TD
    A["1. Análise do Repositório"] --> B["2. Inspeção de app/main.py"]
    
    B --> C["Identificação dos Dados (Seed)"]
    B --> D["Identificação da Rota (Endpoint)"]
    B --> E["Identificação da Estrutura (Payload)"]
    
    C --> C1["Solicitação ID 4 em estado 'PENDING'"]
    D --> D1["PATCH /api/v1/vacations/{vacation_id}/status"]
    E --> E1["StatusUpdate espera 'status': 'APPROVED' | 'REJECTED'"]
    
    C1 --> F["3. Construção da Requisição"]
    D1 --> F
    E1 --> F
    
    F --> G["4. Execução da Chamada (curl)"]
    G --> H["5. Confirmação (Resposta HTTP 200 - REJECTED)"]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style G fill:#bfb,stroke:#333,stroke-width:2px
    style H fill:#fbb,stroke:#333,stroke-width:2px
```
