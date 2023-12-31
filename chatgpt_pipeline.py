import random
import json
from glob import glob

from openai import OpenAI
from conversations import chat_one

import CONSTANTS as c

client = OpenAI()

system_message = """You are a dungeon master, ready to start a one shot for Dungeons and Dragons 5th edition.
Don't make any assumptions about player actions and say the total result with modifiers for any dice rolls.
If the player provides a character sheet, use it to inform your responses.  If a character is proficient in a skill,
then when they roll the dice, add the proficiency bonus and the relevant ability modifier to the result.
To get the ability modifier, subtract 10 from the ability score, divide by 2, and round down."""

def start_game(theme, setting, character_sheet):
  messages = [
    {"role": "system", "content": system_message},
    {"role": "user", "content": f"I would like to play a {theme} game in {setting}.  Here is my character sheet: {character_sheet}"},
    #{"role": "assistant", "content": chat_one.response_one},
    #{"role": "user", "content": chat_one.input_one},
    #{"role": "assistant", "content": chat_one.response_two},
    #{"role": "user", "content": chat_one.input_two},
  ]
  
  completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=messages
  )

  resp = completion.choices[0].message
  return messages + [{"role": resp.role, "content": resp.content }]

if __name__ == "__main__":
   theme = random.choice(c.DND_CAMPAIGN_THEMES)
   setting = random.choice(c.DND_SETTINGS)
   character = random.choice(glob("characters/formatted_characters/*.json"))

   print("Evaluating %s theme in %s with character %s" % (theme, setting, character))
   
   with open(character, "r", encoding="utf-8") as fh:
      character_sheet = fh.read()

   setting_decl = start_game(theme, setting, character_sheet)
   convo_num = len(glob("conversations/*"))
   with open(f"conversations/{convo_num}.json", "w") as fh:
      fh.write(json.dumps(setting_decl))