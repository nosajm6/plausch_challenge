import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
from supabase import create_client
import os

# ---------------------------------------------------------
# Streamlit Setup
# ---------------------------------------------------------
st.set_page_config(page_title="Plausch Challenge", layout="wide")
st_autorefresh(interval=5000, key="refresh")

st.title("Plausch Challenge – Live Rangliste & Spielplan")
st.markdown("Die Seite aktualisiert sich automatisch, sobald neue Resultate gemeldet werden.")

# ---------------------------------------------------------
# Supabase Client (Railway-kompatibel!)
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

# ---------------------------------------------------------
# Team-Namen (Mapping)
# ---------------------------------------------------------
TEAM_NAMES = {
    "A": "Team A",
    "B": "Team B",
    "C": "Team C",
    "D": "Team D",
    "E": "Team E",
    "F": "Team F",
    "G": "Team G",
    "H": "Team H",
}

teams = sorted(TEAM_NAMES.values())

# ---------------------------------------------------------
# Daten laden
# ---------------------------------------------------------
games = load_games()

# ---------------------------------------------------------
# RANGLISTE
# ---------------------------------------------------------
rangliste = pd.DataFrame({"Team": teams, "Punkte": 0})

for g in games:
    if g["score1"] is None or g["score2"] is None:
        continue  # kein Resultat gemeldet

    t1 = g["team_name_1"]
    t2 = g["team_name_2"]
    s1 = g["score1"]
    s2 = g["score2"]

    if s1 > s2:
        rangliste.loc[rangliste.Team == t1, "Punkte"] += 2
    elif s2 > s1:
        rangliste.loc[rangliste.Team == t2, "Punkte"] += 2
    else:
        rangliste.loc[rangliste.Team == t1, "Punkte"] += 1
        rangliste.loc[rangliste.Team == t2, "Punkte"] += 1

rangliste = rangliste.sort_values("Punkte", ascending=False).reset_index(drop=True)

def highlight_row(row):
    if row.name == 0:
        return ["background-color: gold; font-weight: bold"] * len(row)
    elif row.name == 1:
        return ["background-color: silver; font-weight: bold"] * len(row)
    elif row.name == 2:
        return ["background-color: #cd7f32; font-weight: bold"] * len(row)
    return [""] * len(row)

st.markdown("## 🏆 Live Rangliste")
st.dataframe(
    rangliste.style.apply(highlight_row, axis=1),
    use_container_width=True,
)

st.markdown("---")

# ---------------------------------------------------------
# TEAM-FILTER
# ---------------------------------------------------------
st.markdown("## 🔍 Team-Filter")

team_filter_options = ["Alle Teams"] + teams
selected_team = st.selectbox("Team auswählen", team_filter_options)

st.markdown("---")

# ---------------------------------------------------------
# SPIELPLAN
# ---------------------------------------------------------
st.markdown("## 📅 Spielplan – Alle Spiele")

# Spiele nach Slot gruppieren
slots = {}
for g in games:
    slot = g["slot"]
    slots.setdefault(slot, []).append(g)

sorted_slots = dict(sorted(slots.items()))

for slot, games_in_slot in sorted_slots.items():
    st.markdown(f"### Timeslot {slot}: {games_in_slot[0]['time']}")

    teams_with_game = set()

    for g in games_in_slot:
        if g["team_code_1"] == "Spielfrei" or g["team_code_2"] == "Spielfrei":
            continue

        team1 = TEAM_NAMES[g["team_code_1"]]
        team2 = TEAM_NAMES[g["team_code_2"]]

        teams_with_game.add(team1)
        teams_with_game.add(team2)

        if selected_team != "Alle Teams" and selected_team not in (team1, team2):
            continue

        st.markdown(f"**{team1} vs {team2}**")
        st.markdown(f"Sportart: **{g['field']}**")

        # Resultat anzeigen
        if g["score1"] is not None and g["score2"] is not None:
            st.success(f"Resultat: {team1} {g['score1']} – {g['score2']} {team2}")
        else:
            st.info("Noch kein Resultat gemeldet")

        st.markdown("---")

    # Spielfrei anzeigen
    for team in teams:
        if team not in teams_with_game:
            if selected_team != "Alle Teams" and selected_team != team:
                continue

            st.warning(f"**{team}: Spielfrei**")
            st.markdown("---")
