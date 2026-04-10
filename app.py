from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["mindease"]
users_collection = db["users"]

print("✅ Mongo connected")
import pandas as pd

df = pd.read_csv("data.csv")

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
    from flask import session
    # If no one is logged in, default to "Guest"
    display_name = session.get("user", "Guest") 
    return render_template("moodtracker.html", name=display_name)


# ---------------- SAVE MOOD ----------------
@app.route("/save_mood", methods=["POST"])
def save_mood():
    from flask import session
    data = request.json
    username = session.get("user", "Guest")

    # This dictionary is what we save to Mongo
    mood_entry = {
        "username": username,
        "mood": data.get("mood"),
        "time": datetime.now().strftime("%B %d, %Y - %I:%M %p")
    }

    # SAVE TO MONGODB instead of a list
    db["moods"].insert_one(mood_entry)

    return jsonify({"message": "Mood saved successfully"})


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

# ---------------- VIEW HISTORY ----------------
@app.route("/journal_history")
def journal_history():
    from flask import session
    username = session.get("user", "Guest")
    user_entries = list(db["journals"].find({"username": username}).sort("_id", -1))
    return render_template("journal_history.html", entries=user_entries)


# ---------------- GET JOURNALS ----------------
@app.route("/get_journals")
def get_journals():
    return jsonify(journals)

# ---------------- MUSIC PAGE ----------------
@app.route("/music")
@app.route("/music/<mood>") # Adding this lets you pass 'happy', 'sad', etc. in the URL
def music(mood="happy"):
    # Real Spotify Playlist IDs
    spotify_playlists = {
        "happy": "37i9dQZF1EIgG2NEOhqsD7",    
        "sad": "37i9dQZF1DX3rxVfibe1L0",      
        "stressed": "37i9dQZF1DWXe9gFZP0gtP", 
        "angry": "37i9dQZF1EIfTmpqlGn32s"     
    }

    # If the mood isn't in our list, default to 'happy'
    playlist_id = spotify_playlists.get(mood.lower(), "37i9dQZF1EIgG2NEOhqsD7")
    
    return render_template("music.html", playlist_id=playlist_id, current_mood=mood)

# ---------------- INSIGHTS PAGE ----------------
# ---------------- INSIGHTS PAGE (OPTIMIZED) ----------------
@app.route("/insights")
def insights():
    from flask import session
    username = session.get("user", "Guest")

    # 1. Fetch Journals from DB
    user_journals = list(db["journals"].find({"username": username}).sort("_id", -1))
    j_count = len(user_journals)

    # 2. Fetch Moods from DB (This was the missing part!)
    m_count = db["moods"].count_documents({"username": username})

    return render_template("insights.html", 
                           journals=user_journals, 
                           m_count=m_count, 
                           j_count=j_count)


if __name__ == "__main__":
    app.run(debug=True)


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
