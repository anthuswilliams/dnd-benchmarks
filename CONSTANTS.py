DND_CAMPAIGN_THEMES = [
    "Pirate Adventure",
    "Political Intrigue",
    "Epic Quest",
    "Mystery/Investigation",
    "Horror/Survival",
    "Dungeon Delving",
    "War and Conflict",
    "Exploration/Discovery",
    "Heist/Crime",
    "Monster Hunting",
]

DND_SETTINGS = [
    "Forgotten Realms",
    "Dragonlance",
    "Greyhawk",
    "Eberron",
    "Ravenloft",
    "Planescape",
    "Dark Sun",
    "Spelljammer",
    "Mystara",
    "Ravnica",
]

SYSTEM_MESSAGE = """
You are a dungeon master, ready to start a one shot for Dungeons and Dragons 5th edition.
Don't make any assumptions about player actions and say the total result with modifiers for any dice rolls.
If the player provides a character sheet, use it to inform your responses.  If a character is proficient in a skill,
then when they roll the dice, add the proficiency bonus and the relevant ability modifier to the result.
To get the ability modifier, subtract 10 from the ability score, divide by 2, and round down."""

JUDGE_PROMPT = """
Please act as an impartial judge and evaluate the quality of the response provided by an
AI assistant to the user question displayed below. Your evaluation should consider factors
such as the helpfulness, relevance, accuracy, depth, creativity, and level of detail of
the response. Begin your evaluation by providing a short explanation. Be as objective as
possible. After providing your explanation, please rate the response on a scale of 1 to 10
by strictly following this format: "[[rating]]", for example: "Rating: [[5]]"
"""