import streamlit as st

from supabase_utils import get_results, save_result, delete_result

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

st.title("Admin‑Bereich – Resultate bearbeiten")

if st.button("Logout"):
    st.session_state.admin_logged_in = False
    st.rerun()

rows = get_results()

if not rows:
    st.info("Noch keine Resultate eingetragen.")
    st.stop()

st.subheader("Alle gemeldeten Resultate")

for row in rows:
    game_id = row["game_id"]
    time = row["time"]
    field = row["field"]
    team1_name = row["team_name_1"]
    team2_name = row["team_name_2"]
    score1_val = row["score1"]
    score2_val = row["score2"]

    st.markdown(f"## {game_id}: {team1_name} vs {team2_name}")
    st.markdown(f"**Sportart:** {field}  |  **Timeslot:** {time}")

    col1, col2 = st.columns(2)

    with col1:
        new_score1 = st.number_input(
            f"{team1_name}",
            min_value=0,
            value=int(score1_val),
            key=f"score1_{game_id}",
        )

    with col2:
        new_score2 = st.number_input(
            f"{team2_name}",
            min_value=0,
            value=int(score2_val),
            key=f"score2_{game_id}",
        )

    colA, colB = st.columns([1, 1])

    with colA:
        if st.button("Speichern", key=f"save_{game_id}"):
            save_result(
                [
                    game_id,
                    time,
                    field,
                    row["team1"],
                    int(new_score1),
                    row["team2"],
                    int(new_score2),
                ]
            )
            st.success("Resultat aktualisiert!")
            st.rerun()

    with colB:
        if st.button("Löschen", key=f"delete_{game_id}"):
            delete_result(game_id)
            st.warning("Resultat gelöscht!")
            st.rerun()

    st.markdown("---")
