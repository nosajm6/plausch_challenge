import streamlit as st
from supabase import create_client
import pandas as pd
import os

# ---------------------------------------------------------
# Supabase Client
# ---------------------------------------------------------
supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

# ---------------------------------------------------------
# DB Funktionen
# ---------------------------------------------------------
def load_games():
    res = supabase.table("games").select("*").order("game_id").execute()
    return res.data

def update_result(game_id, score1, score2):
    supabase.table("games").update({
        "score1": score1,
        "score2": score2
    }).eq("game_id", game_id).execute()

def delete_result(game_id):
    supabase.table("games").update({
        "score1": None,
        "score2": None
    }).eq("game_id", game_id).execute()

# ---------------------------------------------------------
# Login
# ---------------------------------------------------------
ADMIN_PASSWORD = "admin123"

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    st.title("Admin‑Bereich – Login")

    pw = st.text_input("Passwort eingeben", type="password")

    if st.button("Login"):
        if pw == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.success("Erfolgreich eingeloggt")
            st.rerun()
        else:
            st.error("Falsches Passwort")

    st.stop()

# ---------------------------------------------------------
# Admin UI
# ---------------------------------------------------------
st.title("Admin‑Bereich – Resultate verwalten")

if st.button("Logout"):
    st.session_state.admin_logged_in = False
    st.rerun()

games = load_games()

# ---------------------------------------------------------
# Resultate Tabelle
# ---------------------------------------------------------
st.markdown("## 📊 Alle Resultate")

df = pd.DataFrame(games)
st.dataframe(df, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# Resultate bearbeiten / löschen
# ---------------------------------------------------------
st.markdown("## ✏️ Resultate bearbeiten oder löschen")

for g in games:
    game_id = g["game_id"]
    team1 = g["team_name_1"]
    team2 = g["team_name_2"]

    st.markdown(f"### Spiel {game_id}: {team1} vs {team2}")

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        new_score1 = st.number_input(
            f"{team1} Punkte",
            min_value=0,
            value=g["score1"] if g["score1"] is not None else 0,
            key=f"edit_{game_id}_s1"
        )

    with col2:
        new_score2 = st.number_input(
            f"{team2} Punkte",
            min_value=0,
            value=g["score2"] if g["score2"] is not None else 0,
            key=f"edit_{game_id}_s2"
        )

    with col3:
        if st.button("Speichern", key=f"save_{game_id}"):
            update_result(game_id, int(new_score1), int(new_score2))
            st.success("Resultat aktualisiert")
            st.rerun()

        if st.button("Löschen", key=f"delete_{game_id}"):
            delete_result(game_id)
            st.warning("Resultat gelöscht")
            st.rerun()

    st.markdown("---")
