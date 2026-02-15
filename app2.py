from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("app.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        return f"""
        <h2>Signup Successful ✅</h2>
        <p>Username: {username}</p>
        <a href='/login'>Go to Login</a>
        """

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    return redirect(url_for("home"))

# ---------------- MOOD TRACKER ----------------
@app.route("/mood")
def mood():
    return render_template("mood.html")


# ---------------- JOURNAL ----------------
@app.route("/journal")
def journal():
    return render_template("journal.html")


# ---------------- MUSIC ----------------
@app.route("/music")
def music():
    return render_template("music.html")


# ---------------- RELAXATION ----------------
@app.route("/relax")
def relax():
    return render_template("relax.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8000)
