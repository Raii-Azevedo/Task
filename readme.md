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
- PostgreSQL (producao) ou SQLite (desenvolvimento)

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
# Producao (PostgreSQL)
# DATABASE_URL=postgresql://usuario:senha@localhost:5432/tasksync
```

Sem `DATABASE_URL`, o projeto usa SQLite em `db.sqlite3`.

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

## Rotas

- `/` Dashboard
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
- O Django usa por padrao `db.sqlite3` para evitar conflito de schema.
- O arquivo `app.py` antigo permanece no repositorio apenas como referencia.
