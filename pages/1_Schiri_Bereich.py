import streamlit as st

from db_utils import init_db, get_results, load_games, save_result, TEAM_NAMES

SCHIRI_PASSWORD = "schiri123"

init_db()

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

st.title("Schiri‑Bereich – Resultate melden")

if st.button("Logout"):
    st.session_state.schiri_logged_in = False
    st.rerun()

games = load_games()
existing_results = {r["game_id"]: (r["score1"], r["score2"]) for r in get_results()}

slots = {}
for game_id, g in games.items():
    slots.setdefault(g["slot"], []).append((game_id, g))

sorted_slots = dict(sorted(slots.items()))

st.markdown("### 🔍 Spiele filtern nach Sportart")

sport_filter = st.selectbox(
    "Sportart auswählen",
    ["Alle", "Handball", "Frisbee", "Völkerball"],
)

for slot, games_in_slot in sorted_slots.items():
    st.markdown(f"## Timeslot {slot}: {games_in_slot[0][1]['time']}")

    for game_id, g in games_in_slot:
        if g["team1"] == "Spielfrei" or g["team2"] == "Spielfrei":
            continue

        if sport_filter != "Alle" and g["field"] != sport_filter:
            continue

        team1 = TEAM_NAMES[g["team1"]]
        team2 = TEAM_NAMES[g["team2"]]

        label = "Tore" if g["field"] == "Handball" else "Punkte"

        st.markdown(f"### Spielfeld {g['field']}")

        already_reported = game_id in existing_results

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**{team1}**")
            score1 = st.number_input(
                label,
                min_value=0,
                key=f"{game_id}_score1",
                disabled=already_reported,
            )

        with col2:
            st.markdown(f"**{team2}**")
            score2 = st.number_input(
                label,
                min_value=0,
                key=f"{game_id}_score2",
                disabled=already_reported,
            )

        if already_reported:
            s1, s2 = existing_results[game_id]
            st.success(f"Bereits gemeldet: {team1} {s1} – {s2} {team2}")
            st.button(
                "Resultat bereits gemeldet",
                disabled=True,
                key=f"{game_id}_done",
            )
        else:
            if st.button(
                f"Resultat melden für {team1} vs {team2}",
                key=f"{game_id}_btn",
            ):
                save_result(
                    [
                        game_id,
                        g["time"],
                        g["field"],
                        g["team1"],
                        team1,
                        int(score1),
                        g["team2"],
                        team2,
                        int(score2),
                    ]
                )

                st.success(
                    f"Resultat gespeichert: {team1} {int(score1)} – {int(score2)} {team2}"
                )
                st.rerun()

        st.markdown("---")
