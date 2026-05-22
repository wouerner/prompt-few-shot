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
├── FEW_SHOT_GUIDE.md      # Guia Teórico Completo sobre Few-Shot Prompting
├── requirements.txt       # Dependências de pacotes Python
└── README.md              # Este arquivo de documentação
```

---

## 🚀 Como Executar o Projeto

Siga os passos abaixo para rodar o projeto localmente em sua máquina:

### 1. Clonar ou Acessar o Diretório
Navegue até a pasta raiz do projeto:
```bash
cd prompt-few-shot
```

### 2. Configurar o Ambiente Virtual (Recomendado)
Crie um ambiente virtual Python para isolar as dependências:
```bash
# No Linux/macOS:
python3 -m venv venv
source venv/bin/activate

# No Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> [!TIP]
> **Dica para sistemas Debian/Ubuntu (erro de *ensurepip*):**
> Se ao tentar criar o ambiente virtual ocorrer o erro de `ensurepip` indisponível, você pode corrigi-lo instalando o pacote do sistema:
> ```bash
> sudo apt install python3-venv
> ```
> Ou, caso utilize um ambiente com Python gerenciado externamente, instale o `virtualenv` localmente e use-o para gerar o ambiente virtual isolado:
> ```bash
> python3 -m pip install --user virtualenv --break-system-packages
> python3 -m virtualenv venv
> source venv/bin/activate
> ```

### 3. Instalar as Dependências
Instale todos os pacotes necessários (aplicação e testes) listados no `requirements.txt` utilizando o ambiente ativado:
```bash
pip install -r requirements.txt
```

### 4. Executar a Aplicação
Inicie o servidor de desenvolvimento utilizando o Uvicorn:
```bash
python -m uvicorn app.main:app --reload
```

### 5. Acessar no Navegador
Após inicializar o servidor, você poderá acessar:
- **Aplicação & Playground**: [http://localhost:8000/](http://localhost:8000/)
- **Documentação Interativa da API (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 🧪 Executando os Testes Unitários

O projeto possui uma suíte de testes completa cobrindo endpoints de funcionários, rotas de férias e todas as regras de negócio de saldo e sobreposição de datas.

Para rodar os testes, garanta que as dependências de testes estão instaladas e execute:
```bash
python3 -m pytest
```

### 🥒 Executando os Testes de Feature (BDD)

Também implementamos testes de comportamento BDD usando o framework **Behave** para validar as regras de negócio em linguagem natural (Gherkin em português) para o fluxo de aprovação de férias.

Para rodar os testes BDD, execute o comando na raiz do projeto:
```bash
behave
```

---


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
