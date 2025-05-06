# Aren Koraian
# 5/6/25
# Tic-Tac-Toe
############################

# ChatGPT tic tac toe

import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, redirect, url_for, request, session

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATA_FILE = "users.json"

# Game state
board = [[" " for _ in range(3)] for _ in range(3)]
current_player = "X"

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=2)

def check_winner(b):
    for i in range(3):
        if b[i][0] == b[i][1] == b[i][2] != " ":
            return b[i][0]
        if b[0][i] == b[1][i] == b[2][i] != " ":
            return b[0][i]
    if b[0][0] == b[1][1] == b[2][2] != " ":
        return b[0][0]
    if b[0][2] == b[1][1] == b[2][0] != " ":
        return b[0][2]
    return None

def is_full(b):
    return all(cell != " " for row in b for cell in row)

@app.route("/")
def index():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    users = load_users()
    user_data = users.get(username, {
        "x_score": 0,
        "o_score": 0,
        "games_played": 0
    })

    x_score = user_data.get("x_score", 0)
    o_score = user_data.get("o_score", 0)
    games_played = user_data.get("games_played", 0)

    # Calculate percentages (avoid division by zero)
    x_win_percent = round((x_score / games_played) * 100, 1) if games_played else 0.0
    o_win_percent = round((o_score / games_played) * 100, 1) if games_played else 0.0

    winner = check_winner(board)
    tie = is_full(board) and not winner

    return render_template(
        "index.html",
        board=board,
        current=current_player,
        winner=winner,
        tie=tie,
        username=username,
        x_score=x_score,
        o_score=o_score,
        games_played=games_played,
        x_win_percent=x_win_percent,
        o_win_percent=o_win_percent
    )

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()

        if username in users:
            return render_template("register.html", error="Username already exists.")

        users[username] = {
            "password": generate_password_hash(password),
            "x_score": 0,
            "o_score": 0,
            "games_played": 0
        }

        save_users(users)
        session["username"] = username
        return redirect(url_for("index"))

    return render_template("register.html", error=None)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()

        if username in users and check_password_hash(users[username]["password"], password):
            session["username"] = username
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid credentials.")
    
    return render_template("login.html", error=None)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/move/<int:row>/<int:col>")
def move(row, col):
    global board, current_player
    if "username" not in session:
        return redirect(url_for("login"))

    users = load_users()
    username = session["username"]

    if board[row][col] == " " and not check_winner(board):
        board[row][col] = current_player
        winner = check_winner(board)
        if winner:
            if winner == "X":
                users[username]["x_score"] += 1
            elif winner == "O":
                users[username]["o_score"] += 1
            users[username]["games_played"] += 1
            save_users(users)
        elif not is_full(board):
            current_player = "O" if current_player == "X" else "X"

    return redirect(url_for("index"))

@app.route("/reset")
def reset():
    global board, current_player
    board = [[" " for _ in range(3)] for _ in range(3)]
    current_player = "X"
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
