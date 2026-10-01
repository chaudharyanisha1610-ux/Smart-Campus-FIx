from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def smart_classify(description):
    text = description.lower()

    if any(word in text for word in ["wifi", "internet", "computer", "network", "login"]):
        category = "IT"
        department = "Technical Support"
    elif any(word in text for word in ["water", "leak", "tap", "toilet"]):
        category = "Maintenance"
        department = "Maintenance"
    elif any(word in text for word in ["fan", "light", "electricity", "switch"]):
        category = "Electrical"
        department = "Electrical Department"
    elif any(word in text for word in ["garbage", "dirty", "dust", "clean"]):
        category = "Cleanliness"
        department = "Housekeeping"
    else:
        category = "General"
        department = "General Administration"

    if any(word in text for word in ["fire", "danger", "emergency", "accident"]):
        priority = "HIGH"
    elif any(word in text for word in ["broken", "not working", "problem", "leak"]):
        priority = "MEDIUM"
    else:
        priority = "LOW"

    return category, priority, department


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            category TEXT,
            priority TEXT,
            department TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]

        category, priority, department = smart_classify(description)

        conn = get_db()
        cursor = conn.execute("""
            INSERT INTO issues
            (title, description, category, priority, department, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, description, category, priority, department, "Reported"))

        issue_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return render_template(
            "report.html",
            success=True,
            issue_id=issue_id,
            category=category,
            priority=priority,
            department=department
        )

    return render_template("report.html", success=False)


@app.route("/track", methods=["GET", "POST"])
def track():
    issue = None

    if request.method == "POST":
        issue_id = request.form["issue_id"]

        conn = get_db()
        issue = conn.execute(
            "SELECT * FROM issues WHERE id = ?", (issue_id,)
        ).fetchone()
        conn.close()

    return render_template("track.html", issue=issue)


@app.route("/admin")
def admin():
    conn = get_db()
    issues = conn.execute(
        "SELECT * FROM issues ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template("admin.html", issues=issues)


@app.route("/update/<int:issue_id>", methods=["POST"])
def update(issue_id):
    status = request.form["status"]

    conn = get_db()
    conn.execute(
        "UPDATE issues SET status = ? WHERE id = ?",
        (status, issue_id)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)