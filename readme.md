# TaskSync - Django Migration

TaskSync foi migrado de Streamlit para Django com foco em manter os mesmos dominos de negocio:

- Dashboard estrategico
- Kanban de iniciativas
- Eventos do setor
- Knowledge base (whitepapers, glossario, case studies)
- Empresas target
- Senior advisors

## Stack

- Python 3.12+
- Django 6+
- dj-database-url
- PostgreSQL

## Estrutura Principal

- `config/`: configuracao do projeto Django
- `operations/`: app principal com models, forms, views, urls e admin
- `templates/operations/`: telas server-rendered
- `static/operations/`: estilos globais
- `operations/management/commands/seed_demo_data.py`: seed de dados de exemplo

## Como Rodar

1. Criar e ativar ambiente virtual.
2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. (Opcional) Configurar `.env`:

```env
SECRET_KEY=sua-chave
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
POSTGRES_DB=tasksync
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
# Alternativa: usar uma URL unica
# DATABASE_URL=postgresql://usuario:senha@localhost:5432/tasksync
```

Se `DATABASE_URL` estiver definido, ele sera usado como prioridade.

Sem `DATABASE_URL`, o projeto se comporta assim:

- Se alguma variavel `POSTGRES_*` estiver definida, o Django monta a conexao com PostgreSQL.
- Se nenhuma configuracao de PostgreSQL existir, o ambiente local usa `db.sqlite3` automaticamente.

4. Aplicar migracoes:

```bash
python manage.py migrate
```

5. Popular com dados de exemplo:

```bash
python manage.py seed_demo_data
```

6. Executar servidor:

```bash
python manage.py runserver
```

Abrir: `http://127.0.0.1:8000/`

## Controle de acesso

- O sistema agora abre com tela de login antes do dashboard.
- O login da aplicacao usa apenas o email corporativo cadastrado.
- Apenas emails `@artefact.com` cadastrados em `Authorized emails` no admin podem entrar.

Fluxo recomendado para liberar acesso:

1. Criar um superuser:

```bash
python manage.py createsuperuser
```

2. Entrar em `/admin/`.
3. Cadastrar o email permitido em `Authorized emails`.
4. O usuario Django e criado automaticamente no primeiro acesso, sem senha local.

## Rotas

- `/` Dashboard
- `/login/` Login
- `/tasks/` Kanban
- `/tasks/<id>/` Detalhes da tarefa
- `/events/` Eventos
- `/knowledge/whitepapers/` Whitepapers
- `/knowledge/glossary/` Glossario
- `/knowledge/case-studies/` Case studies
- `/companies/` Empresas target
- `/advisors/` Senior advisors

## Notas da Migracao

- O banco legado do Streamlit (`db.sqlite`) foi preservado.
- O Django agora usa PostgreSQL como banco padrao.
- O arquivo `app.py` antigo permanece no repositorio apenas como referencia.
