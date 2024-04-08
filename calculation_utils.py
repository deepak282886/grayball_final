from fielding_functions import select_stats_field
from calculation_functions import (group_bat, group_bowl, get_batting_stats,
                                   get_bowling_stats, group_bowl_player, group_bat_player)
import pandas as pd


def get_formats(fetch_df):
    unique_formats = fetch_df["match_type"].unique()
    return unique_formats


def handle_multiple(cal_df, threshold):
    unique_teams = pd.DataFrame(cal_df.groupby(["team"])["runs_batter"].sum()).sort_values(by=["runs_batter"],
                                                                                           ascending=False).head(10)
    unique_batting_teams = unique_teams.reset_index()["team"]

    bat_df = cal_df[cal_df["team"].isin(unique_batting_teams)]

    mask = ~cal_df["wickets_player_out"].isnull() & ~cal_df["wickets_kind"].isin(
        ['run out', 'retired hurt', 'obstructing the field', 'timed out'])
    filtered_df = cal_df[mask]
    cal_df['valid_wickets_count'] = cal_df.groupby('team')['team'].transform(
        lambda x: x.map(filtered_df.groupby('team').size()))
    cal_df['valid_wickets_count'].fillna(0, inplace=True)
    df_sorted = cal_df.sort_values(by='valid_wickets_count', ascending=False)

    df_sorted.reset_index(drop=True, inplace=True)

    unique_bowlers_teams = list(df_sorted['bowling_team'].drop_duplicates().head(10))
    bowl_df = cal_df[cal_df["team"].isin(unique_bowlers_teams)]

    team_bat = group_bat(bat_df, threshold)
    team_bowl = group_bowl(bowl_df, threshold)

    unique_teams = pd.DataFrame(cal_df.groupby(["batter"])["runs_batter"].sum()).sort_values(by=["runs_batter"],
                                                                                             ascending=False).head(10)
    unique_batting_players = unique_teams.reset_index()["batter"]

    bat_df = cal_df[cal_df["batter"].isin(unique_batting_players)]

    mask = ~cal_df["wickets_player_out"].isnull() & ~cal_df["wickets_kind"].isin(
        ['run out', 'retired hurt', 'obstructing the field', 'timed out'])
    filtered_df = cal_df[mask]
    cal_df['valid_wickets_count'] = cal_df.groupby('bowler')['bowler'].transform(
        lambda x: x.map(filtered_df.groupby('bowler').size()))
    cal_df['valid_wickets_count'].fillna(0, inplace=True)
    df_sorted = cal_df.sort_values(by='valid_wickets_count', ascending=False)

    df_sorted.reset_index(drop=True, inplace=True)

    unique_bowlers_players = list(df_sorted['bowler'].drop_duplicates().head(10))
    bowl_df = cal_df[cal_df["bowler"].isin(unique_bowlers_players)]

    player_bat = group_bat_player(bat_df, threshold)
    player_bowl = group_bowl_player(bowl_df, threshold)

    return player_bat, player_bowl, team_bat, team_bowl


def handle_multiple_player(cal_df, threshold, team_primary):

    bat_df2 = cal_df[cal_df["team"] == team_primary]
    unique_batting_players = bat_df2.reset_index()["batter"]

    bat_df = cal_df[cal_df["batter"].isin(unique_batting_players)]
    mask = ~cal_df["wickets_player_out"].isnull() & ~cal_df["wickets_kind"].isin(
        ['run out', 'retired hurt', 'obstructing the field', 'timed out'])
    filtered_df = cal_df[mask]
    cal_df['valid_wickets_count'] = cal_df.groupby('bowler')['bowler'].transform(
        lambda x: x.map(filtered_df.groupby('bowler').size()))
    cal_df['valid_wickets_count'].fillna(0, inplace=True)
    df_sorted = cal_df.sort_values(by='valid_wickets_count', ascending=False)

    df_sorted.reset_index(drop=True, inplace=True)

    unique_bowlers_players = list(df_sorted['bowler'].drop_duplicates().head(10))
    bowl_df = cal_df[cal_df["bowler"].isin(unique_bowlers_players)]

    player_bat = group_bat_player(bat_df, threshold)
    player_bowl = group_bowl_player(bowl_df, threshold)

    return player_bat, player_bowl


def handle_multiple_team(cal_df, threshold, player_primary):

    bat_df = cal_df[cal_df["batter"] == player_primary]

    mask = ~cal_df["wickets_player_out"].isnull() & ~cal_df["wickets_kind"].isin(
        ['run out', 'retired hurt', 'obstructing the field', 'timed out'])
    filtered_df = cal_df[mask]
    cal_df['valid_wickets_count'] = cal_df.groupby('bowler')['bowler'].transform(
        lambda x: x.map(filtered_df.groupby('bowler').size()))
    cal_df['valid_wickets_count'].fillna(0, inplace=True)

    bowl_df = cal_df[cal_df["bowler"] == player_primary]

    player_bat = group_bat_player(bat_df, threshold)
    player_bowl = group_bowl_player(bowl_df, threshold)

    return player_bat, player_bowl


def select_stats_pro(fetch_df, base_json, view_json, threshold_list):

    player_text, team_text = "", ""
    if "fielding" in view_json.keys():
        if view_json["fielding"].lower().strip() != "no":
            team_text_p = select_stats_field(fetch_df, base_json, threshold_list)
            team_text += f"{team_text_p}"

    elif "powerplay" in view_json.keys():

        if view_json["powerplay"].lower().strip() != "no":
            pp_num_stats = list(fetch_df["powerplay_number"].unique())
            if len(pp_num_stats):
                for kk in pp_num_stats:
                    sliced_df = fetch_df[fetch_df["powerplay_number"] == kk]
                    team_stats, player_stats = select_stats(sliced_df, base_json, threshold_list)
                    if kk == "NA":
                        kk = "no powerplay"
                    try:
                        player_text += f"In powerplay number {kk}, {player_stats}"
                        team_text += f"In powerplay number {kk}, {team_stats}"
                    except:
                        pass
    else:
        team_text, player_text = select_stats(fetch_df, base_json, threshold_list)

    biggest_text = f"{player_text} {team_text}"
    return biggest_text

def select_stats(fetch_df1, base_json, threshold_list):

    team1 = base_json.get("team1")
    team2 = base_json.get("team2")
    team_category = base_json.get("team_category")
    player1 = base_json.get("player1")
    player2 = base_json.get("player2")
    player_category = base_json.get("player_category")
    detail_level = base_json.get("detail_level")
    team_stats = ""
    player_stats = ""

    unique_formats = get_formats(fetch_df1)
    unique_seasons = fetch_df1["season"].unique()

    for sea in unique_seasons:
        fetch_df = fetch_df1[fetch_df1["season"] == sea]
        for match_f in list(unique_formats):
            cal_df = fetch_df[fetch_df["match_type"] == match_f]
            if detail_level in ["team_level"]:
                if team_category == "single" and team1:
                    bat_df = cal_df[cal_df["team"] == team1]
                    bowl_df = cal_df[cal_df["bowling_team"] == team1]
                    bat_stats = group_bat(bat_df, threshold_list)
                    if len(bat_stats):
                        team_stats += f"In the {sea} season, {team1} batting performance in {match_f} <dataframe>{bat_stats}</dataframe>"
                    bowl_stats = group_bowl(bowl_df, threshold_list)
                    if len(bowl_stats):
                        team_stats += f"In the {sea} season, {team1} bowling performance in {match_f} <dataframe>{bowl_stats}</dataframe>"

                if team_category == "head_to_head" and team1 and team2:
                    bat_stats = group_bat(cal_df[cal_df["team"] == team1], threshold_list)
                    if len(bat_stats):
                        team_stats += f"In the {sea} season, {team1} batting performance against {team2} in {match_f} <dataframe>{bat_stats}</dataframe>"

                    bat_stats = group_bat(cal_df[cal_df["team"] == team2], threshold_list)
                    if len(bat_stats):
                        team_stats += f"In the {sea} season, {team2} batting performance against {team1} in {match_f} <dataframe>{bat_stats}</dataframe>"

                    bowl_stats = group_bowl(cal_df[cal_df["bowling_team"] == team1], threshold_list)
                    if len(bowl_stats):
                        team_stats += f"In the {sea} season, {team1} bowling performance against {team2} in {match_f} <dataframe>{bowl_stats}</dataframe>"

                    bowl_stats = group_bowl(cal_df[cal_df["bowling_team"] == team2], threshold_list)
                    if len(bowl_stats):
                        team_stats += f"In the {sea} season, {team2} bowling performance against {team1} in {match_f} <dataframe>{bowl_stats}</dataframe>"

                if team_category == "head_to_head" and team1 and not team2:
                    bat_df = cal_df[cal_df["team"] == team1]
                    bowl_df = cal_df[cal_df["bowling_team"] == team1]
                    bat_stats = group_bat(bat_df, threshold_list)
                    if len(bat_stats):
                        team_stats += f"In the {sea} season, {team1} batting performance in {match_f} <dataframe>{bat_stats}</dataframe>"
                    bowl_stats = group_bowl(bowl_df, threshold_list)
                    if len(bowl_stats):
                        team_stats += f"In the {sea} season, {team1} bowling performance in {match_f} <dataframe>{bowl_stats}</dataframe>"

                if team_category == "multiple":
                    if team1:
                        team_bat, team_bowl = handle_multiple_player(cal_df, threshold_list, team1)

                        if len(team_bat):
                            player_stats += f"In the {sea} season, Batting performance in {match_f} <dataframe>{team_bat}</dataframe>"

                        if len(team_bowl):
                            player_stats += f"In the {sea} season, Bowling performance in {match_f} <dataframe>{team_bowl}</dataframe>"

                    else:
                        player_bat, player_bowl, team_bat, team_bowl = handle_multiple(cal_df, threshold_list)

                        if len(player_bat):
                            player_stats += f"In the {sea} season, Batting performance in {match_f} <dataframe>{player_bat}</dataframe>"

                        if len(player_bowl):
                            player_stats += f"In the {sea} season, Bowling performance in {match_f} <dataframe>{player_bowl}</dataframe>"

                        if len(team_bat):
                            team_stats += f"In the {sea} season, Batting performance in {match_f} <dataframe>{team_bat}</dataframe>"

                        if len(team_bowl):
                            team_stats += f"In the {sea} season, Bowling performance in {match_f} <dataframe>{team_bowl}</dataframe>"

            if detail_level in ["player_level", "all"]:
                if player_category == "single" and player1:
                    bat_stats = get_batting_stats(cal_df, [player1], threshold_list)
                    if len(bat_stats):
                        player_stats += f"In the {sea} season, {player1} batting performance in {match_f} <dataframe>{bat_stats}</dataframe>"
                    bowl_stats = get_bowling_stats(cal_df, [player1], threshold_list)
                    if len(bowl_stats):
                        player_stats += f"In the {sea} season, {player1} bowling performance in {match_f} <dataframe>{bowl_stats}</dataframe>"

                if player_category == "head_to_head" and player1 and player2:
                    head_to_head_bat = cal_df[
                        (cal_df["batter"].isin([player1])) | (cal_df["non_striker"].isin([player1]))]
                    head_to_head_bat = head_to_head_bat[head_to_head_bat["bowler"].isin([player2])]

                    head_to_head_bowl = cal_df[
                        (cal_df["batter"].isin([player2])) | (cal_df["non_striker"].isin([player2]))]
                    head_to_head_bowl = head_to_head_bowl[head_to_head_bowl["bowler"].isin([player1])]

                    bat_stats = get_batting_stats(head_to_head_bat, [player1], threshold_list)
                    if len(bat_stats):
                        player_stats += f"In the {sea} season, {player1} batting performance against {player2} in {match_f} <dataframe>{bat_stats}</dataframe>"

                    bat_stats = get_batting_stats(head_to_head_bowl, [player2], threshold_list)
                    if len(bat_stats):
                        player_stats += f"In the {sea} season, {player2} batting performance against {player1} in {match_f} <dataframe>{bat_stats}</dataframe>"

                    bowl_stats = get_bowling_stats(head_to_head_bowl[head_to_head_bowl["batter"].isin([player2])], [player1], threshold_list)
                    if len(bowl_stats):
                        player_stats += f"In the {sea} season, {player1} bowling performance against {player2} in {match_f} <dataframe>{bowl_stats}</dataframe>"

                    bowl_stats = get_bowling_stats(head_to_head_bat[head_to_head_bat["batter"].isin([player1])], [player2], threshold_list)
                    if len(bowl_stats):
                        player_stats += f"In the {sea} season, {player2} bowling performance against {player1} in {match_f} <dataframe>{bowl_stats}</dataframe>"

                if player_category == "head_to_head" and player1 and not player2:
                    bat_stats = get_batting_stats(cal_df, [player1], threshold_list)
                    if len(bat_stats):
                        player_stats += f"In the {sea} season, {player1} batting performance in {match_f} <dataframe>{bat_stats}</dataframe>"
                    bowl_stats = get_bowling_stats(cal_df, [player1], threshold_list)
                    if len(bowl_stats):
                        player_stats += f"In the {sea} season, {player1} bowling performance in {match_f} <dataframe>{bowl_stats}</dataframe>"

                if player_category == "partnership" and player1 and player2:
                    partnership_bat_df = cal_df[(cal_df["batter"].isin([player1, player2])) | (
                        cal_df["non_striker"].isin([player1, player2]))]
                    partnership_ball_df = cal_df[cal_df["bowler"].isin([player1, player2])]

                    bat_stats = get_batting_stats(partnership_bat_df, [player1, player2], threshold_list)
                    if len(bat_stats):
                        player_stats += f"In the {sea} season, {player1}_{player2} batting partnership performance in {match_f} <dataframe>{bat_stats}</dataframe>"

                    bowl_stats = get_bowling_stats(partnership_ball_df, [player1, player2], threshold_list)
                    if len(bowl_stats):
                        player_stats += f"In the {sea} season, {player1} and {player2} bowling performance in {match_f} <dataframe>{bowl_stats}</dataframe>"

                if player_category == "multiple":
                    if player1:
                        player_bat, player_bowl = handle_multiple_team(cal_df, threshold_list, player1)
                        if len(player_bat):
                            player_stats += f"In the {sea} season, Batting performance in {match_f} <dataframe>{player_bat}</dataframe>"

                        if len(player_bowl):
                            player_stats += f"In the {sea} season, Bowling performance in {match_f} <dataframe>{player_bowl}</dataframe>"

                    else:
                        player_bat, player_bowl, team_bat, team_bowl = handle_multiple(cal_df, threshold_list)
                        if len(player_bat):
                            player_stats += f"In the {sea} season, Batting performance in {match_f} <dataframe>{player_bat}</dataframe>"

                        if len(player_bowl):
                            player_stats += f"In the {sea} season, Bowling performance in {match_f} <dataframe>{player_bowl}</dataframe>"

                        if len(team_bat):
                            team_stats += f"In the {sea} season, Batting performance in {match_f} <dataframe>{team_bat}</dataframe>"

                        if len(team_bowl):
                            team_stats += f"In the {sea} season, Bowling performance in {match_f} <dataframe>{team_bowl}</dataframe>"

    return team_stats, player_stats
