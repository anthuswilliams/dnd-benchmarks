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
Please act as an impartial judge and evaluate the accuracy of the response provided by an
AI assistant to the user question displayed below. The user will supply the question, the correct answer,
and the AI assistant's prediction in the following format:

[Question]
The user's question
[Correct Answer]
The correct answer to the user's question
[The Start of Assistant's Answer]
The answer the AI assistant returned
[The End of the Assistant's Answer]

If the AI assistant's answer is correct, respond with the value 1. If the AI assistant's answer is incorrect, respond with the value 0.
Do NOT consider the assistant's helpfulness, tone, or any other factor. Consider ONLY the accuracy of the assistant's answer.
"""
