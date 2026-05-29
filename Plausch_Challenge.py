import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import json
from supabase import create_client
import os

from supabase_utils import TEAM_NAMES, get_results

# ---------------------------------------------------------
# Streamlit Setup
# ---------------------------------------------------------
st.set_page_config(page_title="Plausch Challenge", layout="wide")
st_autorefresh(interval=5000, key="refresh")

st.title("Plausch Challenge – Live Rangliste & Spielplan")
st.markdown("Die Seite aktualisiert sich automatisch, sobald neue Resultate gemeldet werden.")

# ---------------------------------------------------------
# Supabase Client (nur falls direkt gebraucht)
# ---------------------------------------------------------
supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

# ---------------------------------------------------------
# Spielplan aus JSON laden
# ---------------------------------------------------------
with open("games.json", "r", encoding="utf-8") as f:
    games = json.load(f)

teams = sorted(TEAM_NAMES.values())

# ---------------------------------------------------------
# Resultate laden
# ---------------------------------------------------------
results = get_results()
result_map = {r["game_id"]: r for r in results}

# ---------------------------------------------------------
# RANGLISTE
# ---------------------------------------------------------
rangliste = pd.DataFrame({"Team": teams, "Punkte": 0})

for r in results:
    t1 = r["team1_name"]
    t2 = r["team2_name"]
    s1 = r["score1"]
    s2 = r["score2"]

    if s1 > s2:
        rangliste.loc[rangliste.Team == t1, "Punkte"] += 2
    elif s2 > s1:
        rangliste.loc[rangliste.Team == t2, "Punkte"] += 2
    else:
        rangliste.loc[rangliste.Team == t1, "Punkte"] += 1
        rangliste.loc[rangliste.Team == t2, "Punkte"] += 1

rangliste = rangliste.sort_values("Punkte", ascending=False).reset_index(drop=True)

# Platznummer hinzufügen (1–6 statt 0–5)
rangliste.insert(0, "Platz", rangliste.index + 1)

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

slots = {}
for game_id, g in games.items():
    slots.setdefault(g["slot"], []).append((game_id, g))

sorted_slots = dict(sorted(slots.items()))

for slot, games_in_slot in sorted_slots.items():
    st.markdown(f"### Timeslot {slot}: {games_in_slot[0][1]['time']}")

    teams_with_game = set()

    for game_id, g in games_in_slot:
        if g["team1"] == "Spielfrei" or g["team2"] == "Spielfrei":
            continue

        team1 = TEAM_NAMES[g["team1"]]
        team2 = TEAM_NAMES[g["team2"]]

        teams_with_game.add(team1)
        teams_with_game.add(team2)

        if selected_team != "Alle Teams" and selected_team not in (team1, team2):
            continue

        st.markdown(f"**{team1} vs {team2}**")
        st.markdown(f"Sportart: **{g['field']}**")

        match = result_map.get(game_id)

        if match:
            st.success(f"Resultat: {team1} {match['score1']} – {match['score2']} {team2}")
        else:
            st.info("Noch kein Resultat gemeldet")

        st.markdown("---")

    for team in teams:
        if team not in teams_with_game:
            if selected_team != "Alle Teams" and selected_team != team:
                continue

            st.warning(f"**{team}: Spielfrei**")
            st.markdown("---")
