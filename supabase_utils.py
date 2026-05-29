import os
from supabase import create_client

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

def save_result(row):
    supabase.table("results").upsert({
        "game_id": row[0],
        "time": row[1],
        "field": row[2],
        "team1": row[3],
        "team1_name": row[4],
        "score1": row[5],
        "team2": row[6],
        "team2_name": row[7],
        "score2": row[8]
    }).execute()

def delete_result(game_id):
    supabase.table("results").delete().eq("game_id", game_id).execute()

def get_results():
    res = supabase.table("results").select("*").execute()
    return res.data
