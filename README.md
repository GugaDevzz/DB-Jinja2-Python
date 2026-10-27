# DB-Jinja2-Python - Catatau Lanches 🍔🚀

\[pt-br\] | [en](#-english-version)

## 🇧🇷 Versão em Português

O **DB-Jinja2-Python** (Catatau Lanches) é uma aplicação web full-stack desenvolvida em Python com **FastAPI**, **Jinja2** (renderização server-side) e **SQLAlchemy**, integrada ao banco de dados relacional **Microsoft SQL Server (LocalDB)** por meio do driver **pyodbc**.

O sistema simula uma plataforma de autoatendimento e pedidos de uma hamburgueria temática, gerenciando desde a navegação no cardápio e persistência de carrinho em cookies até a aplicação de cupons de desconto, emissão de pedidos para a cozinha e baixa proporcional automatizada de insumos no estoque.

> ⚠️ **Status do Projeto: Versão Beta (v0.x)**  
> Este projeto encontra-se em estágio **Beta (funcional e em evolução ativa)**. Todas as regras de negócio essenciais, fluxo de compras e integração com banco de dados estão implementadas e operacionais. Melhorias futuras, refinamentos arquiteturais (como criptografia de senhas, JWT e WebSockets para a cozinha) estão mapeados no [Roadmap de Ideias Futuras](#-status-beta-e-ideias-futuras) e na [Documentação de Requisitos](REQUISITOS.md).

---

### 📌 Sumário

* [Funcionalidades](#-funcionalidades)
* [Status Beta e Ideias Futuras](#-status-beta-e-ideias-futuras)
* [Estrutura do Projeto](#-estrutura-do-projeto)
* [Pré-requisitos](#-pré-requisitos)
* [Configuração do Banco de Dados](#-configuração-do-banco-de-dados)
* [Como Executar](#-como-executar)
* [Documentação das Rotas e Telas](#-documentação-das-rotas-e-telas)
* [Descrição dos Módulos](#-descrição-dos-módulos)
* [Documentação de Requisitos](#-documentação-de-requisitos)
* [Licença](#-licença)

---

### ✨ Funcionalidades

* **Arquitetura Web de Alta Performance:** Construída com FastAPI e executada sobre servidor ASGI assíncrono (Uvicorn).
* **Renderização Dinâmica com Jinja2:** Templates HTML integrados e renderizados no servidor com injeção ágil de variáveis de contexto.
* **Persistência Relacional com SQLAlchemy:** Mapeamento objeto-relacional completo para Microsoft SQL Server abrangendo clientes, produtos, pedidos, itens, ingredientes e fichas técnicas de estoque.
* **Carrinho de Compras Descentralizado em Cookies:** Estado do carrinho mantido no navegador via cookie JSON (`carrinho_catatau`), permitindo navegação fluida sem sobrecarregar o banco de dados antes da compra.
* **Sistema de Cupons de Boas-Vindas:** Validação do cupom `BEMVINDO30` / `CATATAU30` com 30% de desconto na primeira compra de clientes cadastrados, com bloqueio automático pós-utilização.
* **Envio para Cozinha e Baixa Automática de Estoque:** Ao fechar o pedido no checkout, o sistema deduz os ingredientes necessários de cada produto com base na receita cadastrada.
* **Autenticação e Sessão por Cookies:** Login por nome de usuário ou e-mail com cookie seguro (`user_id`, `HttpOnly`, `SameSite=Lax`).
* **Interface Temática e Responsiva:** Folhas de estilo modulares em CSS puro com suporte a navegação desktop e menu mobile.

---

### ⚠️ Status Beta e Ideias Futuras

O projeto foi concebido como um MVP robusto e funcional (versão beta). Algumas melhorias já estão planejadas para as versões de produção:

* 🔒 **Segurança das Senhas:** Implementação de hashing com `bcrypt` ou `argon2` (atualmente armazenadas em texto plano para fins didáticos/prototipagem).
* 🛡️ **Sessões e Tokens:** Migração do cookie `user_id` simples para JWT assinado ou sessões criptografadas com tokens anti-CSRF.
* 🍳 **Painel de Cozinha em Tempo Real (KDS):** Monitor com atualização ao vivo via **WebSockets** para os cozinheiros alterarem o status dos pedidos (`ESPERANDO` ➔ `EM PREPARO` ➔ `PRONTO`).
* 💳 **Gateway de Pagamento:** Integração com Pix dinâmico (QR Code) e cartão de crédito.
* 📦 **Delivery:** Suporte a seleção de entrega com endereço e taxa de frete, além do número de mesa atual.
* 🐳 **Docker e Alembic:** Conteinerização completa com Docker Compose e controle de versão do banco com migrations do Alembic.

---

### 📂 Estrutura do Projeto

```
DB-Jinja2-Python/
├── database/
│   ├── Banco.py             # Configuração da engine SQLAlchemy e sessão do SQL Server
│   ├── Conexao.py           # Script para verificação de conexão e criação de tabelas
│   ├── Diagram_banco.png    # Diagrama de Entidade-Relacionamento do banco de dados
│   ├── Tabelas.py           # Modelos ORM (Cliente, Produto, Pedido, Ingrediente, etc.)
│   └── teste.py             # Utilitário para verificar drivers ODBC instalados
├── models/
│   └── Tabelas.py           # Modelo legado/auxiliar de cadastro
├── static/
│   ├── css/                 # Folhas de estilo modularizadas por tela
│   │   ├── cadastro/        # Estilo da página de cadastro (menucss.css)
│   │   ├── cardapio/        # Estilo do catálogo de lanches (lanches.css)
│   │   ├── contato/         # Estilo da página sobre nós (sobree_nos.css)
│   │   ├── lanches/         # Estilo específico por produto (uniclanche.css, etc.)
│   │   ├── login/           # Estilo da página de login (menucsss.css)
│   │   ├── usuarios/        # Estilo da página de perfil (users.css)
│   │   ├── checkout.css     # Estilo da tela de finalização de pedido
│   │   ├── cupons.css       # Estilo da página promocional de cupons
│   │   └── style.css        # Estilos globais e da página inicial (home)
│   └── imagens/             # Imagens de produtos, logos e banners
│       └── lanches/         # Fotos dos lanches do cardápio
├── templates/
│   ├── cadastro/
│   │   └── menu.html        # Formulário de cadastro de novos clientes
│   ├── cardapio/
│   │   ├── envlanches/      # Telas de detalhes individuais de cada lanche
│   │   └── lanches.html     # Catálogo geral do cardápio
│   ├── contato/
│   │   └── sobre-nos.html   # Página institucional de contato
│   ├── login/
│   │   └── Menu.html        # Tela de login
│   ├── usuarios/
│   │   └── user.html        # Painel de perfil do cliente autenticado
│   ├── checkout.html        # Tela de conferência e envio do pedido
│   ├── cupons.html          # Página interativa de cupons de desconto
│   └── index.html           # Página inicial (home) com promoções e avisos
├── .gitattributes           # Atributos de versionamento Git
├── main.py                  # Ponto de entrada da aplicação FastAPI e rotas
├── requirements.txt         # Lista de dependências Python do projeto
└── REQUISITOS.md            # Documentação formal de requisitos (SRS)
```

---

### 🛠️ Pré-requisitos

(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& c:\Users\...\.venv\Scripts\Activate.ps1) #Se caso der bloqueio no venv
venv\Scripts\activate.ps1 - powershell
venv\Scripts\activate.bat - Command Prompt

Certifique-se de ter os seguintes itens instalados no seu ambiente:
1. **Python 3.8+** (recomendado 3.10 ou superior):
   ```bash
   python --version
   ```

2. **Microsoft SQL Server / LocalDB:**
   * O projeto vem configurado para se conectar à instância `(localdb)\MSSQLLocalDB` com o banco `DBCATATAU`.

3. **Driver ODBC para SQL Server:**
   * **ODBC Driver 17 for SQL Server** (ou compatível).

Instale as dependências do projeto através do arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

### 🗄️ Configuração do Banco de Dados

1. **Verificar os drivers ODBC disponíveis no seu sistema:**
   ```bash
   python database/teste.py
   ```

2. **Criar a base de dados no SQL Server:**
   * Certifique-se de que o banco `DBCATATAU` existe na sua instância LocalDB:
     ```sql
     CREATE DATABASE DBCATATAU;
     ```

3. **Criar automaticamente as tabelas do sistema:**
   * Execute o script de inicialização do schema:
     ```bash
     python -c "from database.Banco import Base, engine; from database.Tabelas import *; Base.metadata.create_all(bind=engine); print('Tabelas criadas com sucesso!')"
     ```

---

### 🚀 Como Executar

1. Navegue até o diretório raiz do projeto:
   ```bash
   cd DB-Jinja2-Python
   ```

2. Inicie o servidor web com **Uvicorn**:
   ```bash
   uvicorn main:app --reload
   ```

3. Abra o navegador e acesse a aplicação:
   * **Página Inicial:** [http://127.0.0.1:8000/catatau](http://127.0.0.1:8000/catatau)
   * **Cardápio:** [http://127.0.0.1:8000/cardapio](http://127.0.0.1:8000/cardapio)
   * **Status da API:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

### 📖 Documentação das Rotas e Telas

| Método | Rota | Tipo | Descrição |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | JSON | Status básico da API (`{"status": "Servidor no ar"}`). |
| `GET` | `/catatau` | HTML | Página inicial com destaques, avisos de entrega e acesso às seções. |
| `GET` | `/cardapio` | HTML | Catálogo de lanches com controle interativo de carrinho. |
| `GET` | `/lanche/{nome}` | HTML | Página detalhada com especificações do lanche selecionado. |
| `GET` | `/cupons` | HTML | Central de cupons promocionais com verificação de elegibilidade. |
| `POST` | `/api/validar-cupom` | JSON | Endpoint da API para cálculo dinâmico de desconto do cupom. |
| `GET` | `/login` | HTML | Formulário de login de clientes. |
| `POST` | `/login` | HTML/Cookie | Processamento de autenticação e emissão do cookie `user_id`. |
| `GET` | `/cadastro` | HTML | Formulário de criação de conta. |
| `POST` | `/cadastro` | Redirect | Criação do cliente, validação de unicidade e login automático. |
| `GET` | `/logout` | Redirect | Encerramento de sessão e destruição do cookie `user_id`. |
| `GET` | `/usuario/{nome}` | HTML | Painel com dados cadastrais do cliente. |
| `POST` | `/carrinho/adicionar` | Redirect | Adiciona um item ao carrinho gravado no cookie `carrinho_catatau`. |
| `POST` | `/carrinho/atualizar` | Redirect | Incrementa ou decrementa unidades de um item no carrinho. |
| `POST` | `/carrinho/remover` | Redirect | Remove completamente um produto do carrinho. |
| `GET` | `/checkout` | HTML | Tela de finalização de pedido com revisão de valores e cupons. |
| `POST` | `/checkout/aplicar` | HTML | Aplica cupom de desconto na sessão de checkout. |
| `POST` | `/checkout/remover` | HTML | Remove cupom aplicado na sessão de checkout. |
| `POST` | `/checkout/enviar` | Redirect | Grava pedido no banco, abate insumos no estoque e esvazia o carrinho. |
| `GET` | `/contato` | HTML | Página institucional "Sobre Nós" e canais de contato. |
| `GET` | `/administrator` | JSON | Lista administrativa rápida contendo todos os clientes cadastrados. |

* **Swagger UI (Documentação Interativa):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

### 🧩 Descrição dos Módulos

* **`main.py`**: Ponto central da aplicação. Configura a instância `FastAPI`, monta o diretório `static`, gerencia o motor de templates `Jinja2Templates`, lida com os cookies de sessão/carrinho e implementa os controladores de todas as rotas.
* **`database/Banco.py`**: Configuração de infraestrutura de dados. Monta a string de conexão via `pyodbc` para o SQL Server LocalDB, define a `engine`, a fábrica de sessões `SessionLocal` e o injetor de dependências `get_db`.
* **`database/Tabelas.py`**: Modelagem das tabelas do banco de dados em classes SQLAlchemy (`Cliente`, `Produto`, `Pedido`, `ItemPedido`, `Ingrediente`, `ProdutoEstoque`).
* **`database/Conexao.py`**: Módulo utilitário para checagem rápida de conectividade com a base de dados e execução do `create_all()`.
* **`database/teste.py`**: Script de diagnóstico para listagem de drivers ODBC instalados na máquina host.
* **`templates/`**: Conjunto de visões HTML dinâmicas processadas pelo Jinja2 com layouts segmentados para home, cardápio, checkout, cupons e autenticação.
* **`static/`**: Recursos estáticos públicos, divididos entre arquivos CSS customizados para cada visão e acervo de imagens e logotipos da hamburgueria.

---

### 📋 Documentação de Requisitos

A especificação formal e detalhada dos **Requisitos Funcionais (RF)**, **Requisitos Não Funcionais (RNF)**, **Regras de Negócio (RN)**, diagrama de dados e detalhamento do backlog beta está disponível no documento:

👉 **[Consulte a Especificação Completa de Requisitos (REQUISITOS.md)](REQUISITOS.md)**

---

## 🇺🇸 English Version

**DB-Jinja2-Python** (Catatau Lanches) is a full-stack web application developed in Python utilizing **FastAPI**, **Jinja2** (server-side rendering), and **SQLAlchemy**, backed by a relational **Microsoft SQL Server (LocalDB)** database via **pyodbc**.

The application models a self-service ordering platform for a burger restaurant, handling everything from menu exploration and cookie-based cart persistence to welcome discount coupons, kitchen order queue submission, and automated ingredient stock deductions.

> ⚠️ **Project Status: Beta Version (v0.x)**  
> This project is currently in its **Beta stage (functional and actively developed)**. Core business rules, purchasing workflows, and database integration are fully operational. Future improvements and architectural upgrades (such as password hashing, JWT authentication, and real-time kitchen WebSockets) are detailed in the [Future Ideas Roadmap](#-beta-status-and-future-ideas) and the [Requirements Specification](REQUISITOS.md).

---

### 📌 Table of Contents

* [Features](#-features-1)
* [Beta Status and Future Ideas](#-beta-status-and-future-ideas)
* [Project Structure](#-project-structure-1)
* [Prerequisites](#-prerequisites-1)
* [Database Setup](#-database-setup)
* [How to Run](#-how-to-run-1)
* [Routes and Pages Documentation](#-routes-and-pages-documentation)
* [Module Breakdown](#-module-breakdown-1)
* [Requirements Documentation](#-requirements-documentation)
* [License](#-license-1)

---

### ✨ Features

* **High-Performance Web Architecture:** Powered by FastAPI and served through an asynchronous ASGI server (Uvicorn).
* **Dynamic Server-Side Rendering with Jinja2:** Pre-rendered HTML templates seamlessly injected with real-time database context.
* **Relational Persistence via SQLAlchemy:** Complete ORM mappings for Microsoft SQL Server covering customers, products, orders, order items, ingredients, and recipe stock associations.
* **Stateless Cookie-Based Shopping Cart:** Cart state retained in browser cookies (`carrinho_catatau`) as JSON, eliminating pre-checkout database overhead.
* **Welcome Discount Coupon Engine:** Validation of coupons (`BEMVINDO30` / `CATATAU30`) granting 30% off for first-time orders by registered users, with automated one-time use locking.
* **Kitchen Order Dispatch with Inventory Deduction:** When an order is completed, product recipes automatically deduct required ingredient quantities from table `ingredientes`.
* **Cookie-Based Authentication:** Clean login by username or email setting secure cookies (`user_id`, `HttpOnly`, `SameSite=Lax`).
* **Modular Responsive UI:** Dedicated CSS stylesheets per module with support for desktop displays and mobile hamburger menus.

---

### ⚠️ Beta Status and Future Ideas

Conceived as a robust and working MVP (beta version), the following technical advancements are scheduled for production releases:

* 🔒 **Password Security:** Implementation of secure hashing via `bcrypt` or `argon2` (currently plain-text for educational/prototyping purposes).
* 🛡️ **Signed Sessions & Tokens:** Transition from simple `user_id` cookies to cryptographically signed JWT tokens and anti-CSRF protection.
* 🍳 **Real-Time Kitchen Display System (KDS):** Live order status board for cooks using **WebSockets** to advance states (`WAITING` ➔ `PREPARING` ➔ `READY`).
* 💳 **Payment Gateway:** Direct integration with instant Pix (dynamic QR Code) and credit card processing.
* 📦 **Delivery Mode:** Home delivery address intake and fee calculation alongside the existing dine-in table number field.
* 🐳 **Docker & Alembic:** Containerization with Docker Compose and automated schema migration management using Alembic.

---

### 📂 Project Structure

```
DB-Jinja2-Python/
├── database/
│   ├── Banco.py             # SQLAlchemy engine setup and SQL Server session factory
│   ├── Conexao.py           # Connectivity validation and table creation script
│   ├── Diagram_banco.png    # Database Entity-Relationship diagram
│   ├── Tabelas.py           # ORM models (Cliente, Produto, Pedido, Ingrediente, etc.)
│   └── teste.py             # Diagnostic tool listing installed pyodbc drivers
├── models/
│   └── Tabelas.py           # Auxiliary/legacy customer registration model
├── static/
│   ├── css/                 # Modular CSS stylesheets per page
│   │   ├── cadastro/        # Registration page styling (menucss.css)
│   │   ├── cardapio/        # Menu catalog styling (lanches.css)
│   │   ├── contato/         # About us page styling (sobree_nos.css)
│   │   ├── lanches/         # Product-specific detail styling (uniclanche.css, etc.)
│   │   ├── login/           # Login screen styling (menucsss.css)
│   │   ├── usuarios/        # Profile page styling (users.css)
│   │   ├── checkout.css     # Checkout view styling
│   │   ├── cupons.css       # Promotional coupons page styling
│   │   └── style.css        # Global and home view stylesheet
│   └── imagens/             # Burger photos, logos, and promotional banners
│       └── lanches/         # Catalog food images
├── templates/
│   ├── cadastro/
│   │   └── menu.html        # Customer registration form
│   ├── cardapio/
│   │   ├── envlanches/      # Dedicated individual burger detail pages
│   │   └── lanches.html     # General food menu catalog
│   ├── contato/
│   │   └── sobre-nos.html   # About us / contact page
│   ├── login/
│   │   └── Menu.html        # Login view
│   ├── usuarios/
│   │   └── user.html        # Authenticated customer profile view
│   ├── checkout.html        # Order checkout and confirmation view
│   ├── cupons.html          # Interactive discount coupon showcase
│   └── index.html           # Home page with banners, specials, and order notices
├── .gitattributes           # Git repository attributes
├── main.py                  # Application entry point and route controllers
├── requirements.txt         # Project Python dependencies
└── REQUISITOS.md            # Software Requirements Specification (SRS)
```

---

### 🛠️ Prerequisites

Ensure your environment satisfies the following requirements:

1. **Python 3.8+** (Python 3.10+ recommended):
   ```bash
   python --version
   ```

2. **Microsoft SQL Server / LocalDB:**
   * Configured out-of-the-box for `(localdb)\MSSQLLocalDB` and database `DBCATATAU`.

3. **ODBC Driver for SQL Server:**
   * **ODBC Driver 17 for SQL Server** (or compatible).

Install all project dependencies:

```bash
pip install -r requirements.txt
```

---

### 🗄️ Database Setup

1. **Verify installed ODBC drivers on your host:**
   ```bash
   python database/teste.py
   ```

2. **Create the target database in SQL Server:**
   * Make sure `DBCATATAU` is created inside your LocalDB instance:
     ```sql
     CREATE DATABASE DBCATATAU;
     ```

3. **Initialize database tables:**
   * Execute schema generation via SQLAlchemy metadata:
     ```bash
     python -c "from database.Banco import Base, engine; from database.Tabelas import *; Base.metadata.create_all(bind=engine); print('Tables created successfully!')"
     ```

---

### 🚀 How to Run

1. Navigate to the project root directory:
   ```bash
   cd DB-Jinja2-Python
   ```

2. Launch the application server with **Uvicorn**:
   ```bash
   uvicorn main:app --reload
   ```

3. Open your browser and access the application:
   * **Home Page:** [http://127.0.0.1:8000/catatau](http://127.0.0.1:8000/catatau)
   * **Menu:** [http://127.0.0.1:8000/cardapio](http://127.0.0.1:8000/cardapio)
   * **API Health Check:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

### 📖 Routes and Pages Documentation

| Method | Route | Response | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | JSON | API healthcheck endpoint (`{"status": "Servidor no ar"}`). |
| `GET` | `/catatau` | HTML | Main landing page featuring specials, order ETA banners, and navigation. |
| `GET` | `/cardapio` | HTML | Interactive food menu with cookie cart updates. |
| `GET` | `/lanche/{nome}` | HTML | Dynamic single-item detail view. |
| `GET` | `/cupons` | HTML | Coupon showcase validating customer eligibility. |
| `POST` | `/api/validar-cupom` | JSON | Async API calculating coupon discount and updated totals. |
| `GET` | `/login` | HTML | Customer login screen. |
| `POST` | `/login` | HTML/Cookie | Validates credentials and sets `user_id` session cookie. |
| `GET` | `/cadastro` | HTML | Customer account registration form. |
| `POST` | `/cadastro` | Redirect | Creates customer, enforces uniqueness, and auto-logs in. |
| `GET` | `/logout` | Redirect | Terminates user session by clearing `user_id` cookie. |
| `GET` | `/usuario/{nome}` | HTML | Profile page rendering customer account data. |
| `POST` | `/carrinho/adicionar` | Redirect | Adds item to `carrinho_catatau` cookie. |
| `POST` | `/carrinho/atualizar` | Redirect | Increments or decrements item quantity in cart cookie. |
| `POST` | `/carrinho/remover` | Redirect | Deletes item from cart cookie. |
| `GET` | `/checkout` | HTML | Order summary view with coupon management and table selector. |
| `POST` | `/checkout/aplicar` | HTML | Applies promotional discount to checkout session. |
| `POST` | `/checkout/remover` | HTML | Detaches active coupon from checkout session. |
| `POST` | `/checkout/enviar` | Redirect | Commits order, deducts ingredient stocks, and resets cart cookie. |
| `GET` | `/contato` | HTML | "About Us" and customer contact channel view. |
| `GET` | `/administrator` | JSON | Quick administrative JSON dump of all registered clients. |

* **Interactive Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

### 🧩 Module Breakdown

* **`main.py`**: Central application script. Initializes `FastAPI`, binds static file mounts, orchestrates `Jinja2Templates`, manages cookie states, and handles route controllers.
* **`database/Banco.py`**: Database setup module. Generates `pyodbc` connection strings for SQL Server LocalDB, initializes `engine`, creates `SessionLocal`, and provides `get_db` dependency.
* **`database/Tabelas.py`**: Database domain models (`Cliente`, `Produto`, `Pedido`, `ItemPedido`, `Ingrediente`, `ProdutoEstoque`).
* **`database/Conexao.py`**: Connectivity helper testing SQL Server communication and invoking `create_all()`.
* **`database/teste.py`**: Diagnostic utility inspecting installed ODBC drivers.
* **`templates/`**: Server-side Jinja2 template collection providing views for Home, Menu, Checkout, Coupons, Login, and Profile.
* **`static/`**: Public static assets including modular per-page CSS stylesheets and image galleries.

---

### 📋 Requirements Documentation

Detailed specifications for **Functional Requirements (FR)**, **Non-Functional Requirements (NFR)**, **Business Rules (BR)**, relational schema, and the Beta roadmap are documented at:

👉 **[View the Complete Requirements Specification (REQUISITOS.md)](REQUISITOS.md)**

---

## 📄 Licença / License

Este projeto está sob a licença MIT / This project is licensed under the MIT License.
