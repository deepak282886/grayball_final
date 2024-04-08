from base_query import select_base_query
from model_response import get_match_specifics
from process_query import process_json
from construct_query import construct_query_conditions
from calculation_utils import select_stats_pro
from correct_names import modify_names
import sqlite3
import pandas as pd


def get_fetch_df(final_query):

    cols = ['match_id', 'team', 'gender', 'innings_number', 'over_number', 'powerplay_type', 'powerplay_number',
            'ball_number',
            'batter', 'batter_number', 'non_striker_number', 'bowler', 'bowler_number', 'non_striker', 'runs_batter',
            'extras_total', 'target_overs', 'target_runs', 'wickets_player_out', 'wickets_kind', 'fielder1_wicket',
            'fielder2_wicket', 'fielder3_wicket', 'legbyes_extras', 'wides_extras', 'byes_extras', 'noballs_extras',
            'penalty_extras', 'match_id_2', 'balls_per_over', 'city', 'dates', 'event_name', 'event_match_number',
            'match_type', 'match_type_number', 'official_match_referees', 'official_reserve_umpires',
            'official_tv_umpires', 'official_umpires', 'outcome_winner', 'outcome_wickets', 'outcome_runs', 'overs',
            'player_of_match', 'players_team1', 'players_team2', 'season', 'team_type', 'teams', 'toss_decision',
            'toss_winner', 'venue', 'team1', 'team2']

    conn = sqlite3.connect('/home/deepak/json_db/version2.db')
    fetch_df = pd.read_sql_query(final_query, conn)

    fetch_df.columns = cols
    if len(fetch_df):
        fetch_df["bowling_team"] = fetch_df.apply(lambda x: x["team1"] if x["team2"] == x["team"] else x["team2"],
                                                  axis=1)
        print(len(fetch_df))
    return fetch_df


def get_final_response(input_q):

    final_text = ""
    entity = get_match_specifics(input_q)
    query_dict = process_json(entity)
    query_dict = modify_names(query_dict)
    base_query, base_json = select_base_query(query_dict)
    slice_query, threshold_list, view_json = construct_query_conditions(query_dict)

    base_query2 = "SELECT * FROM ball_by_ball_data b LEFT JOIN match_info m ON b.match_id = m.match_id WHERE 1=1"

    final_query = f"{base_query}{slice_query}"
    print(final_query, "final")
    if base_query2 == final_query:
        return "slicing not done properly"

    fetch_df = get_fetch_df(final_query)

    recent_number = query_dict.get("recent_number", None)

    if recent_number:
        if isinstance(recent_number, list):
            recent_number = int(recent_number[0])
        elif recent_number:
            if recent_number < 5:
                recent_number = 5
            else:
                recent_number = int(recent_number)

    if recent_number and len(fetch_df):

        fetch_df = fetch_df.sort_values(by='dates', ascending=False)
        result_df = pd.DataFrame()
        for match_type in fetch_df['match_type'].unique():
            filtered_df = fetch_df[fetch_df['match_type'] == match_type].drop_duplicates('match_id', keep='last')
            match_ids = list(filtered_df.head(recent_number)["match_id"])
            last_5 = fetch_df[fetch_df["match_id"].isin(match_ids)]
            result_df = pd.concat([result_df, last_5], ignore_index=True)
        #
        if len(result_df):

            biggest_text = select_stats_pro(fetch_df, base_json, view_json, threshold_list)

            biggest_text = f"In the last {recent_number} matches for each format, {biggest_text}"
            final_text += biggest_text

    if len(fetch_df):
        biggest_text = select_stats_pro(fetch_df, base_json, view_json, threshold_list)
        final_text += biggest_text

    if len(final_text):
        return final_text
    else:
        final_text = "nothing found"
        return final_text

