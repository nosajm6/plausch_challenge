import streamlit as st
from supabase import create_client
import os

# ---------------------------------------------------------
# Supabase Client
# ---------------------------------------------------------
supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

# ---------------------------------------------------------
# Team Mapping
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

# ---------------------------------------------------------
# DB Funktionen
# ---------------------------------------------------------
def load_games():
    res = supabase.table("games").select("*").execute()
    return res.data

def load_results():
    res = supabase.table("results").select("*").execute()
    return res.data

def save_result(game_id, time, field,
                team_code_1, team_name_1, score1,
                team_code_2, team_name_2, score2):

    supabase.table("results").insert({
        "game_id": game_id,
        "time": time,
        "field": field,
        "team_code_1": team_code_1,
        "team_name_1": team_name_1,
        "score1": score1,
        "team_code_2": team_code_2,
        "team_name_2": team_name_2,
        "score2": score2
    }).execute()

# ---------------------------------------------------------
# Login
# ---------------------------------------------------------
SCHIRI_PASSWORD = "schiri123"

if "schiri_logged_in" not in st.session_state:
    st.session_state.schiri_logged_in = False

if not st.session_state.schiri_logged_in:
    st.title("Schiri‑Bereich – Login")

    pw = st.text_input("Passwort eingeben", type="password")

    if st.button("Login"):
        if pw == SCHIRI_PASSWORD:
            st.session_state.schiri_logged_in = True
            st.success("Erfolgreich eingeloggt")
            st.rerun()
        else:
            st.error("Falsches Passwort")

    st.stop()

# ---------------------------------------------------------
# Schiri UI
# ---------------------------------------------------------
st.title("Schiri‑Bereich – Resultate melden")

if st.button("Logout"):
    st.session_state.schiri_logged_in = False
    st.rerun()

games = load_games()
results = load_results()

# Resultate nach game_id mappen
existing_results = {
    r["game_id"]: (r["score1"], r["score2"])
    for r in results
}

# Spiele nach Slot gruppieren
slots = {}
for g in games:
    slot = g["slot"]
    slots.setdefault(slot, []).append(g)

sorted_slots = dict(sorted(slots.items()))

# ---------------------------------------------------------
# Sportart-Filter
# ---------------------------------------------------------
st.markdown("### 🔍 Spiele filtern nach Sportart")

sport_filter = st.selectbox(
    "Sportart auswählen",
    ["Alle", "Handball", "Frisbee", "Völkerball"],
)

# ---------------------------------------------------------
# Spiel-Loop
# ---------------------------------------------------------
for slot, games_in_slot in sorted_slots.items():
    st.markdown(f"## Timeslot {slot}: {games_in_slot[0]['time']}")

    for g in games_in_slot:

        # Spielfrei überspringen
        if g["team_code_1"] == "Spielfrei" or g["team_code_2"] == "Spielfrei":
            continue

        if sport_filter != "Alle" and g["field"] != sport_filter:
            continue

        team1 = TEAM_NAMES[g["team_code_1"]]
        team2 = TEAM_NAMES[g["team_code_2"]]

        label = "Tore" if g["field"] == "Handball" else "Punkte"

        st.markdown(f"### Spielfeld {g['field']} – {team1} vs {team2}")

        already_reported = g["game_id"] in existing_results

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**{team1}**")
            score1 = st.number_input(
                label,
                min_value=0,
                key=f"{g['game_id']}_score1",
                disabled=already_reported,
            )

        with col2:
            st.markdown(f"**{team2}**")
            score2 = st.number_input(
                label,
                min_value=0,
                key=f"{g['game_id']}_score2",
                disabled=already_reported,
            )

        if already_reported:
            s1, s2 = existing_results[g["game_id"]]
            st.success(f"Bereits gemeldet: {team1} {s1} – {s2} {team2}")
            st.button(
                "Resultat bereits gemeldet",
                disabled=True,
                key=f"{g['game_id']}_done",
            )
        else:
            if st.button(
                f"Resultat melden für {team1} vs {team2}",
                key=f"{g['game_id']}_btn",
            ):
                save_result(
                    g["game_id"],
                    g["time"],
                    g["field"],
                    g["team_code_1"],
                    team1,
                    int(score1),
                    g["team_code_2"],
                    team2,
                    int(score2),
                )

                st.success(
                    f"Resultat gespeichert: {team1} {int(score1)} – {team2} {int(score2)}"
                )
                st.rerun()

        st.markdown("---")
