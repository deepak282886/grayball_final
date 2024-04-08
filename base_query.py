from correct_names import get_correct_name


def select_base_query(input_json):
    team1 = None
    team2 = None
    team_category = None
    player1 = None
    player2 = None
    player_category = None
    detail_level = "all"

    if input_json.get("detail_level", None):
        dl = input_json.get("detail_level")
        if len(dl) and isinstance(dl, list):
            if len(dl) > 1:
                detail_level = dl[0]
        elif len(dl):
            detail_level = dl

    if input_json.get("teams_primary", None):
        team12 = input_json.get("teams_primary")
        if len(team12) and isinstance(team12, list):
            if len(team12) > 1:
                team1 = team12[0]
                team2 = team12[1]
            else:
                team1 = team12[0]
        elif len(team12):
            team1 = team12

    if input_json.get("teams_secondary", None):
        team22 = input_json.get("teams_secondary")
        if len(team22) and isinstance(team22, list):
            if len(team22) > 1:
                team2 = team22[0]
                team1 = team22[1]
            else:
                team2 = team22[0]
        elif len(team22):
            team2 = team22

    if input_json.get("teams_category", None):
        team_category = input_json.get("teams_category")

    if input_json.get("players_primary", None):
        player12 = input_json.get("players_primary")
        if len(player12) and isinstance(player12, list):
            if len(player12) > 1:
                player1 = player12[0]
                player2 = player12[1]

            else:
                player1 = player12[0]
        elif len(player12):
            player1 = player12

    if input_json.get("players_secondary", None):
        player22 = input_json.get("players_secondary")
        if len(player22) and isinstance(player22, list):
            if len(player22) > 1:
                player2 = player22[0]
                player1 = player22[1]
            else:
                player2 = player22[0]
        elif len(player22):
            player2 = player22
    if input_json.get("players_category", None):
        player_category = input_json.get("players_category")

    if team2 and not team1:
        team1 = team2

    if not team_category:
        if team1 and team2:

            team_category = "head_to_head"
        elif team1 and not team2:
            team_category = "single"

        else:
            team_category = "multiple"

    if not player_category:
        if player1 and player2:
            player_category = "head_to_head"
        elif player1 and not player2:
            player_category = "single"
        else:
            player_category = "multiple"

    if team1:
        team1x = get_correct_name(team1, "teams")
        if team1x:
            team1 = team1x
        else:
            team1 = None
    if team2:
        team2x = get_correct_name(team2, "teams")
        if team2x:
            team2 = team2x
        else:
            team2 = None

    if player1:
        player1x = get_correct_name(player1, "players")
        if player1x:
            player1 = player1x
        else:
            player1 = None

    if player2:
        player2x = get_correct_name(player2, "players")
        if player2x:
            player2 = player2x
        else:
            player2 = None

    # Initialize the base query
    base_query = "SELECT * FROM ball_by_ball_data b LEFT JOIN match_info m ON b.match_id = m.match_id WHERE 1=1"

    if team_category == "single" and team1:
        base_query += f" AND (m.team1 = '{team1}' OR m.team2 = '{team1}')"

    if player_category == "single" and player1:
        base_query += f" AND (b.batter = '{player1}' OR b.bowler = '{player1}')"

    if team_category == "head_to_head" and team1 and team2:
        base_query += f" AND ((m.team1 = '{team1}' AND m.team2 = '{team2}') OR (m.team1 = '{team2}' AND m.team2 = '{team1}'))"

    if team_category == "head_to_head" and team1 and not team2:
        base_query += f" AND (m.team1 = '{team1}' OR m.team2 = '{team1}')"

    if player_category == "head_to_head" and player1 and player2:
        base_query += f" AND ((b.batter = '{player1}' AND b.bowler = '{player2}') OR (b.batter = '{player2}' AND b.bowler = '{player1}'))"

    if player_category == "head_to_head" and player1 and not player2:
        base_query += f" AND (b.batter = '{player1}' OR b.bowler = '{player1}')"

    if player_category == "partnership" and player1 and player2:
        base_query += f" AND ((b.batter = '{player1}' AND b.non_striker = '{player2}') OR (b.batter = '{player2}' AND b.non_striker = '{player1}'))"

    if player_category == "partnership" and player1 and not player2:
        base_query += f" AND (b.batter = '{player1}' OR b.bowler = '{player1}')"

    if team_category == "multiple" and team1:
        base_query += f" AND (m.team1 = '{team1}' OR m.team2 = '{team1}')"

    if player_category == "multiple" and player1:
        base_query += f" AND (b.batter = '{player1}' OR b.bowler = '{player1}')"

    base_json = {"team1": team1, "team2": team2, "team_category": team_category,
                 "player1": player1, "player2": player2, "player_category": player_category,
                 "detail_level": detail_level}

    return base_query, base_json
