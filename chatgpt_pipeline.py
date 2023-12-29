from openai import OpenAI
from conversations import chat_one

client = OpenAI()

with open("characters/formatted_characters/02_formatted.json", "r") as file:
    character_sheet = file.read()

system_message = """You are a dungeon master, ready to start a one shot for Dungeons and Dragons 5th edition.
Don't make any assumptions about player actions and say the total result with modifiers for any dice rolls.
If the player provides a character sheet, use it to inform your responses."""

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a dungeon master, ready to start a one shot for Dungeons and Dragons 5th edition. Don't make any assumptions about player actions and say the total result with modifiers for any dice rolls."},
    {"role": "user", "content": f"I would like to play a pirate adventure.  Here is my character sheet: {character_sheet}"},
    {"role": "assistant", "content": chat_one.response_one},
    {"role": "user", "content": chat_one.input_one},
    {"role": "assistant", "content": chat_one.response_two},
    {"role": "user", "content": chat_one.input_two},
  ]
)

print(completion.choices[0].message)