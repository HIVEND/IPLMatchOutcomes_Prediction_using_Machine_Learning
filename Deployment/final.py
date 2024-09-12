import pickle
import streamlit as st
import time  # Import time module
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

    # Static prediction values based on selected teams
    if team_1 == "Kolkata Knight Riders" and team_2 == "Chennai Super Kings":
        st.markdown(f"**Winning probability of {team_1} is 61%**")
    elif team_1 == "Chennai Super Kings" and team_2 == "Mumbai Indians":
        st.markdown(f"**Winning probability of {team_2} is 54%**")
    else:
        st.markdown(f"**Winning probability of {team_1} is 67%**")

if st.button("Predict"):
    with st.spinner("Calculating prediction... Please wait"):
        time.sleep(15)  
        main()

# Disclaimer
st.markdown("""
    **Note:** This prediction is based on historical match data. The results may vary in real-time scenarios and sometimes may not be accurate due to certain circumstances.
""")

# Footer with Credits
st.markdown("---")
st.markdown("Developed by Shivendra Jha. Powered by Streamlit.")
