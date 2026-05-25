# 🚀 Few-Shot Prompting - Guia Prático & Simulador de API de Férias

Este projeto é um laboratório prático e interativo projetado para demonstrar o conceito de **Few-Shot Prompting** (aprendizado com poucos exemplos) em Engenharia de Software. Ele apresenta como conectar linguagem natural (solicitações de usuários) a ações reais em sistemas através de uma API estruturada.

O projeto consiste em uma **API REST** construída com FastAPI e um **Dashboard/Playground Interativo** responsivo e elegante em HTML/CSS/JS.

---

## 💻 Sobre o Projeto

Na engenharia de software moderna, integrar Modelos de Linguagem (LLMs) a sistemas legados ou APIs requer extrema consistência no formato dos dados. O **Few-Shot Prompting** resolve isso fornecendo exemplos estruturados de entrada e saída no próprio prompt, garantindo respostas em formatos específicos (como JSON estruturado) sem a necessidade de lógicas complexas de tratamento de erro no backend.

Neste projeto, simulamos um sistema de **Gerenciamento de Férias de Funcionários** onde o usuário pode interagir de duas formas:
1. **Convencional**: Utilizando a interface visual ou a API REST direta.
2. **Inteligente (Playground)**: Escrevendo comandos em linguagem natural (ex: *"Quero solicitar férias para o João de 10 a 20 de dezembro"*) e vendo a "IA" traduzir isso em uma chamada HTTP exata (`POST /api/v1/vacations` com o payload correto) e executá-la no banco de dados.

---

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python 3.8+, [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/), [Pydantic v2](https://docs.pydantic.dev/) para validação de esquemas.
- **Frontend**: HTML5, CSS3 moderno (design elegante com efeitos de vidro/glassmorphism e modo escuro), Vanilla JavaScript (ES6+).
- **Guia Teórico**: Markdown documentado contendo a teoria completa de engenharia de prompt.

---

## 📁 Estrutura de Pastas

```text
prompt-few-shot/
├── app/
│   ├── main.py            # Servidor FastAPI, rotas da API e banco de dados em memória
│   └── static/            # Frontend (SPA) da aplicação
│       ├── app.js         # Lógica do dashboard e simulador de Few-Shot
│       ├── index.html     # Interface do usuário (HTML5 semântico)
│       └── styles.css     # Estilos visuais elegantes, paleta de cores moderna e responsividade
├── tests/                 # Pasta unificada contendo toda a suíte de testes
│   ├── unit/              # Testes unitários e de integração (pytest)
│   └── bdd/               # Testes de comportamento em linguagem Gherkin (behave)
├── FEW_SHOT_GUIDE.md      # Guia Teórico Completo sobre Few-Shot Prompting
├── requirements.txt       # Dependências de pacotes Python
└── README.md              # Este arquivo de documentação
```

---

## 🐳 Executando o Projeto com Docker (Ambiente Único)

Este projeto foi projetado para rodar **exclusivamente em ambiente containerizado (Docker)**. Isso garante consistência total nas dependências de runtime, nos servidores de testes e na visualização de relatórios do **Allure Report**, sem a necessidade de instalações locais adicionais (como Python, dependências do sistema ou instaladores do Allure CLI).

### 📐 Arquitetura do Ambiente no Docker

Abaixo, apresentamos o fluxo de integração e comunicação entre os serviços no ambiente do Docker Compose:

```mermaid
graph TD
    Host[Máquina Hospedeira (Host)]
    subgraph Docker_Compose [Ambiente Docker Compose]
        App[Container API/App:<br>prompt_few_shot_app]
        Allure[Container Allure API:<br>prompt_few_shot_allure]
        AllureUI[Container Allure UI:<br>prompt_few_shot_allure_ui]
        Vol[Volume Compartilhado:<br>./allure-results]
    end

    Host -- "1. Inicia Serviços (docker compose up)" --> Docker_Compose
    Host -- "2. Executa Testes BDD/Unitários" --> App
    App -- "3. Gera Resultados (.json)" --> Vol
    Vol -- "4. Atualiza Relatório automaticamente" --> Allure
    AllureUI -- "5. Consome API" --> Allure
    Host -- "6. Acessa Dashboard & API do Projeto (8080)" --> App
    Host -- "7. Acessa Swagger da API Allure (5050)" --> Allure
    Host -- "8. Acessa Relatório Direto (5050/latest-report)" --> Allure
    Host -- "9. Acessa Interface Gráfica Allure UI (5252)" --> AllureUI

    style Host fill:#f9f9f9,stroke:#333,stroke-width:2px;
    style Docker_Compose fill:#e6f7ff,stroke:#0050b3,stroke-width:2px;
    style App fill:#bae7ff,stroke:#0050b3,stroke-width:1px;
    style Allure fill:#d9f7be,stroke:#389e0d,stroke-width:1px;
    style AllureUI fill:#ffd8bf,stroke:#d4380d,stroke-width:1px;
    style Vol fill:#ffe58f,stroke:#d4b106,stroke-width:1px;
```

---

### 🚀 Como Iniciar a Aplicação

Siga os passos rápidos abaixo para construir e inicializar os containers:

#### 1. Iniciar os Containers
Na raiz do projeto, execute o comando:
```bash
docker compose up --build
```
> [!NOTE]
> O container da aplicação (`app`) roda em modo de desenvolvimento com **hot-reload** ativado (`--reload`). Qualquer modificação feita no código localmente será refletida em tempo real dentro do container graças ao volume de montagem `./app` (mapeado de `. :/app`).

#### 2. Serviços Disponíveis
Após a inicialização bem-sucedida, você poderá acessar diretamente do seu navegador:
*   **Aplicação & Playground Interativo**: [http://localhost:8080/](http://localhost:8080/)
*   **Documentação Interativa da API do Projeto (Swagger)**: [http://localhost:8080/docs](http://localhost:8080/docs)
*   **Interface Gráfica Premium do Allure (Dashboard)**: [http://localhost:5252/allure-docker-service-ui/](http://localhost:5252/allure-docker-service-ui/)
*   **Visualização Direta do Relatório Allure (HTML)**: [http://localhost:5050/allure-docker-service/latest-report](http://localhost:5050/allure-docker-service/latest-report)
*   **Swagger da API do Allure**: [http://localhost:5050/](http://localhost:5050/) (Esta URL raiz exibe a documentação Swagger da API interna do serviço Allure)

---

### 🧪 Executando os Testes & Gerando Relatórios Allure

Com os containers em execução em um terminal, abra uma nova janela de terminal para rodar as suítes de testes:

#### 1. Testes Unitários e de Integração (Pytest + Allure)
Execute o `pytest` dentro do container da aplicação enviando os resultados para a pasta compartilhada:
```bash
docker compose exec app pytest --alluredir=allure-results
```

#### 2. Testes de Comportamento BDD (Behave + Allure)
Execute o `behave` apontando para a pasta `tests/bdd` usando o formatador do Allure para gerar os relatórios na mesma pasta compartilhada:
```bash
docker compose exec app behave -f allure_behave.formatter:AllureFormatter -o allure-results tests/bdd
```

#### 3. Como Visualizar os Resultados do Allure
O container do Allure monitora a pasta `./allure-results` a cada 3 segundos e reconstrói o relatório.

Após executar os testes acima, você tem duas excelentes formas de ver os resultados:
1.  **Interface Gráfica (Recomendado)**: Acesse **[http://localhost:5252/allure-docker-service-ui/](http://localhost:5252/allure-docker-service-ui/)** para ver um painel de controle interativo completo, com histórico, gráficos de tendências, status de cenários e logs de cada etapa de teste.
2.  **Relatório HTML Direto**: Acesse **[http://localhost:5050/allure-docker-service/latest-report](http://localhost:5050/allure-docker-service/latest-report)** para carregar diretamente a página estática mais recente do Allure Report gerada pelo container.

---

### 🧹 Finalizando o Ambiente

Para parar a execução e limpar todos os recursos alocados pelos containers, execute:
```bash
docker compose down
```




## 🧠 O Conceito: Zero-Shot vs. Few-Shot

Para entender a fundo o funcionamento e a importância dessa abordagem, consulte o arquivo **[FEW_SHOT_GUIDE.md](file:///home/wouerner/dev/wouerner/prompt-few-shot/FEW_SHOT_GUIDE.md)** na raiz do projeto.

### Resumo Rápido:
*   **Zero-Shot (Sem Exemplos)**: Solicita a tradução diretamente.
    *   *Prompt:* `"Traduza a frase 'Cadastrar Roberto como Dev' em JSON."`
    *   *Risco:* A IA pode devolver textos adicionais, markdown (` ```json `), chaves incorretas ou inventar campos.
*   **Few-Shot (Com Exemplos)**: Ensina o comportamento desejado mostrando pares de entradas e saídas esperadas antes do comando final.
    *   *Resultado:* Resposta perfeitamente limpa e no formato exato exigido pela API do seu sistema.

---

## 🎮 Usando o Prompt Playground

Ao abrir a interface no navegador:
1. Navegue até a aba **"Prompt Playground"**.
2. Escolha uma das sugestões rápidas ou escreva um comando em linguagem natural no campo de texto (ex: *"Aprovar o pedido de férias de ID 2"*).
3. Clique em **"Gerar Prompt Few-Shot"** para inspecionar como o prompt completo é estruturado nos bastidores com as instruções de sistema, documentação de rotas e exemplos.
4. Clique em **"Simular Resposta da IA"** para que a IA (através do nosso mecanismo simulado) interprete a entrada, gere a chamada REST e a execute no backend. Você verá as tabelas de Funcionários e Férias no Dashboard serem atualizadas em tempo real!

---

## 📄 Licença

Este projeto é de caráter educacional e está livre para uso, modificação e distribuição para fins de aprendizado em engenharia de prompt e desenvolvimento de software.
