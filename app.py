import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-key-change-me")


def db():
    if "db" not in g:
        g.db = sqlite3.connect("voting.db")
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(e=None):
    conn = g.pop("db", None)
    if conn:
        conn.close()


def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return redirect("/login")
            if role and session.get("role") != role:
                return "Forbidden", 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


# ---------- Auth ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        f = request.form
        try:
            db().execute(
                "INSERT INTO users (name, student_id, email, password_hash) VALUES (?,?,?,?)",
                (f["name"], f["student_id"], f["email"], generate_password_hash(f["password"])),
            )
            db().commit()
            flash("Registered! Please log in.")
            return redirect("/login")
        except sqlite3.IntegrityError:
            flash("Student ID or email already registered.")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = db().execute(
            "SELECT * FROM users WHERE student_id = ?", (request.form["student_id"],)
        ).fetchone()
        if user and check_password_hash(user["password_hash"], request.form["password"]):
            session.clear()
            session["user_id"], session["role"] = user["id"], user["role"]
            return redirect("/admin" if user["role"] == "admin" else "/")
        flash("Invalid credentials.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------- Voter ----------
@app.route("/")
@login_required()
def dashboard():
    elections = db().execute("SELECT * FROM elections WHERE is_open = 1").fetchall()
    return render_template("dashboard.html", elections=elections)


@app.route("/vote/<int:eid>", methods=["GET", "POST"])
@login_required("voter")
def vote(eid):
    election = db().execute(
        "SELECT * FROM elections WHERE id = ? AND is_open = 1", (eid,)
    ).fetchone()
    if not election:
        return "Election not open", 404
    candidates = db().execute(
        "SELECT * FROM candidates WHERE election_id = ?", (eid,)
    ).fetchall()

    if request.method == "POST":
        cid = int(request.form["candidate_id"])
        if cid not in [c["id"] for c in candidates]:
            return "Invalid candidate", 400
        try:
            with db() as conn:  # one transaction: both inserts succeed or neither
                conn.execute("INSERT INTO ballots_cast VALUES (?,?)", (eid, session["user_id"]))
                conn.execute(
                    "INSERT INTO votes (election_id, candidate_id) VALUES (?,?)", (eid, cid)
                )
            flash("Your vote has been recorded. Thank you!")
            return redirect("/")
        except sqlite3.IntegrityError:
            flash("You have already voted in this election.")
            return redirect("/")
    return render_template("vote.html", election=election, candidates=candidates)


# ---------- Admin ----------
@app.route("/admin", methods=["GET", "POST"])
@login_required("admin")
def admin():
    if request.method == "POST":
        action = request.form["action"]
        if action == "new_election":
            db().execute("INSERT INTO elections (title) VALUES (?)", (request.form["title"],))
        elif action == "add_candidate":
            db().execute(
                "INSERT INTO candidates (election_id, name, position) VALUES (?,?,?)",
                (request.form["election_id"], request.form["name"], request.form["position"]),
            )
        elif action == "toggle":
            db().execute(
                "UPDATE elections SET is_open = 1 - is_open WHERE id = ?",
                (request.form["election_id"],),
            )
        db().commit()
    elections = db().execute("SELECT * FROM elections").fetchall()
    return render_template("admin.html", elections=elections)


@app.route("/results/<int:eid>")
@login_required("admin")
def results(eid):
    election = db().execute("SELECT * FROM elections WHERE id = ?", (eid,)).fetchone()
    rows = db().execute(
        """SELECT c.name, c.position, COUNT(v.id) AS total
           FROM candidates c LEFT JOIN votes v ON v.candidate_id = c.id
           WHERE c.election_id = ? GROUP BY c.id ORDER BY total DESC""",
        (eid,),
    ).fetchall()
    return render_template("results.html", election=election, rows=rows)


if __name__ == "__main__":
    app.run(debug=True)
