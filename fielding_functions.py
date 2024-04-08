import pandas as pd
import sqlite3


def get_formats(fetch_df):
    unique_formats = fetch_df["match_type"].unique()
    return unique_formats


def slice_threshold(player_stats, threshold):
    # print(threshold, "here", player_stats.columns)
    if len(threshold):
        for thres in threshold:
            if "name" in thres.keys():
                if thres["name"] in player_stats.columns:
                    metric = thres["name"]
                    value = thres["value"]
                    operator = thres["operator"]

                    if operator == "<":
                        player_stats = player_stats[player_stats[metric] < int(value)]
                    elif operator == ">":
                        player_stats = player_stats[player_stats[metric] > int(value)]
                    elif operator == "==":
                        player_stats = player_stats[player_stats[metric] == int(value)]
                    elif operator == "!=":
                        player_stats = player_stats[player_stats[metric] != int(value)]

    return player_stats


def select_stats_field(fetch_df1, base_json, threshold):
    team1 = base_json.get("team1")
    team2 = base_json.get("team2")
    team_category = base_json.get("team_category")
    player1 = base_json.get("player1")
    player2 = base_json.get("player2")
    player_category = base_json.get("player_category")
    detail_level = base_json.get("detail_level")

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

    unique_formats = get_formats(fetch_df1)
    big_text = ""

    conn = sqlite3.connect('/home/deepak/json_db/version2.db')

    unique_seasons = fetch_df1["season"].unique()
    for sea in unique_seasons:
        fetch_df = fetch_df1[fetch_df1["season"] == sea]
        for match_f in list(unique_formats):
            cal_df = fetch_df[fetch_df["match_type"] == match_f]
            if detail_level in ["team_level"]:

                if team_category == "single" and team1:
                    bowl_df = cal_df[cal_df["bowling_team"] == team1]
                    team_text = get_fielding_stats_team(bowl_df, match_f, threshold)
                    big_text += f"In the {sea} season, {team_text}"

                    bowl_df = cal_df[cal_df["team"] == team1]
                    team_text = get_fielding_stats_team(bowl_df, match_f, threshold)
                    big_text += f"In the {sea} season, Against {team1} performance : {team_text}"

                if team_category == "head_to_head" and team1 and team2:
                    bowl_df1 = cal_df[cal_df["bowling_team"] == team1]
                    team_text = get_fielding_stats_team(bowl_df1, match_f, threshold)
                    big_text += f"In the {sea} season, {team_text}"

                    bowl_df1 = cal_df[cal_df["team"] == team1]
                    team_text = get_fielding_stats_team(bowl_df1, match_f, threshold)
                    big_text += f"In the {sea} season,  Against {team1} performance : {team_text}"

                    bowl_df2 = cal_df[cal_df["bowling_team"] == team2]
                    team_text = get_fielding_stats_team(bowl_df2, match_f, threshold)
                    big_text += f"In the {sea} season, {team_text}"

                    bowl_df2 = cal_df[cal_df["team"] == team2]
                    team_text = get_fielding_stats_team(bowl_df2, match_f, threshold)
                    big_text += f"In the {sea} season,  Against {team2} performance : {team_text}"

                if team_category == "head_to_head" and team1 and not team2:
                    bowl_df = cal_df[cal_df["bowling_team"] == team1]
                    team_text = get_fielding_stats_team(bowl_df, match_f, threshold)
                    big_text += f"In the {sea} season, {team_text}"

                    bowl_df = cal_df[cal_df["team"] == team1]
                    team_text = get_fielding_stats_team(bowl_df, match_f, threshold)
                    big_text += f"In the {sea} season,  Against {team1} performance : {team_text}"

                if team_category == "multiple":
                    if team1:

                        bowl_df = cal_df[cal_df["bowling_team"] == team1]
                        team_text = get_fielding_stats_team(bowl_df, match_f, threshold)
                        big_text += f"In the {sea} season, {team_text}"

                        bowl_df = cal_df[cal_df["team"] == team1]
                        team_text = get_fielding_stats_team(bowl_df, match_f, threshold)
                        big_text += f"In the {sea} season,  Against {team1} performance : {team_text}"

                    else:

                        team_text = get_fielding_stats_team(cal_df, match_f, threshold)
                        big_text += f"In the {sea} season, {team_text}"

            if detail_level in ["player_level"]:
                if player_category == "single" and player1:

                    final_query = f"""SELECT * FROM ball_by_ball_data b LEFT JOIN match_info m 
                    ON b.match_id = m.match_id WHERE b.fielder1_wicket = '{player1}'
                    OR b.fielder2_wicket = '{player1}'"""

                    bowl_df = pd.read_sql_query(final_query, conn)
                    bowl_df.columns = cols
                    bowl_df = bowl_df[bowl_df["match_type"] == match_f]
                    player_text = get_fielding_stats_player(bowl_df, match_f, threshold)
                    big_text += f"In the {sea} season, {player_text}"

                    bowl_df = cal_df[(cal_df["batter"].isin([player1]))]
                    player_text = get_fielding_stats_player(bowl_df, match_f, threshold)
                    big_text += f"In the {sea} season,  Against {player1} performance :  {player_text}"

                if player_category == "head_to_head" and player1 and player2:

                    final_query = f"""SELECT * FROM ball_by_ball_data b LEFT JOIN match_info m 
                                        ON b.match_id = m.match_id WHERE b.fielder1_wicket = '{player1}'
                                        OR b.fielder2_wicket = '{player1}'"""

                    bowl_df1 = pd.read_sql_query(final_query, conn)
                    bowl_df1.columns = cols
                    bowl_df1 = bowl_df1[bowl_df1["match_type"] == match_f]
                    player_text = get_fielding_stats_player(bowl_df1, match_f, threshold)
                    big_text += f"In the {sea} season, {player_text}"

                    bowl_df1 = cal_df[(cal_df["batter"].isin([player1]))]
                    player_text = get_fielding_stats_player(bowl_df1, match_f, threshold)
                    big_text += f"In the {sea} season,  Against {player1} performance : {player_text}"

                    final_query = f"""SELECT * FROM ball_by_ball_data b LEFT JOIN match_info m 
                                                            ON b.match_id = m.match_id WHERE b.fielder1_wicket = '{player2}'
                                                            OR b.fielder2_wicket = '{player2}'"""

                    bowl_df2 = pd.read_sql_query(final_query, conn)
                    bowl_df2.columns = cols
                    bowl_df2 = bowl_df2[bowl_df2["match_type"] == match_f]
                    player_text = get_fielding_stats_player(bowl_df2, match_f, threshold)
                    big_text += f"In the {sea} season, {player_text}"

                    bowl_df2 = cal_df[(cal_df["batter"].isin([player2]))]
                    player_text = get_fielding_stats_player(bowl_df2, match_f, threshold)
                    big_text += f"In the {sea} season,  Against {player2} performance : {player_text}"

                if player_category == "head_to_head" and player1 and not player2:

                    final_query = f"""SELECT * FROM ball_by_ball_data b LEFT JOIN match_info m 
                    ON b.match_id = m.match_id WHERE b.fielder1_wicket = '{player1}'
                    OR b.fielder2_wicket = '{player1}'"""

                    bowl_df = pd.read_sql_query(final_query, conn)
                    bowl_df.columns = cols
                    bowl_df = bowl_df[bowl_df["match_type"] == match_f]
                    player_text = get_fielding_stats_player(bowl_df, match_f, threshold)
                    big_text += f"In the {sea} season, {player_text}"

                    bowl_df = cal_df[(cal_df["batter"].isin([player1]))]
                    player_text = get_fielding_stats_player(bowl_df, match_f, threshold)
                    big_text += f"In the {sea} season,  Against {player1} performance :  {player_text}"

                if player_category == "multiple":
                    if player1:

                        final_query = f"""SELECT * FROM ball_by_ball_data b LEFT JOIN match_info m 
                        ON b.match_id = m.match_id WHERE b.fielder1_wicket = '{player1}'
                        OR b.fielder2_wicket = '{player1}'"""

                        bowl_df = pd.read_sql_query(final_query, conn)
                        bowl_df.columns = cols
                        bowl_df = bowl_df[bowl_df["match_type"] == match_f]
                        player_text = get_fielding_stats_player(bowl_df, match_f, threshold)
                        big_text += f"In the {sea} season, {player_text}"

                        bowl_df = cal_df[(cal_df["batter"].isin([player1]))]
                        player_text = get_fielding_stats_player(bowl_df, match_f, threshold)
                        big_text += f"In the {sea} season,  Against {player1} performance :  {player_text}"
                    else:
                        player_text = get_fielding_stats_player(cal_df, match_f, threshold)
                        big_text += f"In the {sea} season, {player_text}"

    return big_text


def get_fielding_stats_team(fetch_df, match_f, thresholds):
    fetch_df["wickets_kind"] = fetch_df["wickets_kind"].replace({"run out": "run_out"})
    sliced_df = fetch_df[fetch_df["wickets_kind"].isin(['run_out', 'caught', 'stumped'])]
    teams = list(sliced_df["bowling_team"].unique())

    team_text = ""
    for t in teams:
        field_df = sliced_df[sliced_df["bowling_team"] == t]
        team_text1 = get_fielding_text_team(field_df, t, match_f, thresholds)
        team_text += team_text1
    return team_text


def get_fielding_stats_player(fetch_df, match_f, thresholds):
    fetch_df["wickets_kind"] = fetch_df["wickets_kind"].replace({"run out": "run_out"})
    sliced_df = fetch_df[fetch_df["wickets_kind"].isin(['run_out', 'caught','stumped'])]
    players1 = list(sliced_df["fielder1_wicket"].unique())
    players2 = list(sliced_df["fielder2_wicket"].unique())
    players_f = players1 + players2
    player_text = ""

    for t in players_f:
        field_df = sliced_df[(sliced_df["fielder1_wicket"] == t) | (sliced_df["fielder2_wicket"] == t)]

        player_text1 = get_fielding_text_player(field_df, t, match_f, thresholds)
        player_text += player_text1

    return player_text


def get_fielding_text_player(field_df, player, match_f, thresholds):
    run_out = len(field_df[field_df["wickets_kind"] == "run_out"])
    stumped = len(field_df[field_df["wickets_kind"] == "stumped"])
    caught = len(field_df[field_df["wickets_kind"] == "caught"])
    run_df = pd.DataFrame({"run_out": run_out, "stumped": stumped, "caught": caught}, index=[0])
    if thresholds:
        run_df = slice_threshold(run_df, thresholds)

    run_df = run_df.sort_values(by=["run_out"], ascending=False)

    field_text = ""
    if len(run_df):
        field_text += f"In the {match_f}, {player} has done {run_out} run outs and {stumped} stumpings and took {caught} catches."

    return field_text


def get_fielding_text_team(field_df, team, format_type, thresholds):
    field_text = ""
    if len(field_df):
        field_list = ["run_out", "stumped", "caught"]
        field_text = f"In the {format_type},"
        for para in field_list:
            run_df1 = pd.DataFrame(field_df[(field_df["wickets_kind"] == f"{para}") & (field_df["team"] != f"{team}")].groupby(["fielder1_wicket"])["wickets_kind"].count())
            run_df2 = pd.DataFrame(field_df[(field_df["wickets_kind"] == f"{para}") & (field_df["team"] != f"{team}")].groupby(["fielder2_wicket"])["wickets_kind"].count())
            run_df = pd.concat([run_df1, run_df2]).reset_index()
            run_df = pd.DataFrame(run_df.groupby(["index"])["wickets_kind"].sum()).reset_index()
            if thresholds:
                run_df = slice_threshold(run_df, thresholds)

            if len(run_df):
                run_df = run_df.sort_values(by=["wickets_kind"], ascending=False)

                field_text += f"In the {format_type} for {team}, "
                for idx, row in run_df.iterrows():
                    if para == "run_out":
                        value = "run outs"
                    if para == "stumped":
                        value = "stumps"
                    if para == "caught":
                        value = "catches"
                    field_text += f"{row['index']} has {row['wickets_kind']} {value}"

    return field_text

