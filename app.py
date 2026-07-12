from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

import os
client = MongoClient(os.environ.get("MONGO_URI"))
db = client["MINDEASE"]
users_collection = db["users"]

print("✅ Mongo connected")

from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime

app = Flask(__name__)
app.secret_key = "any_random_string_here"

@app.route("/check")
def check():
    return "SERVER WORKING"

# ---------------- TEMP STORAGE ----------------
moods = []
journals = []

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("app.html")


# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        print("🔥 Signup route triggered")

        username = request.form.get("username")
        password = request.form.get("password")
        print("Username:", username)
        print("Password:", password)

        try:
            existing = users_collection.find_one({"username": username})
            print("Existing user:", existing)

            result = users_collection.insert_one({
                "username": username,
                "password": password
            })

            print("✅ Inserted ID:", result.inserted_id)

        except Exception as e:
            print("❌ ERROR:", e)

        return redirect(url_for("login")) # 👈 This sends them to the login page

    return render_template("signup.html")

    
# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = users_collection.find_one({"username": username, "password": password})

        if user:
            from flask import session
            session["user"] = username  # 👈 Store the username here
            return redirect(url_for("dashboard"))
        else:
            return "Invalid credentials ❌"
    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    from flask import session
    session.pop("user", None) # 👈 Forget the user
    return redirect(url_for("home"))



# ---------------- MOOD PAGE ----------------

@app.route("/mood")
def mood():

    mood = request.args.get("selected_mood", "")

    bg = "#e0f7fa"

    if mood == "happy":
        bg = "#FFF8D6"

    elif mood == "angry":
        bg = "#FFDADA"

    elif mood == "sad":
        bg = "#DCE8FF"

    elif mood == "stressed":
        bg = "#F4E6FF"

    return render_template(
        "moodtracker.html",
        name=session.get("user","Guest"),
        bg=bg
    )


# ---------------- SAVE MOOD ----------------

@app.route("/save_mood", methods=["POST"])
def save_mood():

    mood = request.form.get("mood")

    mood_entry = {
        "username": session.get("user", "Guest"),
        "mood": mood,
        "time": datetime.now().strftime("%B %d, %Y - %I:%M %p")
    }

    db["moods"].insert_one(mood_entry)

    return redirect(url_for("music", mood=mood))


# ---------------- JOURNAL PAGE ----------------
@app.route("/journal")
def journal():
    return render_template("journal.html")

# ---------------- SAVE JOURNAL (No JS Version) ----------------
@app.route("/save_journal", methods=["POST"])
def save_journal():
    from flask import session
    
    # This is how we get data from a standard HTML form
    left_content = request.form.get("leftText")
    right_content = request.form.get("rightText")
    
    username = session.get("user", "Guest")
    full_text = f"{left_content} | {right_content}"

    entry = {
        "username": username,
        "text": full_text,
        "date": datetime.now().strftime("%B %d, %Y - %I:%M %p")
    }

    # Save to MongoDB
    db["journals"].insert_one(entry)

    # Instead of an alert, we just redirect directly to the history page
    return redirect(url_for("journal_history"))


# ---------------- GET JOURNALS ----------------
@app.route("/journal_history")
def journal_history():

    username = session.get("user", "Guest")

    user_entries = list(
        db["journals"]
        .find({"username": username})
        .sort("_id", -1)
    )

    return render_template(
        "journal_history.html",
        entries=user_entries
    )

# ---------------- MUSIC PAGE ----------------
@app.route("/music")
@app.route("/music/<mood>")
def music(mood="happy"):

    spotify_playlists = {

        "happy": {
            "English 🎵": "0jrlHA5UmxRxJjoykf7qRY",
            "Hindi ✌🏻": "37i9dQZF1DWTwbZHrJRIgD",
            "Punjabi🕺🏻": "0xawH3WmFz4PdLGYYn3gpT",
            "South Indian 🎶": "0dPzC4kI939RwZFiMHHDHl"
        },

        "sad": {
            "English Mood Booster": "37i9dQZF1DX3rxVfibe1L0",
            "Hindi Mood Booster": "37i9dQZF1DX5q67ZpWyRrZ",
            "South Indian Feel Good 🌸": "3NF0iDKGPhSfB5tfRpkVlQ"
        },

        "stressed": {
            "Nature Sounds 🌧️": "37i9dQZF1DX4PP3DA4J0N8",
            "Relaxation 🌿": "37i9dQZF1DXebxttQCq0zA",
            "Devotional 🕉️": "7gFVfcFKRzeOH1cfhVdj0A",
            "Instrumental 🎹": "37i9dQZF1DX4sWSpwq3LiO"
        },

        "angry": {
            "Calm Down 🌊": "37i9dQZF1DWU0ScTcjJBdj",
            "Lo-fi ☕": "37i9dQZF1DWYoYGBbGKurt",
            "Meditation 🧘": "37i9dQZF1DWZqd5JICZI0u"
        }

    }

    playlists = spotify_playlists.get(
        mood.lower(),
        spotify_playlists["happy"]
    )

    return render_template(
        "music.html",
        playlists=playlists,
        current_mood=mood
    )


# ---------------- INSIGHTS PAGE ----------------
# ---------------- INSIGHTS PAGE (OPTIMIZED) ----------------
from collections import Counter

@app.route("/insights")
def insights():

    username = session.get("user", "Guest")

    user_journals = list(
        db["journals"].find({"username": username}).sort("_id", -1)
    )

    j_count = len(user_journals)

    m_count = db["moods"].count_documents({"username": username})

    weekly_moods = list(
        db["moods"]
        .find({"username": username})
        .sort("_id", -1)
        .limit(7)
    )

    mood_names = [m["mood"] for m in weekly_moods]

    if mood_names:
        most_mood = Counter(mood_names).most_common(1)[0][0]
    else:
        most_mood = None

    return render_template(
        "insights.html",
        journals=user_journals,
        j_count=j_count,
        m_count=m_count,
        weekly_moods=weekly_moods,
        most_mood=most_mood
    )

if __name__ == "__main__":
    app.run(debug=True)


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
