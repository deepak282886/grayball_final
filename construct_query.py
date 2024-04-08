def map_param(var_check):
    map_col = {"gender": "b.gender",
               "batsman_position": "b.batter_number",
               "bowler_position": "b.bowler_number",
               "ball": "b.ball_number",
               "runs": "b.runs_batter",
               "wickets": "wickets_taken",
               "matches": "match_id",
               "league": "m.event_name",
               "season": "m.season",
               "date": "m.dates",
               "venue": "m.venue",
               "winner": "m.outcome_winner",
               "toss_won": "m.toss_winner",
               "umpire": "m.official_umpires",
               "mom": "m.player_of_match",
               "overs": "b.over_number",
               "elected": "m.toss_decision",
               "margin_runs": "m.outcome_runs",
               "margin_wickets": "m.margin_wickets",
               "four": "fours",
               "six": "sixes",
               "single": "singles",
               "double": "doubles",
               "three": "threes",
               "byes": "byes",
               "leg_byes": "wides",
               "noball": "no_balls"
               }

    out_var = ""
    if map_col.get(var_check, None):
        out_var = map_col.get(var_check)

    return out_var


def construct_query_conditions(params):

    query_parts = []
    threshold_list = []
    view_json = {}
    # Mapping for the operators to be used in the query string
    operators = {
        'less_than': '<',
        'more_than': '>',
        'equal_to': '==',
        'not_equal_to': '!=',
        # 'between' will be handled separately
    }

    handled_keys = set()  # Keep track of keys already handled to avoid duplication
    field = False
    for key, value in params.items():
        if key == "custom_stats" and value in ['catches', 'stumpings', 'run_outs']:
            field = True

    if field:
        params["fielding"] = "yes"

    for key, value in params.items():

        if key in ["match_format", "innings", "detail_level", "teams_category",
                   "teams_primary", "teams_secondary", "players_primary", "players_secondary", "players_category"]:
            continue

        elif key in ["fielding", "powerplay"] and key not in handled_keys:
            handled_keys.add(key)
            view_json[key] = value

        elif "top" in key and key not in handled_keys:
            handled_keys.add(key)
            threshold_list.append({key: value})

        elif "count" in key and key not in handled_keys:
            handled_keys.add(key)
            cus_name = key.split("_count")[0]
            col_value = params[cus_name]
            handled_keys.add(cus_name)
            col_map = map_param(col_value)
            col_operator = f"{cus_name}_operator"
            handled_keys.add(col_operator)
            if col_operator in params.keys():
                operator = operators.get(params[col_operator], '==')
                if len(col_map) and value:
                    threshold_list.append({"name": col_map, "operator": operator, "value": value})

        elif '_operator' in key and key not in handled_keys:
            field_name = key.replace('_operator', '')
            operator_key = value
            handled_keys.add(field_name)
            handled_keys.add(key)
            if operator_key != 'between':
                operator = operators.get(operator_key, '=')
                col_map = map_param(field_name)
                if len(col_map):
                    query_part = f'{col_map} {operator} {params.get(field_name)}'
                    query_parts.append(query_part)
            else:
                start_key = f'{field_name}_range_start'
                end_key = f'{field_name}_range_end'
                if start_key in params and end_key in params:
                    handled_keys.add(start_key)
                    handled_keys.add(end_key)
                    col_map = map_param(field_name)
                    if len(col_map):
                        query_part = f'{col_map} >= {params[start_key]} and {col_map} <= {params[end_key]}'
                        query_parts.append(query_part)
                        handled_keys.update([start_key, end_key])

        elif 'range_start' in key or 'range_end' in key and key not in handled_keys:

            base_key = key.rsplit('_', 2)[0]
            base_key2 = map_param(base_key)
            if len(base_key2):
                if base_key not in handled_keys:  # Check if not already handled
                    start_key = f'{base_key}_range_start'
                    end_key = f'{base_key}_range_end'
                    handled_keys.add(start_key)
                    handled_keys.add(end_key)

                    handled_keys.add(base_key)
                    if start_key in params and end_key in params:
                        query_part = f'{base_key} >= {params[start_key]} and {base_key2} <= {params[end_key]}'
                        query_parts.append(query_part)
                        handled_keys.update([start_key, end_key])

        elif not key.startswith("custom"):
            if key not in handled_keys and f"{key}_operator" not in params.keys() and f"{key}_count" not in params.keys():
                x_key = map_param(key)
                if len(x_key):
                    query_parts.append(f'{x_key} = "{value}"')

    return " AND ".join(query_parts), threshold_list, view_json
