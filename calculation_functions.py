import pandas as pd
import re

def extract_number_from_metric1(text):
    # Define the regex pattern to search for 'metric1' followed by any number of digits
    pattern = r'metric(\d+)'

    # Search for the pattern in the input text
    match = re.search(pattern, text)

    # If a match is found, convert the matching digits to an integer and return it
    if match:
        return int(
            match.group(1))  # match.group(1) returns the first capture group, i.e., the digits following 'metric1'
    else:
        return None  # Return None if no match is found

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

def slice_top_k(threshold, cumulative_agg):
    if len(threshold):
        for thres in threshold:

            if "top_k" in thres.keys():
                if thres["top_k"] == "top":
                    if "top_k_sort" in thres.keys():
                        if thres["top_k_sort"] in cumulative_agg.columns:
                            cumulative_agg = cumulative_agg.sort_values(by=[thres["top_k_sort"]],
                                                                        ascending=False)
                    if thres["top_k_parameter"]:
                        cumulative_agg = cumulative_agg.head(int(thres["top_k_parameter"]))

                if thres["top_k"] == "last":
                    if "top_k_sort" in thres.keys():
                        if thres["top_k_sort"] in cumulative_agg.columns:
                            cumulative_agg = cumulative_agg.sort_values(by=[thres["top_k_sort"]],
                                                                        ascending=False)
                    if thres["top_k_parameter"]:
                        cumulative_agg = cumulative_agg.head(int(thres["top_k_parameter"]))

                if thres["top_k"] == "worst":
                    if "top_k_sort" in thres.keys():
                        if thres["top_k_sort"] in cumulative_agg.columns:
                            cumulative_agg = cumulative_agg.sort_values(by=[thres["top_k_sort"]],
                                                                        ascending=True)
                    if thres["top_k_parameter"]:
                        cumulative_agg = cumulative_agg.tail(int(thres["top_k_parameter"]))
    return cumulative_agg

def get_batting_stats(odi_batt, player, thresholds):
    # Filter for the specific player and format type
    odi_bat = odi_batt[odi_batt["batter"].isin(player)].copy()
    odi_bat["bowler_extras"] = odi_bat.apply(lambda x: x["noballs_extras"] + x["wides_extras"], axis=1)
    match_level_stats = []

    m_match = list(odi_bat["match_id"].unique())

    for (match_id, innings_number), innings_group in odi_bat.groupby(["match_id", "innings_number"]):
        total_runs = innings_group["runs_batter"].sum()
        total_balls = innings_group[innings_group["bowler_extras"] == 0]["ball_number"].count()
        strike_rate = round(total_runs / total_balls * 100, 2) if total_balls else 0
        scores = innings_group["runs_batter"].sum()
        hundred = 1 if scores >= 100 else 0
        fifty = 1 if 50 <= scores < 100 else 0
        thirties = 1 if 30 <= scores < 50 else 0
        zeros = 1 if scores == 0 else 0
        not_out = 1 if innings_group["wickets_player_out"].isnull().all() else 0
        sixes = sum(innings_group["runs_batter"] == 6)
        fours = sum(innings_group["runs_batter"] == 4)
        doubles = sum(innings_group["runs_batter"] == 2)
        singles = sum(innings_group["runs_batter"] == 1)
        threes = sum(innings_group["runs_batter"] == 3)
        dot_balls = sum(innings_group["runs_batter"] == 0)

        match_level_stats.append({
            "match_id": match_id,
            "innings_number": innings_number,
            "total_runs": total_runs,
            "total_balls": total_balls,
            "strike_rate": strike_rate,
            "hundred": hundred,
            "fifty": fifty,
            "thirties": thirties,
            "zeros": zeros,
            "not_out": not_out,
            "sixes": sixes,
            "fours": fours,
            "doubles": doubles,
            "singles": singles,
            "threes": threes,
            "dot_balls": dot_balls
        })

    match_level_stats = pd.DataFrame(match_level_stats)
    if len(match_level_stats):

        match_level_stats["strike_rate"] = round(match_level_stats["total_runs"] / match_level_stats["total_balls"] * 100, 2)
        match_level_stats["hundred"] = (match_level_stats["total_runs"] >= 100).astype(int)
        match_level_stats["fifty"] = ((match_level_stats["total_runs"] >= 50) & (match_level_stats["total_runs"] < 100)).astype(int)
        match_level_stats["thirties"] = ((match_level_stats["total_runs"] >= 30) & (match_level_stats["total_runs"] < 50)).astype(int)
        match_level_stats["zeroes"] = (match_level_stats["total_runs"] == 0).astype(int)

        # Apply thresholds if provided
        if thresholds:
            match_level_stats = slice_threshold(match_level_stats, thresholds)


        # First, aggregate the cumulative statistics
        cumulative_agg = match_level_stats.agg({
            'total_runs': 'sum',
            'total_balls': 'sum',
            'match_id': 'count',  # Assuming each row in match_level_stats represents an innings
            'not_out': 'sum',
            'fours': 'sum',
            'sixes': 'sum',
            'dot_balls': 'sum',
            'hundred': 'sum',
            'fifty': 'sum',
            'thirties': 'sum',
            'zeroes': 'sum',
            'doubles': 'sum',
            'threes': 'sum',
            'singles': 'sum',
        }).to_frame().T  # Convert Series to DataFrame and transpose for further calculations

        cumulative_agg["innings_number"] = len(m_match)
        # Then, add the calculated fields
        cumulative_agg['average'] = round(cumulative_agg['total_runs'] / (cumulative_agg['match_id'] - cumulative_agg['not_out']), 2)
        cumulative_agg['strike_rate'] = round((cumulative_agg['total_runs'] / cumulative_agg['total_balls']) * 100, 2)
        cumulative_agg.rename(columns={"total_runs": "runs", "total_balls" : "balls"}, inplace=True)
        cumulative_agg = cumulative_agg.round(2)
        cumulative_agg = slice_top_k(thresholds, cumulative_agg)
    else:
        cumulative_agg = []

    return cumulative_agg


def get_bowling_stats(odi_ball, player, thresholds):
    # Add bowler extras column for easier calculations
    odi_ball["bowler_extras"] = odi_ball.apply(lambda x: x["noballs_extras"] + x["wides_extras"], axis=1)

    # Filter the DataFrame for the specified player
    player_data = odi_ball[odi_ball["bowler"].isin(player)]
    # Calculate match-level statistics
    match_level_stats = []
    m_match = list(odi_ball["match_id"].unique())
    print(len(m_match), "matchyyyy22")

    for (match_id, innings_number), group in player_data.groupby(["match_id", "innings_number"]):
        total_runs_given = group["runs_batter"].sum() + group["bowler_extras"].sum()
        no_balls = group["noballs_extras"].sum()
        wides = group["wides_extras"].sum()
        wickets_taken = len(group[~group["wickets_player_out"].isnull() & ~group["wickets_kind"].isin(['run out', 'retired hurt', 'obstructing the field', 'timed out'])])
        dot_balls = len(group[(group["runs_batter"] == 0) & (group["bowler_extras"] == 0)])
        valid_balls = len(group[group["bowler_extras"] == 0])
        overs_bowled = valid_balls / 6
        economy_rate = round(total_runs_given / overs_bowled, 2) if overs_bowled else 0
        bowling_average = round(total_runs_given / wickets_taken, 2) if wickets_taken else 0
        strike_rate = round(valid_balls / wickets_taken, 2) if wickets_taken else 0

        match_level_stats.append({
            "match_id": len(m_match),
            "innings_number": len(m_match),
            "total_runs_given": total_runs_given,
            "no_balls": no_balls,
            "wides": wides,
            "wickets_taken": wickets_taken,
            "dot_balls": dot_balls,
            "valid_balls": valid_balls,
            "overs_bowled": overs_bowled,
            "economy_rate": economy_rate,
            "bowling_average": bowling_average,
            "strike_rate": strike_rate
        })

    player_stats = pd.DataFrame(match_level_stats)

    # Apply thresholds if provided
    if thresholds:
        player_stats = slice_threshold(player_stats, thresholds)

    # Initialize cumulative stats with zeros for wickets categories
    wickets_categories = {str(i): 0 for i in range(1, 6)}
    wickets_categories['5+'] = 0

    # Compute cumulative statistics
    if not player_stats.empty:
        cumulative_stats = player_stats.sum(numeric_only=True).to_dict()
        cumulative_stats.update(wickets_categories)
        # Update wickets categories counts
        for wickets in player_stats["wickets_taken"]:
            if wickets >= 5:
                cumulative_stats["5+"] += 1
            elif wickets in wickets_categories:
                cumulative_stats[str(wickets)] += 1

        cumulative_stats['economy_rate'] = round(cumulative_stats['total_runs_given'] / cumulative_stats['overs_bowled'], 2) if cumulative_stats['overs_bowled'] > 0 else 0
        cumulative_stats['bowling_average'] = round(cumulative_stats['total_runs_given'] / cumulative_stats['wickets_taken'], 2) if cumulative_stats['wickets_taken'] > 0 else 0
        cumulative_stats['strike_rate'] = round(cumulative_stats['valid_balls'] / cumulative_stats['wickets_taken'], 2) if cumulative_stats['wickets_taken'] > 0 else 0
        cumulative_stats = pd.DataFrame([cumulative_stats])
        cumulative_stats = cumulative_stats.round(2)
        cumulative_stats = slice_top_k(thresholds, cumulative_stats)

    else:
        cumulative_stats = []

    return cumulative_stats

def group_bat(odi_bat, thresholds):
    # Initialize an empty list to hold the dictionary of stats for each group (match-level stats)
    match_level_stats = []
    odi_bat["bowler_extras"] = odi_bat.apply(lambda x: x["noballs_extras"] + x["wides_extras"], axis=1)
    # Calculate match-level statistics
    t1 = 0
    for team, group in odi_bat.groupby(["team"]):
        for (match_id, innings_number), innings_group in group.groupby(["match_id", "innings_number"]):
            total_runs = innings_group["runs_batter"].sum()
            t1 += total_runs
            total_extras = innings_group["extras_total"].sum()
            total_balls = innings_group[innings_group["bowler_extras"] == 0]["ball_number"].count()
            strike_rate = round(total_runs / total_balls * 100, 2) if total_balls else 0
            scores = innings_group["runs_batter"].sum()
            hundred = 1 if scores >= 100 else 0
            fifty = 1 if 50 <= scores < 100 else 0
            thirties = 1 if 30 <= scores < 50 else 0
            zeros = 1 if scores == 0 else 0
            not_out = 1 if innings_group["wickets_player_out"].isnull().all() else 0
            sixes = sum(innings_group["runs_batter"] == 6)
            fours = sum(innings_group["runs_batter"] == 4)
            doubles = sum(innings_group["runs_batter"] == 2)
            singles = sum(innings_group["runs_batter"] == 1)
            threes = sum(innings_group["runs_batter"] == 3)
            dot_balls = sum(innings_group["runs_batter"] == 0)

            match_level_stats.append({
                "team": team[0],
                "match_id": match_id,
                "innings_number": innings_number,
                "total_runs": total_runs,
                "total_balls": total_balls,
                "strike_rate": strike_rate,
                "hundred": hundred,
                "fifty": fifty,
                "thirties": thirties,
                "zeros": zeros,
                "not_out": not_out,
                "sixes": sixes,
                "fours": fours,
                "doubles": doubles,
                "singles": singles,
                "threes": threes,
                "dot_balls": dot_balls,
                "total_extras": total_extras
            })
    # print(t1, "righttttttttttt")
    batter_stats = pd.DataFrame(match_level_stats)
    if len(batter_stats):
        # Apply thresholds if provided
        if thresholds:
            batter_stats = slice_threshold(batter_stats, thresholds)

        # Compute cumulative team-level statistics
        team_stats = batter_stats.groupby(['team']).agg({
            "total_runs": "sum",
            "total_balls": "sum",
            "hundred": "sum",
            "match_id": "count",
            "fifty": "sum",
            "thirties": "sum",
            "zeros": "sum",
            "not_out": "sum",
            "sixes": "sum",
            "fours": "sum",
            "doubles": "sum",
            "singles": "sum",
            "threes": "sum",
            "dot_balls": "sum",
            "innings_number": "count",
            "total_extras": "sum"
        }).reset_index()

        # Calculate cumulative strike rate and average for team-level statistics
        team_stats['strike_rate'] = round(team_stats['total_runs'] / team_stats['total_balls'] * 100, 2)
        team_stats['average'] = round(team_stats['total_runs'] / (team_stats['match_id'] - team_stats['not_out']), 2)
        team_stats = team_stats.round(2)
        team_stats = slice_top_k(thresholds, team_stats)
    else:
        team_stats = []

    return team_stats

def group_bowl(odi_ball, thresholds):
    # Calculate match-level statistics
    match_level_stats = []
    odi_ball["bowler_extras"] = odi_ball["noballs_extras"] + odi_ball["wides_extras"]
    team_stats = []
    for team, group in odi_ball.groupby(["bowling_team"]):
        for (match_id, innings_number), innings_group in group.groupby(["match_id", "innings_number"]):
            total_bowler_runs = innings_group["runs_batter"].sum() + innings_group["bowler_extras"].sum()
            no_balls_total = innings_group["noballs_extras"].sum()
            wides_total = innings_group["wides_extras"].sum()
            wickets_taken = len(innings_group[~innings_group["wickets_player_out"].isnull() & ~innings_group["wickets_kind"].isin(['run out', 'retired hurt', 'obstructing the field', 'timed out'])])
            dot_balls = len(innings_group[(innings_group["runs_batter"] == 0) & (innings_group["bowler_extras"] == 0)])
            valid_balls = len(innings_group[innings_group["bowler_extras"] == 0])
            overs_bowled = valid_balls / 6
            economy_rate = total_bowler_runs / overs_bowled if overs_bowled else 0
            bowling_average = total_bowler_runs / wickets_taken if wickets_taken else 0
            strike_rate = valid_balls / wickets_taken if wickets_taken else 0

            match_level_stats.append({
                "bowling_team": team[0],
                "match_id": match_id,
                "innings_number": innings_number,
                "total_runs_given": total_bowler_runs,
                "no_balls": no_balls_total,
                "wides": wides_total,
                "wickets_taken": wickets_taken,
                "dot_balls": dot_balls,
                "valid_balls": valid_balls,
                "overs_bowled": overs_bowled,
                "economy_rate": economy_rate,
                "bowling_average": bowling_average,
                "strike_rate": strike_rate
            })

    bowling_stats = pd.DataFrame(match_level_stats)
    if len(bowling_stats):
        # Apply thresholds if provided
        if thresholds:
            bowling_stats = slice_threshold(bowling_stats, thresholds)

        # Compute cumulative team-level statistics
        team_stats = bowling_stats.groupby(['bowling_team']).agg({
            "total_runs_given": "sum",
            "no_balls": "sum",
            "wides": "sum",
            "wickets_taken": "sum",
            "dot_balls": "sum",
            "valid_balls": "sum",
            "overs_bowled": "sum",
            "innings_number": "count"
        }).reset_index()

        team_stats["1"] = sum(team_stats["wickets_taken"] == 6)
        team_stats["2"] = sum(team_stats["wickets_taken"] == 4)
        team_stats["3"] = sum(team_stats["wickets_taken"] == 2)
        team_stats["4"] = sum(team_stats["wickets_taken"] == 1)
        team_stats["5+"] = sum(team_stats["wickets_taken"] == 3)

        # Additional team-level stats like economy rate and average can be calculated here
        team_stats['economy_rate'] = team_stats['total_runs_given'] / team_stats['overs_bowled']
        team_stats['bowling_average'] = team_stats['total_runs_given'] / team_stats['wickets_taken'] if team_stats['wickets_taken'].sum() > 0 else 0
        team_stats['strike_rate'] = team_stats['valid_balls'] / team_stats['wickets_taken'] if team_stats['wickets_taken'].sum() > 0 else 0
        team_stats = slice_top_k(thresholds, team_stats)
        team_stats = team_stats.round(2)

    else:
        team_stats = []

    return team_stats


def group_bat_player(odi_bat, thresholds):
    # Initialize an empty list to hold the dictionary of stats for each group (match-level stats)
    match_level_stats = []
    odi_bat["bowler_extras"] = odi_bat["noballs_extras"] + odi_bat["wides_extras"]

    # Calculate match-level statistics
    for batter, group in odi_bat.groupby(["batter"]):
        for (match_id, innings_number), innings_group in group.groupby(["match_id", "innings_number"]):
            total_runs = innings_group["runs_batter"].sum()
            total_balls = innings_group[innings_group["bowler_extras"] == 0]["ball_number"].count()
            strike_rate = round(total_runs / total_balls * 100, 2) if total_balls else 0
            scores = innings_group["runs_batter"].sum()
            hundred = 1 if scores >= 100 else 0
            fifty = 1 if 50 <= scores < 100 else 0
            thirties = 1 if 30 <= scores < 50 else 0
            zeros = 1 if scores == 0 else 0
            not_out = 1 if innings_group["wickets_player_out"].isnull().all() else 0
            sixes = sum(innings_group["runs_batter"] == 6)
            fours = sum(innings_group["runs_batter"] == 4)
            doubles = sum(innings_group["runs_batter"] == 2)
            singles = sum(innings_group["runs_batter"] == 1)
            threes = sum(innings_group["runs_batter"] == 3)
            dot_balls = sum(innings_group["runs_batter"] == 0)

            match_level_stats.append({
                "batter": batter,
                "match_id": match_id,
                "innings_number": innings_number,
                "total_runs": total_runs,
                "total_balls": total_balls,
                "strike_rate": strike_rate,
                "hundred": hundred,
                "fifty": fifty,
                "thirties": thirties,
                "zeros": zeros,
                "not_out": not_out,
                "sixes": sixes,
                "fours": fours,
                "doubles": doubles,
                "singles": singles,
                "threes": threes,
                "dot_balls": dot_balls,
            })

    batter_stats = pd.DataFrame(match_level_stats)
    if len(batter_stats):
        # Apply thresholds if provided
        if thresholds:
            batter_stats = slice_threshold(batter_stats, thresholds)


        # Compute cumulative team-level statistics
        team_stats = batter_stats.groupby(['batter']).agg({
            "total_runs": "sum",
            "total_balls": "sum",
            "hundred": "sum",
            "match_id": "count",
            "fifty": "sum",
            "thirties": "sum",
            "zeros": "sum",
            "not_out": "sum",
            "sixes": "sum",
            "fours": "sum",
            "doubles": "sum",
            "singles": "sum",
            "threes": "sum",
            "dot_balls": "sum",
            "innings_number": "count"
        }).reset_index()

        # Calculate cumulative strike rate and average for team-level statistics
        team_stats['strike_rate'] = round(team_stats['total_runs'] / team_stats['total_balls'] * 100, 2)
        team_stats['average'] = round(team_stats['total_runs'] / (team_stats['match_id'] - team_stats['not_out']), 2)
        team_stats = team_stats.round(2)
        team_stats = slice_top_k(thresholds, team_stats)
    else:
        team_stats = []

    return team_stats


def group_bowl_player(odi_ball, thresholds):
    # Calculate match-level statistics
    match_level_stats = []
    odi_ball["bowler_extras"] = odi_ball["noballs_extras"] + odi_ball["wides_extras"]

    for bowler, group in odi_ball.groupby(["bowler"]):
        for (match_id, innings_number), innings_group in group.groupby(["match_id", "innings_number"]):
            total_bowler_runs = innings_group["runs_batter"].sum() + innings_group["bowler_extras"].sum()
            no_balls_total = innings_group["noballs_extras"].sum()
            wides_total = innings_group["wides_extras"].sum()
            wickets_taken = len(innings_group[~innings_group["wickets_player_out"].isnull() & ~innings_group["wickets_kind"].isin(['run out', 'retired hurt', 'obstructing the field', 'timed out'])])
            dot_balls = len(innings_group[(innings_group["runs_batter"] == 0) & (innings_group["bowler_extras"] == 0)])
            valid_balls = len(innings_group[innings_group["bowler_extras"] == 0])
            overs_bowled = valid_balls / 6
            economy_rate = total_bowler_runs / overs_bowled if overs_bowled else 0
            bowling_average = total_bowler_runs / wickets_taken if wickets_taken else 0
            strike_rate = valid_balls / wickets_taken if wickets_taken else 0

            match_level_stats.append({
                "bowler": bowler,
                "match_id": match_id,
                "innings_number": innings_number,
                "total_runs_given": total_bowler_runs,
                "no_balls": no_balls_total,
                "wides": wides_total,
                "wickets_taken": wickets_taken,
                "dot_balls": dot_balls,
                "valid_balls": valid_balls,
                "overs_bowled": overs_bowled,
                "economy_rate": economy_rate,
                "bowling_average": bowling_average,
                "strike_rate": strike_rate
            })

    bowling_stats = pd.DataFrame(match_level_stats)
    if len(bowling_stats):
        # Apply thresholds if provided
        if thresholds:
            bowling_stats = slice_threshold(bowling_stats, thresholds)

        # Compute cumulative team-level statistics
        team_stats = bowling_stats.groupby(['bowler']).agg({
            "total_runs_given": "sum",
            "no_balls": "sum",
            "wides": "sum",
            "wickets_taken": "sum",
            "dot_balls": "sum",
            "valid_balls": "sum",
            "overs_bowled": "sum",
            "innings_number": "count",
            "match_id": "count"
        }).reset_index()

        team_stats["1"] = sum(team_stats["wickets_taken"] == 6)
        team_stats["2"] = sum(team_stats["wickets_taken"] == 4)
        team_stats["3"] = sum(team_stats["wickets_taken"] == 2)
        team_stats["4"] = sum(team_stats["wickets_taken"] == 1)
        team_stats["5+"] = sum(team_stats["wickets_taken"] == 3)

        # Additional team-level stats like economy rate and average can be calculated here
        team_stats['economy_rate'] = team_stats['total_runs_given'] / team_stats['overs_bowled']
        team_stats['bowling_average'] = team_stats['total_runs_given'] / team_stats['wickets_taken'] if team_stats['wickets_taken'].sum() > 0 else 0
        team_stats['strike_rate'] = team_stats['valid_balls'] / team_stats['wickets_taken'] if team_stats['wickets_taken'].sum() > 0 else 0
        team_stats = team_stats.round(2)
        team_stats = slice_top_k(thresholds, team_stats)
    else:
        team_stats = []

    return team_stats


