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
# Team-Namen (zentral)
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
# Resultate speichern / updaten
# row = [game_id, time, field, team1_code, score1, team2_code, score2]
# ---------------------------------------------------------
def save_result(row):
    game_id, time, field, team1_code, score1, team2_code, score2 = row

    supabase.table("results").upsert({
        "game_id": game_id,
        "time": time,
        "field": field,
        "team1": team1_code,
        "team1_name": TEAM_NAMES[team1_code],
        "score1": score1,
        "team2": team2_code,
        "team2_name": TEAM_NAMES[team2_code],
        "score2": score2,
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
    return res.data or []
