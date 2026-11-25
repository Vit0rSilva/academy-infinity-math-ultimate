# Academy Infinite Math Ultimate

Plataforma educacional de Modelagem e Simulação Matemática construída com Flask. Inclui trilha com cinco módulos, quizzes corrigidos no servidor, cadastro/login, persistência de progresso e páginas responsivas.

## Funcionalidades

- Cinco módulos, incluindo **Modelagem Matemática Aplicada**.
- Páginas próprias para catálogo, conteúdo de cada módulo e cada quiz.
- Quizzes com respostas mantidas no backend e aprovação a partir de 70%.
- Cadastro e login com senha protegida por hash; conteúdos e APIs acadêmicas exigem sessão.
- XP calculado pelo melhor resultado de cada módulo, com bônus de conclusão e proteção contra repetição artificial.
- Ofensiva baseada em dias consecutivos com atividade real de estudo.
- Desbloqueio progressivo: o próximo módulo é liberado após a conclusão do anterior.
- Painel do aluno com XP, nível, ofensiva, progresso e histórico de tentativas.
- Simuladores de conjuntos, vetores, transformações, sequências e filas.
- API JSON para módulos, quizzes, autenticação e progresso.

## Executar localmente

Requer Python 3.11 ou superior.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app app run --debug
```

Abra `http://127.0.0.1:5000`.

Sem `DATABASE_URL`, o projeto usa SQLite localmente. Para usar as variáveis do arquivo `.env`, exporte-as no shell ou utilize um carregador de ambiente.

## Banco de dados na Vercel

Use **PostgreSQL serverless**. Neon é a opção recomendada por ter conexão compatível com ambientes serverless e integração simples com a Vercel. Supabase também funciona se for usada a string PostgreSQL com SSL.

No painel da Vercel, configure:

- `DATABASE_URL`: string de conexão PostgreSQL, incluindo `sslmode=require`.
- `SECRET_KEY`: valor longo, aleatório e exclusivo do ambiente.

Não use SQLite na Vercel: o sistema de arquivos das funções é efêmero e não oferece persistência confiável entre execuções.

## Deploy na Vercel

1. Importe este repositório na Vercel.
2. Crie ou conecte um banco Neon.
3. Cadastre `DATABASE_URL` e `SECRET_KEY` em Environment Variables.
4. Faça o deploy. O arquivo `vercel.json` já direciona as rotas para o Flask.

As tabelas são criadas automaticamente na inicialização. Para uma evolução com múltiplos ambientes e alterações frequentes de esquema, adote Flask-Migrate/Alembic.

## Rotas principais

- `/` — experiência completa original.
- `/entrar` — cadastro e login.
- `/painel` — resumo pessoal de XP, ofensiva e progresso.
- `/modulos` e `/modulos/<slug>` — catálogo e aulas.
- `/quiz` e `/quiz/<slug>` — catálogo e avaliação.
- `/api/health` — diagnóstico da aplicação.
- `/api/auth/*` — cadastro, login, sessão e logout.
- `/api/quizzes/<slug>` — questões sem gabarito.
- `/api/quizzes/<slug>/submit` — correção e persistência.

## Testes

```bash
pytest -q
```
