import os
import sqlite3
from pathlib import Path

from flask import Flask, request, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "bbs.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            user_id INTEGER,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    # 6주차부터 이어온 DB에 user_id 컬럼이 없으면 추가 (한 번만 실행됨)
    try:
        conn.execute("ALTER TABLE posts ADD COLUMN user_id INTEGER")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()


def get_post_or_404(post_id):
    conn = get_db()
    post = conn.execute(
        "SELECT posts.*, users.username FROM posts "
        "LEFT JOIN users ON posts.user_id = users.id "
        "WHERE posts.id = ?", (post_id,)
    ).fetchone()
    conn.close()
    return post


def require_owner(post):
    if post is None:
        return "글 없음", 404
    if post["user_id"] != session.get("user_id"):
        return "권한 없음", 403
    return None


# ===== 6주차: 목록 (7주차: 작성자 JOIN) =====
@app.route("/")
def index():
    conn = get_db()
    posts = conn.execute("""
        SELECT posts.*, users.username
        FROM posts
        LEFT JOIN users ON posts.user_id = users.id
        ORDER BY posts.id DESC
    """).fetchall()
    conn.close()
    return render_template("list.html", posts=posts)


# ===== 6주차: 상세 =====
@app.route("/posts/<int:post_id>")
def detail(post_id):
    post = get_post_or_404(post_id)
    if post is None:
        return "글 없음", 404
    return render_template("detail.html", post=post)


# ===== 6주차: 작성 (7주차: 로그인 필수 + user_id 저장) =====
@app.route("/new")
def new_form():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("new.html")


@app.route("/posts", methods=["POST"])
def create_post():
    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()

    if not title or not content:
        return redirect(url_for("new_form"))

    conn = get_db()
    conn.execute(
        "INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)",
        (title, content, session["user_id"])
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


# ===== 6주차: 수정 (7주차: 본인 글만) =====
@app.route("/posts/<int:post_id>/edit")
def edit_form(post_id):
    post = get_post_or_404(post_id)
    err = require_owner(post)
    if err:
        return err
    return render_template("edit.html", post=post)


@app.route("/posts/<int:post_id>/edit", methods=["POST"])
def update_post(post_id):
    post = get_post_or_404(post_id)
    err = require_owner(post)
    if err:
        return err

    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()

    conn = get_db()
    conn.execute(
        "UPDATE posts SET title = ?, content = ? WHERE id = ?",
        (title, content, post_id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("detail", post_id=post_id))


# ===== 6주차: 삭제 (7주차: 본인 글만) =====
@app.route("/posts/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    post = get_post_or_404(post_id)
    err = require_owner(post)
    if err:
        return err

    conn = get_db()
    conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


# ===== 7주차: 회원가입 · 로그인 · 로그아웃 =====
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            return render_template("signup.html", error="아이디와 비밀번호를 입력하세요.")

        password_hash = generate_password_hash(password)
        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("signup.html", error="이미 사용 중인 아이디입니다.")
        conn.close()
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))

        return render_template("login.html", error="아이디 또는 비밀번호가 틀립니다.")

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("index"))

from opendata import fetch_air_quality

@app.route("/dashboard")
def dashboard():
    sido = request.args.get("sido", "서울").strip()
    rows, source = fetch_air_quality(sido)
    return render_template(
        "dashboard.html",
        rows=rows,
        sido=sido,
        source=source,
    )

if __name__ == "__main__":
    create_tables()
    app.run(debug=True, port=5001)


