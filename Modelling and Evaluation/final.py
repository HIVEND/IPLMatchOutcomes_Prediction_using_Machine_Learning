import pickle
import streamlit as st
from Dict import stadium_size, bat, teams, team_

class Queue:
    def __init__(self):
        self.items = []
    def is_empty(self):
        return self.items == []
    def enqueue(self, item):
        self.items.insert(0, item)
    def dequeue(self):
        return self.items.pop()
    def peek(self):
        return self.items[-1]
    def size(self):
        return len(self.items)

st.set_page_config(page_title="IPL Match Predictor", layout="wide")
st.title("🏏 IPL Match Outcome Predictor")
st.markdown("### Predict the outcome of IPL matches based on team selections and conditions")
st.sidebar.title("Selected Players")
col1_sidebar, col2_sidebar = st.sidebar.columns(2)
col1, col2 = st.columns(2)
with col1:
    team_1 = st.selectbox("🏏 Select the batting team", sorted(teams), key='team_1')

with col2:
    team_2_options = [team for team in sorted(teams) if team != team_1]
    team_2 = st.selectbox("🏏 Select the bowling team", team_2_options, key='team_2')

if not hasattr(st.session_state, "lineup_1"):
    st.session_state.lineup_1 = {team: [] for team in teams}

if not hasattr(st.session_state, "lineup_2"):
    st.session_state.lineup_2 = {team: [] for team in teams}
# Display available players based on selected team_1
col1, col2 = st.columns(2)
with col1:
    if team_1:
        Availabe_players_1 = teams.get(team_1)
        st.write("Available Players for " + team_1)
        lineup_1 = st.multiselect("Select players", Availabe_players_1)

        # Limit selection to 11 players
        if len(lineup_1) != 11:
            st.warning("Please select only 11 players.")
            lineup_1 = lineup_1[:11]

        # Update session state
        st.session_state.lineup_1[team_1] = lineup_1

    # Display selected players in the sidebar for team_1
    with col1_sidebar:
        st.markdown("### " + team_1)
        if st.session_state.lineup_1.get(team_1):
            for player in st.session_state.lineup_1.get(team_1):
                st.write(player)
        else:
            st.write("No players selected yet.")
if not hasattr(st.session_state, "selected_players"):
    st.session_state.lineup_2 = {team: [] for team in teams}

with col2:
    if team_2:
        Availabe_players_2 = teams.get(team_2)
        st.write("Available Players for " + team_2)
        lineup_2 = st.multiselect("Select players", Availabe_players_2)

        # Limit selection to 11 players
        if len(lineup_2) != 11:
            st.warning("Please select 11 players.")
            lineup_2 = lineup_2[:11]

        # Update session state
        st.session_state.lineup_2[team_2] = lineup_2

    # Display selected players in the sidebar for team_2
    with col2_sidebar:
        st.markdown("### " + team_2)
        if st.session_state.lineup_2.get(team_2):
            for player in st.session_state.lineup_2.get(team_2):
                st.write(player)
        else:
            st.write("No players selected yet.")
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    stadium = st.selectbox("🏟️ Select Host City", sorted(stadium_size), key='stadium')
    toss_decision = st.selectbox("🎲 Toss Decision", ["Batting", "Bowling"], key='toss_decision')

with col2:
    year = st.selectbox("📅 Year", [i for i in range(2015, 2026)], key='year')

toss = toss_decision == "Batting"
stadium = stadium_size[stadium]
def main():
    Team_1 = team_[team_1]
    Team_2 = team_[team_2]

    try:
        with open("LR_1.pkl", "rb") as f:
            LR_1 = pickle.load(f)
    except FileNotFoundError:
        st.error("Model file 'LR_1.pkl' not found. Please upload the correct file.")
        return

    try:
        with open("RF_2.pkl", "rb") as f:
            RF_2 = pickle.load(f)
    except FileNotFoundError:
        st.error("Model file 'RF_2.pkl' not found. Please upload the correct file.")
        return

    def get_key(dictionary, target_value):
        keys_with_target_value = ''
        for key, value in dictionary.items():
            if value == target_value:
                keys_with_target_value = key
                break
        return keys_with_target_value

    players_T1 = Queue()
    players_T2 = Queue()
    for i in lineup_1:
        j = bat[i]
        players_T1.enqueue(j)
    for i in lineup_2:
        j = bat[i]
        players_T2.enqueue(j)

    on_field = Queue()
    on_field.enqueue(players_T1.dequeue())
    on_field.enqueue(players_T1.dequeue())
    inn = 1
    total_runs_1 = 0
    a_r = 0
    b_r = 0
    r_f = 1

    six = 0
    five = 0
    four = 0
    three = 0
    two = 0
    one = 0
    zero = 0

    all_out = False

    for j in range(20):  # Using a fixed number of overs instead of bowlers
        r_f_o = 1
        if all_out:
            break
        for k in range(1, 7):
            if (LR_1.predict_proba([[inn, j, k, stadium, toss, on_field.peek(), Team_2, Team_1, year]])[:, 1]) * r_f * r_f_o > 0.33:
                r_f = 0.8
                r_f_o -= 0.1
                a = on_field.dequeue()
                total_runs_1 += a_r
                st.write(get_key(bat, a), ':', str(a_r), '\t', "wicket taken by", get_key(ball, Team_2)) # type: ignore
                a_r = 0

                if players_T1.is_empty():
                    all_out = True
                    break
                on_field.enqueue(players_T1.dequeue())
                on_field.enqueue(on_field.dequeue())
            else:
                r_f = 1
                b = RF_2.predict_proba([[inn, j, k, stadium, toss, on_field.peek(), Team_2, Team_1, year]])

                for i in range(7):
                    if b[:, i] > 0.37:
                        b = i
                        break
                else:
                    if b[:, 4] > 0.27:
                        b = 4
                        four += 1
                    elif b[:, 6] > 0.25:
                        b = 6
                        six += 1
                    elif b[:, 3] > 0.16:
                        b = 3
                        three += 1
                    elif b[:, 5] > 0.16:
                        b = 5
                        five += 1
                    elif b[:, 2] > 0.24:
                        b = 2
                        two += 1
                    elif b[:, 1] > 0.2:
                        b = 1
                        one += 1
                    else:
                        b = 0
                        zero += 1

                a_r += b

                if b % 2 == 1:
                    on_field.enqueue(on_field.dequeue())
                    a_r, b_r = b_r, a_r

        if j != 19:
            on_field.enqueue(on_field.dequeue())
            a_r, b_r = b_r, a_r

    total_runs_1 += a_r + b_r
    if not all_out:
        st.write(get_key(bat, on_field.dequeue()), ':', str(a_r), '\t', 'not out')
    st.write(get_key(bat, on_field.dequeue()), ':', str(b_r), '\t', 'not out')
    st.write("Total runs =", str(total_runs_1), "+ Extras")
    st.write(six, five, four, three, two, one, zero)
    st.write("\n" + "="*60 + "\n", end='\n\n')

    on_field = Queue()
    on_field.enqueue(players_T2.dequeue())
    on_field.enqueue(players_T2.dequeue())

    inn = 2
    total_runs = 0
    a_r = 0
    b_r = 0
    r_f = 1

    six = 0
    five = 0
    four = 0
    three = 0
    two = 0
    one = 0
    zero = 0

    all_out = False

    for j in range(20):
        r_f_o = 1
        if all_out:
            break
        for k in range(1, 7):
            if (LR_1.predict_proba([[inn, j, k, stadium, toss, on_field.peek(), Team_1, Team_2, year]])[:, 1]) * r_f * r_f_o > 0.33:
                r_f = 0.8
                r_f_o -= 0.1
                a = on_field.dequeue()
                total_runs += a_r
                st.write(get_key(bat, a), ':', str(a_r), '\t', "wicket taken by", get_key(all, Team_1))
                a_r = 0

                if players_T2.is_empty():
                    all_out = True
                    break
                on_field.enqueue(players_T2.dequeue())
                on_field.enqueue(on_field.dequeue())
            else:
                r_f = 1
                b = RF_2.predict_proba([[inn, j, k, stadium, toss, on_field.peek(), Team_1, Team_2, year]])

                for i in range(7):
                    if b[:, i] > 0.37:
                        b = i
                        break
                else:
                    if b[:, 4] > 0.27:
                        b = 4
                        four += 1
                    elif b[:, 6] > 0.25:
                        b = 6
                        six += 1
                    elif b[:, 3] > 0.16:
                        b = 3
                        three += 1
                    elif b[:, 5] > 0.16:
                        b = 5
                        five += 1
                    elif b[:, 2] > 0.24:
                        b = 2
                        two += 1
                    elif b[:, 1] > 0.2:
                        b = 1
                        one += 1
                    else:
                        b = 0
                        zero += 1

                a_r += b

                if b % 2 == 1:
                    on_field.enqueue(on_field.dequeue())
                    a_r, b_r = b_r, a_r

        if j != 19:
            on_field.enqueue(on_field.dequeue())
            a_r, b_r = b_r, a_r

    total_runs += a_r + b_r
    if not all_out:
        st.write(get_key(bat, on_field.dequeue()), ':', str(a_r), '\t', 'not out')
    st.write(get_key(bat, on_field.dequeue()), ':', str(b_r), '\t', 'not out')
    st.write("Total runs =", str(total_runs), "+ Extras")
    st.write(six, five, four, three, two, one, zero)

    result = "Draw"
    if total_runs_1 > total_runs:
        result = "Team 1 wins"
    elif total_runs_1 < total_runs:
        result = "Team 2 wins"

    st.write("\n" + "="*60 + "\n")
    st.markdown(f"### **Match Result**: {result}")

if st.button("Predict Match Outcome"):
    main()
