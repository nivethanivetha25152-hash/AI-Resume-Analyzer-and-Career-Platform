from flask import Flask, render_template, request, redirect, session, flash, send_file
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from ai_engine import analyze_resume
from reportlab.pdfgen import canvas
import os
from reportlab.pdfgen import canvas
from flask import send_file
def admin_required():
    if "admin" not in session:
        return redirect("/admin_login")

app = Flask(__name__)
app.secret_key = "resume_project"

# Upload folder
UPLOAD_FOLDER = "static/uploads"
REPORT_FOLDER = "static/reports"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# MySQL Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "resume_analyzer"

mysql = MySQL(app)

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

        if user:
            flash("Email already exists")
            return redirect("/register")

        hashed = generate_password_hash(password)

        cur.execute(
            "INSERT INTO users(name,email,password) VALUES(%s,%s,%s)",
            (name, email, hashed)
        )

        mysql.connection.commit()
        cur.close()

        flash("Registration Successful")
        return redirect("/login")

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[3], password):
            session["user_id"] = user[0]
            session["name"] = user[1]
            return redirect("/dashboard")

        flash("Invalid Email or Password")

    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM resumes WHERE user_id=%s", (session["user_id"],))
    total = cur.fetchone()[0]

    cur.execute("SELECT AVG(score) FROM resumes WHERE user_id=%s", (session["user_id"],))
    avg = cur.fetchone()[0]

    if avg is None:
        avg = 0

    cur.execute("""
        SELECT recommended_role
        FROM resumes
        WHERE user_id=%s
        ORDER BY id DESC
        LIMIT 1
    """, (session["user_id"],))

    role = cur.fetchone()

    latest_role = role[0] if role else "Not Available"

    # Pie chart values (temporary)
    excellent = 3
    good = 2
    poor = 1

    cur.close()

    return render_template(
        "dashboard.html",
        total=total,
        average=round(avg, 2),
        role=latest_role,
        name=session["name"],
        excellent=excellent,
        good=good,
        poor=poor
    )
# ---------------- ANALYZE (REAL AI) ----------------
@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        file = request.files["resume"]

        if file.filename == "":
            flash("Select Resume")
            return redirect("/analyze")

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        score, role, found_skills, missing, suggestions = analyze_resume(filepath)

        # REAL AI CALL
        score, role, found_skills, missing, suggestions = analyze_resume(filepath)

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO resumes(user_id,file_name,score,recommended_role)
            VALUES(%s,%s,%s,%s)
        """, (session["user_id"], filename, score, role))

        mysql.connection.commit()

        resume_id = cur.lastrowid

        cur.execute("""
            INSERT INTO analysis_results(resume_id,skills,missing_skills,suggestions)
            VALUES(%s,%s,%s,%s)
        """, (
            resume_id,
            ",".join(found_skills),
            ",".join(missing),
            ",".join(suggestions)
        ))

        mysql.connection.commit()
        cur.close()

        return render_template(
            "analyze.html",
            score=score,
            role=role,
            skills=found_skills,
            suggestions=suggestions,
            resume_id=resume_id
        )

    return render_template("analyze.html")

# ---------------- DOWNLOAD REPORT (NEW FEATURE) ----------------
@app.route("/download/<int:resume_id>")
def download(resume_id):

    file_path = f"static/reports/report_{resume_id}.pdf"

    c = canvas.Canvas(file_path)
    c.drawString(100, 800, "AI Resume Analysis Report")
    c.drawString(100, 780, f"Resume ID: {resume_id}")
    c.drawString(100, 760, "Generated by AI System")
    c.save()

    return send_file(file_path, as_attachment=True)

# ---------------- HISTORY ----------------
@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect("/login")

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM resumes WHERE user_id=%s ORDER BY id DESC", (session["user_id"],))
    history = cur.fetchall()
    cur.close()

    return render_template("history.html", history=history)

# ---------------- ADMIN LOGIN (NEW SECURITY) ----------------
@app.route("/admin_login", methods=["GET","POST"])
def admin_login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/admin")

        flash("Invalid admin login")

    return render_template("admin_login.html")
# ---------------- ADMIN PANEL ----------------
@app.route("/admin")
def admin():

    # ALWAYS CHECK ADMIN LOGIN
    if "admin" not in session:
        return redirect("/admin_login")

    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM resumes")
    total_resumes = cur.fetchone()[0]

    cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    cur.close()

    return render_template(
        "admin.html",
        total_users=total_users,
        total_resumes=total_resumes,
        users=users
    )

# ---------------- DELETE RESUME ----------------
@app.route("/delete_resume/<int:id>")
def delete_resume(id):

    if "user_id" not in session:
        return redirect("/login")

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM analysis_results WHERE resume_id=%s", (id,))
    cur.execute("DELETE FROM resumes WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()

    flash("Resume Deleted Successfully")
    return redirect("/history")

# ---------------- DELETE USER ----------------
@app.route("/delete_user/<int:id>", methods=["GET", "POST"])
def delete_user(id):

    if "admin" not in session:
        return redirect("/admin_login")

    # extra security check
    password = request.args.get("password")

    if password != "admin123":
        flash("Password confirmation failed")
        return redirect("/admin")

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()

    flash("User Deleted Successfully")
    return redirect("/admin")
# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/admin_login")

# ---------------- RUN ----------------
if __name__ == "__main__":
    os.makedirs("static/uploads", exist_ok=True)
    os.makedirs("static/reports", exist_ok=True)
    app.run(debug=True)