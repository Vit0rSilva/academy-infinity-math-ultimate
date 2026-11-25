import os
from datetime import datetime, timedelta, timezone
from functools import wraps
from zoneinfo import ZoneInfo

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from werkzeug.security import check_password_hash, generate_password_hash

from data import MODULES, QUIZZES, get_module

db = SQLAlchemy()
BAHIA_TZ = ZoneInfo("America/Bahia")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def public(self):
        return {"id": self.id, "name": self.name, "email": self.email}


class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    module_slug = db.Column(db.String(80), nullable=False)
    best_score = db.Column(db.Integer, default=0, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    __table_args__ = (UniqueConstraint("user_id", "module_slug", name="uq_progress_user_module"),)

    def public(self):
        return {
            "module_slug": self.module_slug,
            "best_score": self.best_score or 0,
            "completed": bool(self.completed),
        }


class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    module_slug = db.Column(db.String(80), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    activity_date = db.Column(db.Date, nullable=False, index=True)
    activity_kind = db.Column(db.String(40), nullable=False)
    module_slug = db.Column(db.String(80))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    __table_args__ = (UniqueConstraint("user_id", "activity_date", name="uq_activity_user_date"),)


def bahia_today():
    return datetime.now(BAHIA_TZ).date()


def get_current_user():
    user_id = session.get("user_id")
    return db.session.get(User, user_id) if user_id else None


def progress_map(user):
    if not user:
        return {}
    return {item.module_slug: item for item in Progress.query.filter_by(user_id=user.id).all()}


def longest_streak(days):
    if not days:
        return 0
    ascending = sorted(set(days))
    longest = current = 1
    for previous, current_day in zip(ascending, ascending[1:]):
        if current_day - previous == timedelta(days=1):
            current += 1
            longest = max(longest, current)
        else:
            current = 1
    return longest


def calculate_streak(activity_dates, today=None):
    today = today or bahia_today()
    days = sorted(set(activity_dates), reverse=True)
    if not days or days[0] < today - timedelta(days=1):
        return 0, longest_streak(days)
    streak = 1
    for newer, older in zip(days, days[1:]):
        if newer - older == timedelta(days=1):
            streak += 1
        else:
            break
    return streak, longest_streak(days)


def build_module_states(user):
    records = progress_map(user)
    states = []
    previous_completed = True
    for module in MODULES:
        record = records.get(module["slug"])
        unlocked = bool(user) and previous_completed
        state = {
            **module,
            "unlocked": unlocked,
            "completed": bool(record and record.completed),
            "best_score": record.best_score if record else 0,
        }
        states.append(state)
        previous_completed = state["completed"]
    return states


def build_user_stats(user):
    if not user:
        return {
            "xp": 0,
            "streak": 0,
            "longest_streak": 0,
            "completed_modules": 0,
            "total_modules": len(MODULES),
            "progress_percent": 0,
            "level": 1,
        }
    records = list(progress_map(user).values())
    score_total = sum(item.best_score or 0 for item in records)
    completion_bonus = sum(50 for item in records if item.completed)
    xp = score_total + completion_bonus
    completed = sum(1 for item in records if item.completed)
    activity_dates = [row.activity_date for row in UserActivity.query.filter_by(user_id=user.id).all()]
    streak, longest = calculate_streak(activity_dates)
    return {
        "xp": xp,
        "streak": streak,
        "longest_streak": longest,
        "completed_modules": completed,
        "total_modules": len(MODULES),
        "progress_percent": round(score_total / len(MODULES)),
        "level": 1 + xp // 250,
    }


def record_activity(user, kind, module_slug=None):
    today = bahia_today()
    existing = UserActivity.query.filter_by(user_id=user.id, activity_date=today).first()
    if not existing:
        db.session.add(
            UserActivity(
                user_id=user.id,
                activity_date=today,
                activity_kind=kind,
                module_slug=module_slug,
            )
        )


def module_is_unlocked(user, slug):
    return any(state["slug"] == slug and state["unlocked"] for state in build_module_states(user))


def safe_next_url(value):
    return value if value and value.startswith("/") and not value.startswith("//") else ""


def page_login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not get_current_user():
            return redirect(url_for("login_page", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def api_login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not get_current_user():
            return jsonify(error="Entre na sua conta para continuar.", auth_required=True), 401
        return view(*args, **kwargs)

    return wrapped


def create_app(test_config=None):
    app = Flask(__name__)
    database_url = os.getenv("DATABASE_URL", "sqlite:///academy.db")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-change-me"),
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("VERCEL") == "1",
    )
    if test_config:
        app.config.update(test_config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.context_processor
    def inject_account_context():
        user = get_current_user()
        return {"current_user": user, "stats": build_user_stats(user)}

    @app.get("/")
    def home():
        user = get_current_user()
        return render_template("index.html", modules=MODULES, module_states=build_module_states(user))

    @app.get("/entrar")
    def login_page():
        next_url = safe_next_url(request.args.get("next", ""))
        if get_current_user():
            return redirect(next_url or url_for("dashboard"))
        return render_template("auth.html", next_url=next_url)

    @app.get("/painel")
    @page_login_required
    def dashboard():
        user = get_current_user()
        attempts = (
            QuizAttempt.query.filter_by(user_id=user.id)
            .order_by(QuizAttempt.created_at.desc())
            .limit(5)
            .all()
        )
        return render_template(
            "dashboard.html",
            module_states=build_module_states(user),
            recent_attempts=attempts,
            module_titles={module["slug"]: module["title"] for module in MODULES},
        )

    @app.get("/modulos")
    def modules_page():
        return render_template("modules.html", module_states=build_module_states(get_current_user()))

    @app.get("/modulos/<slug>")
    @page_login_required
    def module_detail(slug):
        module = get_module(slug)
        if not module:
            return render_template("404.html"), 404
        user = get_current_user()
        if not module_is_unlocked(user, slug):
            return redirect(url_for("dashboard", locked=slug))
        record_activity(user, "module_view", slug)
        db.session.commit()
        return render_template("module_detail.html", module=module)

    @app.get("/quiz")
    @page_login_required
    def quizzes_page():
        return render_template("quizzes.html", module_states=build_module_states(get_current_user()))

    @app.get("/quiz/<slug>")
    @page_login_required
    def quiz_detail(slug):
        module = get_module(slug)
        user = get_current_user()
        if not module or slug not in QUIZZES:
            return render_template("404.html"), 404
        if not module_is_unlocked(user, slug):
            return redirect(url_for("dashboard", locked=slug))
        return render_template("quiz.html", module=module)

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", database=db.engine.url.get_backend_name())

    @app.get("/api/modules")
    def api_modules():
        return jsonify(build_module_states(get_current_user()))

    @app.get("/api/modules/<slug>")
    @api_login_required
    def api_module(slug):
        module = get_module(slug)
        if not module:
            return jsonify(error="Módulo não encontrado."), 404
        if not module_is_unlocked(get_current_user(), slug):
            return jsonify(error="Conclua o módulo anterior para desbloquear este conteúdo."), 403
        return jsonify(module)

    @app.get("/api/quizzes/<slug>")
    @api_login_required
    def api_quiz(slug):
        questions = QUIZZES.get(slug)
        if not questions:
            return jsonify(error="Quiz não encontrado."), 404
        if not module_is_unlocked(get_current_user(), slug):
            return jsonify(error="Conclua o módulo anterior para desbloquear este quiz."), 403
        safe_questions = [{k: v for k, v in question.items() if k != "answer"} for question in questions]
        return jsonify(module=get_module(slug), questions=safe_questions)

    @app.post("/api/quizzes/<slug>/submit")
    @api_login_required
    def submit_quiz(slug):
        questions = QUIZZES.get(slug)
        user = get_current_user()
        if not questions:
            return jsonify(error="Quiz não encontrado."), 404
        if not module_is_unlocked(user, slug):
            return jsonify(error="Conclua o módulo anterior para desbloquear este quiz."), 403
        payload = request.get_json(silent=True) or {}
        answers = payload.get("answers")
        if not isinstance(answers, list) or len(answers) != len(questions):
            return jsonify(error="Envie uma resposta para cada questão."), 400

        results = []
        score = 0
        for question, answer in zip(questions, answers):
            correct = answer == question["answer"]
            score += int(correct)
            results.append(
                {
                    "id": question["id"],
                    "correct": correct,
                    "correct_answer": question["answer"],
                    "explanation": question["explanation"],
                }
            )

        percentage = round(score * 100 / len(questions))
        old_stats = build_user_stats(user)
        db.session.add(QuizAttempt(user_id=user.id, module_slug=slug, score=score, total=len(questions)))
        progress = Progress.query.filter_by(user_id=user.id, module_slug=slug).first()
        if not progress:
            progress = Progress(user_id=user.id, module_slug=slug, best_score=0, completed=False)
            db.session.add(progress)
        progress.best_score = max(progress.best_score or 0, percentage)
        progress.completed = progress.completed or percentage >= 70
        record_activity(user, "quiz_submit", slug)
        db.session.commit()
        new_stats = build_user_stats(user)

        return jsonify(
            score=score,
            total=len(questions),
            percentage=percentage,
            passed=percentage >= 70,
            results=results,
            saved=True,
            xp_earned=new_stats["xp"] - old_stats["xp"],
            stats=new_stats,
            modules=build_module_states(user),
        )

    @app.post("/api/auth/register")
    def register():
        payload = request.get_json(silent=True) or {}
        name = str(payload.get("name", "")).strip()
        email = str(payload.get("email", "")).strip().lower()
        password = str(payload.get("password", ""))
        if len(name) < 2 or "@" not in email or len(password) < 6:
            return jsonify(error="Informe nome, e-mail válido e senha com ao menos 6 caracteres."), 400
        if User.query.filter_by(email=email).first():
            return jsonify(error="Este e-mail já está cadastrado."), 409
        user = User(name=name, email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        session.clear()
        session["user_id"] = user.id
        return jsonify(user=user.public(), stats=build_user_stats(user)), 201

    @app.post("/api/auth/login")
    def login():
        payload = request.get_json(silent=True) or {}
        email = str(payload.get("email", "")).strip().lower()
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, str(payload.get("password", ""))):
            return jsonify(error="E-mail ou senha inválidos."), 401
        session.clear()
        session["user_id"] = user.id
        return jsonify(user=user.public(), stats=build_user_stats(user))

    @app.post("/api/auth/logout")
    def logout():
        session.clear()
        return jsonify(ok=True)

    @app.get("/api/auth/me")
    def me():
        user = get_current_user()
        if not user:
            return jsonify(user=None, stats=build_user_stats(None), progress=[], modules=build_module_states(None))
        return jsonify(
            user=user.public(),
            stats=build_user_stats(user),
            progress=[item.public() for item in progress_map(user).values()],
            modules=build_module_states(user),
        )

    @app.get("/api/progress")
    @api_login_required
    def api_progress():
        user = get_current_user()
        return jsonify(stats=build_user_stats(user), modules=build_module_states(user))

    @app.errorhandler(404)
    def not_found(_error):
        if request.path.startswith("/api/"):
            return jsonify(error="Recurso não encontrado."), 404
        return render_template("404.html"), 404

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
