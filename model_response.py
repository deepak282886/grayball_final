import boto3
import json


def get_haiku_response(prompt):
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1',
        aws_access_key_id='AKIATROVE4AWEMIHPN46',
        aws_secret_access_key='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')

    # Variables for Bedrock API
    modelId = "anthropic.claude-3-haiku-20240307-v1:0"
    contentType = 'application/json'
    accept = 'application/json'

    # Messages
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }
    ]

    # Body
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "temperature": 0.05,
        "system": """<system> Act as a cricket expert. 
        Your task is to analyse cricket queries. 
        While doing the task, your goal is to clearly identify the specific details required for analysis. 
        Use the label description to form your response as per json schema.
        """,
        "messages": messages
    })

    # Run Bedrock API
    response = bedrock.invoke_model(
        modelId=modelId,
        contentType=contentType,
        accept=accept,
        body=body
    )

    # Print response
    response_body = json.loads(response.get('body').read())
    return response_body['content'][0]['text']


def get_match_specifics(input_q):
    prop = """<task>
    Your task is to analyse cricket queries.
    Use the json description to form your response as per json_schema.
    Your task is just extracting details from the query not add information.
    Always have detail_level parameter as described in label_description.
    </task>
    <label_description>
    [livematch : if live match is mentioned [live],
    dateofbirth : if date of birth is mentioned type: date,
    gender : if gender is mentioned,
    battingstyle : if batting style is mentioned ['right-hand-bat', 'left-hand-bat'],
    bowlingstyle : if bowling style is mentioned ['right-arm-fast', 'slow-left-arm-orthodox', 
    'right-arm-offbreak','legbreak', 'right-arm-fast-medium', 
    'left-arm-fast-medium', 'legbreak-googly', 'left-arm-fast', 'left-arm-chinaman'],
    batsman_position : if batsman position is mentioned [1,2,3,4,5,6,7,8,9,10,11],
    bowler_position : if bowling position is mentioned [1,2,3,4,5,6,7,8,9,10,11],
    ball : if ball number is mentioned [1,2,3,4,5,6],
    powerplay : if powerplay is mentioned [yes],
    fielding : if fielding stats are required [yes],
    runs : if custom number of runs are mentioned,
    innings : if innings is mentioned [1,2,3,4],
    custom_stats : ['overs', 'margin_runs', 'margin_wickets', 'matches', 'innings_batted', 'total_balls', 
    'not_outs', 'runs_scored', 'batting_average', 'strike_rate', 
    'fours', 'sixes', 'doubles', 'dot_balls_played', 'threes', 'singles', 'innings_bowled', 
    'balls_bowled', 'runs_conceded', 'wickets_taken', 'bowling_average', 
    'economy_rate', 'strike_rate_bowl', 'dot_balls_bowled', 'catches', 
    'stumpings', 'run_outs', 'byes', 'leg_byes', 'wides', 'noball'],
,
    custom_stats_count : number of custom stats,
    detail_level: ["player_level", "team_level"],
    teams_category : ["single", "head_to_head", "multiple"],
    teams_primary : "Primary Team Name",
    teams_secondary : "Secondary Team Name (for comparisons)",
    players_category : ["single", "partnership", "head_to_head", "multiple"],
    players_primary : Primary Player Name,
    players_secondary": Secondary Player Name(s) (for comparisons or partnerships)",
    league : name of the league/series, 
    match_format : name of the format if mentioned, 
    stage : stage of the tournament, 
    round : round of the tournament, 
    date : specific date, 
    venue : venue name, 
    winner : match winner name, 
    toss_won : toss winner name, 
    draw : if draw match is asked yes or no, 
    umpire : umpire name, 
    mom : man of the match, 
    overs : overs number, 
    elected : chose to ball or bat if mentined,
    super_over : if super over required yes or no, 
    follow_on : it is a cricket term that happens in test cricket if follow on required yes or no, 
    top_k : [top,last,recent,worst],
    top_k_parameter : number,
    recent_number : number of recent matches required,
    top_k_sort : ['matches', 'innings_batted', 'total_balls', 
    'not_outs', 'runs_scored', 'batting_average', 'strike_rate', 
    'fours', 'sixes', 'doubles', 'dot_balls_played', 'threes', 'singles', 'innings_bowled', 
    'balls_bowled', 'runs_conceded', 'wickets_taken', 'bowling_average', 
    'economy_rate', 'strike_rate_bowl', 'dot_balls_bowled', 'catches', 
    'stumpings', 'run_outs', 'byes', 'leg_byes', 'wides', 'noball']
    ]

    </label_description>

    <json_schema>:

    {
    "param_1" : 
     { name : choose from label_list,
    "parameter_value" : "choose value for the name",
    "range_start": "start of range if required",
    "range_end": "end of range if required",
    "operator": "choose a operator is required [less_than, more_than, equal_to, between, not_equal_to]"}
    }
    </json_schema>

    <example>

    input : How many times India has won by more than 30 runs
    
    {
    "param_1" : 
     { name : "detail_level",
    "parameter_value" : "team_level"},
    "param_2" : 
     { name : "teams_category",
    "parameter_value" : "single"},
    "param_3" : 
     { name : "players_primary",
    "parameter_value" : "india"},
    "param_4" :
    { name : "custom_stats",
    "parameter_value" : "margin_runs"},
    "param_5" :
    { name : "custom_stats_count",
    "parameter_value" : 30,
    "operator":  "more_than"},
    }

    input : Can you tell me about the recent fixture where india lost
    
    {
    "param_1" : 
     { name : "detail_level",
    "parameter_value" : "team_level"},
    "param_2" : 
     { name : "teams_category",
    "parameter_value" : "single"},
    "param_3" : 
     { name : "players_primary",
    "parameter_value" : "india"},
    "param_4" :
    { name : "winner",
    "parameter_value" : "india",
    "operator" : "not_equal_to"},
    }
    
    input : what is the strike rate of virat kohli?

    {
    "param_1" : 
     { name : "detail_level",
    "parameter_value" : "player_level"},
    "param_2" : 
     { name : "players_category",
    "parameter_value" : "single"},
    "param_3" : 
     { name : "players_primary",
    "parameter_value" : "virat kohli"}
    }

    input : "how did kohli performed in his hundredth match?"

    {
    "param_1" : 
     { name : "detail_level",
    "parameter_value" : "player_level"},
    "param_2" : 
     { name : "players_category",
    "parameter_value" : "single"},
    "param_3" : 
     { name : "players_primary",
    "parameter_value" : "virat kohli"},
    "param_4" : 
     { name : "custom_stats",
    "parameter_value" : "matches"},
    "param_5" :
    { name : "custom_stats_count",
    "parameter_value" : 100,
    "operator":  "equal_to"},
    }

    input : "how did kohli performed from 2022 to 2024?"

    {
    "param_1" : 
     { name : "detail_level",
    "parameter_value" : "player_level"},
    "param_2" : 
     { name : "players_category",
    "parameter_value" : "single"},
    "param_3" : 
     { name : "players_primary",
    "parameter_value" : "virat kohli"},
    "param_4" : 
     { name : "date",
    "range_start" : 2022,
    "range_end" : 2024},
    }

    input : what is the strike rate of virat kohli in the ongoing match?

    {
    "param_1" : 
     { name : "detail_level",
    "parameter_value" : "player_level"},
    "param_2" : 
     { name : "players_category",
    "parameter_value" : "single"},
    "param_3" : 
     { name : "players_primary",
    "parameter_value" : "virat kohli"},
    "param_4" : 
     { name : "livematch",
    "parameter_value" : "live"}
    }

    </example>

    <instruction>
    Always give detail_level and team_category or player_category.
    If no value is mentioned for stats then don't give custom stats. 
    If anything asked about fielding then give fielding as yes. 
    When it is nothing then don't give zero as well. Just give empty.
    Margin runs are runs by which a teams wins a match eg. India won by 30 runs means 30 runs margin similarly for wickets.
    Don't mention over range if no custom range is asked excluding the powerplays and phases.
    Don't mention over range or any other key if not explicitly mentioned in the query.
    If nothing is available then just give empty json.
    Don't give any comment or explanation. 
    Just extract the information given in the question.
    Verify your result before giving the answer.
    Don't output keys with empty values.
    Don't get confused between team name and player name.
    No information should be missing from the output json.
    You can't give custom_boundaries_count alone. 
    If any custom_stats is mentioned only then use both custom_stats and custom_stats_count as per the given stats in it's list.
    </instruction>
    """

    prompt_f = f"{prop} query: {input_q}"
    response = get_haiku_response(prompt_f)

    return response
