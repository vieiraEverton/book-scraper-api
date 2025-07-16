# Book Scraper API

A **Book Scraper API** é um serviço RESTful que fornece informações de livros extraídos automaticamente de [books.toscrape.com](https://books.toscrape.com/). Ideal para consumo por aplicações front-end, pipelines de dados e modelos de Machine Learning.

## ✨ Features

* **Web Scraping** automático de título, preço, rating, disponibilidade, categoria e imagem
* **API** construída com FastAPI; documentação interativa via Swagger UI
* **Autenticação JWT** para proteger rotas sensíveis
* **Persistência SQLite** via SQLModel para usuários e, futuramente, dados de livros
* **Healthcheck** em `/api/v1/health`

## 🛠️ Requisitos

* Python 3.12+
* Poetry
* Git

## 🚀 Instalação e Setup

1. Clone este repositório:

   ```bash
   git clone https://github.com/vieiraEverton/book-scraper-api.git
   cd book-scraper-api
   ```

2. Habilite venv in-project (opcional, mas recomendado):

   ```bash
   poetry config virtualenvs.in-project true --local
   ```

3. Instale dependências e crie o ambiente virtual:

   ```bash
   poetry install
   ```

4. Crie o arquivo de variáveis de ambiente `.env` na raiz:

   ```dotenv
   SECRET_KEY=uma_chave_bem_grande_e_secreta
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   DATABASE_URL=sqlite:///./data/bookapi.db
   ADMIN_PASSWORD=uma_senha_bem_dificil
   ```

5. Execute a aplicação:

   ```bash
   poetry run uvicorn api.main:app --reload
   ```

   Acesse: [http://127.0.0.1:8000/api/v1/docs](http://127.0.0.1:8000/api/v1/docs)

## 🗂️ Estrutura do Projeto

```
book-scraper-api/
├── api/
│   ├── models/        # SQLModel tables (User, Book…)
│   ├── schemas/       # Pydantic schemas (DTOs)
│   ├── services/      # Lógica de negócio (serviço de users, books…)
│   ├── routers/       # Endpoints agrupados por recursos
│   ├── db.py          # Engine, Session e inicialização SQLite
│   ├── config.py      # Configurações via Pydantic Settings e .env
│   ├── security.py    # JWT, hashing e dependências de segurança
│   └── main.py        # Instância FastAPI, middlewares e startup events
├── data/
│   └── bookapi.db     # Banco SQLite (gerado em runtime)
├── scripts/           # Scripts de scraping e ETL
├── tests/             # Testes automatizados (pytest)
├── .env               # Variáveis de ambiente
├── README.md          # Documentação do projeto
├── pyproject.toml     # Configuração Poetry
└── poetry.lock
```

## 📦 Endpoints Principais

| Método | Rota                              | Descrição                                 |
| ------ | --------------------------------- | ----------------------------------------- |
| GET    | `/api/v1/health`                  | Healthcheck da API                        |
| POST   | `/api/v1/auth/login`              | Retorna JWT para usuário existente        |
| GET    | `/api/v1/books`                   | Lista todos os livros (protegido)         |
| GET    | `/api/v1/books/{id}`              | Detalhes de um livro por ID (protegido)   |
| GET    | `/api/v1/books/search?title=&...` | Busca de livros por título e/ou categoria |
| GET    | `/api/v1/categories`              | Lista todas as categorias                 |

> ⚠️ Os endpoints de livros são protegidos por JWT. Use o token retornado em `Authorization: Bearer <token>`.

## 🔒 Autenticação

1. Faça login:

   ```bash
   curl -X POST \
     http://127.0.0.1:8000/api/v1/auth/login \
     -F "username=admin" -F "password=uma_senha_bem_dificil"
   ```
2. Copie o `access_token` e inclua no header das requisições protegidas:

   ```
   Authorization: Bearer <access_token>
   ```

## 📄 License

Este projeto está licenciado sob a [MIT License](LICENSE).
