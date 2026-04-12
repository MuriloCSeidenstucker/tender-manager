# Tender Manager

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg)](https://www.docker.com/)
[![Pytest](https://img.shields.io/badge/tests-pytest-0A9EDC.svg)](https://pytest.org/)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub_Actions-2088FF.svg)](./.github/workflows/pipeline.yaml)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](./LICENSE)

Tender Manager é um MVP de estudo voltado a portfólio para gerenciamento de licitações. A aplicação permite cadastrar usuários, registrar empresas, acompanhar licitações por empresa e visualizar métricas consolidadas em um dashboard anual.

## Sumário

- [Visão Geral](#visao-geral)
- [Funcionalidades](#funcionalidades)
- [Stack Utilizada](#stack-utilizada)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Como Fazer um Fork e Testar](#como-fazer-um-fork-e-testar)
- [Pré-requisitos](#pre-requisitos)
- [Configuração do Ambiente](#configuracao-do-ambiente)
- [Executando com Docker](#executando-com-docker)
- [Executando Localmente com Poetry](#executando-localmente-com-poetry)
- [Como Testar o Frontend](#como-testar-o-frontend)
- [Como Validar que a Aplicação Funcionou](#como-validar-que-a-aplicacao-funcionou)
- [Rodando os Testes](#rodando-os-testes)
- [Variáveis de Ambiente](#variaveis-de-ambiente)
- [Pipeline e Qualidade](#pipeline-e-qualidade)
- [Licença](#licenca)

## Visão Geral

O projeto foi construído para simular um fluxo básico de gestão de licitações:

- o usuário cria uma conta e faz login
- cadastra empresas vinculadas ao seu usuário
- registra licitações relacionadas a cada empresa
- acompanha o status e o resultado dessas licitações
- consulta um dashboard com métricas por ano

O backend foi desenvolvido com FastAPI e SQLAlchemy assíncrono. O frontend é uma interface estática em HTML, CSS e JavaScript que consome a API.

## Funcionalidades

- Cadastro de usuário
- Login com autenticação via JWT
- Atualização de perfil e senha
- Exclusão de conta
- Cadastro, listagem, edição e exclusão de empresas
- Cadastro, listagem, edição e exclusão de licitações por empresa
- Filtros de consulta para empresas e licitações
- Dashboard com total de licitações, vitórias e valor arrecadado por ano
- Documentação automática da API via Swagger

## Stack Utilizada

### Backend

- Python 3.13
- FastAPI
- SQLAlchemy Async
- Alembic
- JWT
- Pydantic Settings

### Banco de dados

- PostgreSQL

### Frontend

- HTML
- CSS
- JavaScript

### Testes e qualidade

- Pytest
- Pytest Asyncio
- Pytest Cov
- Factory Boy
- Freezegun
- Testcontainers
- Black
- isort
- Pylint
- pre-commit

### Infraestrutura

- Docker
- Docker Compose
- GitHub Actions

## Estrutura do Projeto

```text
tender-manager/
|- .github/workflows/   # pipeline de CI
|- frontend/            # interface web estática
|- migrations/          # migrações do banco com Alembic
|- src/
|  |- infra/            # entidades e configuração de banco
|  |- routers/          # rotas da API
|  |- schemas/          # contratos de entrada e saída
|  |- services/         # regras de negócio
|  |- app.py            # ponto de entrada da aplicação
|  |- settings.py       # configurações via variáveis de ambiente
|- tests/               # testes automatizados
|- compose.yaml         # orquestração com Docker
|- Dockerfile           # imagem da aplicação
|- pyproject.toml       # dependências e tarefas do projeto
```

## Como Fazer um Fork e Testar

### 1. Fazer o fork no GitHub

1. Acesse o repositório original no GitHub.
2. Clique em `Fork`.
3. Escolha sua conta ou organização de destino.

### 2. Clonar o seu fork

```bash
git clone https://github.com/SEU-USUARIO/tender-manager.git
cd tender-manager
```

### 3. Configurar o ambiente

Crie o arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

No Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

### 4. Subir a aplicação

O caminho recomendado é usar Docker:

```bash
docker-compose up --build
```

### 5. Abrir a API e o frontend

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- Frontend: abrir a pasta no VS Code e iniciar o `Live Server` no arquivo `frontend/index.html`

## Pré-requisitos

Para executar o projeto com conforto, tenha instalado:

- Git
- Docker
- Docker Compose
- Python 3.13
- Poetry
- VS Code
- Extensão `Live Server` no VS Code

## Configuração do Ambiente

O projeto utiliza variáveis de ambiente carregadas a partir do arquivo `.env`.

Exemplo base:

```env
POSTGRES_DB=app_db
POSTGRES_USER=app_user
POSTGRES_PASSWORD=your_password_here

DATABASE_URL=postgresql+psycopg://app_user:your_password_here@tendermanager_database:5432/app_db

SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Observação importante:

- o `DATABASE_URL` acima está pronto para o ambiente Docker
- se você rodar a aplicação localmente sem containers, o host do banco provavelmente precisará ser `localhost`

## Executando com Docker

Esta é a forma principal recomendada para testar o projeto.

### 1. Subir os containers

```bash
docker-compose up --build
```

Esse comando sobe:

- um container PostgreSQL
- um container da aplicação FastAPI

### 2. Acessar a API

Depois que os containers estiverem prontos:

- API: `http://localhost:8000`
- Documentação Swagger: `http://localhost:8000/docs`
- Documentação ReDoc: `http://localhost:8000/redoc`

### 3. O que acontece na subida da aplicação

Ao iniciar o container da aplicação, o projeto:

- executa as migrações com Alembic
- sobe o servidor Uvicorn na porta `8000`

### 4. Parar os containers

```bash
docker-compose down
```

## Executando Localmente com Poetry

Se você preferir rodar sem Docker, use este fluxo como alternativa.

### 1. Instalar dependências

```bash
poetry install --with dev
```

### 2. Ajustar o `.env` para execução local

Exemplo:

```env
POSTGRES_DB=app_db
POSTGRES_USER=app_user
POSTGRES_PASSWORD=your_password_here
DATABASE_URL=postgresql+psycopg://app_user:your_password_here@localhost:5432/app_db
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Executar as migrações

```bash
poetry run alembic upgrade head
```

### 4. Subir a API

```bash
poetry run uvicorn src.app:app --reload
```

Depois disso:

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

## Como Testar o Frontend

O frontend deste projeto é estático e foi utilizado com a extensão `Live Server` no VS Code.

### Passo a passo

1. Abra o repositório no VS Code.
2. Instale ou habilite a extensão `Live Server`.
3. Abra o arquivo `frontend/index.html`.
4. Clique em `Open with Live Server`.

Importante:

- a API deve estar rodando em `http://localhost:8000`
- o frontend faz requisições para esse endereço

## Como Validar que a Aplicação Funcionou

Roteiro de validação:

1. Acesse `http://localhost:8000` e confirme a resposta `Hello World!`
2. Acesse `http://localhost:8000/docs` e verifique se a documentação da API abriu
3. Abra o frontend com Live Server
4. Crie uma conta
5. Faça login
6. Cadastre uma empresa
7. Cadastre uma licitação para essa empresa
8. Acesse o dashboard e confira as métricas

## Rodando os Testes

Para executar a suíte de testes:

```bash
poetry run task test
```

Ou, se preferir:

```bash
poetry run pytest -s -x --cov=src -vv
```

Observação importante:

- os testes utilizam `testcontainers`
- portanto, o Docker deve estar instalado e em execução

## Variáveis de Ambiente

### Banco de dados

- `POSTGRES_DB`: nome do banco PostgreSQL
- `POSTGRES_USER`: usuário do banco
- `POSTGRES_PASSWORD`: senha do banco
- `DATABASE_URL`: URL de conexão usada pela aplicação

### Autenticação

- `SECRET_KEY`: chave usada para assinar os tokens JWT
- `ALGORITHM`: algoritmo de assinatura do token
- `ACCESS_TOKEN_EXPIRE_MINUTES`: tempo de expiração do token em minutos

## Pipeline e Qualidade

O projeto possui pipeline em [`.github/workflows/pipeline.yaml`](./.github/workflows/pipeline.yaml).

O workflow executa:

- checkout do repositório
- configuração do Python 3.13
- instalação do Poetry
- validação do lockfile
- instalação das dependências
- execução dos testes

Comandos úteis para desenvolvimento:

```bash
poetry run task lint
poetry run task test
pre-commit install
```

## Endpoints Principais

Alguns endpoints importantes da API:

- `POST /users/` cria um usuário
- `POST /auth/token` autentica e retorna um token JWT
- `POST /auth/refresh_token` renova o token
- `POST /companies/` cria uma empresa
- `GET /companies/` lista empresas do usuário autenticado
- `POST /companies/{company_id}/tenders/` cria uma licitação
- `GET /companies/{company_id}/tenders/` lista licitações da empresa
- `GET /dashboard/metrics` retorna métricas por ano

Para explorar todos os contratos de requisição e resposta, use:

- `http://localhost:8000/docs`

## Licença

Este projeto está licenciado sob os termos da licença MIT. Consulte o arquivo [LICENSE](./LICENSE) para mais detalhes.
