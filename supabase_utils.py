import os
from supabase import create_client

# ---------------------------------------------------------
# Supabase Client
# ---------------------------------------------------------
supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

# ---------------------------------------------------------
# Team-Namen (zentral für ganze App)
# ---------------------------------------------------------
TEAM_NAMES = {
    "A": "Rasselbande",
    "B": "Hüpfigi Hüehner",
    "C": "Hüebelibueb:innen",
    "D": "TV Walperswil",
    "E": "T vou Seerdoof",
    "F": "Wäutklass Chaostruppe",
}

# ---------------------------------------------------------
# Resultate speichern
# ---------------------------------------------------------
def save_result(row):
    supabase.table("results").upsert({
        "game_id": row[0],
        "time": row[1],
        "field": row[2],
        "team1": row[3],
        "team1_name": TEAM_NAMES[row[3]],
        "score1": row[5],
        "team2": row[6],
        "team2_name": TEAM_NAMES[row[6]],
        "score2": row[8]
    }).execute()

# ---------------------------------------------------------
# Resultat löschen
# ---------------------------------------------------------
def delete_result(game_id):
    supabase.table("results").delete().eq("game_id", game_id).execute()

# ---------------------------------------------------------
# Resultate laden
# ---------------------------------------------------------
def get_results():
    res = supabase.table("results").select("*").execute()
    return res.data
