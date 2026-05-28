import sqlite3
import json

DB_FILE = "results.db"
GAMES_FILE = "games.json"

TEAM_NAMES = {
    "A": "Rasselbande",
    "B": "Hüpfigi Hüehner",
    "C": "Hüebelibueb:innen",
    "D": "TV Walperswil",
    "E": "T vou Seerdoof",
    "F": "Wäutklass Chaostruppe",
}

# ---------------------------------------------------------
# INITIALISIERUNG
# ---------------------------------------------------------

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS results (
            game_id TEXT PRIMARY KEY,
            time TEXT,
            field TEXT,
            team1 TEXT,
            team1_name TEXT,
            score1 INTEGER,
            team2 TEXT,
            team2_name TEXT,
            score2 INTEGER
        )
    """)
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# SPEICHERN
# ---------------------------------------------------------

def save_result(row):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO results
        (game_id, time, field, team1, team1_name, score1, team2, team2_name, score2)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, row)
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# LÖSCHEN
# ---------------------------------------------------------

def delete_result(game_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM results WHERE game_id = ?", (game_id,))
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# LADEN
# ---------------------------------------------------------

def get_results():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM results")
    rows = c.fetchall()
    conn.close()

    results = []
    for r in rows:
        results.append({
            "game_id": r[0],
            "time": r[1],
            "field": "Völkerball" if r[2] == "Voelkerball" else r[2],
            "team1": r[3],
            "team_name_1": r[4],
            "score1": r[5],
            "team2": r[6],
            "team_name_2": r[7],
            "score2": r[8],
        })
    return results

# ---------------------------------------------------------
# SPIELPLAN
# ---------------------------------------------------------

def load_games():
    with open(GAMES_FILE, "r", encoding="utf-8") as f:
        games = json.load(f)

    for g in games.values():
        if g["field"] == "Voelkerball":
            g["field"] = "Völkerball"

    return games
