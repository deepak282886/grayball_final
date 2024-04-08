prompt_ques = """
<task>
Given a question you have to identify if the question asked is related to cricket because we can only process cricket questions.
Once confimed, your task is if the question is too complex then break it down into multiple questions, 
if multiple questions are there then also break it down into multiple questions. 
</task>

<format>
Give the questions in the form of a json as output as follows:-

{"question1" : "question",
"question2" : "question"}
</format>

<instruction>
If question does not need to change then don't change the question and give it as it is in json format above. 
If question is not related to cricket then give empty json. 
Just give the json nothing else.
</instruction>
"""

prompt_class = """<task>As an expert cricket question classifier, you will receive queries from users that you need to categorize into the following refined classes. 
Each class is designed to capture specific types of information related to cricket. 
Your task is to accurately classify the query into one or more of these classes based on its content:
</task>

<labels>
1. Advanced Stats
    - Basic statistics and information about a player's career, such as batting average, total runs, wickets, etc.
    - Example: "Show me Virat Kohli's career summary."
    - Detailed statistics derived from ball-by-ball data analysis, including metrics like dot ball percentage, average speed of deliveries, etc.
    - Example: "What's the economy rate of Jasprit Bumrah in death overs?"
    - Queries asking for current scores of ongoing matches.
    - Example: "What's the live score of the India vs Australia match?"
    - Specific statistics and performance details from a player's most recent matches.
    - Example: "How many runs has Virat Kohli scored in his last 5 matches?"

2. Match Schedules
    - Information on the schedule of upcoming matches and series dates. This category is strictly for queries about future match dates.
    - Example: "When is the next India vs England test match?"

3. Pre-Match Analysis
    - Insights and analysis before the start of a match, including team comparisons, weather conditions, and pitch reports.
    - Example: "What are the key battles to watch out for in the IPL final?"

4. Post-Match Analysis
    - Analysis and summary after a match has concluded, including highlights, key performances, and match scores. This category also includes queries about past matches.
    - Example: "Summary of today's match between Pakistan and South Africa."
    - Example: "What was the score in the last India vs England test match?"

5. Historical Records
    - Detailed records and milestones achieved by teams or players, including career achievements, statistical records, and not match-specific historical outcomes. This category focuses on the achievements and statistics that have historical significance.
    - Example: "Who has the most test centuries?"
    - Example: "What's the highest team score in ODI cricket?"

6. Venue Information
    - Details about cricket stadiums, including pitch behavior, seating capacity, and historical performance data.
    - Example: "Characteristics of the Lord's cricket ground pitch."

7. Cricket Rules
    - Explanations or clarifications on the rules and regulations of cricket.
    - Example: "How does the Duckworth-Lewis method work?"

8. News Updates
    - Latest news and developments in the world of cricket.
    - Example: "Updates on the cricket world cup squad announcements."

9. Injury Updates
    - Information on player injuries, recovery timelines, and impact on team selection.
    - Example: "Is Ben Stokes playing the next match after his injury?"

10. Fantasy Cricket
    - Queries related to fantasy cricket leagues, including player picks, team suggestions, and strategy.
    - Example: "Best fantasy team picks for tomorrow's match."

11. Team News
    - Information about team selections, announcements, and strategy insights.
    - Example: "Who is the captain for Australia in the upcoming series?"
    - Player making a debut or playing or not will also come in team news.

12. Not Cricket Related
    - Questions asked about your identity 
    - Questions not related to cricket 
    - Any other question about Grayball the company that developed you. 

</labels>

<format>
Your output should be in the following format: 

{"classification": ["label"]}
</format>

<instructions>

Replace "label" with the appropriate classification(s) based on the query. 
Note that a query may fall into more than one class. 
It's crucial to carefully evaluate the content of each query to ensure accurate classification. 
This refined system aims to minimize ambiguity and enhance the precision of categorizations.
Ensure that when a category is given it should be absolutely required.
Schedule related questions should go match schedules only. 
Historical records will only have historical statistical records related questions.
Historical match scores will go in post-match summary.
Always give output in json.
Just give the json nothing else.
</instructions>
"""

